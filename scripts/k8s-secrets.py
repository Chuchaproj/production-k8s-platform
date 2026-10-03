#!/usr/bin/env python3
import argparse
import json
import os
import secrets
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--context", default="kind-portfolio")
parser.add_argument("--namespace", default="platform")
parser.add_argument("--release", default="platform")
args = parser.parse_args()
password = os.getenv("POSTGRES_PASSWORD") or secrets.token_hex(24)
grafana = os.getenv("GRAFANA_PASSWORD") or secrets.token_hex(24)
secret = {"apiVersion": "v1", "kind": "Secret", "type": "Opaque",
          "metadata": {"name": "platform-secrets", "namespace": args.namespace},
          "stringData": {"POSTGRES_PASSWORD": password, "GRAFANA_PASSWORD": grafana,
                         "DATABASE_URL": f"postgresql://platform:{password}@{args.release}-postgres:5432/platform"}}
# Create, rather than apply: accidental regeneration must not rotate a live DB credential.
subprocess.run(["kubectl", "--context", args.context, "create", "-f", "-"], input=json.dumps(secret), text=True, check=True)
