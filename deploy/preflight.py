"""Read-only deployment admission; never pulls images or initializes data."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []
    expected = {
        "PYTHON_BASE_IMAGE": "python:3.12.8-slim-bookworm",
        "NGINX_BASE_IMAGE": "nginx:1.30.6-alpine",
        "POSTGRES_IMAGE": None,
        "UV_BASE_IMAGE": None,
    }
    for key, prefix in expected.items():
        value = os.environ.get(key, "")
        if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}", value):
            failures.append(f"{key}: verified digest required")
        elif value.endswith("0" * 64):
            failures.append(f"{key}: zero digest is not verified")
        elif prefix and value.split("@")[0] not in {prefix, f"docker.io/library/{prefix}"}:
            failures.append(f"{key}: approved version required")

    try:
        project = tomllib.loads((root / "backend/pyproject.toml").read_text())
        lock = tomllib.loads((root / "backend/uv.lock").read_text())
        if project["project"]["requires-python"] != "==3.12.8":
            failures.append("backend: exact Python declaration required")
        if lock.get("requires-python") != "==3.12.8":
            failures.append("backend: exact lock baseline required")
        if not any(p["name"] == "uvicorn" and p["version"] == "0.37.0"
                   for p in lock.get("package", [])):
            failures.append("backend: locked Uvicorn 0.37.0 required")
    except (OSError, ValueError, KeyError):
        failures.append("backend: project and valid lock must be delivered")
    if not (root / "frontend/dist/index.html").is_file():
        failures.append("frontend: real dist delivery required")

    if sys.platform != "linux":
        failures.append("environment: Netcatty Linux required")
    else:
        for key, default in [
            ("RAG_PGDATA_ROOT", "/opt/rag-story-1-1/postgres"),
            ("RAG_LOCK_ROOT", "/opt/rag-story-1-1/locks"),
            ("RAG_ASSET_ROOT", "/opt/rag-story-1-1/assets"),
        ]:
            path = Path(os.environ.get(key, default)).resolve()
            allowed = Path("/opt/rag-story-1-1")
            if not path.is_relative_to(allowed) or not path.is_dir():
                failures.append(f"{key}: existing project directory required")
                continue
            result = subprocess.run(
                ["findmnt", "-T", str(path), "-n", "-o", "FSTYPE"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode or result.stdout.strip() not in {"ext4", "xfs", "btrfs"}:
                failures.append(f"{key}: verified local filesystem required")
    for key in ["RAG_TLS_CERT_FILE", "RAG_TLS_KEY_FILE",
                "RAG_POSTGRES_PASSWORD_FILE", "RAG_POSTGRES_PGPASS_FILE"]:
        if not Path(os.environ.get(key, "/nonexistent")).is_file():
            failures.append(f"{key}: existing secret file required")
    print(json.dumps({"status": "blocked" if failures else "ready-for-build",
                      "failures": failures}, indent=2))
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
