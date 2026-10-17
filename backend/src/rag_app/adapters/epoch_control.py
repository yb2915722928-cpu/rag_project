"""Independent epoch control record, deliberately outside the restore database."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
from typing import Any

from sqlalchemy import text

from rag_app.adapters.postgres import validate_schema, verify_namespace
from rag_app.contracts.errors import GuardError
from rag_app.modules.execution.calls import Epoch, SQLSession


CONTROL_FILE_ENV = "RAG_EPOCH_CONTROL_FILE"
CONTROL_MAX_BYTES = 4096
_EPOCH = re.compile(r"[A-Za-z0-9_-]{32,64}\Z")
_DEPLOYMENT = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_KEYS = {"deployment_id", "epoch", "cutover_at", "maintenance_version"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def epoch_mirror(session: SQLSession, *, schema: str) -> tuple[str, str, Any, int]:
    """Compare the read control value with the short-transaction DB mirror."""

    verify_namespace(session, schema)
    row = session.execute(
        text(
            "SELECT deployment_id, epoch, cutover_at, maintenance_version "
            f'FROM {_quoted_schema(schema)}.rag_epoch_mirror WHERE singleton'
        ),
    ).one_or_none()
    if row is None:
        raise GuardError("EPOCH_MIRROR_MISSING")
    return (
        str(row[0]), str(row[1]), row[2], int(row[3]),
    )


def _quoted_schema(schema: str) -> str:
    return '"' + validate_schema(schema).replace('"', '""') + '"'


class FileEpochControl:
    """Reads one bounded control file; nothing here writes inside a PG transaction."""

    def __init__(
        self, path: str | os.PathLike[str], *, schema: str = "public",
    ) -> None:
        self._path = Path(path)
        self._schema = validate_schema(schema)

    @classmethod
    def from_environment(cls, *, schema: str = "public") -> FileEpochControl:
        value = os.getenv(CONTROL_FILE_ENV)
        if not value:
            raise GuardError("EPOCH_CONTROL_MISSING")
        return cls(value, schema=schema)

    @property
    def path(self) -> Path:
        return self._path

    def current(self) -> Epoch:
        # Read on every decision: a control change must not be hidden by a
        # process-local cache, and the file read is outside any PG transaction.
        return self._load()

    def _load(self) -> Epoch:
        try:
            with self._path.open("rb") as handle:
                raw = handle.read(CONTROL_MAX_BYTES + 1)
        except FileNotFoundError:
            raise GuardError("EPOCH_CONTROL_MISSING") from None
        except OSError:
            raise GuardError("EPOCH_CONTROL_INVALID") from None
        if len(raw) > CONTROL_MAX_BYTES:
            raise GuardError("EPOCH_CONTROL_INVALID")
        try:
            document = json.loads(raw.decode("utf-8"))
            if not isinstance(document, dict) or set(document) != _KEYS:
                raise ValueError("unexpected control shape")
            deployment = document["deployment_id"]
            epoch = document["epoch"]
            version = document["maintenance_version"]
            cutover = document["cutover_at"]
            if (
                not isinstance(deployment, str)
                or _DEPLOYMENT.fullmatch(deployment) is None
                or not isinstance(epoch, str)
                or _EPOCH.fullmatch(epoch) is None
                or type(version) is not int
                or version < 1
                or not isinstance(cutover, str)
                or not cutover.endswith("Z")
            ):
                raise ValueError("invalid control values")
            parsed = Epoch(
                deployment_id=deployment, epoch=epoch,
                cutover_at=datetime.fromisoformat(cutover[:-1] + "+00:00"),
                maintenance_version=version,
            )
        except (ValueError, UnicodeDecodeError):
            raise GuardError("EPOCH_CONTROL_INVALID") from None
        return parsed

    def verify_mirror(
        self, session: SQLSession, *, expected: Epoch | None = None,
    ) -> None:
        # The caller normally reads the control file before opening its short
        # PG transaction and passes that value here; no file I/O is required
        # while a database transaction is active.
        expected = self.current() if expected is None else expected
        try:
            actual = epoch_mirror(session, schema=self._schema)
        except GuardError:
            raise
        except Exception:
            raise GuardError("EPOCH_MIRROR_MISSING") from None
        if actual != (
            expected.deployment_id, expected.epoch,
            expected.cutover_at, expected.maintenance_version,
        ):
            raise GuardError("EPOCH_MIRROR_MISMATCH")


def initialize_epoch_control(
    path: str | os.PathLike[str], *, deployment_id: str,
) -> Epoch:
    """Explicit maintenance action: create once, never overwrite an existing record."""

    target = Path(path)
    if target.exists():
        raise GuardError("EPOCH_CONTROL_INVALID")
    if _DEPLOYMENT.fullmatch(deployment_id) is None:
        raise GuardError("EPOCH_CONTROL_INVALID")
    value = Epoch(
        deployment_id=deployment_id,
        epoch=secrets.token_urlsafe(32),
        cutover_at=utc_now(),
        maintenance_version=1,
    )
    payload = json.dumps(
        {
            "deployment_id": value.deployment_id,
            "epoch": value.epoch,
            "cutover_at": value.cutover_at.isoformat().replace("+00:00", "Z"),
            "maintenance_version": value.maintenance_version,
        },
        separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")
    descriptor = None
    created = False
    failure: BaseException | None = None
    try:
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o400,
        )
        created = True
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = None
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException as exc:
        failure = exc
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
    if failure is not None:
        if isinstance(failure, GuardError):
            raise failure from None
        # Never leave a partially written record that could later pass an
        # existence check.  Only remove a file this call actually created; a
        # lost O_EXCL race leaves the existing record untouched.
        if created:
            try:
                target.unlink()
            except OSError:
                pass
        raise GuardError("EPOCH_CONTROL_INVALID") from None
    return value


def mirror_epoch(uow: Any, value: Epoch, *, schema: str) -> None:
    """Maintenance-only mirror write; caller owns the short application UoW."""

    with uow.transaction() as session:
        verify_namespace(session, schema)
        session.execute(
            text(
                f"INSERT INTO {_quoted_schema(schema)}.rag_epoch_mirror "
                "(singleton, deployment_id, epoch, cutover_at, "
                "maintenance_version) "
                "VALUES (true, :deployment_id, :epoch, :cutover_at, "
                ":maintenance_version) "
                "ON CONFLICT (singleton) DO UPDATE SET "
                "deployment_id = EXCLUDED.deployment_id, "
                "epoch = EXCLUDED.epoch, cutover_at = EXCLUDED.cutover_at, "
                "maintenance_version = EXCLUDED.maintenance_version"
            ),
            {
                "deployment_id": value.deployment_id,
                "epoch": value.epoch,
                "cutover_at": value.cutover_at,
                "maintenance_version": value.maintenance_version,
            },
        )
