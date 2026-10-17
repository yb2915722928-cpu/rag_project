"""Real Linux child supervision for one bounded stage and one send grant.

The child receives only a private socketpair fd; all command, grant and result
bytes travel as bounded length-prefixed frames.  The child never derives
another process, never performs DNS and exits after its single result.

Physical slot identity is ``deployment_id + slot_id``.  A new boot or a new
supervisor instance must not bypass a child that is still alive (or whose stop
is unproven).  Occupancy is a small record on an explicitly chosen local
filesystem, guarded by ``fcntl.flock`` and replaced atomically, so separate
supervisors observe the same claim.  A state root that cannot be created is a
caller error; there is no silent in-memory fallback.

``/proc`` is the only source of pid/start-token facts.  If it cannot be read,
the result is "unknown" and therefore never a proof of absence or an authority
to signal.  Signals are sent only to a pid whose start token and process group
still match the registered child.
"""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator

from rag_app.modules.execution.supervision import (
    BoundedOutput,
    ChildFailure,
    ChildIdentity,
    ChildLimits,
    ChildResult,
    ChildSlot,
    ChildStage,
    ChildSupervisionError,
    MAX_WIRE_FRAME_BYTES,
    SendGrant,
    SendState,
    StageCommand,
    StopProof,
    StopReason,
    close_ipc,
    command_to_wire,
    drain_bounded,
    grant_to_wire,
    normalize_child_result,
    read_frame,
    result_from_wire,
    write_frame,
)


_ENV_ALLOWLIST = (
    "PATH", "LANG", "LC_ALL", "PYTHONPATH", "PYTHONIOENCODING",
    "PYTHONUNBUFFERED", "TZ",
)
_PROC = Path("/proc")


class _ProcUnknown(Exception):
    """The kernel process table could not be verified for this pid."""


@dataclass(frozen=True, slots=True)
class _ProcStat:
    pid: int
    ppid: int
    pgrp: int
    session: int
    start_ticks: int
    state: str


def _read_proc_stat(pid: int) -> _ProcStat | None:
    """Verified stat row, ``None`` if absent, ``_ProcUnknown`` if unreadable."""
    try:
        raw = (_PROC / str(pid) / "stat").read_text(encoding="ascii")
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
    """Full verified snapshot, or ``None`` when the table is not trustworthy."""
    snapshot: dict[int, _ProcStat] = {}
    try:
        entries = os.listdir(_PROC)
    except OSError:
        return None
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            pid = int(entry)
        except ValueError:
            continue
        try:
            stat = _read_proc_stat(pid)
        except _ProcUnknown:
            return None
        if stat is not None:
            snapshot[pid] = stat
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
    """Return (leader state, other live members); ``None`` means unverified."""
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
    """Descendants by ppid tree and by the child's own group/session."""
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


def _signal_verified(
    pid: int, start_ticks: int, group: int, signum: int,
) -> bool:
    """Signal only when /proc still shows this exact child as the leader."""
    try:
        stat = _read_proc_stat(pid)
    except _ProcUnknown:
        return False
    if (
        stat is None
        or stat.start_ticks != start_ticks
        or stat.pgrp != group
    ):
        return False
    try:
        os.killpg(group, signum)
    except OSError as exc:
        return exc.errno == errno.ESRCH
    return True


class _OutputDrain:
    """Drain stdout/stderr without retaining bytes; only counters are kept."""

    def __init__(self, stream: BinaryIO | None, maximum: int) -> None:
        self._stream = stream
        self._counter = [0]
        self._overflow = [False]
        self._finished = False
        self._thread = None
        if stream is not None:
            self._thread = threading.Thread(
                target=drain_bounded,
                args=(stream,),
                kwargs={
                    "maximum": maximum,
                    "counter": self._counter,
                    "overflow": self._overflow,
                },
                name="rag-child-output",
                daemon=True,
            )
            self._thread.start()

    def snapshot(self) -> BoundedOutput:
        return BoundedOutput(
            stdout_bytes=self._counter[0],
            stdout_overflow=self._overflow[0],
        )

    def finish(self) -> BoundedOutput:
        if self._finished:
            return self.snapshot()
        self._finished = True
        if self._thread is not None:
            try:
                self._thread.join(timeout=1.0)
                if self._thread.is_alive() and self._stream is not None:
                    self._stream.close()
                    self._thread.join(timeout=1.0)
            except (OSError, ValueError):
                pass
            if self._thread.is_alive():
                self._overflow[0] = True
        return self.snapshot()


