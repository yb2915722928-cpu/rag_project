"""Supervised native writer for one bounded upload original.

The API process never writes the original itself.  It starts one private
Linux child, forwards bounded UTF-8 chunks over a private socketpair, and
waits for a per-chunk acknowledgement before accepting more input.  The child
owns the local file writes, the asset lifecycle shared lock, and the final
atomic rename.  It inherits the controller's upload-slot descriptor and keeps
it open until the child exits, so a dead controller cannot release the slot by
merely closing its own descriptor.

All failures are finite public storage codes.  Paths, file contents, OS
messages and child tracebacks never cross this module boundary.
"""

from __future__ import annotations

import json
import math
import os
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rag_app.adapters.original_store import StoreUnavailable


FRAME_INIT = 1
FRAME_CHUNK = 2
FRAME_ACK = 3
FRAME_FINISH = 4
FRAME_RESULT = 5
FRAME_ABORT = 6
FRAME_ERROR = 7
FRAME_READY = 8

_FRAME_HEADER = struct.Struct("!BI")
_ACK = struct.Struct("!IQ")
_MAX_CONTROL_BYTES = 16_384
_MAX_CHUNK_BYTES = 1_048_576
_MAX_FILE_BYTES = 8 * 1024 * 1024 * 1024
_MAX_WAIT_SECONDS = 300.0

_FINITE_FAILURES = frozenset({
    "CONFIGURATION_INVALID",
    "FILE_LIMIT_EXCEEDED",
    "STORAGE_PRESSURE",
    "UPLOAD_CONTENT_CONFLICT",
    "UPLOAD_EXPIRED",
    "UPLOAD_IN_PROGRESS",
})

_ENV_ALLOWLIST = (
    "PATH", "LANG", "LC_ALL", "PYTHONPATH", "PYTHONIOENCODING",
    "PYTHONUNBUFFERED", "TZ",
)
_PROC = Path("/proc")


class _IpcFailure(Exception):
    """A finite transport or child failure; never contains diagnostic text."""

    __slots__ = ("code",)

    def __init__(self, code: str) -> None:
        self.code = _finite_code(code)
        super().__init__(self.code)


class _ProcUnknown(Exception):
    """The kernel process table could not be verified for this pid."""


def _finite_code(code: object) -> str:
    return code if isinstance(code, str) and code in _FINITE_FAILURES else "STORAGE_PRESSURE"


def _child_env() -> dict[str, str]:
    env = {name: os.environ[name] for name in _ENV_ALLOWLIST if name in os.environ}
    source_root = str(Path(__file__).resolve().parents[2])
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        source_root if not existing else source_root + os.pathsep + existing
    )
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def _json_frame(kind: int, value: dict[str, object]) -> bytes:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise _IpcFailure("STORAGE_PRESSURE") from None
    if len(payload) > _MAX_CONTROL_BYTES:
        raise _IpcFailure("STORAGE_PRESSURE")
    return _FRAME_HEADER.pack(kind, len(payload)) + payload


def _empty_frame(kind: int) -> bytes:
    return _FRAME_HEADER.pack(kind, 0)


def _chunk_frame(sequence: int, chunk: memoryview) -> bytes:
    if len(chunk) > _MAX_CHUNK_BYTES:
        raise _IpcFailure("FILE_LIMIT_EXCEEDED")
    payload = struct.pack("!I", sequence) + chunk.tobytes()
    return _FRAME_HEADER.pack(FRAME_CHUNK, len(payload)) + payload


def _decode_control(payload: bytes) -> dict[str, object]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise _IpcFailure("STORAGE_PRESSURE") from None
    if not isinstance(value, dict):
        raise _IpcFailure("STORAGE_PRESSURE")
    return value


def _error_code(payload: bytes) -> str:
    return _finite_code(_decode_control(payload).get("code"))


def _send_frame(sock: socket.socket, frame: bytes, deadline: float) -> None:
    view = memoryview(frame)
    try:
        while view:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise _IpcFailure("UPLOAD_EXPIRED")
            try:
                sock.settimeout(remaining)
                written = sock.send(view)
            except InterruptedError:
                continue
            except TimeoutError:
                raise _IpcFailure("UPLOAD_EXPIRED") from None
            except OSError:
                raise _IpcFailure("STORAGE_PRESSURE") from None
            if written <= 0:
                raise _IpcFailure("STORAGE_PRESSURE")
            view = view[written:]
    finally:
        try:
            sock.settimeout(None)
        except OSError:
            pass


