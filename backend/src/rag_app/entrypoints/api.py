from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import SecretStr
from starlette.exceptions import HTTPException

from rag_app.application.health import HealthStatus
from rag_app.bootstrap.config import Settings
from rag_app.bootstrap.runtime import build_runtime
from rag_app.contracts.errors import SafeError
from rag_app.entrypoints.contract_probe import (
    PrivateHttpMiddleware, failure_response, register_contract_probe,
)
from rag_app.entrypoints.upload_api import register_upload_routes


def create_app(
    settings: Settings | None = None, *, contract_test_token: SecretStr | None = None,
) -> FastAPI:
    settings = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app):
        runtime = build_runtime(settings)
        app.state.runtime = runtime
        try:
            yield
        finally:
            runtime.close()

    app = FastAPI(
        title="RAG_all API", version="0.1.0", lifespan=lifespan,
        redirect_slashes=False,
    )
    app.add_middleware(PrivateHttpMiddleware)

    @app.exception_handler(SafeError)
    async def safe_failure(request, exc):
        return failure_response(request.state.request_id, exc.code)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return failure_response(request.state.request_id, "VALIDATION_ERROR")

    @app.exception_handler(HTTPException)
    async def http_failure(request, exc):
        code = {
            401: "AUTH_REQUIRED", 403: "ACTION_FORBIDDEN",
            404: "RESOURCE_UNAVAILABLE", 405: "METHOD_NOT_ALLOWED",
            413: "REQUEST_BODY_LIMIT_EXCEEDED", 415: "UNSUPPORTED_MEDIA_TYPE",
            422: "VALIDATION_ERROR",
        }.get(exc.status_code, "INTERNAL_ERROR")
        response = failure_response(request.state.request_id, code)
        if exc.status_code == 405:
            response.headers["Allow"] = "POST" if request.url.path.startswith(
                "/__maintenance/contracts/",
            ) else "GET"
        return response

    @app.get("/health", response_model=HealthStatus)
    def health() -> HealthStatus:
        return HealthStatus()

    register_contract_probe(
        app, contract_test_token if settings.environment != "production" else None,
    )
    register_upload_routes(app, settings=settings)
    return app


