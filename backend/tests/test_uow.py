from __future__ import annotations

from unittest.mock import Mock

import pytest

from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import GuardError, SafeError


def test_uow_commits_once_after_success() -> None:
    session = Mock()
    uow = UnitOfWork(lambda: session)
    with uow.transaction() as active:
        assert active is session
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_uow_rolls_back_and_never_commits_after_failure() -> None:
    session = Mock()
    uow = UnitOfWork(lambda: session)
    with pytest.raises(SafeError) as caught:
        with uow.transaction():
            raise RuntimeError("injected")
    assert isinstance(caught.value.diagnostic_cause, RuntimeError)
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()
    session.close.assert_called_once_with()


@pytest.mark.parametrize("stage", ["body", "commit"])
@pytest.mark.parametrize("cleanup_stages", [(), ("rollback",), ("close",), ("rollback", "close")])
def test_original_failure_survives_rollback_and_close_failures(
    stage, cleanup_stages, caplog, capsys,
) -> None:
    secret = "BODY_PASSWORD_SIGNED_URL_SENTINEL"
    original = RuntimeError(secret)
    session = Mock()
    for cleanup_stage in cleanup_stages:
        getattr(session, cleanup_stage).side_effect = RuntimeError(secret + "_" + cleanup_stage)
    if stage == "commit":
        session.commit.side_effect = original
    with pytest.raises(SafeError) as caught:
        with UnitOfWork(lambda: session).transaction():
            if stage == "body":
                raise original
    assert caught.value.diagnostic_cause is original
    assert len(caught.value.cleanup_errors) == len(cleanup_stages)
    session.close.assert_called_once()
    assert secret not in str(caught.value) + repr(caught.value) + caplog.text
    assert secret not in "".join(capsys.readouterr())


def test_close_failure_after_commit_does_not_claim_rollback() -> None:
    session = Mock()
    failure = RuntimeError("close-secret")
    session.close.side_effect = failure
    with pytest.raises(SafeError) as caught:
        with UnitOfWork(lambda: session).transaction():
            pass
    assert caught.value.code == "DATABASE_CLEANUP_FAILED"
    assert caught.value.diagnostic_cause is failure
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_session_creation_failure_is_safe() -> None:
    failure = RuntimeError("driver-password")
    with pytest.raises(SafeError) as caught:
        with UnitOfWork(Mock(side_effect=failure)).transaction():
            pytest.fail("unreachable")
    assert caught.value.diagnostic_cause is failure
    assert "driver-password" not in str(caught.value)


def test_repository_executes_without_committing() -> None:
    from rag_app.adapters.postgres import ProbeRepository

    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = True
    ProbeRepository(session, schema="target").add(42, "repository-body")
    assert session.execute.call_count == 2
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
    session.close.assert_not_called()


def test_guard_failure_rolls_back_and_keeps_its_finite_code() -> None:
    session = Mock()
    with pytest.raises(GuardError) as caught:
        with UnitOfWork(lambda: session).transaction():
            raise GuardError("CALL_FENCE_STALE")
    assert caught.value.code == "CALL_FENCE_STALE"
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()
    session.close.assert_called_once_with()