def _pair_output(
    process: subprocess.Popen, limits: ChildLimits,
) -> tuple[_OutputDrain, _OutputDrain]:
    return (
        _OutputDrain(process.stdout, limits.max_stdout_bytes),
        _OutputDrain(process.stderr, limits.max_stderr_bytes),
    )


def _combined_output(
    drains: tuple[_OutputDrain, _OutputDrain],
) -> BoundedOutput:
    stdout = drains[0].finish()
    stderr = drains[1].finish()
    return BoundedOutput(
        stdout_bytes=stdout.stdout_bytes,
        stderr_bytes=stderr.stdout_bytes,
        stdout_overflow=stdout.stdout_overflow,
        stderr_overflow=stderr.stdout_overflow,
    )


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
            target=self._run, name="rag-child-descendants", daemon=True,
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

    def snapshot(self) -> dict[int, int]:
        return dict(self._found)

    def finish(self) -> dict[int, int]:
        self._stop.set()
        self._thread.join(timeout=0.5)
        if self._thread.is_alive():
            self._unknown = True
        return self.snapshot()


def _wire_limit(limits: ChildLimits) -> int:
    """JSON+base64 expansion cannot be bounded by the decoded payload alone."""
    decoded = max(limits.max_frame_bytes, limits.max_result_bytes)
    return min(MAX_WIRE_FRAME_BYTES, decoded * 2 + 65_536)


@dataclass
class _Handle:
    identity: ChildIdentity
    process: subprocess.Popen
    sock: socket.socket
    limits: ChildLimits
    output: tuple[_OutputDrain, _OutputDrain]
    state: str = "spawned"
    command: StageCommand | None = None
    grant: SendGrant | None = None
    grant_written: bool = False
    proof: StopProof | None = None
    result: ChildResult | None = None
    descendants: dict[int, int] | None = None
    monitor: _DescendantMonitor | None = None


@dataclass(frozen=True, slots=True)
class _SlotRecord:
    deployment_id: str
    slot_id: str
    boot_id: str
    attempt: int
    child_instance: str
    pid: int = 0
    process_group: int = 0
    start_ticks: int = 0
    started_monotonic: float = 0.0
    state: str = "starting"
    stop_failure: str | None = None
    proven: bool = False


