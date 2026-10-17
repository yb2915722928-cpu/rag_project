from fastapi.testclient import TestClient

from rag_app.entrypoints.api import create_app
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError
from unittest.mock import Mock
import rag_app.entrypoints.api as api


def test_health_endpoint_has_no_secret_or_body() -> None:
    with TestClient(create_app(Settings())) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "service": "rag-api", "check": "liveness"}
    assert "secret" not in response.text.lower()


def test_lifespan_uses_settings_and_disposes_engine(monkeypatch) -> None:
    runtime = Mock()
    build = Mock(return_value=runtime)
    monkeypatch.setattr(api, "build_runtime", build)
    settings = Settings(database_url="postgresql+psycopg://user@localhost/example")
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        assert client.app.state.runtime is runtime
    build.assert_called_once_with(settings)
    runtime.close.assert_called_once_with()


def test_actual_http_error_path_is_safe(monkeypatch, caplog, capsys) -> None:
    sentinel = "HTTP_PASSWORD_BODY_SIGNED_URL_SENTINEL"
    app = create_app(Settings())

    @app.get("/_test_failure")
    def failing():
        from rag_app.application.uow import UnitOfWork
        session = Mock()
        session.execute.side_effect = RuntimeError(sentinel)
        with UnitOfWork(lambda: session).transaction() as active:
            active.execute("SELECT :body", {"body": sentinel})

    with TestClient(app) as client:
        response = client.get("/_test_failure")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_OPERATION_FAILED"
    assert response.headers["cache-control"] == "no-store"
    assert sentinel not in response.text + caplog.text + "".join(capsys.readouterr())

