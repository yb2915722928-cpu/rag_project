import logging
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import StatementError

from rag_app.adapters.postgres import create_pg_engine
from rag_app.application.uow import UnitOfWork
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError

SENTINEL = "PASSWORD_BODY_SIGNED_URL_SENTINEL"


@pytest.mark.parametrize("url", [
    f"sqlite:///{SENTINEL}",
    f"postgresql+asyncpg://user:{SENTINEL}@localhost/db",
    f"postgresql://user:{SENTINEL}@localhost/db",
    f"https://host/?signature={SENTINEL}",
    f"postgresql+psycopg://user:{SENTINEL}@localhost:bad/db",
])
def test_settings_and_adapter_reject_invalid_driver_safely(url, caplog, capsys) -> None:
    for factory in (lambda: Settings(database_url=url), lambda: create_pg_engine(url)):
        with pytest.raises(SafeError) as caught:
            factory()
        assert caught.value.code == "CONFIGURATION_INVALID"
        assert SENTINEL not in str(caught.value) + repr(caught.value)
    assert SENTINEL not in caplog.text + "".join(capsys.readouterr())


def test_settings_secret_repr_and_engine_parameter_hiding() -> None:
    settings = Settings(database_url=f"postgresql+psycopg://user:{SENTINEL}@localhost/db")
    assert SENTINEL not in repr(settings) + str(settings.model_dump())
    engine = create_pg_engine(settings.database_url.get_secret_value())
    try:
        assert engine.hide_parameters is True
        assert engine.dialect.driver == "psycopg"
        assert not engine.echo
    finally:
        engine.dispose()


def test_parameter_and_driver_errors_remain_internal(caplog, capsys) -> None:
    caplog.set_level(logging.DEBUG)
    original = StatementError("driver-" + SENTINEL, "INSERT INTO t VALUES (:body)",
                              {"body": SENTINEL}, RuntimeError(SENTINEL))
    session = Mock()
    session.execute.side_effect = original
    with pytest.raises(SafeError) as caught:
        with UnitOfWork(lambda: session).transaction() as active:
            active.execute("INSERT INTO t VALUES (:body)", {"body": SENTINEL})
    assert caught.value.diagnostic_cause is original
    assert SENTINEL not in str(caught.value) + caplog.text + "".join(capsys.readouterr())
