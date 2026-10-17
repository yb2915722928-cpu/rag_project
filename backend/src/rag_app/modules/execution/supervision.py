"""Bounded child supervision values and private IPC framing.

This module is deliberately framework-free and has no database, provider or
credential imports.  A grant may contain a resolved egress plan and request;
those attributes are hidden from repr and are never included in error text.
"""

from __future__ import annotations

import base64
import binascii
import json
import math
import socket
import struct
import time
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import BinaryIO, Protocol, runtime_checkable

from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressError,
    EgressPlan,
    EgressProfile,
    EgressPurpose,
    EgressRequest,
    EgressTarget,
    HostPort,
    ResolvedAddress,
)


MAX_STAGE_PAYLOAD_BYTES = 16 * 1_048_576
MAX_WIRE_FRAME_BYTES = MAX_STAGE_PAYLOAD_BYTES * 2 + 65_536
MAX_WIRE_IDENTIFIER = 128
_FRAME_HEADER = struct.Struct("!I")


class ChildStage(StrEnum):
    MODEL = "model"
    PARSE = "parse"
    EMBEDDING = "embedding"
    VISION = "vision"
    EGRESS = "egress"


class SendState(StrEnum):
    NOT_SENT = "not_sent"
    MAY_HAVE_SENT = "may_have_sent"
    RESPONSE_RECEIVED = "response_received"


class StopReason(StrEnum):
    COMPLETED = "completed"
    DEADLINE = "deadline"
    IPC_LOST = "ipc_lost"
    CONTROLLER_STOP = "controller_stop"
    CHILD_ERROR = "child_error"


class ChildFailure(StrEnum):
    INVALID_ARGUMENT = "invalid_argument"
    INVALID_STATE = "invalid_state"
    IPC_IO = "ipc_io"
    IPC_PROTOCOL = "ipc_protocol"
    TIMEOUT = "timeout"
    CHILD_EXITED = "child_exited"
    RESULT_TOO_LARGE = "result_too_large"
    STAGE_FAILED = "stage_failed"
    GRANT_REUSED = "grant_reused"
    IDENTITY_MISMATCH = "identity_mismatch"
    DESCENDANTS_FOUND = "descendants_found"
    STOP_UNPROVEN = "stop_unproven"


def _failure(value: ChildFailure) -> ChildSupervisionError:
    return ChildSupervisionError(value)


def _positive_int(value: object, *, maximum: int) -> int:
    if type(value) is not int or value < 1 or value > maximum:
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return value


def _non_negative_int(value: object, *, maximum: int) -> int:
    if type(value) is not int or value < 0 or value > maximum:
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return value


def _finite_float(value: object, *, maximum: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) <= 0
        or float(value) > maximum
    ):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return float(value)


def _grace_float(value: object, *, maximum: float) -> float:
    if value is None or isinstance(value, bool):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    if float(value) < 0 or float(value) > maximum:
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return float(value)


def _identifier(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_WIRE_IDENTIFIER
        or not value.isascii()
        or any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)
    ):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return value


@dataclass(frozen=True, slots=True)
class ChildLimits:
    max_frame_bytes: int = 1_048_576
    max_result_bytes: int = 1_048_576
    max_stdout_bytes: int = 65_536
    max_stderr_bytes: int = 65_536
    startup_s: float = 5.0
    term_grace_s: float = 5.0
    kill_grace_s: float = 10.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "max_frame_bytes",
            _positive_int(self.max_frame_bytes, maximum=MAX_STAGE_PAYLOAD_BYTES),
        )
        object.__setattr__(
            self, "max_result_bytes",
            _positive_int(self.max_result_bytes, maximum=MAX_STAGE_PAYLOAD_BYTES),
        )
        object.__setattr__(
            self, "max_stdout_bytes",
            _non_negative_int(self.max_stdout_bytes, maximum=MAX_STAGE_PAYLOAD_BYTES),
        )
        object.__setattr__(
            self, "max_stderr_bytes",
            _non_negative_int(self.max_stderr_bytes, maximum=MAX_STAGE_PAYLOAD_BYTES),
        )
        object.__setattr__(self, "startup_s", _finite_float(self.startup_s, maximum=300.0))
        object.__setattr__(
            self, "term_grace_s",
            _grace_float(self.term_grace_s, maximum=60.0),
        )
        object.__setattr__(
            self, "kill_grace_s",
            _grace_float(self.kill_grace_s, maximum=300.0),
        )


