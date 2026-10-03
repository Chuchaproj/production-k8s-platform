#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  inject) docker compose stop redis ;;
  recover) docker compose start redis ;;
  *) echo 'Usage: bash scripts/incident.sh inject|recover' >&2; exit 2 ;;
esac
