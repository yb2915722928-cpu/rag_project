"""Private child entrypoint for one bounded stage and at most one send grant.

The child receives a single already-prepared socket fd.  It has no database
connection, no master key, no provider SDK, and no authority to start another
stage.  Every capability in this Story is an explicit local fake; in
particular the egress stage consumes the controller-resolved plan and never
performs DNS or opens a network connection.
"""

from __future__ import annotations

import hashlib
import json
import socket
import sys
import time
from typing import NoReturn

from rag_app.modules.execution.supervision import (
    ChildFailure,
    ChildResult,
    ChildStage,
    ChildSupervisionError,
    MAX_WIRE_FRAME_BYTES,
    SendGrant,
    SendState,
    StageCommand,
    close_ipc,
    command_from_wire,
    grant_from_wire,
    read_frame,
    result_to_wire,
    write_frame,
)


_CHILD_FRAME_LIMIT = MAX_WIRE_FRAME_BYTES
_COMMAND_WAIT_S = 300.0
_GRANT_WAIT_S = 300.0
_FAKE_INPUT_MAX_BYTES = 8 * 1_048_576
_FAKE_RESULT_MAX_BYTES = 1_048_576


def _fail() -> NoReturn:
    raise SystemExit(2)


def _json_payload(value: object) -> bytes:
    encoded = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(encoded) > _FAKE_RESULT_MAX_BYTES:
        raise ChildSupervisionError(ChildFailure.RESULT_TOO_LARGE)
    return encoded


def _fake_stage_result(command: StageCommand) -> bytes:
    if len(command.payload) > _FAKE_INPUT_MAX_BYTES:
        raise ChildSupervisionError(ChildFailure.RESULT_TOO_LARGE)
    digest = hashlib.sha256(command.payload).hexdigest()
    return _json_payload({
        "fake": command.stage.value,
        "input_bytes": len(command.payload),
        "sha256": digest,
    })


def _fake_egress_result(grant: SendGrant) -> bytes:
    """Consume the approved plan locally; do not resolve or connect anywhere."""
    if grant.plan is None or grant.request is None:
        raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
    if time.monotonic() >= grant.send_stop_by_monotonic:
        raise ChildSupervisionError(ChildFailure.TIMEOUT)
    body = grant.request.body
    if len(body) > _FAKE_INPUT_MAX_BYTES:
        raise ChildSupervisionError(ChildFailure.RESULT_TOO_LARGE)
    return _json_payload({
        "fake": "egress",
        "method": grant.request.method,
        "request_bytes": len(body),
        "request_sha256": hashlib.sha256(body).hexdigest(),
        "addresses": len(grant.plan.addresses),
        "connect_address": grant.plan.connect_address.address,
        "host": grant.plan.target.host,
        "status": 200,
    })


def _send_result(sock: socket.socket, result: ChildResult) -> None:
    try:
        write_frame(
            sock, result_to_wire(result), _CHILD_FRAME_LIMIT,
            deadline_monotonic=time.monotonic() + 5.0,
        )
    except ChildSupervisionError:
        return


def _receive_grant(sock: socket.socket) -> SendGrant:
    message = read_frame(
        sock, _CHILD_FRAME_LIMIT,
        deadline_monotonic=time.monotonic() + _GRANT_WAIT_S,
        too_large_failure=ChildFailure.RESULT_TOO_LARGE,
        empty_failure=ChildFailure.CHILD_EXITED,
    )
    return grant_from_wire(message)


def _run(sock: socket.socket) -> int:
    write_frame(
        sock, {"type": "ready"}, _CHILD_FRAME_LIMIT,
        deadline_monotonic=time.monotonic() + 5.0,
    )
    message = read_frame(
        sock, _CHILD_FRAME_LIMIT,
        deadline_monotonic=time.monotonic() + _COMMAND_WAIT_S,
        too_large_failure=ChildFailure.RESULT_TOO_LARGE,
        empty_failure=ChildFailure.CHILD_EXITED,
    )
    command = command_from_wire(message)
    write_frame(
        sock,
        {
            "type": "prepared",
            "call_id": command.call_id,
            "attempt": command.attempt,
            "stage": command.stage.value,
        },
        _CHILD_FRAME_LIMIT,
        deadline_monotonic=time.monotonic() + 5.0,
    )

    if command.stage is ChildStage.EGRESS:
        try:
            grant = _receive_grant(sock)
        except ChildSupervisionError as exc:
            _send_result(sock, ChildResult(
                call_id=command.call_id,
                grant_id=None,
                send_state=SendState.NOT_SENT,
                response_status=None,
                payload=b"",
                failure=exc.failure,
            ))
            return 1
        if (
            grant.call_id != command.call_id
            or grant.attempt != command.attempt
        ):
            _send_result(sock, ChildResult(
                call_id=command.call_id,
                grant_id=None,
                send_state=SendState.NOT_SENT,
                response_status=None,
                payload=b"",
                failure=ChildFailure.IDENTITY_MISMATCH,
            ))
            return 1
        try:
            body = _fake_egress_result(grant)
        except ChildSupervisionError as exc:
            _send_result(sock, ChildResult(
                call_id=command.call_id,
                grant_id=grant.grant_id,
                send_state=SendState.MAY_HAVE_SENT,
                response_status=None,
                payload=b"",
                failure=exc.failure,
            ))
            return 1
        _send_result(sock, ChildResult(
            call_id=command.call_id,
            grant_id=grant.grant_id,
            send_state=SendState.RESPONSE_RECEIVED,
            response_status=200,
            payload=body,
        ))
        return 0

    try:
        body = _fake_stage_result(command)
    except ChildSupervisionError as exc:
        _send_result(sock, ChildResult(
            call_id=command.call_id,
            grant_id=None,
            send_state=SendState.NOT_SENT,
            response_status=None,
            payload=b"",
            failure=exc.failure,
        ))
        return 1
    _send_result(sock, ChildResult(
        call_id=command.call_id,
        grant_id=None,
        send_state=SendState.NOT_SENT,
        response_status=None,
        payload=body,
    ))
    return 0


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if (
        len(arguments) != 2
        or arguments[0] != "--ipc-fd"
        or not arguments[1].isascii()
        or not arguments[1].isdecimal()
    ):
        return 2
    try:
        fd = int(arguments[1])
    except ValueError:
        return 2
    if not 0 <= fd <= 2**31 - 1:
        return 2
    try:
        sock = socket.socket(fileno=fd)
    except OSError:
        return 2
    status = 1
    try:
        status = _run(sock)
    except BaseException:
        # No traceback or payload is written; the parent keeps its conservative
        # send state if it had already granted this call.
        status = 1
    finally:
        close_ipc(sock)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
