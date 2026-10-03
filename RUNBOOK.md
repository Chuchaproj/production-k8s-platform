# Redis outage runbook

## Symptom

`GET /items` returns 503 or Ingress returns 503 after all pods become unready. `GET /live` stays 200; `GET /ready` fails. Writes may succeed even while cache invalidation fails. Never blindly retry POST without an idempotency key; this application intentionally has none.

## Observe and diagnose

Look at `dependency_failures_total{dependency="redis"}`, HTTP 5xx rate and p95 latency. Prometheus `up` alone does not prove readiness. In Loki query `{job="backend"} |= "503"`; stdout logs carry route/status/duration. A scrape outage is a different failure.

```bash
docker compose ps
docker compose logs --tail=100 backend redis
docker compose exec redis redis-cli ping
curl -i http://127.0.0.1:8280/ready
kubectl --context kind-portfolio -n platform get pods,endpoints,events
kubectl --context kind-portfolio -n platform logs deployment/platform-backend -c backend --tail=100
kubectl --context kind-portfolio -n platform describe pod -l app=platform-backend
```

## Root cause and safe reproduction

In the controlled drill the operator stops Redis: `make incident`. Kubernetes equivalent in the dedicated lab: `kubectl --context kind-portfolio -n platform scale statefulset/platform-redis --replicas=0`. The API requires Redis and returns a bounded 503 instead of hanging. In a real event verify logs, endpoints, DNS (`getent hosts redis` in a diagnostic container), TCP reachability and resource pressure before assigning cause. Do not interpret the injected cause as a universal diagnosis.

## Recovery

`make recover`, then `make smoke`. Kubernetes: scale Redis back to 1, wait for the StatefulSet rollout and check API readiness via port-forward. Confirm error rate recedes, not only process start. An alert's `for` and rate window delay firing/resolution. Preserve PVCs; deleting data is not a recovery step.

## Prevention

Consider cache fail-open if business semantics allow it, Redis HA, a circuit breaker, bounded retries with jitter, proper write idempotency and independent synthetic readiness alerts. Test outage behavior before rollout. Maintain a DB restore rehearsal; backend replicas cannot compensate for loss of a single database.
