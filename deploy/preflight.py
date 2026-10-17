"""Read-only deployment admission; never pulls images or initializes data."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


def image_failure(key: str, value: str, approved: str | None) -> str | None:
    if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}", value):
        return f"{key}: verified digest required"
    if value.endswith("0" * 64):
        return f"{key}: zero digest is not verified"
    if approved and value.split("@")[0] not in {approved, f"docker.io/library/{approved}"}:
        return f"{key}: approved version required"
    return None


def numeric_id(value: str) -> int | None:
    return int(value) if re.fullmatch(r"[1-9][0-9]{0,9}", value) else None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []
    if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 12, 8):
        failures.append("environment: CPython 3.12.8 required for admission")
    expected = {
        "PYTHON_BASE_IMAGE": "python:3.12.8-slim-bookworm",
        "NGINX_BASE_IMAGE": "nginx:1.30.6-alpine",
        "POSTGRES_IMAGE": None,
        "UV_BASE_IMAGE": None,
    }
    for key, prefix in expected.items():
        failure = image_failure(key, os.environ.get(key, ""), prefix)
        if failure:
            failures.append(failure)

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
    if not (root / "deploy/worker/healthcheck.py").is_file():
        failures.append("worker: liveness probe file required")

    if sys.platform != "linux":
        failures.append("environment: Netcatty Linux required")
    else:
        pg_uid = numeric_id(os.environ.get("RAG_POSTGRES_UID", ""))
        pg_gid = numeric_id(os.environ.get("RAG_POSTGRES_GID", ""))
        if pg_uid is None or pg_gid is None:
            failures.append("RAG_POSTGRES_UID/GID: verified numeric ids required")
        directories = [
            ("RAG_PGDATA_ROOT", "/opt/rag-story-1-1/postgres", pg_uid, pg_gid, True),
            ("RAG_LOCK_ROOT", "/opt/rag-story-1-1/locks", 65532, 65532, True),
            ("RAG_ASSET_ROOT", "/opt/rag-story-1-1/assets", 65532, 65532, True),
            ("RAG_EPOCH_ROOT", "/opt/rag-story-1-1/epoch", 65532, 65532, False),
        ]
        for key, default, owner_uid, owner_gid, need_write in directories:
            path = Path(os.environ.get(key, default)).resolve()
            allowed = Path("/opt/rag-story-1-1")
            if not path.is_relative_to(allowed) or not path.is_dir():
                failures.append(f"{key}: existing project directory required")
                continue
            try:
                status = path.stat()
            except OSError:
                failures.append(f"{key}: directory metadata unavailable")
                continue
            if owner_uid is not None and status.st_uid != owner_uid:
                failures.append(f"{key}: owner uid must be {owner_uid}")
            if owner_gid is not None and status.st_gid != owner_gid:
                failures.append(f"{key}: owner gid must be {owner_gid}")
            if need_write and (status.st_mode & 0o200) != 0o200:
                failures.append(f"{key}: owner write permission required")
            if (status.st_mode & 0o500) != 0o500:
                failures.append(f"{key}: owner read and traverse permissions required")
            try:
                result = subprocess.run(
                    ["findmnt", "-T", str(path), "-n", "-o", "FSTYPE"],
                    capture_output=True, text=True, timeout=5,
                )
            except (OSError, subprocess.SubprocessError):
                failures.append(f"{key}: filesystem probe failed")
                continue
            if result.returncode or result.stdout.strip() not in {"ext4", "xfs", "btrfs"}:
                failures.append(f"{key}: verified local filesystem required")
    for key in ["RAG_TLS_CERT_FILE", "RAG_TLS_KEY_FILE",
                "RAG_POSTGRES_PASSWORD_FILE", "RAG_POSTGRES_PGPASS_FILE"]:
        value = os.environ.get(key, "")
        if not Path(value or "/nonexistent").is_file():
            failures.append(f"{key}: existing secret file required")
        elif Path(value).resolve().is_relative_to(root.resolve()):
            failures.append(f"{key}: secret file must live outside the repository")
    if sys.platform == "linux":
        failures.extend(secret_file_failures())
    failures = list(dict.fromkeys(failures))
    print(json.dumps({"status": "blocked" if failures else "ready-for-build",
                      "failures": failures}, indent=2))
    return 2 if failures else 0


def secret_file_failures() -> list[str]:
    """Local Compose file secrets keep host ownership/mode; verify both."""
    failures: list[str] = []
    pgpass = os.environ.get("RAG_POSTGRES_PGPASS_FILE", "")
    password = os.environ.get("RAG_POSTGRES_PASSWORD_FILE", "")
    pg_uid = os.environ.get("RAG_POSTGRES_UID", "")
    pg_gid = os.environ.get("RAG_POSTGRES_GID", "")
    uid_ok = re.fullmatch(r"[1-9][0-9]{0,9}", pg_uid) is not None
    gid_ok = re.fullmatch(r"[1-9][0-9]{0,9}", pg_gid) is not None
    failures.extend(secret_mode_failures(
        "RAG_POSTGRES_PGPASS_FILE", pgpass, "65532", "65532",
    ))
    failures.extend(secret_mode_failures(
        "RAG_POSTGRES_PASSWORD_FILE", password,
        pg_uid if uid_ok else None, pg_gid if gid_ok else None,
    ))
    for key in ("RAG_TLS_CERT_FILE", "RAG_TLS_KEY_FILE"):
        path = os.environ.get(key, "")
        if path:
            failures.extend(secret_mode_failures(key, path, "65532", "65532"))
    return failures


def secret_mode_failures(
    key: str, path: str, uid: str | None, gid: str | None,
) -> list[str]:
    """Check the host file users will actually get; no chmod/chown is applied."""
    if not path:
        return []
    try:
        status = os.stat(path)
    except OSError:
        return []
    failures: list[str] = []
    mode = status.st_mode & 0o777
    if mode not in (0o400, 0o600):
        failures.append(f"{key}: mode must be 0400 or 0600 with owner read")
    for label, value, actual in (
        ("uid", uid, status.st_uid), ("gid", gid, status.st_gid),
    ):
        if value is None:
            continue
        if not re.fullmatch(r"[0-9]{1,10}", value):
            failures.append(f"{key}: verified numeric owner {label} required")
            continue
        if actual != int(value):
            failures.append(f"{key}: owner {label} must be {value}")
    return failures


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # Never print a traceback or diagnostic object from admission checks.
        print(json.dumps({
            "status": "blocked",
            "failures": ["preflight: internal admission check failed"],
        }, indent=2))
        raise SystemExit(2)
