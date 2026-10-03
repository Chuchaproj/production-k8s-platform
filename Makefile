.PHONY: init install test lint up down smoke incident recover helm-check
init:
	python3 scripts/init-env.py
install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
test:
	.venv/bin/python -m pytest -q
lint:
	.venv/bin/ruff check app tests scripts
	shellcheck scripts/*.sh
	yamllint -c .yamllint compose.yaml monitoring helm/platform/files .github
	hadolint Dockerfile
up:
	docker compose up -d --build --wait --wait-timeout 180
down:
	docker compose down
smoke:
	python3 scripts/smoke.py
incident:
	bash scripts/incident.sh inject
recover:
	bash scripts/incident.sh recover
helm-check:
	helm lint helm/platform
	helm template platform helm/platform > /tmp/platform-rendered.yaml

.PHONY: secrets
secrets:
	bash scripts/check-secrets.sh

.PHONY: manifests manifests-check
manifests:
	helm template platform helm/platform --namespace platform > k8s/platform.yaml
manifests-check:
	helm template platform helm/platform --namespace platform | diff -u k8s/platform.yaml -
