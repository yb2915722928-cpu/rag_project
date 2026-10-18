"""Private child entrypoint for one bounded original upload.

The child receives a private socketpair fd and the controller's upload-slot
fd.  It keeps the slot fd open until process exit, takes the asset lifecycle
shared lock before its first byte, and writes only the caller-provided staging
path.  The final rename is performed by ``BoundedWriter`` after fsync.
"""

from __future__ import annotations

import json
import math
import os
import signal
import socket
import struct
import sys
import time
from typing import NoReturn

from rag_app.adapters.original_store import (
    BoundedWriter,
    StoreUnavailable,
    close_lifecycle,
    open_lifecycle_shared,
)


FRAME_INIT = 1
FRAME_CHUNK = 2
FRAME_ACK = 3
FRAME_FINISH = 4
FRAME_RESULT = 5
FRAME_ABORT = 6
FRAME_ERROR = 7
FRAME_READY = 8
FRAME_ABORTED = 9

_FRAME_HEADER = struct.Struct("!BI")
_ACK = struct.Struct("!IQ")
_MAX_CONTROL_BYTES = 16_384
_MAX_CHUNK_BYTES = 1_048_576
_MAX_FILE_BYTES = 8 * 1024 * 1024 * 1024
_MAX_WAIT_SECONDS = 300.0
_STARTUP_WAIT_S = 30.0

_FINITE_FAILURES = frozenset({
    "CONFIGURATION_INVALID",
    "FILE_LIMIT_EXCEEDED",
    "STORAGE_PRESSURE",
    "UPLOAD_CONTENT_CONFLICT",
    "UPLOAD_EXPIRED",
    "UPLOAD_IN_PROGRESS",
})


class _ChildFailure(Exception):
    __slots__ = ("code",)

    def __init__(self, code: str) -> None:
        self.code = code if code in _FINITE_FAILURES else "STORAGE_PRESSURE"
        super().__init__(self.code)


class _ChildTimeout(Exception):
    pass


class _ChildEof(Exception):
    pass


class _Terminated(Exception):
    pass


def _finite_code(code: object) -> str:
    return code if isinstance(code, str) and code in _FINITE_FAILURES else "STORAGE_PRESSURE"


def _recv_exact(sock: socket.socket, size: int, deadline: float) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _ChildTimeout()
        try:
            sock.settimeout(remaining)
            part = sock.recv(size - len(chunks))
        except InterruptedError:
            continue
        except TimeoutError:
            raise _ChildTimeout() from None
        except OSError:
            raise _ChildEof() from None
        if not part:
            raise _ChildEof()
        chunks.extend(part)
    return bytes(chunks)


def _read_frame(
    sock: socket.socket, max_payload: int, deadline: float,
) -> tuple[int, bytes]:
    header = _recv_exact(sock, _FRAME_HEADER.size, deadline)
    kind, length = _FRAME_HEADER.unpack(header)
    if length > max_payload:
        raise _ChildFailure("FILE_LIMIT_EXCEEDED")
    payload = _recv_exact(sock, length, deadline)
    return kind, payload


def _send_frame(sock: socket.socket, frame: bytes, deadline: float) -> None:
    view = memoryview(frame)
    while view:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _ChildTimeout()
        try:
            sock.settimeout(remaining)
            written = sock.send(view)
        except InterruptedError:
            continue
        except TimeoutError:
            raise _ChildTimeout() from None
        except OSError:
            raise _ChildEof() from None
        if written <= 0:
            raise _ChildEof()
        view = view[written:]


def _json_frame(kind: int, value: dict[str, object]) -> bytes:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(payload) > _MAX_CONTROL_BYTES:
        raise _ChildFailure("STORAGE_PRESSURE")
    return _FRAME_HEADER.pack(kind, len(payload)) + payload


def _empty_frame(kind: int) -> bytes:
    return _FRAME_HEADER.pack(kind, 0)


def _ack_frame(sequence: int, total: int) -> bytes:
    return _FRAME_HEADER.pack(FRAME_ACK, _ACK.size) + _ACK.pack(sequence, total)


def _decode_control(payload: bytes) -> dict[str, object]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise _ChildFailure("STORAGE_PRESSURE") from None
    if not isinstance(value, dict):
        raise _ChildFailure("STORAGE_PRESSURE")
    return value


def _safe_error(sock: socket.socket, code: str) -> None:
    try:
        _send_frame(
            sock,
            _json_frame(FRAME_ERROR, {"code": _finite_code(code)}),
            time.monotonic() + 2.0,
        )
    except BaseException:
        pass


def _safe_control(
    sock: socket.socket, kind: int, value: dict[str, object],
) -> None:
    try:
        _send_frame(
            sock, _json_frame(kind, value), time.monotonic() + 5.0,
        )
    except BaseException:
        pass


def _absolute_path(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 4096
        or "\x00" in value
        or not os.path.isabs(value)
    ):
        raise _ChildFailure("CONFIGURATION_INVALID")
    return value


