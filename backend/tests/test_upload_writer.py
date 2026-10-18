"""Real Linux process, lock and IPC acceptance for the upload writer child."""

from __future__ import annotations

import ast
import fcntl
import hashlib
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from rag_app.adapters import upload_supervisor as module
from rag_app.adapters.original_store import StoreUnavailable, UploadSlot


pytestmark = pytest.mark.skipif(
    sys.platform != "linux",
    reason="The upload writer is a Linux process-group acceptance path.",
)


@pytest.fixture
def paths(tmp_path):
    root = tmp_path / "store"
    assets = root / "assets" / "aa" / "prefix"
    staging = root / "staging" / "prefix.part"
    locks = root / "locks"
    for directory in (assets, staging.parent, locks):
        directory.mkdir(parents=True)
    return SimpleNamespace(
        root=root,
        assets=assets,
        staging=staging,
        final=assets / "original",
        locks=locks,
        lifecycle=locks / "prefix.lock",
        slot=locks / "upload-slot.lock",
    )


class HeldSlot:
    """An UploadSlot plus the descriptor the production wiring must expose."""

    def __init__(self, path: Path) -> None:
        self.slot = UploadSlot(path)
        self.slot.acquire(wait_s=0)

    @property
    def fd(self) -> int:
        descriptor = self.slot._descriptor
        assert descriptor is not None
        return descriptor

    def release(self) -> None:
        self.slot.release()


def make_writer(paths, slot_fd: int, **overrides):
    values = {
        "staging": str(paths.staging),
        "final": str(paths.final),
        "lifecycle_lock": str(paths.lifecycle),
        "slot_fd": slot_fd,
        "max_bytes": 1_048_576,
        "page_bytes": 4096,
        "chunk_bytes": 16_384,
        "absolute_deadline_monotonic": time.monotonic() + 30.0,
        "no_progress_s": 5.0,
        "stop_grace_s": 0.5,
    }
    values.update(overrides)
    return module.SupervisedUploadWriter(**values)


def direct_children(pid: int) -> set[int]:
    found: set[int] = set()
    try:
        tasks = os.listdir(f"/proc/{pid}/task")
    except OSError:
        return found
    for task in tasks:
        try:
            text = Path(f"/proc/{pid}/task/{task}/children").read_text(
                encoding="ascii",
            )
        except OSError:
            continue
        for token in text.split():
            try:
                found.add(int(token))
            except ValueError:
                continue
    return found


