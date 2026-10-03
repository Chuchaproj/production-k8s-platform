import subprocess
from pathlib import Path

import yaml


def main():
    expected = list(yaml.safe_load_all(Path("k8s/platform.yaml").read_text()))
    rendered = subprocess.check_output(
        ["helm", "template", "platform", "helm/platform", "--namespace", "platform"],
        text=True,
    )
    actual = list(yaml.safe_load_all(rendered))
    if expected != actual:
        raise SystemExit("Manifest objects differ from Helm output; run make manifests and review the diff")
    print(f"Manifest objects match Helm output ({len(actual)} documents)")


if __name__ == "__main__":
    main()
