"""Baseline maintenance and an idle worker; no business scheduler or external calls."""

import os
import select
import signal

from rag_app.bootstrap.config import Settings
from rag_app.bootstrap.runtime import build_runtime
from rag_app.contracts.errors import SafeError


def check_database(settings: Settings | None = None) -> None:
    runtime = build_runtime(settings if settings is not None else Settings())
    failure = None
    try:
        runtime.check_database()
    except Exception as exc:
        failure = exc
    finally:
        try:
            runtime.close()
        except Exception as cleanup_error:
            if failure is None:
                raise
            if isinstance(failure, SafeError):
                failure.cleanup_errors += (cleanup_error,)
            else:
                failure = SafeError(
                    "DATABASE_OPERATION_FAILED", diagnostic_cause=failure,
                    cleanup_errors=(cleanup_error,),
                )
    if failure is not None:
        raise failure from None


def run_worker(settings: Settings | None = None) -> None:
    stopping = False
    handlers = {}
    pipe = ()
    previous_wakeup = None
    runtime = None
    failure = None
    cleanup = []

    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True

    try:
        pipe = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        previous_wakeup = signal.set_wakeup_fd(pipe[1], warn_on_full_buffer=False)
        for signum in (signal.SIGTERM, signal.SIGINT):
            handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, request_stop)
        runtime = build_runtime(settings if settings is not None else Settings())
        runtime.check_database()
        # A self-pipe avoids locks and lost notifications inside signal handlers.
        # The short application UoW is already closed before select can wait.
        while not stopping:
            select.select([pipe[0]], [], [], 60)
            try:
                os.read(pipe[0], 4096)
            except BlockingIOError:
                pass
    except BaseException as exc:
        failure = exc
    finally:
        if runtime is not None:
            try:
                runtime.close()
            except BaseException as exc:
                cleanup.append(exc)
        if previous_wakeup is not None:
            try:
                signal.set_wakeup_fd(previous_wakeup)
            except BaseException as exc:
                cleanup.append(exc)
        for signum, handler in handlers.items():
            try:
                signal.signal(signum, handler)
            except BaseException as exc:
                cleanup.append(exc)
        for fd in pipe:
            try:
                os.close(fd)
            except BaseException as exc:
                cleanup.append(exc)

    if failure is not None:
        if isinstance(failure, SafeError):
            failure.cleanup_errors += tuple(cleanup)
            raise failure from None
        if isinstance(failure, Exception):
            raise SafeError(
                "DATABASE_OPERATION_FAILED", diagnostic_cause=failure,
                cleanup_errors=tuple(cleanup),
            ) from None
        raise failure
    if cleanup:
        raise SafeError(
            "DATABASE_CLEANUP_FAILED", diagnostic_cause=cleanup[0],
            cleanup_errors=tuple(cleanup[1:]),
        ) from None