@dataclass(frozen=True, slots=True)
class ChildSlot:
    deployment_id: str
    boot_id: str
    slot_id: str
    attempt: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "deployment_id", _identifier(self.deployment_id))
        object.__setattr__(self, "boot_id", _identifier(self.boot_id))
        object.__setattr__(self, "slot_id", _identifier(self.slot_id))
        object.__setattr__(self, "attempt", _positive_int(self.attempt, maximum=2**31 - 1))


@dataclass(frozen=True, slots=True)
class ChildIdentity:
    slot: ChildSlot
    child_instance: str
    pid: int
    process_group: int
    start_ticks: int

    def __post_init__(self) -> None:
        if not isinstance(self.slot, ChildSlot):
            raise _failure(ChildFailure.INVALID_ARGUMENT)
        object.__setattr__(self, "child_instance", _identifier(self.child_instance))
        object.__setattr__(self, "pid", _positive_int(self.pid, maximum=2**31 - 1))
        object.__setattr__(
            self, "process_group",
            _positive_int(self.process_group, maximum=2**31 - 1),
        )
        object.__setattr__(
            self, "start_ticks",
            _non_negative_int(self.start_ticks, maximum=2**63 - 1),
        )


@dataclass(frozen=True, slots=True)
class StageCommand:
    call_id: str
    attempt: int
    stage: ChildStage
    payload: bytes = field(repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "call_id", _identifier(self.call_id))
        object.__setattr__(self, "attempt", _non_negative_int(self.attempt, maximum=2**31 - 1))
        try:
            stage = ChildStage(self.stage)
        except (TypeError, ValueError):
            raise _failure(ChildFailure.INVALID_ARGUMENT) from None
        object.__setattr__(self, "stage", stage)
        if not isinstance(self.payload, bytes) or len(self.payload) > MAX_STAGE_PAYLOAD_BYTES:
            raise _failure(ChildFailure.INVALID_ARGUMENT)


@dataclass(frozen=True, slots=True)
class SendGrant:
    grant_id: str = field(repr=False)
    call_id: str
    attempt: int
    boot_id: str
    child_instance: str
    send_stop_by_monotonic: float
    plan: EgressPlan | None = field(default=None, repr=False)
    request: EgressRequest | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "grant_id", _identifier(self.grant_id))
        object.__setattr__(self, "call_id", _identifier(self.call_id))
        object.__setattr__(self, "attempt", _non_negative_int(self.attempt, maximum=2**31 - 1))
        object.__setattr__(self, "boot_id", _identifier(self.boot_id))
        object.__setattr__(self, "child_instance", _identifier(self.child_instance))
        object.__setattr__(
            self, "send_stop_by_monotonic",
            _finite_float(self.send_stop_by_monotonic, maximum=math.inf),
        )
        if (self.plan is None) != (self.request is None):
            raise _failure(ChildFailure.INVALID_ARGUMENT)
        if self.plan is not None and not isinstance(self.plan, EgressPlan):
            raise _failure(ChildFailure.INVALID_ARGUMENT)
        if self.request is not None and not isinstance(self.request, EgressRequest):
            raise _failure(ChildFailure.INVALID_ARGUMENT)


@dataclass(frozen=True, slots=True)
class ChildResult:
    call_id: str
    grant_id: str | None = field(repr=False)
    send_state: SendState
    response_status: int | None
    payload: bytes = field(repr=False)
    failure: ChildFailure | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "call_id", _identifier(self.call_id))
        if self.grant_id is not None:
            object.__setattr__(self, "grant_id", _identifier(self.grant_id))
        try:
            send_state = SendState(self.send_state)
        except (TypeError, ValueError):
            raise _failure(ChildFailure.INVALID_ARGUMENT) from None
        object.__setattr__(self, "send_state", send_state)
        if self.response_status is not None and (
            type(self.response_status) is not int
            or not 100 <= self.response_status <= 599
        ):
            raise _failure(ChildFailure.INVALID_ARGUMENT)
        if not isinstance(self.payload, bytes):
            raise _failure(ChildFailure.INVALID_ARGUMENT)
        if self.failure is not None:
            try:
                object.__setattr__(self, "failure", ChildFailure(self.failure))
            except (TypeError, ValueError):
                raise _failure(ChildFailure.INVALID_ARGUMENT) from None
        if send_state is SendState.NOT_SENT:
            if self.grant_id is not None or self.response_status is not None:
                raise _failure(ChildFailure.INVALID_ARGUMENT)
        elif send_state is SendState.MAY_HAVE_SENT:
            if self.grant_id is None or self.response_status is not None:
                raise _failure(ChildFailure.INVALID_ARGUMENT)
        elif send_state is SendState.RESPONSE_RECEIVED:
            if self.grant_id is None or self.response_status is None:
                raise _failure(ChildFailure.INVALID_ARGUMENT)


