#!/usr/bin/env python3
import secrets
from pathlib import Path

path = Path(".env")
if path.exists():
    raise SystemExit(".env already exists; refusing to overwrite")
path.write_text("COMPOSE_PROJECT_NAME=platform\nPOSTGRES_PASSWORD=" + secrets.token_hex(24) +
                "\nGRAFANA_PASSWORD=" + secrets.token_hex(24) + "\nLAB_LATENCY_SECONDS=0\n")
path.chmod(0o600)
print("Created .env with random local credentials")
