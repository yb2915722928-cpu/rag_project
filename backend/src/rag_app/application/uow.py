from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager

from typing import Any, Protocol

from rag_app.contracts.errors import GuardError, SafeError


class TransactionSession(Protocol):
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


class UnitOfWork:
    """Owns one short transaction; repositories must never commit."""

    def __init__(self, session_factory: Callable[[], TransactionSession]) -> None:
        self._session_factory = session_factory

    @contextmanager
    def transaction(self) -> Iterator[TransactionSession]:
        session = None
        failure = None
        cleanup = []
        try:
            session = self._session_factory()
            yield session
            session.commit()
        except BaseException as exc:
            failure = exc
            if session is not None:
                try:
                    session.rollback()
                except BaseException as rollback_error:
                    cleanup.append(rollback_error)
        finally:
            if session is not None:
                try:
                    session.close()
                except BaseException as close_error:
                    cleanup.append(close_error)
        if failure is not None:
            if isinstance(failure, GuardError) and not cleanup:
                # A finite execution guard decision is not a database failure;
                # it rolls back and keeps its own code for the caller.
                raise failure from None
            if not isinstance(failure, Exception):
                raise failure
            code = failure.code if isinstance(failure, SafeError) else "DATABASE_OPERATION_FAILED"
            raise SafeError(
                code, diagnostic_cause=failure, cleanup_errors=tuple(cleanup),
            ) from None
        if cleanup:
            raise SafeError(
                "DATABASE_CLEANUP_FAILED", diagnostic_cause=cleanup[0],
                cleanup_errors=tuple(cleanup[1:]),
            ) from None