@dataclass(frozen=True, slots=True)
class StopProof:
    identity: ChildIdentity
    exited: bool
    exit_code: int | None
    process_group_empty: bool
    no_descendants: bool
    ipc_closed: bool
    send_fds_closed: bool
    grant_destroyed: bool
    proven_monotonic: float
    failure: ChildFailure | None = None

    @property
    def proven(self) -> bool:
        return (
            self.failure is None
            and self.exited
            and self.process_group_empty
            and self.no_descendants
            and self.ipc_closed
            and self.send_fds_closed
            and self.grant_destroyed
        )


class ChildSupervisionError(Exception):
    """A finite supervision failure with no payload, URL or secret."""

    __slots__ = ("failure",)

    def __init__(self, failure: ChildFailure) -> None:
        if not isinstance(failure, ChildFailure):
            failure = ChildFailure.INVALID_ARGUMENT
        self.failure = failure
        super().__init__(f"child supervision failed: {failure.value}")


@runtime_checkable
class ChildSupervisor(Protocol):
    def spawn(self, slot: ChildSlot, limits: ChildLimits) -> ChildIdentity:
        ...

    def prepare(
        self, identity: ChildIdentity, command: StageCommand, *, timeout_s: float = 5.0,
    ) -> None:
        ...

    def grant(self, identity: ChildIdentity, grant: SendGrant) -> None:
        ...

    def receive(
        self, identity: ChildIdentity, *, timeout_s: float = 30.0,
    ) -> ChildResult:
        ...

    def stop(self, identity: ChildIdentity, reason: StopReason) -> StopProof:
        ...

    def inspect(self, identity: ChildIdentity) -> StopProof:
        ...


def _json_bytes(message: object) -> bytes:
    try:
        text = json.dumps(
            message, ensure_ascii=True, separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError):
        raise _failure(ChildFailure.IPC_PROTOCOL) from None
    return text.encode("utf-8")


def encode_frame(message: object, max_frame_bytes: int) -> bytes:
    if type(max_frame_bytes) is not int or not 1 <= max_frame_bytes <= MAX_WIRE_FRAME_BYTES:
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    payload = _json_bytes(message)
    if len(payload) > max_frame_bytes:
        raise _failure(ChildFailure.RESULT_TOO_LARGE)
    return _FRAME_HEADER.pack(len(payload)) + payload