def _recv_exact(
    sock: socket.socket, size: int, *, deadline: float, timeout_code: str,
) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _IpcFailure(timeout_code)
        try:
            sock.settimeout(remaining)
            part = sock.recv(size - len(chunks))
        except InterruptedError:
            continue
        except TimeoutError:
            raise _IpcFailure(timeout_code) from None
        except OSError:
            raise _IpcFailure("STORAGE_PRESSURE") from None
        if not part:
            raise _IpcFailure("STORAGE_PRESSURE")
        chunks.extend(part)
    return bytes(chunks)


def _recv_frame(
    sock: socket.socket,
    max_payload: int,
    *,
    deadline: float,
    timeout_code: str,
) -> tuple[int, bytes]:
    header = _recv_exact(
        sock, _FRAME_HEADER.size, deadline=deadline, timeout_code=timeout_code,
    )
    kind, length = _FRAME_HEADER.unpack(header)
    if length > max_payload:
        raise _IpcFailure("STORAGE_PRESSURE")
    payload = _recv_exact(
        sock, length, deadline=deadline, timeout_code=timeout_code,
    )
    return kind, payload


@dataclass(frozen=True, slots=True)
class _ProcStat:
    pid: int
    ppid: int
    pgrp: int
    session: int
    start_ticks: int
    state: str


def _read_proc_stat(pid: int) -> _ProcStat | None:
    try:
        # ``comm`` can contain arbitrary bytes; only the numeric fields after
        # the final parenthesis are parsed, so replacement there is harmless.
        raw = (_PROC / str(pid) / "stat").read_bytes().decode("ascii", "replace")
    except (FileNotFoundError, ProcessLookupError):
        return None
    except OSError:
        raise _ProcUnknown() from None
    close = raw.rfind(")")
    open_paren = raw.find("(")
    if close < 1 or open_paren < 1:
        raise _ProcUnknown()
    try:
        parsed_pid = int(raw[:open_paren].strip())
        tail = raw[close + 2:].split()
        if len(tail) < 20:
            raise _ProcUnknown()
        return _ProcStat(
            pid=parsed_pid,
            state=tail[0],
            ppid=int(tail[1]),
            pgrp=int(tail[2]),
            session=int(tail[3]),
            start_ticks=int(tail[19]),
        )
    except (ValueError, IndexError):
        raise _ProcUnknown() from None


def _scan_proc() -> dict[int, _ProcStat] | None:
    snapshot: dict[int, _ProcStat] = {}
    try:
        entries = os.listdir(_PROC)
    except OSError:
        return None
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            stat = _read_proc_stat(int(entry))
        except _ProcUnknown:
            return None
        if stat is not None:
            snapshot[stat.pid] = stat
    return snapshot


def _process_state(pid: int, start_ticks: int) -> bool | None:
    """True = live and matching; False = verified absent/reused; None = unknown."""

    if start_ticks <= 0:
        return None
    try:
        stat = _read_proc_stat(pid)
    except _ProcUnknown:
        return None
    if stat is None:
        return False
    if stat.start_ticks != start_ticks:
        return False
    return stat.state != "Z"


def _group_state(
    pid: int, start_ticks: int, group: int,
) -> tuple[bool | None, list[_ProcStat] | None]:
    leader = _process_state(pid, start_ticks)
    snapshot = _scan_proc()
    if snapshot is None:
        return leader, None
    members = [
        stat for stat in snapshot.values()
        if stat.state != "Z" and stat.pid != pid
        and (stat.pgrp == group or stat.session == pid)
    ]
    return leader, members


