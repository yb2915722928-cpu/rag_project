"""Local ext4 original storage: server paths, flock lifecycle, atomic rename.

Two distinct locks, matching R2/R3:

* the **upload slot** is one system-wide exclusive ``flock`` held by the
  controller for one in-flight transfer.  It is released only after the child
  writer is confirmed exited, or by the kernel when the controller dies.
* the **asset lifecycle lock** is a shared ``flock`` taken by the writer child
  itself before its first byte and held until every FD is closed, so a future
  cleanup can take the exclusive side and cannot race an open writer.

Paths are always generated here.  A display name never becomes a path segment,
and nothing in this module is called while a PostgreSQL transaction is open.
"""

from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
import time
from typing import Any

try:  # Native writer semantics are Linux-only; imports stay usable elsewhere.
    import fcntl
except ImportError:  # pragma: no cover - exercised on Windows development hosts
    fcntl = None  # type: ignore[assignment]

from rag_app.contracts.errors import ALL_MESSAGES
from rag_app.modules.library.uploads import validate_asset_prefix


class StoreUnavailable(Exception):
    """Finite local-storage failure; never contains a path or an OS message."""

    def __init__(self, code: str) -> None:
        self.code = code if code in ALL_MESSAGES else "DATABASE_OPERATION_FAILED"
        super().__init__(self.code)


def _require_linux_flock() -> None:
    if fcntl is None:
        raise StoreUnavailable("STORAGE_PRESSURE")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class UploadSlot:
    """Cross-process single upload slot; the kernel releases it on process death."""

    def __init__(self, lock_path: Path) -> None:
        self._lock_path = lock_path
        self._descriptor: int | None = None

    @property
    def held(self) -> bool:
        return self._descriptor is not None

    @property
    def fileno(self) -> int:
        """Inherited descriptor for the supervised writer; never duplicated here."""

        if self._descriptor is None:
            raise StoreUnavailable("CONCURRENCY_LIMIT_EXCEEDED")
        return self._descriptor

    def acquire(self, *, wait_s: int) -> None:
        _require_linux_flock()
        if self._descriptor is not None:
            raise StoreUnavailable("CONCURRENCY_LIMIT_EXCEEDED")
        try:
            descriptor = os.open(
                self._lock_path,
                os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o600,
            )
        except OSError:
            raise StoreUnavailable("STORAGE_PRESSURE") from None
        deadline = time.monotonic() + max(0, wait_s)
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    os.close(descriptor)
                    raise StoreUnavailable("STORAGE_PRESSURE") from None
                if time.monotonic() >= deadline:
                    os.close(descriptor)
                    raise StoreUnavailable("CONCURRENCY_LIMIT_EXCEEDED") from None
                time.sleep(0.02)
                continue
            self._descriptor = descriptor
            return

    def release(self) -> None:
        descriptor = self._descriptor
        self._descriptor = None
        if descriptor is None:
            return
        # The caller may release only after a supervised writer has proven it
        # stopped.  Unlocking an open-file-description shared with a live child
        # would release the physical slot for that child as well.
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(descriptor)
        except OSError:
            pass

    def close(self) -> None:
        """Close this process's reference without unlocking a shared child's lock."""

        descriptor = self._descriptor
        self._descriptor = None
        if descriptor is None:
            return
        try:
            os.close(descriptor)
        except OSError:
            pass


class LocalOriginalStore:
    """Bounded local storage rooted on an operator-provided absolute directory."""

    def __init__(
        self, root: str | os.PathLike[str], *, page_bytes: int,
    ) -> None:
        _require_linux_flock()
        base = Path(root)
        if not base.is_absolute():
            raise StoreUnavailable("CONFIGURATION_INVALID")
        self._root = base
        self._assets = base / "assets"
        self._staging = base / "staging"
        self._locks = base / "locks"
        self._page_bytes = page_bytes
        self._ensure(self._assets)
        self._ensure(self._staging)
        self._ensure(self._locks)

    @staticmethod
    def _ensure(path: Path) -> None:
        try:
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError:
            raise StoreUnavailable("STORAGE_PRESSURE") from None

    @property
    def root(self) -> Path:
        return self._root

    def slot(self) -> UploadSlot:
        return UploadSlot(self._locks / "upload-slot.lock")

    def paths(self, prefix: str) -> dict[str, str]:
        """Server-generated paths for one non-reusable prefix."""

        validate_asset_prefix(prefix)
        final_dir = self._assets / prefix[:2] / prefix
        staging = self._staging / (prefix + ".part")
        return {
            "final_dir": str(final_dir),
            "final": str(final_dir / "original"),
            "staging": str(staging),
            "lock": str(self._locks / (prefix + ".lock")),
            "relative": f"assets/{prefix[:2]}/{prefix}/original",
        }

    def prepare_paths(self, prefix: str) -> dict[str, str]:
        paths = self.paths(prefix)
        try:
            Path(paths["final_dir"]).mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError:
            raise StoreUnavailable("STORAGE_PRESSURE") from None
        return paths

    def resolve_relative(self, relative: str) -> Path:
        """Only a server-recorded relative path; never a client value."""

        if not isinstance(relative, str) or not relative.startswith("assets/"):
            raise StoreUnavailable("SOURCE_LOCATOR_UNAVAILABLE")
        candidate = (self._root / relative).resolve()
        root = self._root.resolve()
        if root not in candidate.parents:
            raise StoreUnavailable("SOURCE_LOCATOR_UNAVAILABLE")
        return candidate

    def free_bytes(self) -> int:
        try:
            stat = os.statvfs(self._root)
        except OSError:
            raise StoreUnavailable("STORAGE_PRESSURE") from None
        return stat.f_bavail * stat.f_frsize

    def discard_staging(self, staging: str) -> bool:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            return True
        except OSError:
            return False
        return True