def decode_frame(data: bytes, max_frame_bytes: int) -> dict[str, object]:
    if not isinstance(data, bytes) or type(max_frame_bytes) is not int:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    if len(data) < _FRAME_HEADER.size:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    length = _FRAME_HEADER.unpack(data[: _FRAME_HEADER.size])[0]
    if length > max_frame_bytes:
        raise _failure(ChildFailure.RESULT_TOO_LARGE)
    if len(data) != _FRAME_HEADER.size + length:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    try:
        message = json.loads(data[_FRAME_HEADER.size:].decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise _failure(ChildFailure.IPC_PROTOCOL) from None
    if not isinstance(message, dict):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return message


def _remaining(deadline_monotonic: float) -> float:
    remaining = float(deadline_monotonic) - time.monotonic()
    if not math.isfinite(remaining) or remaining <= 0:
        raise _failure(ChildFailure.TIMEOUT)
    return remaining


def _recv_exact(
    sock: socket.socket,
    size: int,
    *,
    deadline_monotonic: float,
    empty_failure: ChildFailure,
) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        # A socket timeout is relative.  Recompute the absolute deadline before
        # every receive so a stream of small chunks cannot extend the phase.
        remaining = _remaining(deadline_monotonic)
        try:
            sock.settimeout(remaining)
        except OSError:
            raise _failure(ChildFailure.IPC_IO) from None
        try:
            chunk = sock.recv(size - len(chunks))
        except InterruptedError:
            continue
        except TimeoutError:
            raise _failure(ChildFailure.TIMEOUT) from None
        except OSError:
            raise _failure(ChildFailure.IPC_IO) from None
        if not chunk:
            if not chunks:
                raise _failure(empty_failure)
            raise _failure(ChildFailure.IPC_IO)
        chunks.extend(chunk)
    return bytes(chunks)


def read_frame(
    sock: socket.socket,
    max_frame_bytes: int,
    *,
    deadline_monotonic: float,
    too_large_failure: ChildFailure = ChildFailure.RESULT_TOO_LARGE,
    empty_failure: ChildFailure = ChildFailure.CHILD_EXITED,
) -> dict[str, object]:
    if not isinstance(sock, socket.socket):
        raise _failure(ChildFailure.IPC_IO)
    try:
        header = _recv_exact(
            sock,
            _FRAME_HEADER.size,
            deadline_monotonic=deadline_monotonic,
            empty_failure=empty_failure,
        )
        length = _FRAME_HEADER.unpack(header)[0]
        if length > max_frame_bytes:
            raise _failure(too_large_failure)
        payload = _recv_exact(
            sock,
            length,
            deadline_monotonic=deadline_monotonic,
            empty_failure=ChildFailure.IPC_IO,
        )
    finally:
        try:
            sock.settimeout(None)
        except OSError:
            pass
    try:
        message = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise _failure(ChildFailure.IPC_PROTOCOL) from None
    if not isinstance(message, dict):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return message


def write_frame(
    sock: socket.socket,
    message: object,
    max_frame_bytes: int,
    *,
    deadline_monotonic: float,
) -> None:
    if not isinstance(sock, socket.socket):
        raise _failure(ChildFailure.IPC_IO)
    frame = encode_frame(message, max_frame_bytes)
    view = memoryview(frame)
    try:
        while view:
            # sendall keeps one relative timeout across its internal sends;
            # send in bounded steps so the absolute deadline is authoritative.
            sock.settimeout(_remaining(deadline_monotonic))
            try:
                written = sock.send(view)
            except InterruptedError:
                continue
            except TimeoutError:
                raise _failure(ChildFailure.TIMEOUT) from None
            except OSError:
                raise _failure(ChildFailure.IPC_IO) from None
            if written <= 0:
                raise _failure(ChildFailure.IPC_IO)
            view = view[written:]
    finally:
        try:
            sock.settimeout(None)
        except OSError:
            pass


def close_ipc(sock: socket.socket) -> None:
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: object, *, maximum: int) -> bytes:
    if not isinstance(value, str) or len(value) > (maximum * 4 // 3) + 4:
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError):
        raise _failure(ChildFailure.INVALID_ARGUMENT) from None
    if len(decoded) > maximum:
        raise _failure(ChildFailure.RESULT_TOO_LARGE)
    return decoded


def _as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return value


def _as_list(value: object, *, maximum: int = 256) -> list[object]:
    if not isinstance(value, list) or len(value) > maximum:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return value


def _as_str(value: object) -> str:
    if not isinstance(value, str):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return value


def _as_int(value: object) -> int:
    if type(value) is not int:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return value


def _as_float(value: object) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return float(value)


def _pair(value: object) -> tuple[object, object]:
    if not isinstance(value, list) or len(value) != 2:
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return value[0], value[1]


def command_to_wire(command: StageCommand) -> dict[str, object]:
    if not isinstance(command, StageCommand):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return {
        "type": "command",
        "call_id": command.call_id,
        "attempt": command.attempt,
        "stage": command.stage.value,
        "payload": _b64encode(command.payload),
    }


def command_from_wire(message: object) -> StageCommand:
    data = _as_dict(message)
    if data.get("type") != "command":
        raise _failure(ChildFailure.IPC_PROTOCOL)
    try:
        stage = ChildStage(_as_str(data.get("stage")))
    except ValueError:
        raise _failure(ChildFailure.IPC_PROTOCOL) from None
    return StageCommand(
        call_id=_as_str(data.get("call_id")),
        attempt=_as_int(data.get("attempt")),
        stage=stage,
        payload=_b64decode(
            data.get("payload"), maximum=MAX_STAGE_PAYLOAD_BYTES,
        ),
    )


def _host_port_to_wire(value: HostPort) -> list[object]:
    return [value.host, value.port]


