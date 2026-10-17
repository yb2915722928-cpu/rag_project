"""Linux child supervision: bounded IPC, one grant, and stop proofs."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
from dataclasses import replace
import uuid

import pytest

from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressPlan,
    EgressProfile,
    EgressPurpose,
    EgressRequest,
    EgressTarget,
    HostPort,
    ResolvedAddress,
)
from rag_app.modules.execution.supervision import (
    ChildFailure,
    ChildIdentity,
    ChildLimits,
    ChildResult,
    ChildSlot,
    ChildStage,
    ChildSupervisionError,
    SendGrant,
    SendState,
    StageCommand,
    StopProof,
    StopReason,
    decode_frame,
    encode_frame,
    grant_from_wire,
    grant_to_wire,
    result_from_wire,
    result_to_wire,
)


pytestmark = pytest.mark.skipif(
    sys.platform != "linux",
    reason="Child supervision is a Linux process-group acceptance path.",
)


SECRET = "SECRET" + "_" + "7f3c9a1d2e4b6c8d"
SECRET_URL_TARGET = "/signed/" + SECRET + "?signature=" + SECRET


def slot() -> ChildSlot:
    nonce = uuid.uuid4().hex
    return ChildSlot(
        deployment_id="test_dep",
        boot_id="boot_" + nonce,
        slot_id="slot_" + nonce,
        attempt=1,
    )


@pytest.fixture
def state_root(tmp_path):
    root = tmp_path / "state"
    root.mkdir()
    return root


def limits(**overrides) -> ChildLimits:
    values = {
        "max_frame_bytes": 1_048_576,
        "max_result_bytes": 1_048_576,
        "max_stdout_bytes": 65_536,
        "max_stderr_bytes": 65_536,
        "startup_s": 5.0,
        "term_grace_s": 0.5,
        "kill_grace_s": 1.0,
    }
    values.update(overrides)
    return ChildLimits(**values)


def plan() -> EgressPlan:
    profile = EgressProfile(
        EgressPurpose.API, frozenset({HostPort("api.example.com", 443)}),
    )
    target = EgressTarget(
        profile, "api.example.com", 443, SECRET_URL_TARGET,
    )
    address = ResolvedAddress(AddressFamily.IPV4, "93.184.216.34")
    return EgressPlan(target=target, addresses=(address,), connect_address=address)


def request() -> EgressRequest:
    return EgressRequest(
        method="POST",
        headers=(("Content-Type", "application/json"),),
        body=b'{"prompt":"' + SECRET.encode("ascii") + b'"}',
        api_authorization="Bearer " + SECRET,
    )


def grant(identity: ChildIdentity, *, stop_after: float = 60.0) -> SendGrant:
    return SendGrant(
        grant_id="grant_" + uuid.uuid4().hex,
        call_id="call_" + uuid.uuid4().hex,
        attempt=identity.slot.attempt,
        boot_id=identity.slot.boot_id,
        child_instance=identity.child_instance,
        send_stop_by_monotonic=time.monotonic() + stop_after,
        plan=plan(),
        request=request(),
    )


def prepared_egress(supervisor, identity, call_id=None):
    call_id = call_id or "call_" + uuid.uuid4().hex
    supervisor.prepare(
        identity,
        StageCommand(
            call_id=call_id,
            attempt=identity.slot.attempt,
            stage=ChildStage.EGRESS,
            payload=b"",
        ),
    )
    return call_id


def stop(supervisor, identity, reason=StopReason.COMPLETED) -> StopProof:
    proof = supervisor.stop(identity, reason)
    assert proof.identity == identity
    assert proof.proven, proof
    return proof


def wait_exit(identity, timeout: float = 5.0) -> None:
    from rag_app.adapters import child_supervisor as module

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if module._process_state(
            identity.pid, identity.start_ticks,
        ) is False:
            return
        time.sleep(0.02)
    pytest.fail("the child did not exit within the bounded wait")


def test_frame_bound_rejects_oversize_and_truncation() -> None:
    with pytest.raises(ChildSupervisionError) as caught:
        encode_frame({"value": "x" * 100}, 8)
    assert caught.value.failure is ChildFailure.RESULT_TOO_LARGE

    frame = encode_frame({"type": "ready"}, 64)
    assert decode_frame(frame, 64) == {"type": "ready"}
    with pytest.raises(ChildSupervisionError):
        decode_frame(frame[:-1], 64)
    with pytest.raises(ChildSupervisionError):
        decode_frame(frame + b"x", 64)


def test_grant_and_result_wire_round_trip_hides_secrets_from_repr() -> None:
    local_plan = plan()
    local_request = request()
    value = SendGrant(
        grant_id="grant_roundtrip",
        call_id="call_roundtrip",
        attempt=1,
        boot_id="boot_roundtrip",
        child_instance="child_roundtrip",
        send_stop_by_monotonic=time.monotonic() + 30,
        plan=local_plan,
        request=local_request,
    )
    assert SECRET not in repr(value)
    assert SECRET not in repr(local_plan)
    assert SECRET not in repr(local_request)

    decoded = grant_from_wire(grant_to_wire(value))
    assert decoded.call_id == value.call_id
    assert decoded.plan is not None and decoded.request is not None
    assert decoded.plan.connect_address == local_plan.connect_address
    assert decoded.plan.target.request_target == local_plan.target.request_target
    assert decoded.request.body == local_request.body
    assert decoded.request.api_authorization == local_request.api_authorization

    result = ChildResult(
        call_id=value.call_id,
        grant_id=value.grant_id,
        send_state=SendState.RESPONSE_RECEIVED,
        response_status=200,
        payload=b'{"ok":true}',
    )
    assert result_from_wire(result_to_wire(result)) == result


def test_child_source_has_no_database_or_provider_adapter_imports() -> None:
    path = (
        Path(__file__).parents[1]
        / "src/rag_app/entrypoints/call_child.py"
    )
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = (
        "rag_app.adapters",
        "rag_app.bootstrap",
        "rag_app.application",
        "sqlalchemy",
        "psycopg",
        "httpx",
        "fastapi",
    )
    assert not any(
        name == prefix or name.startswith(prefix + ".")
        for name in imported
        for prefix in forbidden
    )


@pytest.mark.parametrize(
    "stage",
    [ChildStage.MODEL, ChildStage.PARSE, ChildStage.EMBEDDING, ChildStage.VISION],
)
def test_child_runs_one_explicit_fake_stage_and_exits(stage, state_root) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        payload = b'{"input":"bounded"}'
        supervisor.prepare(
            identity,
            StageCommand(
                call_id="call_" + uuid.uuid4().hex,
                attempt=identity.slot.attempt,
                stage=stage,
                payload=payload,
            ),
            timeout_s=5.0,
        )
        result = supervisor.receive(identity, timeout_s=5.0)
        assert result.send_state is SendState.NOT_SENT
        assert result.response_status is None
        assert result.failure is None
        decoded = json.loads(result.payload)
        assert decoded["fake"] == stage.value
        assert decoded["input_bytes"] == len(payload)
        assert decoded["sha256"] == hashlib.sha256(payload).hexdigest()
        stop(supervisor, identity)
    finally:
        assert supervisor.close()


def test_egress_consumes_the_resolved_plan_and_receives_one_grant(
    state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        call_id = prepared_egress(supervisor, identity)
        send_grant = replace(grant(identity), call_id=call_id)
        supervisor.grant(identity, send_grant)
        result = supervisor.receive(identity, timeout_s=5.0)
        assert result.send_state is SendState.RESPONSE_RECEIVED
        assert result.response_status == 200
        assert result.grant_id == send_grant.grant_id
        decoded = json.loads(result.payload)
        assert decoded["fake"] == "egress"
        assert decoded["host"] == "api.example.com"
        assert decoded["connect_address"] == "93.184.216.34"
        assert decoded["request_sha256"] == hashlib.sha256(
            request().body,
        ).hexdigest()
        assert SECRET not in result.payload.decode("utf-8")
        stop(supervisor, identity)
    finally:
        assert supervisor.close()


def test_second_grant_is_finite_and_never_consumed(state_root) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        call_id = prepared_egress(supervisor, identity)
        first = replace(grant(identity), call_id=call_id)
        supervisor.grant(identity, first)
        with pytest.raises(ChildSupervisionError) as caught:
            supervisor.grant(identity, replace(first, grant_id="grant_second"))
        assert caught.value.failure is ChildFailure.GRANT_REUSED
        stop(supervisor, identity)
    finally:
        assert supervisor.close()


@pytest.mark.parametrize("field", ["boot_id", "child_instance"])
def test_misbound_grant_is_rejected_before_the_child_sees_it(
    field, state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        call_id = prepared_egress(supervisor, identity)
        send_grant = replace(grant(identity), call_id=call_id)
        if field == "boot_id":
            send_grant = replace(send_grant, boot_id="other-boot")
        else:
            send_grant = replace(send_grant, child_instance="other-child")
        with pytest.raises(ChildSupervisionError) as caught:
            supervisor.grant(identity, send_grant)
        assert caught.value.failure is ChildFailure.IDENTITY_MISMATCH
        stop(supervisor, identity)
    finally:
        assert supervisor.close()


def test_egress_without_grant_times_out_as_not_sent(state_root) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        prepared_egress(supervisor, identity)
        result = supervisor.receive(identity, timeout_s=0.15)
        assert result.send_state is SendState.NOT_SENT
        assert result.failure is ChildFailure.TIMEOUT
        stop(supervisor, identity, StopReason.DEADLINE)
    finally:
        assert supervisor.close()


def test_child_exit_after_grant_is_conservative_may_have_sent(
    state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        call_id = prepared_egress(supervisor, identity)
        send_grant = replace(grant(identity), call_id=call_id)
        # Stop the child before the grant so it cannot race a response.
        os.kill(identity.pid, signal.SIGSTOP)
        supervisor.grant(identity, send_grant)
        os.kill(identity.pid, signal.SIGKILL)
        result = supervisor.receive(identity, timeout_s=2.0)
        assert result.send_state is SendState.MAY_HAVE_SENT
        assert result.grant_id == send_grant.grant_id
        assert result.response_status is None
        assert result.failure in {
            ChildFailure.CHILD_EXITED,
            ChildFailure.IPC_IO,
            ChildFailure.TIMEOUT,
        }
        stop(supervisor, identity, StopReason.CHILD_ERROR)
    finally:
        assert supervisor.close()


def test_live_child_in_another_supervisor_blocks_the_same_physical_slot(
    state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    first = LinuxChildSupervisor(state_root=state_root)
    second = LinuxChildSupervisor(state_root=state_root)
    local_slot = slot()
    identity = first.spawn(local_slot, limits())
    try:
        with pytest.raises(ChildSupervisionError) as caught:
            second.spawn(local_slot, limits())
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
        with pytest.raises(ChildSupervisionError) as caught:
            second.spawn(
                replace(local_slot, boot_id="new_boot_" + uuid.uuid4().hex),
                limits(),
            )
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
        # Even after the old child dies, the slot stays blocked until a
        # controller that owns it proves exit, FD/IPC closure and no descendants.
        os.kill(identity.pid, signal.SIGKILL)
        wait_exit(identity)
        with pytest.raises(ChildSupervisionError) as caught:
            second.spawn(local_slot, limits())
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
    finally:
        stop(first, identity)
        assert first.close()
        assert second.close()


def test_unreleased_starting_claim_from_crashed_spawn_blocks_the_slot(
    state_root,
) -> None:
    from rag_app.adapters import child_supervisor as module
    from rag_app.adapters.child_supervisor import (
        LinuxChildSupervisor, _SlotLedger, _SlotRecord,
    )

    supervisor = LinuxChildSupervisor(state_root=state_root)
    local_slot = slot()
    own_pid = os.getpid()
    stat = module._read_proc_stat(own_pid)
    assert stat is not None
    with supervisor._ledger.locked(
        local_slot.deployment_id, local_slot.slot_id,
    ) as path:
        _SlotLedger.write(path, _SlotRecord(
            deployment_id=local_slot.deployment_id,
            slot_id=local_slot.slot_id,
            boot_id=local_slot.boot_id,
            attempt=local_slot.attempt,
            child_instance="crashed_controller_child",
            pid=own_pid,
            process_group=os.getpgid(0),
            start_ticks=stat.start_ticks,
            started_monotonic=time.monotonic(),
            state="starting",
        ))
    try:
        with pytest.raises(ChildSupervisionError) as caught:
            supervisor.spawn(local_slot, limits())
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
    finally:
        assert supervisor.close()


def test_stop_unproven_persists_across_supervisor_instances(state_root) -> None:
    from rag_app.adapters import child_supervisor as module
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    first = LinuxChildSupervisor(state_root=state_root)
    second = LinuxChildSupervisor(state_root=state_root)
    local_slot = slot()
    identity = first.spawn(local_slot, limits())
    original_state = module._process_state
    original_group = module._group_state
    module._process_state = lambda *args, **kwargs: True
    module._group_state = lambda *args, **kwargs: (True, [object()])
    try:
        proof = first.stop(identity, StopReason.CONTROLLER_STOP)
        assert proof.proven is False
        assert proof.failure is ChildFailure.STOP_UNPROVEN
        with pytest.raises(ChildSupervisionError) as caught:
            second.spawn(local_slot, limits())
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
    finally:
        module._process_state = original_state
        module._group_state = original_group
        stop(first, identity, StopReason.CONTROLLER_STOP)
        assert first.close()
        assert second.close()


def test_proc_unknown_is_never_proof_of_absence(monkeypatch, state_root) -> None:
    from rag_app.adapters import child_supervisor as module
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    identity = supervisor.spawn(slot(), limits())
    # Freeze the sampler before /proc becomes unreadable; otherwise its
    # per-tick "unknown" flag would also cover the restored good period.
    supervisor._handles[identity.child_instance].monitor.finish()
    original_scan = module._scan_proc
    original_read = module._read_proc_stat
    try:
        monkeypatch.setattr(module, "_scan_proc", lambda: None)

        def unknown(pid):
            raise module._ProcUnknown()

        monkeypatch.setattr(module, "_read_proc_stat", unknown)
        proof = supervisor.stop(identity, StopReason.CONTROLLER_STOP)
        assert proof.proven is False
        assert proof.failure is ChildFailure.STOP_UNPROVEN
        # Unreadable /proc must not be treated as an empty descendant set, and
        # the unproven result must remain the persistent answer for this call.
        assert proof.no_descendants is False
        assert proof.process_group_empty is False
        monkeypatch.setattr(module, "_scan_proc", original_scan)
        monkeypatch.setattr(module, "_read_proc_stat", original_read)
    finally:
        # The child was never signalled while /proc was unreadable.
        assert supervisor.inspect(identity).proven is False
        supervisor._handles[identity.child_instance].proof = None
        stop(supervisor, identity, StopReason.CONTROLLER_STOP)
        assert supervisor.close()


def test_foreign_identity_is_never_signalled(monkeypatch, state_root) -> None:
    from rag_app.adapters import child_supervisor as module
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    identity = supervisor.spawn(slot(), limits())
    signals = []
    original_signal = module._signal_verified

    def record_signal(pid, ticks, group, signum):
        signals.append((pid, ticks, group, signum))
        raise AssertionError("a foreign identity must never be signalled")

    monkeypatch.setattr(module, "_signal_verified", record_signal)
    try:
        forged = replace(identity, start_ticks=identity.start_ticks + 999)
        proof = supervisor.stop(forged, StopReason.CONTROLLER_STOP)
        assert proof.proven is False
        assert proof.failure is ChildFailure.STOP_UNPROVEN
        assert signals == []
    finally:
        monkeypatch.setattr(module, "_signal_verified", original_signal)
        stop(supervisor, identity, StopReason.CONTROLLER_STOP)
        assert supervisor.close()


def test_secret_is_not_in_child_argv_environment_or_logs(
    monkeypatch, caplog, capsys, state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    monkeypatch.setenv(
        "RAG_DATABASE_URL",
        "postgresql+psycopg://user:" + SECRET + "@host/db",
    )
    monkeypatch.setenv("RAG_MASTER_KEY", SECRET)
    monkeypatch.setenv("CHILD_SECRET_SENTINEL", SECRET)
    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        cmdline = Path(f"/proc/{identity.pid}/cmdline").read_bytes()
        environ = Path(f"/proc/{identity.pid}/environ").read_bytes()
        assert SECRET.encode("ascii") not in cmdline
        assert SECRET.encode("ascii") not in environ
        assert b"RAG_DATABASE_URL" not in environ
        assert b"RAG_MASTER_KEY" not in environ
        assert b"CHILD_SECRET_SENTINEL" not in environ
        assert b"--ipc-fd" in cmdline
        stop(supervisor, identity)
    finally:
        assert supervisor.close()
    captured = "".join(capsys.readouterr())
    assert SECRET not in captured + caplog.text


def test_proven_stop_allows_the_same_slot_to_spawn_again(state_root) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    local_slot = slot()
    try:
        first = supervisor.spawn(local_slot, limits())
        with pytest.raises(ChildSupervisionError) as caught:
            supervisor.spawn(local_slot, limits())
        assert caught.value.failure is ChildFailure.STOP_UNPROVEN
        stop(supervisor, first)
        second = supervisor.spawn(local_slot, limits())
        assert second.child_instance != first.child_instance
        stop(supervisor, second)
    finally:
        assert supervisor.close()


def test_identity_reuse_with_a_stale_start_token_is_not_the_same_child(
    state_root,
) -> None:
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(state_root=state_root)
    try:
        identity = supervisor.spawn(slot(), limits())
        forged = replace(identity, start_ticks=identity.start_ticks + 1)
        with pytest.raises(ChildSupervisionError) as caught:
            supervisor.prepare(
                forged,
                StageCommand(
                    call_id="call_" + uuid.uuid4().hex,
                    attempt=forged.slot.attempt,
                    stage=ChildStage.MODEL,
                    payload=b"x",
                ),
            )
        assert caught.value.failure is ChildFailure.IDENTITY_MISMATCH
        stop(supervisor, identity)
    finally:
        assert supervisor.close()


def test_slow_fragmented_ipc_cannot_extend_the_absolute_deadline() -> None:
    import socket as socket_module
    import threading

    from rag_app.modules.execution.supervision import read_frame

    payload = json.dumps({
        "type": "result", "call_id": "call_" + uuid.uuid4().hex,
        "grant_id": None, "send_state": "not_sent",
        "response_status": None, "payload": "", "failure": None,
    }).encode("utf-8")
    reader, writer = socket_module.socketpair(
        socket_module.AF_UNIX, socket_module.SOCK_STREAM,
    )
    stop_writer = threading.Event()

    def dribble():
        try:
            frame = encode_frame(json.loads(payload), 1_048_576)
            # Deliver the complete header at once so the old relative-timeout
            # defect is exercised in the body receive, not in the header.
            writer.sendall(frame[:4])
            for index in range(4, len(frame)):
                if stop_writer.is_set():
                    return
                writer.sendall(frame[index:index + 1])
                time.sleep(0.12)
        except OSError:
            return

    thread = threading.Thread(target=dribble, daemon=True)
    thread.start()
    try:
        started = time.monotonic()
        with pytest.raises(ChildSupervisionError) as caught:
            read_frame(
                reader,
                1_048_576,
                deadline_monotonic=time.monotonic() + 0.35,
            )
        elapsed = time.monotonic() - started
        assert caught.value.failure is ChildFailure.TIMEOUT
        assert elapsed < 1.0
    finally:
        stop_writer.set()
        reader.close()
        writer.close()
