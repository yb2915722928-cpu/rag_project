from unittest.mock import Mock

from rag_app.application.baseline import check_baseline
from rag_app.application.uow import UnitOfWork
from rag_app.bootstrap.config import Settings
from rag_app.bootstrap.runtime import build_runtime


def test_baseline_is_one_application_uow():
    session = Mock()
    repository = Mock()
    factory = Mock(return_value=repository)
    check_baseline(UnitOfWork(lambda: session), factory)
    factory.assert_called_once_with(session)
    repository.check.assert_called_once()
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_bootstrap_disposes_the_same_engine():
    runtime = build_runtime(Settings())
    assert runtime.engine.hide_parameters
    assert runtime.engine.dialect.name == "postgresql"
    runtime.close()
