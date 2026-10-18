from dataclasses import dataclass
from functools import partial
import sys
import threading
from typing import Any

from sqlalchemy.engine import Engine

from rag_app.adapters.call_postgres import CallRepository
from rag_app.adapters.epoch_control import FileEpochControl
from rag_app.adapters.original_store import LocalOriginalStore
from rag_app.adapters.postgres import BaselineRepository, create_pg_engine, create_uow
from rag_app.application.baseline import check_baseline
from rag_app.application.call_lifecycle import CallLifecycle
from rag_app.application.uow import UnitOfWork
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import GuardError, SafeError
from rag_app.modules.execution.calls import LockOrder
from rag_app.modules.library.uploads import UploadLimits

TARGET_PYTHON = (3, 12, 8)


def require_python() -> None:
    if sys.implementation.name != "cpython" or sys.version_info[:3] != TARGET_PYTHON:
        raise SafeError("RUNTIME_VERSION_MISMATCH")


@dataclass
class Runtime:
    engine: Engine
    uow: UnitOfWork
    schema: str
    control: FileEpochControl | None = None
    settings: Settings | None = None
    _upload_store: LocalOriginalStore | None = None
    _upload_lock: Any = None

    def check_database(self) -> None:
        check_baseline(self.uow, partial(BaselineRepository, schema=self.schema))
        if self.control is None:
            # A missing independent record is isolation, not an implicit new
            # epoch; the database is never used to synthesize one.
            raise SafeError("STARTUP_DEPENDENCY_UNAVAILABLE")
        try:
            # The independent record is read before the short PG transaction.
            expected = self.control.current()
            with self.uow.transaction() as session:
                self.control.verify_mirror(session, expected=expected)
        except GuardError as exc:
            # Fail closed with a finite public code; guard text stays internal.
            raise SafeError(
                "STARTUP_DEPENDENCY_UNAVAILABLE", diagnostic_cause=exc,
            ) from None

    def call_lifecycle(self) -> CallLifecycle:
        if self.control is None:
            raise SafeError("STARTUP_DEPENDENCY_UNAVAILABLE")
        return build_call_lifecycle(self.control, self.schema)

    def upload_limits(self) -> UploadLimits:
        if self.settings is None:
            raise SafeError("STARTUP_DEPENDENCY_UNAVAILABLE")
        settings = self.settings
        return UploadLimits(
            max_file_bytes=settings.upload_max_file_bytes,
            start_window_s=settings.upload_start_window_s,
            total_window_s=settings.upload_total_window_s,
            no_progress_s=settings.upload_no_progress_s,
            lease_s=settings.upload_lease_s,
            renew_s=settings.upload_renew_s,
            chunk_bytes=settings.upload_chunk_bytes,
            slot_wait_s=settings.upload_slot_wait_s,
            stop_grace_s=settings.upload_stop_grace_s,
            page_bytes=settings.upload_page_bytes,
            replay_verify_s=settings.upload_replay_verify_s,
        )

    def original_store(self) -> LocalOriginalStore:
        """One lazily-created store; construction never runs in a PG transaction."""

        if self.settings is None or self.settings.upload_root is None:
            raise SafeError("STARTUP_DEPENDENCY_UNAVAILABLE")
        if self._upload_store is not None:
            return self._upload_store
        lock = self._upload_lock
        if lock is None:
            lock = threading.Lock()
            self._upload_lock = lock
        with lock:
            if self._upload_store is None:
                self._upload_store = LocalOriginalStore(
                    self.settings.upload_root,
                    page_bytes=self.settings.upload_page_bytes,
                )
            return self._upload_store

    def upload_repository(self, session):
        from rag_app.adapters.upload_postgres import UploadRepository

        return UploadRepository(session, schema=self.schema)

    def close(self) -> None:
        try:
            self.engine.dispose()
        except Exception as exc:
            raise SafeError("DATABASE_CLEANUP_FAILED", diagnostic_cause=exc) from None


def build_runtime(settings: Settings) -> Runtime:
    engine = create_pg_engine(settings.database_url.get_secret_value(), settings.database_schema)
    control = (
        None if settings.epoch_control_file is None
        else FileEpochControl(settings.epoch_control_file, schema=settings.database_schema)
    )
    return Runtime(
        engine, create_uow(engine), settings.database_schema, control,
        settings=settings,
    )


def build_call_lifecycle(
    control: FileEpochControl, schema: str,
) -> CallLifecycle:
    """Assembly entry reused by API/worker and the real-PG test harness."""

    def stores(session):
        return CallRepository(session, schema=schema, lock_order=LockOrder())

    return CallLifecycle(control, stores)