def _descendants(pid: int) -> dict[int, int] | None:
    snapshot = _scan_proc()
    if snapshot is None:
        return None
    by_parent: dict[int, list[int]] = {}
    for stat in snapshot.values():
        by_parent.setdefault(stat.ppid, []).append(stat.pid)
    found: dict[int, int] = {}
    pending = [pid]
    seen = {pid}
    while pending:
        parent = pending.pop()
        for child in by_parent.get(parent, ()):
            if child in seen:
                continue
            seen.add(child)
            stat = snapshot.get(child)
            if stat is not None and stat.state != "Z":
                found[child] = stat.start_ticks
                pending.append(child)
    for stat in snapshot.values():
        if stat.pid == pid or stat.state == "Z":
            continue
        if stat.pgrp == pid or stat.session == pid:
            found.setdefault(stat.pid, stat.start_ticks)
    return found


def _signal_verified(pid: int, start_ticks: int, group: int, signum: int) -> bool:
    try:
        stat = _read_proc_stat(pid)
    except _ProcUnknown:
        return False
    if stat is None or stat.start_ticks != start_ticks or stat.pgrp != group:
        return False
    try:
        os.killpg(group, signum)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    return True


class _DescendantMonitor:
    """Sample descendants while the child can still create them."""

    def __init__(self, root_pid: int) -> None:
        self._root_pid = root_pid
        self._found: dict[int, int] = {}
        self._unknown = False
        self._stop = threading.Event()
        initial = _descendants(root_pid)
        if initial is None:
            self._unknown = True
        else:
            self._found.update(initial)
        self._thread = threading.Thread(
            target=self._run, name="rag-upload-descendants", daemon=True,
        )
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            found = _descendants(self._root_pid)
            if found is None:
                self._unknown = True
            else:
                for pid, ticks in found.items():
                    self._found.setdefault(pid, ticks)
            self._stop.wait(0.2)

    @property
    def unknown(self) -> bool:
        return self._unknown

    def finish(self) -> dict[int, int]:
        self._stop.set()
        self._thread.join(timeout=0.5)
        if self._thread.is_alive():
            self._unknown = True
        return dict(self._found)


@dataclass(frozen=True, slots=True)
class _ChildIdentity:
    pid: int
    process_group: int
    start_ticks: int


