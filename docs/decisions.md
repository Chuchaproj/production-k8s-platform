# Architecture decisions

* PostgreSQL is the durable source of truth. The SQL query is capped at 100 rows; no promise of pagination or migration automation.
* Redis caches list reads for five seconds. Writes commit in PostgreSQL and then increment a Redis generation; readers publish under the generation they observed, so concurrent old fills do not overwrite the active generation. The two stores are not atomic: if generation invalidation fails, a stale cache can survive for at most five seconds. Redis is deliberately required to exercise its outage; a real optional cache should fall back to DB within a capacity budget.
* HTTP and WebSocket share Nginx. Compose DNS resolves service names; TCP carries HTTP/WebSocket and DB sessions. CoreDNS also serves UDP/TCP DNS in Kubernetes. Ingress TLS and public DNS are deliberately outside the isolated quick start.
* Each process has a five-connection pool. At max four replicas, application pools consume up to 20 DB connections; reserve capacity for maintenance/exporters. HPA is CPU-based and cannot solve DB saturation.
* PDB affects voluntary evictions, not node crashes. Soft spreading allows a single-node lab; hard spreading would leave replicas Pending without enough nodes.
* Single data replicas and local PVCs make this runnable, not highly available. A production design needs managed/replicated databases, network controls, recovery objectives and tested backups.
* Seven-day telemetry retention is a lab cap, not a business retention policy. Alert thresholds and SLOs are proposed engineering exercises, not observed service guarantees.

Primary references: [probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [histograms](https://prometheus.io/docs/practices/histograms/), [Loki/Alloy](https://grafana.com/docs/loki/latest/setup/install/docker/).

The Kubernetes Ingress uses Traefik; Compose retains standalone Nginx. Community ingress-nginx retired in March 2026; do not install an unmaintained controller for this portfolio. See [Kubernetes statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/).
