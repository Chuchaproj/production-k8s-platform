#!/usr/bin/env bash
set -euo pipefail
gitleaks git --redact --no-banner .
gitleaks git --pre-commit --staged --redact --no-banner .
scan_dir="$(mktemp -d)"
trap 'rm -rf "$scan_dir"' EXIT
python3 - "$scan_dir" <<'PYFILES'
import pathlib
import shutil
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
files = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
for raw in set(files.split(b"\0")) - {b""}:
    source = pathlib.Path(raw.decode())
    if source.is_file():
        target = root / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
PYFILES
gitleaks dir "$scan_dir" --redact --no-banner