def _host_port_from_wire(value: object) -> HostPort:
    host, port = _pair(value)
    return HostPort(_as_str(host), _as_int(port))


def _plan_to_wire(plan: EgressPlan) -> dict[str, object]:
    if not isinstance(plan, EgressPlan):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return {
        "purpose": plan.target.profile.purpose.value,
        "allowed_targets": [
            _host_port_to_wire(target)
            for target in sorted(
                plan.target.profile.allowed_targets,
                key=lambda item: (item.host, item.port),
            )
        ],
        "host": plan.target.host,
        "port": plan.target.port,
        "request_target": plan.target.request_target,
        "addresses": [
            [address.family.value, address.address] for address in plan.addresses
        ],
        "connect_address": [
            plan.connect_address.family.value, plan.connect_address.address,
        ],
    }


def _plan_from_wire(value: object) -> EgressPlan:
    try:
        data = _as_dict(value)
        try:
            purpose = EgressPurpose(_as_str(data.get("purpose")))
        except ValueError:
            raise _failure(ChildFailure.IPC_PROTOCOL) from None
        allowed = frozenset(
            _host_port_from_wire(item)
            for item in _as_list(data.get("allowed_targets"))
        )
        profile = EgressProfile(purpose, allowed)
        target = EgressTarget(
            profile,
            _as_str(data.get("host")),
            _as_int(data.get("port")),
            _as_str(data.get("request_target")),
        )
        addresses = tuple(
            ResolvedAddress(
                AddressFamily(_as_str(family)),
                _as_str(address),
            )
            for family, address in (
                _pair(item) for item in _as_list(data.get("addresses"))
            )
        )
        connect_family, connect_address = _pair(data.get("connect_address"))
        return EgressPlan(
            target=target,
            addresses=addresses,
            connect_address=ResolvedAddress(
                AddressFamily(_as_str(connect_family)),
                _as_str(connect_address),
            ),
        )
    except (EgressError, TypeError, ValueError):
        raise _failure(ChildFailure.IPC_PROTOCOL) from None


def _request_to_wire(request: EgressRequest) -> dict[str, object]:
    if not isinstance(request, EgressRequest):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return {
        "method": request.method,
        "headers": [[name, value] for name, value in request.headers],
        "body": _b64encode(request.body),
        "api_authorization": request.api_authorization,
    }


def _request_from_wire(value: object) -> EgressRequest:
    try:
        data = _as_dict(value)
        headers = tuple(
            (_as_str(name), _as_str(header_value))
            for name, header_value in (
                _pair(item) for item in _as_list(data.get("headers"), maximum=100)
            )
        )
        authorization = data.get("api_authorization")
        if authorization is not None:
            authorization = _as_str(authorization)
        return EgressRequest(
            method=_as_str(data.get("method")),
            headers=headers,
            body=_b64decode(data.get("body"), maximum=MAX_STAGE_PAYLOAD_BYTES),
            api_authorization=authorization,
        )
    except (EgressError, TypeError, ValueError):
        raise _failure(ChildFailure.IPC_PROTOCOL) from None


def grant_to_wire(grant: SendGrant) -> dict[str, object]:
    if not isinstance(grant, SendGrant):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return {
        "type": "grant",
        "grant_id": grant.grant_id,
        "call_id": grant.call_id,
        "attempt": grant.attempt,
        "boot_id": grant.boot_id,
        "child_instance": grant.child_instance,
        "send_stop_by_monotonic": grant.send_stop_by_monotonic,
        "plan": _plan_to_wire(grant.plan) if grant.plan is not None else None,
        "request": _request_to_wire(grant.request) if grant.request is not None else None,
    }


def grant_from_wire(message: object) -> SendGrant:
    data = _as_dict(message)
    if data.get("type") != "grant":
        raise _failure(ChildFailure.IPC_PROTOCOL)
    plan_data = data.get("plan")
    request_data = data.get("request")
    if (plan_data is None) != (request_data is None):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    return SendGrant(
        grant_id=_as_str(data.get("grant_id")),
        call_id=_as_str(data.get("call_id")),
        attempt=_as_int(data.get("attempt")),
        boot_id=_as_str(data.get("boot_id")),
        child_instance=_as_str(data.get("child_instance")),
        send_stop_by_monotonic=_as_float(data.get("send_stop_by_monotonic")),
        plan=_plan_from_wire(plan_data) if plan_data is not None else None,
        request=_request_from_wire(request_data) if request_data is not None else None,
    )


