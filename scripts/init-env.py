#!/usr/bin/env python3
import secrets
import os
from pathlib import Path

path = Path(".env")
if path.exists():
    raise SystemExit(".env already exists; refusing to overwrite")
with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as output:
    output.write("COMPOSE_PROJECT_NAME=platform\nPOSTGRES_PASSWORD=" + secrets.token_hex(24) +
                "\nGRAFANA_PASSWORD=" + secrets.token_hex(24) + "\n")
print("Created .env with random local credentials")