def _bounded_int(value: object, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise _ChildFailure("CONFIGURATION_INVALID")
    return value


def _bounded_float(value: object, low: float, high: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or not low <= float(value) <= high
    ):
        raise _ChildFailure("CONFIGURATION_INVALID")
    return float(value)


def _parse_init(message: dict[str, object]) -> dict[str, object]:
    allowed = {
        "version", "staging", "final", "lifecycle_lock", "max_bytes",
        "page_bytes", "chunk_bytes", "absolute_deadline_monotonic",
        "no_progress_s",
    }
    if set(message) != allowed or message.get("version") != 1:
        raise _ChildFailure("UPLOAD_IN_PROGRESS")
    staging = _absolute_path(message.get("staging"))
    final = _absolute_path(message.get("final"))
    lifecycle_lock = _absolute_path(message.get("lifecycle_lock"))
    if staging == final:
        raise _ChildFailure("CONFIGURATION_INVALID")
    max_bytes = _bounded_int(message.get("max_bytes"), 1, _MAX_FILE_BYTES)
    page_bytes = _bounded_int(message.get("page_bytes"), 0, _MAX_FILE_BYTES)
    chunk_bytes = _bounded_int(
        message.get("chunk_bytes"), 1, _MAX_CHUNK_BYTES,
    )
    deadline = _bounded_float(
        message.get("absolute_deadline_monotonic"), 1.0, math.inf,
    )
    no_progress_s = _bounded_float(
        message.get("no_progress_s"), 1e-6, _MAX_WAIT_SECONDS,
    )
    if time.monotonic() >= deadline:
        raise _ChildFailure("UPLOAD_EXPIRED")
    return {
        "staging": staging,
        "final": final,
        "lifecycle_lock": lifecycle_lock,
        "max_bytes": max_bytes,
        "page_bytes": page_bytes,
        "chunk_bytes": chunk_bytes,
        "absolute_deadline_monotonic": deadline,
        "no_progress_s": no_progress_s,
    }


def _run(sock: socket.socket, slot_fd: int) -> int:
    try:
        os.fstat(slot_fd)
    except OSError:
        return 2

    writer: BoundedWriter | None = None
    lifecycle: int | None = None
    finished = False
    try:
        kind, payload = _read_frame(
            sock, _MAX_CONTROL_BYTES, time.monotonic() + _STARTUP_WAIT_S,
        )
        if kind != FRAME_INIT:
            raise _ChildFailure("UPLOAD_IN_PROGRESS")
        config = _parse_init(_decode_control(payload))

        lifecycle = open_lifecycle_shared(str(config["lifecycle_lock"]))
        writer = BoundedWriter(
            staging=str(config["staging"]),
            final=str(config["final"]),
            max_bytes=int(config["max_bytes"]),
            page_bytes=int(config["page_bytes"]),
        )
        writer.__enter__()
        _safe_control(sock, FRAME_READY, {"type": "ready"})

        last_progress = time.monotonic()
        expected = 0
        received = 0
        chunk_bytes = int(config["chunk_bytes"])
        absolute_deadline = float(config["absolute_deadline_monotonic"])
        no_progress_s = float(config["no_progress_s"])
        max_payload = max(_MAX_CONTROL_BYTES, chunk_bytes + 4)

        while True:
            deadline = min(absolute_deadline, last_progress + no_progress_s)
            kind, payload = _read_frame(sock, max_payload, deadline)
            if kind == FRAME_CHUNK:
                if len(payload) < 4:
                    raise _ChildFailure("UPLOAD_CONTENT_CONFLICT")
                sequence = struct.unpack("!I", payload[:4])[0]
                data = payload[4:]
                if sequence != expected:
                    raise _ChildFailure("UPLOAD_IN_PROGRESS")
                if len(data) > chunk_bytes:
                    raise _ChildFailure("FILE_LIMIT_EXCEEDED")
                writer.feed(data)
                received += len(data)
                expected += 1
                last_progress = time.monotonic()
                _send_frame(
                    sock, _ack_frame(sequence, received),
                    time.monotonic() + 5.0,
                )
                continue
            if kind == FRAME_FINISH:
                size, digest = writer.finish()
                finished = True
                _safe_control(sock, FRAME_RESULT, {
                    "type": "result", "bytes": size, "sha256": digest,
                })
                return 0
            if kind == FRAME_ABORT:
                writer.abort()
                finished = True
                _safe_control(sock, FRAME_ABORTED, {"type": "aborted"})
                return 0
            raise _ChildFailure("UPLOAD_IN_PROGRESS")
    except _ChildTimeout:
        _safe_error(sock, "UPLOAD_EXPIRED")
        return 1
    except _ChildEof:
        return 1
    except _Terminated:
        return 1
    except StoreUnavailable as exc:
        _safe_error(sock, _finite_code(exc.code))
        return 1
    except _ChildFailure as exc:
        _safe_error(sock, exc.code)
        return 1
    except (OSError, ValueError, struct.error, json.JSONDecodeError):
        _safe_error(sock, "STORAGE_PRESSURE")
        return 1
    finally:
        if writer is not None and not finished:
            writer.abort()
        if lifecycle is not None:
            close_lifecycle(lifecycle)


def _parse_arguments(arguments: list[str]) -> tuple[int, int] | None:
    values: dict[str, int] = {}
    index = 0
    while index < len(arguments):
        if index + 1 >= len(arguments):
            return None
        name = arguments[index]
        raw = arguments[index + 1]
        if name not in {"--ipc-fd", "--slot-fd"} or name in values:
            return None
        if not raw.isascii() or not raw.isdecimal():
            return None
        try:
            number = int(raw)
        except ValueError:
            return None
        if not 3 <= number <= 2**31 - 1:
            return None
        values[name] = number
        index += 2
    if set(values) != {"--ipc-fd", "--slot-fd"}:
        return None
    if values["--ipc-fd"] == values["--slot-fd"]:
        return None
    return values["--ipc-fd"], values["--slot-fd"]


def _terminate(signum: int, frame: object) -> NoReturn:
    raise _Terminated()


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    parsed = _parse_arguments(arguments)
    if parsed is None:
        return 2
    ipc_fd, slot_fd = parsed
    try:
        sock = socket.socket(fileno=ipc_fd)
    except OSError:
        return 2
    signal.signal(signal.SIGTERM, _terminate)
    signal.signal(signal.SIGINT, _terminate)
    try:
        return _run(sock, slot_fd)
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