class SupervisedUploadWriter:
    """Write one original through a supervised child and prove it stopped.

    ``slot_fd`` is the controller's already-held upload-slot descriptor.  This
    class never acquires, unlocks or closes it: the child inherits a duplicate
    of the same open file description and keeps it until process exit.  The
    caller may release the slot only after ``stop_proven`` is true.
    """

    def __init__(
        self,
        *,
        staging: str,
        final: str,
        lifecycle_lock: str,
        slot_fd: int,
        max_bytes: int,
        page_bytes: int,
        chunk_bytes: int,
        absolute_deadline_monotonic: float,
        no_progress_s: float,
        stop_grace_s: float,
    ) -> None:
        if sys.platform != "linux":
            raise StoreUnavailable("CONFIGURATION_INVALID")
        for name, value in (
            ("staging", staging),
            ("final", final),
            ("lifecycle_lock", lifecycle_lock),
        ):
            if (
                not isinstance(value, str)
                or not value
                or len(value) > 4096
                or "\x00" in value
                or not os.path.isabs(value)
            ):
                raise StoreUnavailable("CONFIGURATION_INVALID")
        if staging == final:
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if type(slot_fd) is not int or not 3 <= slot_fd <= 2**31 - 1:
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if type(max_bytes) is not int or not 1 <= max_bytes <= _MAX_FILE_BYTES:
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if type(page_bytes) is not int or not 0 <= page_bytes <= _MAX_FILE_BYTES:
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if type(chunk_bytes) is not int or not 1 <= chunk_bytes <= _MAX_CHUNK_BYTES:
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if (
            isinstance(absolute_deadline_monotonic, bool)
            or not isinstance(absolute_deadline_monotonic, (int, float))
            or not math.isfinite(float(absolute_deadline_monotonic))
            or float(absolute_deadline_monotonic) <= 0
        ):
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if (
            isinstance(no_progress_s, bool)
            or not isinstance(no_progress_s, (int, float))
            or not math.isfinite(float(no_progress_s))
            or not 0 < float(no_progress_s) <= _MAX_WAIT_SECONDS
        ):
            raise StoreUnavailable("CONFIGURATION_INVALID")
        if (
            isinstance(stop_grace_s, bool)
            or not isinstance(stop_grace_s, (int, float))
            or not math.isfinite(float(stop_grace_s))
            or not 0 <= float(stop_grace_s) <= _MAX_WAIT_SECONDS
        ):
            raise StoreUnavailable("CONFIGURATION_INVALID")

        self._staging = staging
        self._final = final
        self._lifecycle_lock = lifecycle_lock
        self._slot_fd = slot_fd
        self._max_bytes = max_bytes
        self._page_bytes = page_bytes
        self._chunk_bytes = chunk_bytes
        self._absolute_deadline = float(absolute_deadline_monotonic)
        self._no_progress_s = float(no_progress_s)
        self._stop_grace_s = float(stop_grace_s)

        self._process: subprocess.Popen[Any] | None = None
        self._sock: socket.socket | None = None
        self._identity: _ChildIdentity | None = None
        self._monitor: _DescendantMonitor | None = None
        self._state = "new"
        self._failure_code: str | None = None
        self._stop_proven = False
        self._bytes = 0
        self._sequence = 0
        self._last_progress = 0.0
        self._lock = threading.RLock()

    @property
    def stop_proven(self) -> bool:
        """True only after the child is verified stopped and locks are released."""

        return self._stop_proven

    def __enter__(self) -> SupervisedUploadWriter:
        with self._lock:
            if self._state != "new":
                raise StoreUnavailable("UPLOAD_IN_PROGRESS")
            try:
                self._spawn()
            except StoreUnavailable:
                self._state = "failed"
                self._mark_absent_if_unstarted()
                raise
            except _IpcFailure as exc:
                self._state = "failed"
                self._failure_code = exc.code
                self._mark_absent_if_unstarted()
                raise StoreUnavailable(exc.code) from None
            except Exception:
                self._state = "failed"
                self._mark_absent_if_unstarted()
                raise StoreUnavailable("STORAGE_PRESSURE") from None
            self._state = "open"
            return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        if self._state != "finished":
            self.abort()
        return False

    def _spawn(self) -> None:
        try:
            os.fstat(self._slot_fd)
        except OSError:
            raise _IpcFailure("CONFIGURATION_INVALID") from None

        parent_sock, child_sock = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM,
        )
        self._sock = parent_sock
        process: subprocess.Popen[Any] | None = None
        try:
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "rag_app.entrypoints.upload_child",
                    "--ipc-fd", str(child_sock.fileno()),
                    "--slot-fd", str(self._slot_fd),
                ],
                shell=False,
                close_fds=True,
                pass_fds=(child_sock.fileno(), self._slot_fd),
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=_child_env(),
            )
            self._process = process
            child_sock.close()

            try:
                stat = _read_proc_stat(process.pid)
            except _ProcUnknown:
                raise _IpcFailure("UPLOAD_IN_PROGRESS") from None
            if stat is None or stat.state == "Z":
                raise _IpcFailure("STORAGE_PRESSURE")
            try:
                group = os.getpgid(process.pid)
            except OSError:
                group = stat.pgrp
            if group != process.pid:
                raise _IpcFailure("UPLOAD_IN_PROGRESS")
            self._identity = _ChildIdentity(
                pid=process.pid,
                process_group=group,
                start_ticks=stat.start_ticks,
            )
            self._monitor = _DescendantMonitor(process.pid)

            startup_deadline = min(
                self._absolute_deadline,
                time.monotonic() + min(15.0, max(5.0, self._no_progress_s)),
            )
            _send_frame(
                parent_sock,
                _json_frame(FRAME_INIT, {
                    "version": 1,
                    "staging": self._staging,
                    "final": self._final,
                    "lifecycle_lock": self._lifecycle_lock,
                    "max_bytes": self._max_bytes,
                    "page_bytes": self._page_bytes,
                    "chunk_bytes": self._chunk_bytes,
                    "absolute_deadline_monotonic": self._absolute_deadline,
                    "no_progress_s": self._no_progress_s,
                }),
                startup_deadline,
            )
            kind, payload = _recv_frame(
                parent_sock,
                _MAX_CONTROL_BYTES,
                deadline=startup_deadline,
                timeout_code="STORAGE_PRESSURE",
            )
            if kind == FRAME_ERROR:
                raise _IpcFailure(_error_code(payload))
            if kind != FRAME_READY:
                raise _IpcFailure("STORAGE_PRESSURE")
            self._last_progress = time.monotonic()
        except BaseException:
            self._close_ipc()
            # Keep the proof on the object the caller already holds: a failed
            # enter may still release the slot only when this is true.
            self._stop_proven = self._stop_process()
            raise
        finally:
            try:
                child_sock.close()
            except OSError:
                pass

    def feed(self, chunk: bytes) -> None:
        """Write one bounded chunk, waiting for the child's durable ACK."""

        with self._lock:
            if self._state != "open":
                raise StoreUnavailable(self._failure_code or "UPLOAD_IN_PROGRESS")
            if not isinstance(chunk, bytes):
                if isinstance(chunk, (bytearray, memoryview)):
                    chunk = bytes(chunk)
                else:
                    self._fail("UPLOAD_CONTENT_CONFLICT")
            if not chunk:
                return
            if self._bytes + len(chunk) > self._max_bytes:
                self._fail("FILE_LIMIT_EXCEEDED")
            view = memoryview(chunk)
            offset = 0
            try:
                while offset < len(view):
                    self._require_progress_budget()
                    piece = view[offset:offset + self._chunk_bytes]
                    sequence = self._sequence
                    _send_frame(
                        self._socket(), _chunk_frame(sequence, piece),
                        self._io_deadline(),
                    )
                    kind, payload = _recv_frame(
                        self._socket(),
                        _MAX_CONTROL_BYTES,
                        deadline=self._io_deadline(),
                        timeout_code="UPLOAD_EXPIRED",
                    )
                    if kind == FRAME_ERROR:
                        raise _IpcFailure(_error_code(payload))
                    if kind != FRAME_ACK or len(payload) != _ACK.size:
                        raise _IpcFailure("STORAGE_PRESSURE")
                    ack_sequence, ack_total = _ACK.unpack(payload)
                    expected_total = self._bytes + len(piece)
                    if ack_sequence != sequence or ack_total != expected_total:
                        raise _IpcFailure("STORAGE_PRESSURE")
                    self._bytes = expected_total
                    self._sequence += 1
                    self._last_progress = time.monotonic()
                    offset += len(piece)
            except _IpcFailure as exc:
                self._fail(exc.code)
            except (OSError, struct.error, ValueError):
                self._fail("STORAGE_PRESSURE")

    def finish(self) -> tuple[int, str]:
        """Finish, fsync and atomically commit; return real length and hash."""

        with self._lock:
            if self._state != "open":
                raise StoreUnavailable(self._failure_code or "UPLOAD_IN_PROGRESS")
            if self._bytes == 0:
                self._fail("UPLOAD_CONTENT_CONFLICT")
            if time.monotonic() >= self._absolute_deadline:
                self._fail("UPLOAD_EXPIRED")
            try:
                deadline = self._io_deadline()
                _send_frame(
                    self._socket(), _empty_frame(FRAME_FINISH), deadline,
                )
                kind, payload = _recv_frame(
                    self._socket(),
                    _MAX_CONTROL_BYTES,
                    deadline=deadline,
                    timeout_code="UPLOAD_EXPIRED",
                )
                if kind == FRAME_ERROR:
                    raise _IpcFailure(_error_code(payload))
                if kind != FRAME_RESULT:
                    raise _IpcFailure("STORAGE_PRESSURE")
                result = _decode_control(payload)
                size = result.get("bytes")
                digest = result.get("sha256")
                if (
                    type(size) is not int
                    or size != self._bytes
                    or not isinstance(digest, str)
                    or len(digest) != 64
                    or any(character not in "0123456789abcdef" for character in digest)
                ):
                    raise _IpcFailure("STORAGE_PRESSURE")
            except _IpcFailure as exc:
                self._fail(exc.code)
            except (OSError, struct.error, ValueError):
                self._fail("STORAGE_PRESSURE")

            self._close_ipc()
            self._state = "finishing"
            proven = self._stop_process()
            self._stop_proven = proven
            if not proven:
                self._state = "failed"
                self._failure_code = "UPLOAD_IN_PROGRESS"
                raise StoreUnavailable("UPLOAD_IN_PROGRESS")
            self._state = "finished"
            return size, digest

    def abort(self) -> None:
        """Stop writing and remove the staging file when the child can do so."""

        with self._lock:
            if self._state in {"finished", "aborted"}:
                return
            if self._state == "new":
                self._state = "aborted"
                # No child was started, so no writer can still be running.
                self._stop_proven = self._sock is None and self._process is None
                return
            self._state = "aborting"
            self._terminate(graceful=True)
            self._state = "aborted"

    def _mark_absent_if_unstarted(self) -> None:
        """No Popen and no IPC: no writer can still be running on this slot."""

        if self._process is None and self._sock is None:
            self._stop_proven = True

    def _socket(self) -> socket.socket:
        if self._sock is None or self._sock.fileno() < 0:
            raise _IpcFailure("STORAGE_PRESSURE")
        return self._sock

    def _io_deadline(self) -> float:
        deadline = min(
            self._absolute_deadline,
            self._last_progress + self._no_progress_s,
        )
        if time.monotonic() >= deadline:
            raise _IpcFailure("UPLOAD_EXPIRED")
        return deadline

    def _require_progress_budget(self) -> None:
        now = time.monotonic()
        if (
            now >= self._absolute_deadline
            or now - self._last_progress >= self._no_progress_s
        ):
            raise _IpcFailure("UPLOAD_EXPIRED")

    def _fail(self, code: str) -> None:
        finite = _finite_code(code)
        with self._lock:
            if self._state in {"failed", "aborted", "finished"}:
                raise StoreUnavailable(self._failure_code or finite)
            self._failure_code = finite
            self._state = "failed"
            self._terminate(graceful=True)
            raise StoreUnavailable(finite)

    def _terminate(self, *, graceful: bool) -> None:
        if graceful and self._sock is not None and self._sock.fileno() >= 0:
            try:
                deadline = time.monotonic() + min(
                    0.5, max(0.05, self._stop_grace_s),
                )
                _send_frame(self._sock, _empty_frame(FRAME_ABORT), deadline)
            except BaseException:
                pass
        self._close_ipc()
        self._stop_proven = self._stop_process()

    def _close_ipc(self) -> None:
        sock = self._sock
        self._sock = None
        if sock is None:
            return
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass

    def _stop_process(self) -> bool:
        """Wait for exit, then verify identity, descendants, IPC and locks."""

        process = self._process
        if process is None:
            # Spawn never reached Popen; there is no child to stop.
            return self._sock is None
        identity = self._identity
        grace = max(0.05, self._stop_grace_s)
        if identity is None:
            try:
                process.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except OSError:
                    pass
                try:
                    process.wait(timeout=grace)
                except subprocess.TimeoutExpired:
                    pass
            return False

        try:
            process.wait(timeout=grace)
        except (subprocess.TimeoutExpired, OSError):
            pass
        if process.poll() is None:
            _signal_verified(
                identity.pid, identity.start_ticks,
                identity.process_group, signal.SIGTERM,
            )
            try:
                process.wait(timeout=grace)
            except (subprocess.TimeoutExpired, OSError):
                pass
        if process.poll() is None:
            _signal_verified(
                identity.pid, identity.start_ticks,
                identity.process_group, signal.SIGKILL,
            )
            try:
                process.wait(timeout=grace)
            except (subprocess.TimeoutExpired, OSError):
                pass

        try:
            recorded = (
                self._monitor.finish() if self._monitor is not None else {}
            )
            monitor_unknown = (
                self._monitor.unknown if self._monitor is not None else True
            )
            _, members = _group_state(
                identity.pid, identity.start_ticks, identity.process_group,
            )
            current = _descendants(identity.pid)
            descendants_absent = (
                not monitor_unknown
                and current is not None
                and all(
                    _process_state(pid, ticks) is False
                    for pid, ticks in recorded.items()
                )
                and all(
                    _process_state(pid, ticks) is False
                    for pid, ticks in current.items()
                )
            )
            exited = _process_state(identity.pid, identity.start_ticks) is False
            group_empty = members == []
            ipc_closed = self._sock is None
            # A verified exit closes every child fd, and the descendant check
            # covers inherited lifecycle-lock descriptors.  Probing the lock
            # itself would confuse an unrelated cleanup holder with our writer.
            return bool(
                exited
                and group_empty
                and descendants_absent
                and ipc_closed
            )
        except Exception:
            # Unverified facts are never a proof of absence.
            return False