def wait_new_child(parent: int, before: set[int], timeout: float = 5.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        new = direct_children(parent) - before
        if new:
            return new.pop()
        time.sleep(0.02)
    pytest.fail("the upload child was not visible in /proc")


def process_exists(pid: int) -> bool:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    except OSError:
        return False
    close = raw.rfind(")")
    if close < 0:
        return False
    fields = raw[close + 2:].split()
    return bool(fields) and fields[0] != "Z"


def wait_absent(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not process_exists(pid):
            return True
        time.sleep(0.02)
    return not process_exists(pid)


def lock_is_free(path: Path) -> bool:
    descriptor: int | None = None
    try:
        descriptor = os.open(
            path,
            os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        except OSError:
            pass
        return True
    except OSError:
        return False
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def wait_lock_free(path: Path, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if lock_is_free(path):
            return True
        time.sleep(0.02)
    return lock_is_free(path)


def test_legitimate_stream_writes_exact_bytes_hash_and_proves_stop(paths) -> None:
    data = ("Hello 世界\n" * 5000).encode("utf-8")
    slot = HeldSlot(paths.slot)
    before = direct_children(os.getpid())
    try:
        writer = make_writer(
            paths, slot.fd, max_bytes=len(data) + 16,
            chunk_bytes=4096, page_bytes=4096,
        )
        with writer:
            child = wait_new_child(os.getpid(), before)
            assert not lock_is_free(paths.lifecycle)
            writer.feed(data[:1])
            writer.feed(data[1:7777])
            writer.feed(data[7777:])
            assert paths.staging.exists()
            assert paths.staging.stat().st_size > 0
            # A second open file description cannot take the held slot.
            assert not lock_is_free(paths.slot)
            size, digest = writer.finish()
        assert writer.stop_proven
        assert size == len(data)
        assert digest == hashlib.sha256(data).hexdigest()
        assert paths.final.read_bytes() == data
        assert not paths.staging.exists()
        assert wait_absent(child)
        assert wait_lock_free(paths.lifecycle)
        # The writer only passed the slot fd; it did not LOCK_UN the parent's
        # open file description.
        assert not lock_is_free(paths.slot)
    finally:
        slot.release()
    assert wait_lock_free(paths.slot)


def test_incremental_utf8_across_single_byte_chunks(paths) -> None:
    data = "你好🙂".encode("utf-8")
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(
            paths, slot.fd, max_bytes=len(data), chunk_bytes=1, page_bytes=0,
        )
        with writer:
            for byte in data:
                writer.feed(bytes([byte]))
            size, digest = writer.finish()
        assert writer.stop_proven
        assert size == len(data)
        assert digest == hashlib.sha256(data).hexdigest()
        assert paths.final.read_bytes() == data
    finally:
        slot.release()


def test_feed_splits_input_into_bounded_ipc_chunks(paths, monkeypatch) -> None:
    recorded: list[int] = []
    original = module._chunk_frame

    def recording(sequence: int, chunk: memoryview) -> bytes:
        recorded.append(len(chunk))
        return original(sequence, chunk)

    monkeypatch.setattr(module, "_chunk_frame", recording)
    data = b"x" * 20_000
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(
            paths, slot.fd, max_bytes=len(data), chunk_bytes=4096,
        )
        with writer:
            writer.feed(data)
        assert writer.stop_proven
        assert recorded
        assert max(recorded) <= 4096
        assert sum(recorded) == len(data)
        assert paths.final.read_bytes() == data
    finally:
        slot.release()


def test_oversize_upload_fails_bounded_and_keeps_the_slot(paths) -> None:
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(paths, slot.fd, max_bytes=4)
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.feed(b"abcde")
        assert caught.value.code == "FILE_LIMIT_EXCEEDED"
        assert writer.stop_proven
        assert not paths.staging.exists()
        assert not paths.final.exists()
        assert not lock_is_free(paths.slot)
    finally:
        slot.release()


def test_bad_utf8_fails_bounded_and_removes_staging(paths) -> None:
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(paths, slot.fd)
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.feed(b"valid")
                writer.feed(b"\xff")
        assert caught.value.code == "UPLOAD_CONTENT_CONFLICT"
        assert writer.stop_proven
        assert not paths.staging.exists()
        assert not paths.final.exists()
    finally:
        slot.release()


def test_zero_byte_finish_fails(paths) -> None:
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(paths, slot.fd)
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.finish()
        assert caught.value.code == "UPLOAD_CONTENT_CONFLICT"
        assert writer.stop_proven
        assert not paths.staging.exists()
        assert not paths.final.exists()
    finally:
        slot.release()


def test_absolute_deadline_is_not_refreshed(paths) -> None:
    deadline = time.monotonic() + 2.0
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(
            paths, slot.fd, absolute_deadline_monotonic=deadline,
            no_progress_s=5.0, stop_grace_s=2.0,
        )
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.feed(b"a")
                time.sleep(max(0.0, deadline - time.monotonic()) + 0.1)
                writer.feed(b"b")
        assert caught.value.code == "UPLOAD_EXPIRED"
        assert writer.stop_proven
        assert not paths.staging.exists()
        assert not paths.final.exists()
    finally:
        slot.release()


def test_no_progress_deadline_fails_without_refresh(paths) -> None:
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(
            paths, slot.fd, no_progress_s=0.4,
            absolute_deadline_monotonic=time.monotonic() + 30.0,
            stop_grace_s=2.0,
        )
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.feed(b"a")
                time.sleep(0.6)
                writer.feed(b"b")
        assert caught.value.code == "UPLOAD_EXPIRED"
        assert writer.stop_proven
        assert not paths.staging.exists()
        assert not paths.final.exists()
    finally:
        slot.release()


def test_abort_removes_staging_and_proves_stop(paths) -> None:
    slot = HeldSlot(paths.slot)
    before = direct_children(os.getpid())
    try:
        writer = make_writer(paths, slot.fd)
        with writer:
            child = wait_new_child(os.getpid(), before)
            writer.feed(b"partial")
            writer.abort()
            writer.abort()
            assert writer.stop_proven
            assert not paths.staging.exists()
            assert not paths.final.exists()
            assert wait_absent(child)
            assert wait_lock_free(paths.lifecycle)
            assert not lock_is_free(paths.slot)
    finally:
        slot.release()


def test_dead_child_fails_and_still_proves_stop(paths) -> None:
    slot = HeldSlot(paths.slot)
    before = direct_children(os.getpid())
    try:
        writer = make_writer(paths, slot.fd)
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                child = wait_new_child(os.getpid(), before)
                os.kill(child, signal.SIGKILL)
                assert wait_absent(child)
                writer.feed(b"cannot-write")
        assert caught.value.code in {"STORAGE_PRESSURE", "UPLOAD_EXPIRED"}
        assert writer.stop_proven
        assert not paths.final.exists()
    finally:
        slot.release()


def test_stopped_child_applies_bounded_backpressure(paths) -> None:
    slot = HeldSlot(paths.slot)
    before = direct_children(os.getpid())
    try:
        writer = make_writer(
            paths, slot.fd, max_bytes=2 * 1024 * 1024,
            chunk_bytes=1024 * 1024, page_bytes=4096,
            no_progress_s=0.5, stop_grace_s=0.5,
        )
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                child = wait_new_child(os.getpid(), before)
                os.kill(child, signal.SIGSTOP)
                started = time.monotonic()
                writer.feed(b"x" * (1024 * 1024))
                elapsed = time.monotonic() - started
                assert elapsed < 6.0
        assert caught.value.code in {"UPLOAD_EXPIRED", "STORAGE_PRESSURE"}
        assert writer.stop_proven
    finally:
        slot.release()


def test_finish_requires_a_proven_stop(paths, monkeypatch) -> None:
    slot = HeldSlot(paths.slot)
    try:
        writer = make_writer(paths, slot.fd)
        with pytest.raises(StoreUnavailable) as caught:
            with writer:
                writer.feed(b"committed")
                # A live descendant is exactly the fact that keeps a stop
                # unproven even after the direct child has exited.
                monkeypatch.setattr(
                    module, "_descendants", lambda pid: {os.getpid(): 1},
                )
                monkeypatch.setattr(
                    module, "_process_state", lambda pid, ticks: True,
                )
                writer.finish()
        assert caught.value.code == "UPLOAD_IN_PROGRESS"
        assert writer.stop_proven is False
        assert paths.final.read_bytes() == b"committed"
        assert not paths.staging.exists()
    finally:
        slot.release()


def test_child_environment_is_allowlisted(paths, monkeypatch) -> None:
    monkeypatch.setenv("RAG_TEST_SECRET_TOKEN", "must-not-reach-the-child")
    slot = HeldSlot(paths.slot)
    before = direct_children(os.getpid())
    try:
        writer = make_writer(paths, slot.fd)
        with writer:
            child = wait_new_child(os.getpid(), before)
            entries = Path(f"/proc/{child}/environ").read_bytes().split(b"\0")
            assert not any(
                entry.startswith(b"RAG_TEST_SECRET_TOKEN=") for entry in entries
            )
            writer.feed(b"ok")
    finally:
        slot.release()


def test_invalid_path_and_closed_slot_fail_finitely(paths) -> None:
    with pytest.raises(StoreUnavailable) as caught:
        make_writer(paths, 3, staging="relative/path")
    assert caught.value.code == "CONFIGURATION_INVALID"

    writer = make_writer(paths, 2**30)
    with pytest.raises(StoreUnavailable) as caught:
        with writer:
            pass
    assert caught.value.code == "CONFIGURATION_INVALID"
    # No child was ever started, so no writer can still be running.
    assert writer.stop_proven is True


_CONTROLLER = r"""
import fcntl
import os
import sys
import time
from pathlib import Path

from rag_app.adapters.upload_supervisor import SupervisedUploadWriter


def children(pid):
    found = set()
    for task in os.listdir(f"/proc/{pid}/task"):
        try:
            text = Path(f"/proc/{pid}/task/{task}/children").read_text(
                encoding="ascii",
            )
        except OSError:
            continue
        for token in text.split():
            try:
                found.add(int(token))
            except ValueError:
                continue
    return found


slot_path, staging, final, lifecycle, pidfile, readyfile = sys.argv[1:7]
before = children(os.getpid())
descriptor = os.open(
    slot_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600,
)
fcntl.flock(descriptor, fcntl.LOCK_EX)
writer = SupervisedUploadWriter(
    staging=staging,
    final=final,
    lifecycle_lock=lifecycle,
    slot_fd=descriptor,
    max_bytes=1024 * 1024,
    page_bytes=4096,
    chunk_bytes=4096,
    absolute_deadline_monotonic=time.monotonic() + 60.0,
    no_progress_s=60.0,
    stop_grace_s=5.0,
)
with writer:
    deadline = time.monotonic() + 10.0
    child = None
    while time.monotonic() < deadline:
        new = children(os.getpid()) - before
        if new:
            child = new.pop()
            break
        time.sleep(0.02)
    if child is None:
        raise SystemExit(3)
    Path(pidfile).write_text(str(child), encoding="ascii")
    ready = Path(readyfile)
    temporary = ready.with_name(ready.name + ".tmp")
    temporary.write_text("ready", encoding="ascii")
    os.replace(temporary, ready)
    writer.feed(b"x" * 8192)
    time.sleep(60)
"""


def test_dead_controller_child_keeps_the_upload_slot(paths, tmp_path) -> None:
    pidfile = tmp_path / "child.pid"
    readyfile = tmp_path / "ready"
    backend = Path(__file__).parents[1]
    env = dict(os.environ)
    source = str(backend / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = source if not existing else source + os.pathsep + existing
    controller = subprocess.Popen(
        [
            sys.executable, "-c", _CONTROLLER,
            str(paths.slot), str(paths.staging), str(paths.final),
            str(paths.lifecycle), str(pidfile), str(readyfile),
        ],
        cwd=backend,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    child: int | None = None
    try:
        deadline = time.monotonic() + 15.0
        while time.monotonic() < deadline:
            if readyfile.exists() and pidfile.exists():
                break
            if controller.poll() is not None:
                pytest.fail("the controller exited before the child was ready")
            time.sleep(0.02)
        else:
            pytest.fail("the controller did not report a ready child")
        child = int(pidfile.read_text(encoding="ascii"))
        assert process_exists(child)

        os.kill(child, signal.SIGSTOP)
        os.kill(controller.pid, signal.SIGKILL)
        controller.wait(timeout=5.0)

        # The stopped child still owns the inherited upload-slot descriptor.
        assert process_exists(child)
        assert not lock_is_free(paths.slot)
        assert not lock_is_free(paths.lifecycle)

        os.kill(child, signal.SIGKILL)
        assert wait_absent(child)
        assert wait_lock_free(paths.slot, timeout=10.0)
        assert wait_lock_free(paths.lifecycle, timeout=10.0)
    finally:
        if child is not None and process_exists(child):
            try:
                os.kill(child, signal.SIGKILL)
            except OSError:
                pass
        if controller.poll() is None:
            try:
                os.kill(controller.pid, signal.SIGKILL)
            except OSError:
                pass
        try:
            controller.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            pass


def _raw_child(paths, slot_fd: int, *, chunk_bytes: int = 4096):
    parent, child = __import__("socket").socketpair()
    process = subprocess.Popen(
        [
            sys.executable, "-m", "rag_app.entrypoints.upload_child",
            "--ipc-fd", str(child.fileno()),
            "--slot-fd", str(slot_fd),
        ],
        pass_fds=(child.fileno(), slot_fd),
        close_fds=True,
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=module._child_env(),
    )
    child.close()
    try:
        module._send_frame(
            parent,
            module._json_frame(module.FRAME_INIT, {
                "version": 1,
                "staging": str(paths.staging),
                "final": str(paths.final),
                "lifecycle_lock": str(paths.lifecycle),
                "max_bytes": 1024 * 1024,
                "page_bytes": 4096,
                "chunk_bytes": chunk_bytes,
                "absolute_deadline_monotonic": time.monotonic() + 30.0,
                "no_progress_s": 5.0,
            }),
            time.monotonic() + 5.0,
        )
        kind, _ = module._recv_frame(
            parent, module._MAX_CONTROL_BYTES,
            deadline=time.monotonic() + 5.0, timeout_code="STORAGE_PRESSURE",
        )
        assert kind == module.FRAME_READY
    except BaseException:
        parent.close()
        process.kill()
        process.wait(timeout=5.0)
        raise
    return process, parent


@pytest.mark.parametrize(
    "kind,payload,expected",
    [
        (99, b"", "UPLOAD_IN_PROGRESS"),
        (
            module.FRAME_CHUNK,
            struct.pack("!I", 0) + b"x" * 5001,
            "FILE_LIMIT_EXCEEDED",
        ),
    ],
)
def test_child_rejects_unknown_or_oversize_commands(
    paths, kind, payload, expected,
) -> None:
    slot = HeldSlot(paths.slot)
    process = parent = None
    try:
        process, parent = _raw_child(paths, slot.fd)
        module._send_frame(
            parent,
            module._FRAME_HEADER.pack(kind, len(payload)) + payload,
            time.monotonic() + 5.0,
        )
        reply_kind, reply = module._recv_frame(
            parent, module._MAX_CONTROL_BYTES,
            deadline=time.monotonic() + 5.0, timeout_code="STORAGE_PRESSURE",
        )
        assert reply_kind == module.FRAME_ERROR
        assert module._decode_control(reply)["code"] == expected
        assert process.wait(timeout=5.0) == 1
        assert not paths.staging.exists()
        assert wait_lock_free(paths.lifecycle)
        assert not lock_is_free(paths.slot)
    finally:
        if parent is not None:
            try:
                parent.close()
            except OSError:
                pass
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5.0)
        slot.release()


def test_upload_child_source_is_local_only() -> None:
    backend = Path(__file__).parents[1]
    path = backend / "src/rag_app/entrypoints/upload_child.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = (
        "sqlalchemy", "psycopg", "httpx", "fastapi",
        "rag_app.bootstrap", "rag_app.application",
    )
    assert not any(
        name == prefix or name.startswith(prefix + ".")
        for name in imported for prefix in forbidden
    )
    assert all(
        name == "rag_app.adapters.original_store"
        for name in imported if name.startswith("rag_app.adapters")
    )
    for token in (
        "subprocess", "socket.socketpair", "socket.create_connection",
        "socket.getaddrinfo", "urllib", "http.client", "os.system",
        "os.popen",
    ):
        assert token not in source
