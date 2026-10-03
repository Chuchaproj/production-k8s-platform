import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field
from redis.asyncio import Redis

logger = logging.getLogger("platform")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
log_dir = os.getenv("LOG_DIR")
if log_dir:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger.addHandler(logging.FileHandler(Path(log_dir) / "app.log"))
requests = Counter("http_requests_total", "HTTP responses", ["method", "route", "status"])
latency = Histogram("http_request_duration_seconds", "HTTP duration", ["method", "route"],
                    buckets=[.01, .05, .1, .25, .5, 1, 2, 5, 10])
failures = Counter("dependency_failures_total", "Failed dependency operations", ["dependency"])


@asynccontextmanager
async def lifespan(app):
    pool = AsyncConnectionPool(os.environ["DATABASE_URL"], min_size=1, max_size=5,
                               timeout=2, open=False, kwargs={"connect_timeout": 3})
    cache = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=2, socket_connect_timeout=2)
    await pool.open()
    app.state.pool, app.state.cache = pool, cache
    try:
        await pool.wait(timeout=30)
        async with pool.connection() as conn:
            await conn.execute("SELECT pg_advisory_xact_lock(42810)")
            await conn.execute("CREATE TABLE IF NOT EXISTS items (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL)")
        yield
    finally:
        await cache.aclose()
        await pool.close()


app = FastAPI(title="Homelab platform", lifespan=lifespan)


@app.middleware("http")
async def observe(request, call_next):
    start = time.monotonic()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route not in ("/metrics", "/live", "/ready"):
            duration = time.monotonic() - start
            requests.labels(request.method, route, str(status)).inc()
            latency.labels(request.method, route).observe(duration)
            logger.info(json.dumps({"method": request.method, "route": route,
                                    "status": status, "duration_seconds": duration}))


@app.get("/live")
async def live():
    return {"status": "alive"}


@app.get("/ready")
async def ready():
    try:
        async with app.state.pool.connection() as conn:
            await conn.execute("SELECT 1")
        await app.state.cache.ping()
    except Exception:
        raise HTTPException(503, "Dependencies unavailable") from None
    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")


class Item(BaseModel):
    name: str = Field(min_length=1, max_length=200)


@app.post("/items", status_code=201)
async def create_item(item: Item):
    try:
        async with app.state.pool.connection() as conn:
            cursor = await conn.execute("INSERT INTO items(name) VALUES (%s) RETURNING id", (item.name,))
            row = await cursor.fetchone()
    except Exception:
        failures.labels("postgres").inc()
        raise HTTPException(503, "Database unavailable") from None
    # Invalidate cache after the transaction commits; reads use DB as source of truth.
    try:
        await app.state.cache.incr("items:version")
    except Exception:
        failures.labels("redis").inc()
        logger.warning('cache_invalidation_failed')
    return {"id": row[0], "name": item.name}


@app.get("/items")
async def list_items():
    # Redis is a required dependency in this lab so its outage is observable as 503.
    try:
        version = await app.state.cache.get("items:version") or b"0"
        if isinstance(version, bytes):
            version = version.decode()
        cache_key = f"items:{version}"
        cached = await app.state.cache.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        failures.labels("redis").inc()
        raise HTTPException(503, "Cache unavailable") from None
    try:
        async with app.state.pool.connection() as conn:
            cursor = await conn.execute("SELECT id, name FROM items ORDER BY id DESC LIMIT 100")
            rows = await cursor.fetchall()
    except Exception:
        failures.labels("postgres").inc()
        raise HTTPException(503, "Database unavailable") from None
    result = [{"id": row[0], "name": row[1]} for row in rows]
    try:
        await app.state.cache.setex(cache_key, 5, json.dumps(result))
    except Exception:
        failures.labels("redis").inc()
        logger.warning("cache_fill_failed")
    return result


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            await ws.send_json({"echo": message})
    except WebSocketDisconnect:
        return
