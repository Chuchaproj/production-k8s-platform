#!/usr/bin/env bash
set -euo pipefail
gitleaks git --redact --no-banner .
gitleaks git --pre-commit --staged --redact --no-banner .
scan_dir="$(mktemp -d)"
trap 'rm -rf "$scan_dir"' EXIT
git archive HEAD | tar -x -C "$scan_dir"
gitleaks dir "$scan_dir" --redact --no-banner
