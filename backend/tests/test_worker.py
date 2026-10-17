from unittest.mock import Mock

import pytest

from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError
from rag_app.entrypoints import worker


def test_worker_uses_same_bootstrap_and_closes(monkeypatch):
    runtime = Mock()
    build = Mock(return_value=runtime)
    monkeypatch.setattr(worker, "build_runtime", build)
    settings = Settings()
    worker.check_database(settings)
    build.assert_called_once_with(settings)
    runtime.check_database.assert_called_once_with()
    runtime.close.assert_called_once_with()


def test_worker_preserves_primary_failure_on_cleanup_error(monkeypatch):
    primary = SafeError("DATABASE_VERSION_MISMATCH")
    runtime = Mock()
    runtime.check_database.side_effect = primary
    runtime.close.side_effect = SafeError("DATABASE_CLEANUP_FAILED")
    monkeypatch.setattr(worker, "build_runtime", Mock(return_value=runtime))
    with pytest.raises(SafeError) as caught:
        worker.check_database(Settings())
    assert caught.value is primary
    assert len(caught.value.cleanup_errors) == 1
    runtime.close.assert_called_once()
