# Local validation — production-k8s-platform

## Final portfolio audit

The final audit rebuilt the documented custom image tag, reran application tests and applicable linters, and ran Trivy with all detected severities. [SECURITY.md](SECURITY.md) supersedes the previous image snapshot. Local Git history is preserved with additional normal commits. No publication or hosted workflow run occurred.

Current source, staged files and history were scanned. Local ignored generated `.env` files were scanned separately: two credential detections in the Kubernetes lab, three in the SRE lab; the IaC service has no credential `.env`. Credentials remain private, ignored and mode 0600; their values are not included in any report. Publication/source scans reported no leaks.

## Observed results

| Check | Result | Evidence / scope |
|---|---|---|
| Application tests | PASS | 4 tests; health, WebSocket/API behavior and versioned cache checks. TestClient emits one development deprecation warning about httpx. |
| Static checks | PASS | Ruff, ShellCheck, yamllint and Hadolint; generated Kubernetes YAML checked separately. |
| Docker build and Compose configuration | PASS | Non-root backend built; `docker compose config --quiet` accepted the generated local environment. Single-platform build without provenance imports into kind. |
| Compose deployment | PASS | PostgreSQL/Redis/backend/Nginx/observability started; exact newly inserted item was read back and WebSocket echo passed through Nginx. |
| Dependency incident | PASS | Redis stopped: API 503; Redis restored: smoke succeeded. |
| Observability | PASS | Backend and Prometheus targets up; Grafana health and provisioned dashboard; Loki log ingestion observed. Promtool config, rules and outage unit test passed. |
| Helm | PASS | `helm lint`, `helm template`; icon recommendation is informational. Optional Secret rejects missing values, and renders all three required keys from protected generated values. |
| Kubernetes manifests | PASS | Rendered objects accepted by Kubernetes 1.37 server dry-run using kubectl 1.37.1; chart installed on disposable kind. Raw manifests have the same resource ownership and were schema-checked, not installed over Helm. |
| Kubernetes API / ingress | PASS | REST through Traefik; live WebSocket through Service and Traefik ingress; both backend replicas Ready. |
| Persistence | PASS | Newly written row survived PostgreSQL pod replacement; PVC remained Bound; connection pool recovered. |
| Metrics / HPA | PASS | Prometheus discovered both backend pod targets; metrics-server supplied CPU; HPA settled at two replicas with healthy CPU measurements (final snapshot 15% / 70%). Scale-out under sustained CPU pressure was not exercised. |
| Release lifecycle | PASS | Helm upgrade, rollback to a healthy revision and upgrade back; rollout readiness confirmed. |
| Kubernetes Redis incident | PASS | Redis scaled to zero: API 503; scaled back: readiness and smoke restored. |
| Terraform / Ansible | NOT APPLICABLE | These tools belong to the separate IaC project. |

## Corrections verified during implementation

Docker Desktop initially left new containers in Created. An explicitly authorized restart restored container creation; existing Grandora containers were restored and remained healthy. Initial concurrent labs on a three-node kind cluster exhausted this host's resources and caused API timeouts. The final full runtime sequence passed on the documented single-node profile with other labs stopped. The optional three-node layout is provided, but is not evidence of real HA.

Docker Desktop containerd rejected imported dependency archives containing multi-platform content. Locally built backend images now use `provenance: false`; kind imports succeeded. Dependencies are pulled by cluster nodes. Pod configuration is reloaded on Helm releases; singleton monitoring may briefly restart during an upgrade.

## NOT TESTED and remaining limitations

- Real node-loss tolerance, multi-host HA, CPU-driven HPA scale-out, long-lived connection draining under load and public TLS ingress.
- Separate raw-manifest deployment ownership; schema validation was executed, runtime installation used Helm.
- External alert delivery and every alert's real firing/clearing transition. Rule syntax and one outage unit scenario were tested.
- Backup restoration, disaster recovery, schema migrations and remote storage recovery.
- API authentication, Redis authentication, NetworkPolicy and data-tier replication are not implemented; this is a private homelab.
- Grafana Kubernetes storage is ephemeral; local kind storage is node-local. PVC persistence is not a backup.
- Runtime Python dependency audit reported no known vulnerabilities in the pinned dependency graph; this does not erase the OS findings below.

The disposable kind cluster and Compose services were removed after testing. Compose named volumes remain for local inspection; deletion of kind also deletes its node-local lab data.

## Validation boundary

Date: 2026-10-03. Host: macOS, 8 GiB physical RAM; Docker Desktop Linux VM approximately 3.8 GiB. Runtime checks were performed sequentially. Docker 29.5.3, Compose 5.1.4, Python 3.11, Trivy 0.75.0 and Gitleaks 8.30.0 were available. No paid resources were created. PASS means the stated check was observed locally, not that every production failure mode is covered.

`make install`, application tests, Docker builds and the documented local deployment/smoke/cleanup paths were exercised. Sources are independently versioned in this repository. Commit dates are real; no history was squashed or backdated. GitHub publication is pending explicit approval.

## Security and publication checks

- PASS: Gitleaks scanned local Git history, staged changes and the tracked publication tree. No finding was reported. This is a detector result, not proof that every possible secret is absent.
- PASS: `.env`, environment variants, virtual environments, generated artifacts and private key files are ignored; `.env.example` is tracked. No local credential file is included in the publication tree.
- PASS WITH SCOPE LIMITS: the final Alpine custom runtime scan reports zero detected vulnerabilities. The previous Debian image had 44 HIGH; the audit investigates every unique CVE and removes affected base packages without suppressions. See [security report](docs/security-scan.md). Third-party stack images and exploitability were not audited. The CI custom-runtime vulnerability gate blocks HIGH/CRITICAL; secret scanning also blocks.
- PASS: actionlint and YAML lint checked workflow syntax. GitHub Actions execution, environment protection and CI status badges are **NOT TESTED** because the repository has not been published. No badge asserts a successful remote check.

## Recheck

Run `make install test lint secrets` in a clean checkout with the prerequisites from README. Generate local credentials where required; do not copy someone else's `.env`. Follow README deployment and cleanup commands one project at a time. Image findings and dependency versions are a dated snapshot; refresh scans before publication or wider use.

Final runtime recheck: rebuilt Alpine Compose REST/WS and Redis recovery; Grafana shared payload read-back; smoke passed with more than 100 rows. Fresh kind install, shared telemetry configuration, Traefik REST/WS, PostgreSQL pod replacement, both backend scrape targets, Redis recovery, HPA CPU (17% / 70%, two replicas), upgrade/rollback and server dry-run all passed. Cold startup initially restarted API pods while PostgreSQL was still unavailable; rollout converged and final application checks passed. Generated manifests match the chart. Multi-host failover remains NOT TESTED.
