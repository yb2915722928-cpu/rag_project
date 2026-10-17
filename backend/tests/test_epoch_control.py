"""Independent epoch control: missing, damaged, contradictions and no rotation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from rag_app.adapters import epoch_control
from rag_app.adapters.epoch_control import (
    CONTROL_MAX_BYTES, FileEpochControl, initialize_epoch_control,
)
from rag_app.contracts.errors import GuardError


def control_document(**overrides):
    document = {
        "deployment_id": "deployment-1",
        "epoch": "a" * 43,
        "cutover_at": "2026-10-18T00:00:00Z",
        "maintenance_version": 1,
    }
    document.update(overrides)
    return document


def write_control(path: Path, **overrides) -> None:
    path.write_text(json.dumps(control_document(**overrides)), encoding="utf-8")


def test_missing_control_is_isolated_and_never_synthesized(tmp_path):
    path = tmp_path / "absent.json"
    control = FileEpochControl(path)
    with pytest.raises(GuardError) as caught:
        control.current()
    assert caught.value.code == "EPOCH_CONTROL_MISSING"
    assert not path.exists()


def test_environment_without_control_fails_finite(monkeypatch):
    monkeypatch.delenv(epoch_control.CONTROL_FILE_ENV, raising=False)
    with pytest.raises(GuardError, match="EPOCH_CONTROL_MISSING"):
        FileEpochControl.from_environment()


@pytest.mark.parametrize("payload", [
    b"{",
    b"[]",
    b'{"deployment_id": "d"}',
    b'\xff\xfe',
    json.dumps(control_document(epoch="short")).encode(),
    json.dumps(control_document(maintenance_version=0)).encode(),
    json.dumps(control_document(maintenance_version=True)).encode(),
    json.dumps(control_document(cutover_at="2026-10-18T00:00:00+00:00")).encode(),
    json.dumps(control_document(extra="value")).encode(),
])
def test_damaged_control_is_invalid(tmp_path, payload):
    path = tmp_path / "control.json"
    path.write_bytes(payload)
    with pytest.raises(GuardError, match="EPOCH_CONTROL_INVALID"):
        FileEpochControl(path).current()


def test_oversized_control_is_rejected_without_parsing(tmp_path):
    path = tmp_path / "control.json"
    path.write_bytes(b"{" + b"a" * CONTROL_MAX_BYTES + b"}")
    with pytest.raises(GuardError, match="EPOCH_CONTROL_INVALID"):
        FileEpochControl(path).current()


def test_initialization_creates_one_random_bounded_record(tmp_path):
    path = tmp_path / "control.json"
    created = initialize_epoch_control(path, deployment_id="deployment-1")
    assert len(created.epoch) >= 32
    assert created.deployment_id == "deployment-1"
    assert created.maintenance_version == 1
    assert created.cutover_at.tzinfo is not None
    document = json.loads(path.read_text(encoding="utf-8"))
    assert set(document) == {
        "deployment_id", "epoch", "cutover_at", "maintenance_version",
    }
    assert document["epoch"] == created.epoch
    assert document["cutover_at"].endswith("Z")


def test_second_initialization_fails_and_preserves_existing_bytes(tmp_path):
    path = tmp_path / "control.json"
    initialize_epoch_control(path, deployment_id="deployment-1")
    original = path.read_bytes()
    with pytest.raises(GuardError, match="EPOCH_CONTROL_INVALID"):
        initialize_epoch_control(path, deployment_id="deployment-2")
    assert path.read_bytes() == original


def test_current_always_reads_the_control_record(tmp_path):
    path = tmp_path / "control.json"
    write_control(path, epoch="a" * 43)
    control = FileEpochControl(path)
    assert control.current().epoch == "a" * 43
    write_control(path, epoch="b" * 43, maintenance_version=2)
    assert control.current().epoch == "b" * 43
    assert control.current().maintenance_version == 2


def test_mirror_uses_expected_value_read_before_the_transaction(tmp_path, monkeypatch):
    path = tmp_path / "control.json"
    write_control(path)
    control = FileEpochControl(path)
    expected = control.current()
    seen = {}

    def mirror(session, *, schema):
        seen["schema"] = schema
        return (
            expected.deployment_id, expected.epoch, expected.cutover_at,
            expected.maintenance_version,
        )

    monkeypatch.setattr(epoch_control, "epoch_mirror", mirror)
    write_control(path, epoch="b" * 43)
    control.verify_mirror(Mock(), expected=expected)
    assert seen["schema"] == "public"


def test_mirror_missing_or_contradictory_is_isolated(tmp_path, monkeypatch):
    path = tmp_path / "control.json"
    write_control(path)
    control = FileEpochControl(path, schema="target")
    monkeypatch.setattr(
        epoch_control, "epoch_mirror",
        lambda session, *, schema: (
            "deployment-1", "c" * 43,
            datetime(2026, 10, 18, tzinfo=timezone.utc), 1,
        ),
    )
    with pytest.raises(GuardError, match="EPOCH_MIRROR_MISMATCH"):
        control.verify_mirror(Mock())

    def missing(session, *, schema):
        raise GuardError("EPOCH_MIRROR_MISSING")

    monkeypatch.setattr(epoch_control, "epoch_mirror", missing)
    with pytest.raises(GuardError, match="EPOCH_MIRROR_MISSING"):
        control.verify_mirror(Mock())


def test_unexpected_mirror_failure_is_missing_not_leaked(tmp_path, monkeypatch):
    path = tmp_path / "control.json"
    write_control(path)
    control = FileEpochControl(path)

    def broken(session, *, schema):
        raise RuntimeError("PRIVATE_SQL_SENTINEL")

    monkeypatch.setattr(epoch_control, "epoch_mirror", broken)
    with pytest.raises(GuardError) as caught:
        control.verify_mirror(Mock())
    assert caught.value.code == "EPOCH_MIRROR_MISSING"
    assert "PRIVATE_SQL_SENTINEL" not in str(caught.value)


def test_control_record_rejects_non_utc_cutover(tmp_path):
    path = tmp_path / "control.json"
    write_control(path)
    control = FileEpochControl(path)
    assert control.current().cutover_at == datetime(
        2026, 10, 18, tzinfo=timezone.utc,
    )
    # The record is absolute, not offset by the reading process timezone.
    assert control.current().cutover_at.utcoffset() == timedelta(0)
