from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


class Connection:
    async def execute(self, sql, params=None):
        return SimpleNamespace(fetchone=AsyncMock(return_value=(7,)),
                               fetchall=AsyncMock(return_value=[(7, "lab")]))


class Pool:
    @asynccontextmanager
    async def connection(self):
        yield Connection()


@pytest.fixture
def client():
    app.state.pool = Pool()
    app.state.cache = SimpleNamespace(ping=AsyncMock(), get=AsyncMock(return_value=None),
                                      incr=AsyncMock(return_value=1), setex=AsyncMock())
    return TestClient(app)


def test_rest_and_validation(client):
    assert client.get("/ready").status_code == 200
    assert client.post("/items", json={"name": "lab"}).json() == {"id": 7, "name": "lab"}
    assert client.post("/items", json={"name": ""}).status_code == 422
    assert client.get("/items").json() == [{"id": 7, "name": "lab"}]


def test_outage_keeps_liveness(client):
    app.state.cache.ping.side_effect = ConnectionError()
    app.state.cache.get.side_effect = ConnectionError()
    assert client.get("/items").status_code == 503
    assert client.get("/ready").status_code == 503
    assert client.get("/live").status_code == 200
    assert "dependency_failures_total" in client.get("/metrics").text


def test_websocket(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_text("hello")
        assert ws.receive_json() == {"echo": "hello"}


def test_versioned_cache_and_write_invalidation(client):
    app.state.cache.get.side_effect = [b"4", b'[{"id":9,"name":"cached"}]']
    assert client.get("/items").json() == [{"id": 9, "name": "cached"}]
    assert app.state.cache.setex.await_count == 0
    assert client.post("/items", json={"name": "new"}).status_code == 201
    app.state.cache.incr.assert_awaited_once_with("items:version")