def open_lifecycle_shared(lock_path: str) -> int:
    """Writer-side shared lifecycle lock; taken before the first byte."""

    descriptor = os.open(
        lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600,
    )
    fcntl.flock(descriptor, fcntl.LOCK_SH)
    return descriptor


def close_lifecycle(descriptor: int) -> None:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    except OSError:
        pass
    try:
        os.close(descriptor)
    except OSError:
        pass


class BoundedWriter:
    """Write-only sink used by the child; enforces byte and UTF-8 bounds."""

    def __init__(
        self, *, staging: str, final: str, max_bytes: int, page_bytes: int,
    ) -> None:
        self._staging = staging
        self._final = final
        self._max_bytes = max_bytes
        self._page_bytes = page_bytes
        self._digest = hashlib.sha256()
        self._bytes = 0
        self._handle: Any = None
        self._decoder = None

    def __enter__(self) -> BoundedWriter:
        import codecs

        self._decoder = codecs.getincrementaldecoder("utf-8")("strict")
        self._handle = open(
            self._staging, "wb", buffering=self._page_bytes or 64 * 1024,
        )
        return self

    def feed(self, chunk: bytes) -> None:
        if not chunk:
            return
        self._bytes += len(chunk)
        if self._bytes > self._max_bytes:
            raise StoreUnavailable("FILE_LIMIT_EXCEEDED")
        self._digest.update(chunk)
        try:
            self._decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            raise StoreUnavailable("UPLOAD_CONTENT_CONFLICT") from None
        written = 0
        view = memoryview(chunk)
        while written < len(chunk):
            written += self._handle.write(view[written:])

    def finish(self) -> tuple[int, str]:
        try:
            self._decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            raise StoreUnavailable("UPLOAD_CONTENT_CONFLICT") from None
        if self._bytes == 0:
            raise StoreUnavailable("UPLOAD_CONTENT_CONFLICT")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        self._handle = None
        os.replace(self._staging, self._final)
        _fsync_directory(Path(self._final).parent)
        return self._bytes, self._digest.hexdigest()

    def abort(self) -> None:
        if self._handle is not None:
            try:
                self._handle.close()
            except OSError:
                pass
            self._handle = None
        try:
            os.unlink(self._staging)
        except OSError:
            pass

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is not None or self._handle is not None:
            self.abort()


class VerifySink:
    """Re-hash a duplicate PUT without rewriting or replacing the original."""

    def __init__(self, *, max_bytes: int) -> None:
        self._max_bytes = max_bytes
        self._digest = hashlib.sha256()
        self._bytes = 0
        self._decoder = None

    def __enter__(self) -> VerifySink:
        import codecs

        self._decoder = codecs.getincrementaldecoder("utf-8")("strict")
        return self

    def feed(self, chunk: bytes) -> None:
        if not chunk:
            return
        self._bytes += len(chunk)
        if self._bytes > self._max_bytes:
            raise StoreUnavailable("FILE_LIMIT_EXCEEDED")
        self._digest.update(chunk)
        try:
            self._decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            raise StoreUnavailable("UPLOAD_CONTENT_CONFLICT") from None

    def finish(self) -> tuple[int, str]:
        try:
            self._decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            raise StoreUnavailable("UPLOAD_CONTENT_CONFLICT") from None
        return self._bytes, self._digest.hexdigest()

    def abort(self) -> None:
        return

    def __exit__(self, exc_type, exc, traceback) -> None:
        return