class _SlotLedger:
    """One flock-guarded JSON record per deployment+slot."""

    def __init__(self, state_root: Path) -> None:
        self._root = state_root
        self._slots = state_root / "slots"
        try:
            self._slots.mkdir(parents=True, exist_ok=True, mode=0o700)
        except OSError:
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT) from None

    @property
    def root(self) -> Path:
        return self._root

    @staticmethod
    def name(deployment_id: str, slot_id: str) -> str:
        return hashlib.sha256(
            (deployment_id + "\0" + slot_id).encode("utf-8"),
        ).hexdigest() + ".json"

    @contextmanager
    def locked(self, deployment_id: str, slot_id: str) -> Iterator[Path]:
        path = self._slots / self.name(deployment_id, slot_id)
        lock_path = path.with_suffix(".lock")
        descriptor = None
        try:
            descriptor = os.open(
                lock_path,
                os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o600,
            )
            fcntl.flock(descriptor, fcntl.LOCK_EX)
        except OSError:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None
        try:
            yield path
        finally:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(descriptor)
            except OSError:
                pass

    @staticmethod
    def read(path: Path) -> _SlotRecord | None:
        try:
            descriptor = os.open(
                path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            )
        except FileNotFoundError:
            return None
        except OSError:
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None
        try:
            with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                raw = stream.read()
        except OSError:
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None
        try:
            data = json.loads(raw)
            return _SlotRecord(
                deployment_id=str(data["deployment_id"]),
                slot_id=str(data["slot_id"]),
                boot_id=str(data["boot_id"]),
                attempt=int(data["attempt"]),
                child_instance=str(data["child_instance"]),
                pid=int(data["pid"]),
                process_group=int(data["process_group"]),
                start_ticks=int(data["start_ticks"]),
                started_monotonic=float(data["started_monotonic"]),
                state=str(data["state"]),
                stop_failure=(
                    None if data.get("stop_failure") is None
                    else str(data["stop_failure"])
                ),
                proven=bool(data.get("proven", False)),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None

    @staticmethod
    def write(path: Path, record: _SlotRecord) -> None:
        try:
            _SlotLedger._write(path, record)
        except OSError:
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None

    @staticmethod
    def _write(path: Path, record: _SlotRecord) -> None:
        payload = json.dumps(
            {
                "deployment_id": record.deployment_id,
                "slot_id": record.slot_id,
                "boot_id": record.boot_id,
                "attempt": record.attempt,
                "child_instance": record.child_instance,
                "pid": record.pid,
                "process_group": record.process_group,
                "start_ticks": record.start_ticks,
                "started_monotonic": record.started_monotonic,
                "state": record.state,
                "stop_failure": record.stop_failure,
                "proven": record.proven,
            },
            ensure_ascii=True, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
        )
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("short persistent write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, path)
        try:
            directory = os.open(
                path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC,
            )
        except OSError:
            return
        try:
            try:
                os.fsync(directory)
            except OSError:
                # tmpfs can reject directory fsync while still providing
                # atomic rename and flock; the record itself was fsynced.
                pass
        finally:
            os.close(directory)


class LinuxChildSupervisor:
    """Linux supervisor with a persistent deployment+slot occupancy ledger."""

    def __init__(
        self,
        *,
        state_root: str | os.PathLike[str],
        child_executable: str | None = None,
    ) -> None:
        if sys.platform != "linux":
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if state_root is None:
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        root = Path(state_root)
        if not root.is_absolute():
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        self._executable = child_executable or sys.executable
        self._ledger = _SlotLedger(root)
        self._handles: dict[str, _Handle] = {}
        self._proofs: dict[str, StopProof] = {}
        self._lock = threading.Lock()

    @property
    def state_root(self) -> Path:
        return self._ledger.root

    @staticmethod
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

    def _get(self, identity: ChildIdentity) -> _Handle:
        handle = self._handles.get(identity.child_instance)
        if handle is None or handle.identity != identity:
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        return handle

    def _read(self, slot: ChildSlot) -> _SlotRecord | None:
        with self._ledger.locked(slot.deployment_id, slot.slot_id) as path:
            return _SlotLedger.read(path)

    def _write(self, slot: ChildSlot, record: _SlotRecord) -> None:
        with self._ledger.locked(slot.deployment_id, slot.slot_id) as path:
            _SlotLedger.write(path, record)

    # -- spawn -----------------------------------------------------------

    def spawn(self, slot: ChildSlot, limits: ChildLimits) -> ChildIdentity:
        if not isinstance(slot, ChildSlot) or not isinstance(limits, ChildLimits):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        child_instance = uuid.uuid4().hex
        with self._ledger.locked(slot.deployment_id, slot.slot_id) as path:
            previous = _SlotLedger.read(path)
            if previous is not None:
                self._require_releasable(previous)
            _SlotLedger.write(path, _SlotRecord(
                deployment_id=slot.deployment_id,
                slot_id=slot.slot_id,
                boot_id=slot.boot_id,
                attempt=slot.attempt,
                child_instance=child_instance,
                started_monotonic=time.monotonic(),
                state="starting",
            ))

        handle = None
        parent_sock = None
        started: tuple[int, int, int] | None = None
        observed: dict[str, object] = {"process": None}
        try:
            identity, handle, parent_sock, started = self._start(
                slot, limits, child_instance, observed,
            )
            self._write(slot, _SlotRecord(
                deployment_id=slot.deployment_id,
                slot_id=slot.slot_id,
                boot_id=slot.boot_id,
                attempt=slot.attempt,
                child_instance=child_instance,
                pid=identity.pid,
                process_group=identity.process_group,
                start_ticks=identity.start_ticks,
                started_monotonic=time.monotonic(),
                state="active",
            ))
            with self._lock:
                self._handles[identity.child_instance] = handle
            return identity
        except BaseException:
            if parent_sock is not None:
                try:
                    close_ipc(parent_sock)
                except BaseException:
                    pass
            # The manifest, not the return values lost by the exception, is
            # the source of truth for whether a process was started.
            try:
                current = self._read(slot)
            except ChildSupervisionError:
                current = None
            started_from_record = None
            process_started = (
                observed["process"] is not None
                or (current is not None and current.pid > 0)
            )
            if current is not None and current.child_instance == child_instance:
                if (
                    process_started
                    and current.process_group > 0
                    and current.start_ticks > 0
                ):
                    started_from_record = (
                        current.pid,
                        current.process_group,
                        current.start_ticks,
                    )
            if started_from_record is not None:
                started = started_from_record
            elif started is None and handle is not None:
                started = (
                    handle.identity.pid,
                    handle.identity.process_group,
                    handle.identity.start_ticks,
                )
            if not process_started:
                # Only the pre-claim existed; Popen was never reached.
                proven = True
            elif started is None:
                # Popen happened but its identity was not verifiable.  A live
                # child may exist, so keep the slot blocked.
                process = observed["process"]
                if isinstance(process, subprocess.Popen):
                    try:
                        process.wait(timeout=5)
                    except BaseException:
                        pass
                proven = False
            else:
                proven = self._cleanup_started(started, limits)
            try:
                persisted_pid = 0
                persisted_group = 0
                persisted_ticks = 0
                if current is not None and current.child_instance == child_instance:
                    persisted_pid = current.pid
                    persisted_group = current.process_group
                    persisted_ticks = current.start_ticks
                self._write(slot, _SlotRecord(
                    deployment_id=slot.deployment_id,
                    slot_id=slot.slot_id,
                    boot_id=slot.boot_id,
                    attempt=slot.attempt,
                    child_instance=child_instance,
                    pid=persisted_pid,
                    process_group=persisted_group,
                    start_ticks=persisted_ticks,
                    started_monotonic=time.monotonic(),
                    state="released" if proven else "blocked",
                    stop_failure=(
                        None if proven else ChildFailure.STOP_UNPROVEN.value
                    ),
                    proven=proven,
                ))
            except ChildSupervisionError:
                # Keep the original failure; the persisted claim is either
                # starting/active/blocked and cannot be silently reused.
                pass
            if handle is not None:
                # Dispose only this controller's local resources.  The
                # persisted record above decides whether the slot is released
                # or must stay blocked for explicit reconciliation.
                if handle.monitor is not None:
                    try:
                        handle.monitor.finish()
                    except BaseException:
                        pass
                for drain in handle.output:
                    try:
                        drain.finish()
                    except BaseException:
                        pass
                self._close_socket(handle)
                try:
                    handle.process.wait(timeout=5)
                except BaseException:
                    pass
            raise

    def _require_releasable(self, record: _SlotRecord) -> None:
        if not (record.proven and record.state == "released"):
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN)
        if record.pid <= 0:
            return
        if record.start_ticks <= 0 or record.process_group <= 0:
            # A release without a verified identity cannot prove absence.
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN)
        leader, members = _group_state(
            record.pid, record.start_ticks, record.process_group,
        )
        if leader is not False or members != []:
            raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN)

    def _start(
        self,
        slot: ChildSlot,
        limits: ChildLimits,
        child_instance: str,
        observed: dict[str, object],
    ) -> tuple[ChildIdentity, _Handle, socket.socket, tuple[int, int, int]]:
        parent_sock, child_sock = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM,
        )
        process = None
        started: tuple[int, int, int] | None = None
        try:
            process = subprocess.Popen(
                [
                    self._executable, "-m", "rag_app.entrypoints.call_child",
                    "--ipc-fd", str(child_sock.fileno()),
                ],
                shell=False,
                close_fds=True,
                pass_fds=(child_sock.fileno(),),
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self._child_env(),
            )
            observed["process"] = process
            child_sock.close()
            # Persist the Popen-owned pid before /proc or IPC can fail.  A
            # zero start token is deliberately unreleasable: it denies a new
            # spawn until an explicit reconciliation proves the child gone.
            self._write(slot, _SlotRecord(
                deployment_id=slot.deployment_id,
                slot_id=slot.slot_id,
                boot_id=slot.boot_id,
                attempt=slot.attempt,
                child_instance=child_instance,
                pid=process.pid,
                process_group=0,
                start_ticks=0,
                started_monotonic=time.monotonic(),
                state="starting",
            ))
            try:
                stat = _read_proc_stat(process.pid)
            except _ProcUnknown:
                raise ChildSupervisionError(ChildFailure.STOP_UNPROVEN) from None
            if stat is None or stat.state == "Z":
                raise ChildSupervisionError(ChildFailure.CHILD_EXITED)
            try:
                group = os.getpgid(process.pid)
            except OSError:
                group = stat.pgrp
            started = (process.pid, group, stat.start_ticks)
            # Persist the verified start token before any further blocking
            # step so a crash cannot leave an unowned live process.
            self._write(slot, _SlotRecord(
                deployment_id=slot.deployment_id,
                slot_id=slot.slot_id,
                boot_id=slot.boot_id,
                attempt=slot.attempt,
                child_instance=child_instance,
                pid=process.pid,
                process_group=group,
                start_ticks=stat.start_ticks,
                started_monotonic=time.monotonic(),
                state="starting",
            ))
            message = read_frame(
                parent_sock,
                limits.max_frame_bytes,
                deadline_monotonic=time.monotonic() + limits.startup_s,
                too_large_failure=ChildFailure.RESULT_TOO_LARGE,
                empty_failure=ChildFailure.CHILD_EXITED,
            )
            if message.get("type") != "ready":
                raise ChildSupervisionError(ChildFailure.IPC_PROTOCOL)
            identity = ChildIdentity(
                slot=slot,
                child_instance=child_instance,
                pid=process.pid,
                process_group=group,
                start_ticks=stat.start_ticks,
            )
            outputs = _pair_output(process, limits)
            handle = _Handle(
                identity=identity,
                process=process,
                sock=parent_sock,
                limits=limits,
                output=outputs,
                monitor=_DescendantMonitor(process.pid),
            )
            return identity, handle, parent_sock, started
        except BaseException:
            try:
                close_ipc(parent_sock)
            except BaseException:
                pass
            try:
                if child_sock.fileno() >= 0:
                    child_sock.close()
            except BaseException:
                pass
            # If no verified start token was recorded, no signal is safe: a
            # reused pid/group must never be signalled.  The persisted claim
            # remains blocked for explicit reconciliation.
            if process is not None:
                try:
                    process.wait(timeout=5)
                except BaseException:
                    pass
                for stream in (process.stdout, process.stderr):
                    try:
                        stream.close()
                    except BaseException:
                        pass
            raise

    def _cleanup_started(
        self, started: tuple[int, int, int], limits: ChildLimits,
    ) -> bool:
        """Bounded verified stop after a later spawn step failed."""
        pid, group, ticks = started
        suspected = _descendants(pid)
        leader, members = _group_state(pid, ticks, group)
        if leader is None or members is None:
            return False
        if suspected is None:
            return False
        for child_pid, child_ticks in suspected.items():
            # Detached descendants are not in the child's group.  Record them
            # as blocking; this owner has no verified authority to signal them.
            if _process_state(child_pid, child_ticks) is not False:
                return False
        if leader:
            _signal_verified(pid, ticks, group, signal.SIGTERM)
        deadline = time.monotonic() + limits.term_grace_s
        while time.monotonic() < deadline:
            leader, members = _group_state(pid, ticks, group)
            if leader is False and members == []:
                break
            if leader is None or members is None:
                return False
            time.sleep(0.02)
        leader, members = _group_state(pid, ticks, group)
        if leader is None or members is None:
            return False
        if leader or members:
            _signal_verified(pid, ticks, group, signal.SIGKILL)
            deadline = time.monotonic() + limits.kill_grace_s
            while time.monotonic() < deadline:
                leader, members = _group_state(pid, ticks, group)
                if leader is False and members == []:
                    break
                if leader is None or members is None:
                    return False
                time.sleep(0.02)
        leader, members = _group_state(pid, ticks, group)
        if leader is not False or members != []:
            return False
        # Recheck after termination: a descendant that was merely unverifiable
        # earlier must now be provably absent before the slot is released.
        for child_pid, child_ticks in suspected.items():
            if _process_state(child_pid, child_ticks) is not False:
                return False
        return True

    # -- one stage / one grant ------------------------------------------

    def prepare(
        self, identity: ChildIdentity, command: StageCommand, *,
        timeout_s: float = 5.0,
    ) -> None:
        handle = self._get(identity)
        if not isinstance(command, StageCommand):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if handle.state != "spawned":
            raise ChildSupervisionError(ChildFailure.INVALID_STATE)
        if command.attempt != identity.slot.attempt:
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        # Identity and manifest owner are rechecked before touching the socket.
        if _process_state(identity.pid, identity.start_ticks) is not True:
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        record = self._read(identity.slot)
        if (
            record is None
            or record.child_instance != identity.child_instance
            or record.pid != identity.pid
            or record.start_ticks != identity.start_ticks
            or record.state not in {"starting", "active"}
        ):
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        if record.process_group != identity.process_group:
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        deadline = time.monotonic() + float(timeout_s)
        try:
            write_frame(
                handle.sock,
                command_to_wire(command),
                handle.limits.max_frame_bytes,
                deadline_monotonic=deadline,
            )
            message = read_frame(
                handle.sock,
                handle.limits.max_frame_bytes,
                deadline_monotonic=deadline,
                too_large_failure=ChildFailure.RESULT_TOO_LARGE,
                empty_failure=ChildFailure.CHILD_EXITED,
            )
        except ChildSupervisionError as exc:
            handle.state = "failed"
            self._abort_handle(handle)
            raise ChildSupervisionError(exc.failure) from None
        if (
            message.get("type") != "prepared"
            or message.get("call_id") != command.call_id
            or message.get("attempt") != command.attempt
            or message.get("stage") != command.stage.value
        ):
            handle.state = "failed"
            self._abort_handle(handle)
            raise ChildSupervisionError(ChildFailure.IPC_PROTOCOL)
        handle.command = command
        handle.state = "prepared"

    def _abort_handle(self, handle: _Handle) -> None:
        try:
            close_ipc(handle.sock)
        except BaseException:
            pass
        identity = handle.identity
        leader, _ = _group_state(
            identity.pid, identity.start_ticks, identity.process_group,
        )
        if leader is True:
            _signal_verified(
                identity.pid, identity.start_ticks,
                identity.process_group, signal.SIGTERM,
            )
            try:
                handle.process.wait(timeout=handle.limits.term_grace_s)
            except BaseException:
                _signal_verified(
                    identity.pid, identity.start_ticks,
                    identity.process_group, signal.SIGKILL,
                )
                try:
                    handle.process.wait(timeout=handle.limits.kill_grace_s)
                except BaseException:
                    pass

    def grant(self, identity: ChildIdentity, grant: SendGrant) -> None:
        handle = self._get(identity)
        if not isinstance(grant, SendGrant):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if handle.grant_written:
            raise ChildSupervisionError(ChildFailure.GRANT_REUSED)
        if handle.state != "prepared" or handle.command is None:
            raise ChildSupervisionError(ChildFailure.INVALID_STATE)
        if handle.command.stage is not ChildStage.EGRESS:
            raise ChildSupervisionError(ChildFailure.INVALID_STATE)
        if grant.plan is None or grant.request is None:
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if (
            grant.call_id != handle.command.call_id
            or grant.attempt != handle.command.attempt
            or grant.boot_id != identity.slot.boot_id
            or grant.child_instance != identity.child_instance
        ):
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        # A write may partially reach the child; record that fact first.
        handle.grant = grant
        handle.grant_written = True
        handle.state = "granted"
        try:
            write_frame(
                handle.sock,
                grant_to_wire(grant),
                _wire_limit(handle.limits),
                deadline_monotonic=time.monotonic() + 30.0,
            )
        except ChildSupervisionError as exc:
            raise ChildSupervisionError(exc.failure) from None

    def receive(
        self, identity: ChildIdentity, *, timeout_s: float = 30.0,
    ) -> ChildResult:
        handle = self._get(identity)
        if handle.state not in {"prepared", "granted"} or handle.command is None:
            raise ChildSupervisionError(ChildFailure.INVALID_STATE)
        try:
            message = read_frame(
                handle.sock,
                _wire_limit(handle.limits),
                deadline_monotonic=time.monotonic() + float(timeout_s),
                too_large_failure=ChildFailure.RESULT_TOO_LARGE,
                empty_failure=ChildFailure.CHILD_EXITED,
            )
            result = result_from_wire(message)
            if result.call_id != handle.command.call_id:
                raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
            if len(result.payload) > handle.limits.max_result_bytes:
                raise ChildSupervisionError(ChildFailure.RESULT_TOO_LARGE)
            result = normalize_child_result(
                result,
                grant_written=handle.grant_written,
                grant=handle.grant,
            )
        except ChildSupervisionError as exc:
            result = self._conservative_result(handle, exc.failure)
        handle.result = result
        handle.state = "result"
        return result

    def _conservative_result(
        self, handle: _Handle, failure: ChildFailure,
    ) -> ChildResult:
        if handle.grant_written and handle.grant is not None:
            return ChildResult(
                call_id=handle.grant.call_id,
                grant_id=handle.grant.grant_id,
                send_state=SendState.MAY_HAVE_SENT,
                response_status=None,
                payload=b"",
                failure=failure,
            )
        command = handle.command
        if command is None:
            raise ChildSupervisionError(ChildFailure.INVALID_STATE)
        return ChildResult(
            call_id=command.call_id,
            grant_id=None,
            send_state=SendState.NOT_SENT,
            response_status=None,
            payload=b"",
            failure=failure,
        )

    # -- stop proof ------------------------------------------------------

    def _inspect_handle(self, handle: _Handle) -> StopProof:
        identity = handle.identity
        leader, members = _group_state(
            identity.pid, identity.start_ticks, identity.process_group,
        )
        recorded = handle.monitor.snapshot() if handle.monitor is not None else {}
        monitor_unknown = (
            handle.monitor.unknown if handle.monitor is not None else True
        )
        descendants_absent = (
            not monitor_unknown
            and all(
                _process_state(pid, ticks) is False
                for pid, ticks in recorded.items()
            )
        )
        output = _combined_output(handle.output)
        if leader is False:
            self._close_socket(handle)
            handle.grant = None
        grant_destroyed = not handle.grant_written or handle.grant is None
        verified = (
            leader is False
            and members == []
            and descendants_absent
            and handle.sock.fileno() < 0
            and grant_destroyed
            and output.bounded
        )
        return StopProof(
            identity=identity,
            exited=leader is False,
            exit_code=handle.process.returncode,
            process_group_empty=members == [],
            no_descendants=descendants_absent,
            ipc_closed=handle.sock.fileno() < 0,
            send_fds_closed=handle.sock.fileno() < 0,
            grant_destroyed=grant_destroyed,
            proven_monotonic=time.monotonic(),
            failure=None if verified else ChildFailure.STOP_UNPROVEN,
        )

    def inspect(self, identity: ChildIdentity) -> StopProof:
        final = self._proofs.get(identity.child_instance)
        if final is not None and final.identity == identity:
            return final
        handle = self._handles.get(identity.child_instance)
        if handle is None or handle.identity != identity:
            return self._foreign_proof(identity)
        return self._inspect_handle(handle)

    @staticmethod
    def _foreign_proof(identity: ChildIdentity) -> StopProof:
        """Without a local handle there is no authority to prove or signal."""
        return StopProof(
            identity=identity,
            exited=False,
            exit_code=None,
            process_group_empty=False,
            no_descendants=False,
            ipc_closed=False,
            send_fds_closed=False,
            grant_destroyed=False,
            proven_monotonic=time.monotonic(),
            failure=ChildFailure.STOP_UNPROVEN,
        )

    def _terminate_handle(
        self, handle: _Handle, reason: StopReason,
    ) -> StopProof:
        identity = handle.identity
        suspected = _descendants(identity.pid)
        collect_unknown = suspected is None
        # Hold the sampler's verdict from before the stop attempt: once its
        # thread is joined, its "unknown" state is a fact about the sampled
        # window, not about this final verification.
        sampled_before = handle.monitor.unknown if handle.monitor else True
        try:
            close_ipc(handle.sock)
        except BaseException:
            pass
        leader, members = _group_state(
            identity.pid, identity.start_ticks, identity.process_group,
        )
        if leader is None:
            self._finish_monitor(handle)
            return self._unproven(handle, suspected, monitor_unknown=True)
        if leader or members:
            _signal_verified(
                identity.pid, identity.start_ticks,
                identity.process_group, signal.SIGTERM,
            )
        deadline = time.monotonic() + handle.limits.term_grace_s
        while time.monotonic() < deadline:
            handle.process.poll()
            leader, members = _group_state(
                identity.pid, identity.start_ticks, identity.process_group,
            )
            if leader is False and members == []:
                break
            if leader is None or members is None:
                break
            time.sleep(0.02)
        leader, members = _group_state(
            identity.pid, identity.start_ticks, identity.process_group,
        )
        if leader is None or members is None:
            self._finish_monitor(handle)
            return self._unproven(handle, suspected, monitor_unknown=True)
        if leader or members:
            _signal_verified(
                identity.pid, identity.start_ticks,
                identity.process_group, signal.SIGKILL,
            )
            deadline = time.monotonic() + handle.limits.kill_grace_s
            while time.monotonic() < deadline:
                handle.process.poll()
                leader, members = _group_state(
                    identity.pid, identity.start_ticks, identity.process_group,
                )
                if leader is False and members == []:
                    break
                if leader is None or members is None:
                    break
                time.sleep(0.02)
        try:
            handle.process.wait(timeout=1.0)
        except BaseException:
            pass
        recorded = handle.monitor.finish() if handle.monitor is not None else {}
        monitor_unknown = sampled_before or (
            handle.monitor.unknown if handle.monitor is not None else True
        )
        if suspected is None:
            suspected = {}
        suspected.update(recorded)
        handle.descendants = dict(suspected)
        leader, members = _group_state(
            identity.pid, identity.start_ticks, identity.process_group,
        )
        live_descendants = [
            pid for pid, ticks in suspected.items()
            if _process_state(pid, ticks) is not False
        ]
        output = _combined_output(handle.output)
        verified = (
            not collect_unknown
            and not monitor_unknown
            and leader is False
            and members == []
            and not live_descendants
            and output.bounded
        )
        if leader is False:
            self._close_socket(handle)
        ipc_closed = handle.sock.fileno() < 0
        if leader is False:
            handle.grant = None
        grant_destroyed = not handle.grant_written or handle.grant is None
        return StopProof(
            identity=identity,
            exited=leader is False,
            exit_code=handle.process.returncode,
            process_group_empty=members == [],
            no_descendants=not live_descendants,
            ipc_closed=ipc_closed,
            send_fds_closed=ipc_closed,
            grant_destroyed=grant_destroyed,
            proven_monotonic=time.monotonic(),
            failure=(
                None if verified and ipc_closed and grant_destroyed
                else ChildFailure.STOP_UNPROVEN
            ),
        )

    @staticmethod
    def _finish_monitor(handle: _Handle) -> None:
        if handle.monitor is not None:
            try:
                handle.monitor.finish()
            except BaseException:
                pass

    @staticmethod
    def _unproven(
        handle: _Handle, suspected: dict[int, int] | None, *,
        monitor_unknown: bool,
    ) -> StopProof:
        return StopProof(
            identity=handle.identity,
            exited=False,
            exit_code=handle.process.returncode,
            process_group_empty=False,
            no_descendants=not monitor_unknown and suspected is not None,
            ipc_closed=handle.sock.fileno() < 0,
            send_fds_closed=False,
            grant_destroyed=False,
            proven_monotonic=time.monotonic(),
            failure=ChildFailure.STOP_UNPROVEN,
        )

    @staticmethod
    def _close_socket(handle: _Handle) -> None:
        try:
            handle.sock.close()
        except OSError:
            pass

    def _recover_registered(self, identity: ChildIdentity) -> StopProof:
        """Recover a persisted child owned by a dead controller.

        Only a registered, matching identity may be signalled.  Even after a
        verified exit this instance cannot prove the old IPC/send FDs and grant
        were destroyed, so the returned proof stays unproven.
        """
        try:
            record = self._read(identity.slot)
        except ChildSupervisionError:
            return self._foreign_proof(identity)
        if (
            record is None
            or record.child_instance != identity.child_instance
            or record.pid != identity.pid
            or record.process_group != identity.process_group
            or record.start_ticks != identity.start_ticks
        ):
            return self._foreign_proof(identity)
        leader = _process_state(record.pid, record.start_ticks)
        if leader is not True:
            return self._foreign_proof(identity)
        _signal_verified(
            record.pid, record.start_ticks, record.process_group, signal.SIGTERM,
        )
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if _process_state(record.pid, record.start_ticks) is False:
                break
            time.sleep(0.02)
        if _process_state(record.pid, record.start_ticks) is not False:
            _signal_verified(
                record.pid, record.start_ticks,
                record.process_group, signal.SIGKILL,
            )
            deadline = time.monotonic() + 10.0
            while time.monotonic() < deadline:
                if _process_state(record.pid, record.start_ticks) is False:
                    break
                time.sleep(0.02)
        return self._foreign_proof(identity)

    def stop(self, identity: ChildIdentity, reason: StopReason) -> StopProof:
        if not isinstance(reason, StopReason):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        handle = self._handles.get(identity.child_instance)
        if handle is None or handle.identity != identity:
            final = self._proofs.get(identity.child_instance)
            if (
                final is not None
                and final.proven
                and final.identity == identity
            ):
                return final
            return self._recover_registered(identity)
        if handle.proof is not None and handle.proof.proven:
            return handle.proof
        proof = self._terminate_handle(handle, reason)
        handle.proof = proof
        handle.state = "stopped"
        self._proofs[identity.child_instance] = proof
        try:
            self._write(identity.slot, _SlotRecord(
                deployment_id=identity.slot.deployment_id,
                slot_id=identity.slot.slot_id,
                boot_id=identity.slot.boot_id,
                attempt=identity.slot.attempt,
                child_instance=identity.child_instance,
                pid=identity.pid,
                process_group=identity.process_group,
                start_ticks=identity.start_ticks,
                started_monotonic=proof.proven_monotonic,
                state="released" if proof.proven else "blocked",
                stop_failure=(
                    None if proof.failure is None else proof.failure.value
                ),
                proven=proof.proven,
            ))
        except ChildSupervisionError:
            proof = StopProof(
                identity=proof.identity,
                exited=proof.exited,
                exit_code=proof.exit_code,
                process_group_empty=proof.process_group_empty,
                no_descendants=proof.no_descendants,
                ipc_closed=proof.ipc_closed,
                send_fds_closed=proof.send_fds_closed,
                grant_destroyed=proof.grant_destroyed,
                proven_monotonic=proof.proven_monotonic,
                failure=ChildFailure.STOP_UNPROVEN,
            )
            handle.proof = proof
            self._proofs[identity.child_instance] = proof
            return proof
        if proof.proven:
            with self._lock:
                self._handles.pop(identity.child_instance, None)
        return proof

    def output_bytes(self, identity: ChildIdentity) -> tuple[int, int]:
        handle = self._get(identity)
        return (
            handle.output[0].snapshot().stdout_bytes,
            handle.output[1].snapshot().stdout_bytes,
        )

    def close(self) -> bool:
        proven = True
        for child_instance in list(self._handles):
            handle = self._handles.get(child_instance)
            if handle is None:
                continue
            try:
                proof = self.stop(handle.identity, StopReason.CONTROLLER_STOP)
            except ChildSupervisionError:
                proven = False
                continue
            proven = proven and proof.proven
        return proven