def result_to_wire(result: ChildResult) -> dict[str, object]:
    if not isinstance(result, ChildResult):
        raise _failure(ChildFailure.INVALID_ARGUMENT)
    return {
        "type": "result",
        "call_id": result.call_id,
        "grant_id": result.grant_id,
        "send_state": result.send_state.value,
        "response_status": result.response_status,
        "payload": _b64encode(result.payload),
        "failure": result.failure.value if result.failure is not None else None,
    }


def result_from_wire(message: object) -> ChildResult:
    data = _as_dict(message)
    if data.get("type") != "result":
        raise _failure(ChildFailure.IPC_PROTOCOL)
    try:
        send_state = SendState(_as_str(data.get("send_state")))
    except ValueError:
        raise _failure(ChildFailure.IPC_PROTOCOL) from None
    failure = data.get("failure")
    if failure is not None:
        try:
            failure = ChildFailure(_as_str(failure))
        except ValueError:
            raise _failure(ChildFailure.IPC_PROTOCOL) from None
    grant_id = data.get("grant_id")
    if grant_id is not None:
        grant_id = _as_str(grant_id)
    status = data.get("response_status")
    if status is not None:
        status = _as_int(status)
    return ChildResult(
        call_id=_as_str(data.get("call_id")),
        grant_id=grant_id,
        send_state=send_state,
        response_status=status,
        payload=_b64decode(data.get("payload"), maximum=MAX_STAGE_PAYLOAD_BYTES),
        failure=failure,
    )


def normalize_child_result(
    result: ChildResult,
    *,
    grant_written: bool,
    grant: SendGrant | None,
) -> ChildResult:
    """Never let a child self-report downgrade a sent grant to not_sent."""
    if not isinstance(result, ChildResult):
        raise _failure(ChildFailure.IPC_PROTOCOL)
    if not grant_written:
        if result.send_state is not SendState.NOT_SENT:
            raise _failure(ChildFailure.INVALID_STATE)
        return result
    if grant is None:
        raise _failure(ChildFailure.INVALID_STATE)
    grant_id = grant.grant_id
    if result.call_id != grant.call_id:
        return replace(
            result, call_id=grant.call_id, grant_id=grant_id,
            send_state=SendState.MAY_HAVE_SENT, response_status=None,
            payload=b"",
            failure=ChildFailure.IDENTITY_MISMATCH,
        )
    if result.send_state is SendState.NOT_SENT:
        return replace(
            result, grant_id=grant_id, send_state=SendState.MAY_HAVE_SENT,
            response_status=None, payload=b"",
        )
    if result.send_state is SendState.MAY_HAVE_SENT:
        if result.grant_id is not None and result.grant_id != grant_id:
            return replace(
                result, grant_id=grant_id, response_status=None,
                payload=b"",
                failure=ChildFailure.IDENTITY_MISMATCH,
            )
        return replace(
            result, grant_id=grant_id, response_status=None, payload=b"",
        )
    if (
        result.grant_id != grant_id
        or result.response_status is None
    ):
        return replace(
            result, grant_id=grant_id, send_state=SendState.MAY_HAVE_SENT,
            response_status=None, payload=b"",
            failure=ChildFailure.IDENTITY_MISMATCH,
        )
    return result


@dataclass(frozen=True, slots=True)
class BoundedOutput:
    """Only counters are retained; child output bytes are never stored or logged."""

    stdout_bytes: int = 0
    stderr_bytes: int = 0
    stdout_overflow: bool = False
    stderr_overflow: bool = False

    @property
    def bounded(self) -> bool:
        return not self.stdout_overflow and not self.stderr_overflow


def drain_bounded(
    stream: BinaryIO,
    *,
    maximum: int,
    counter: list[int],
    overflow: list[bool],
) -> None:
    """Drain a process stream while retaining no bytes beyond a counter."""
    try:
        while True:
            try:
                chunk = stream.read(65_536)
            except (OSError, ValueError):
                return
            if not chunk:
                return
            counter[0] += len(chunk)
            if counter[0] > maximum:
                overflow[0] = True
                # Stop retaining/reading beyond the bound.  The producer will
                # block on a full pipe and the supervisor will terminate it.
                return
    except BaseException:
        return
