"""Isolated DTO probe and shared private HTTP projection; no business execution."""

from __future__ import annotations

from secrets import compare_digest
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import SecretStr, ValidationError
from pydantic.json_schema import models_json_schema

from rag_app.contracts.public import (
    PUBLIC_MODELS, AcceptedResponse, FailedResponse, OperationResponse, PublicError,
)
from rag_app.entrypoints.json_guard import BoundedJsonError, read_bounded_json


PROBE_PATH = "/__maintenance/contracts/{model_name}"
TOKEN_HEADER = b"x-rag-contract-test"


def failure_response(request_id: str, code: str) -> JSONResponse:
    """Project only public policy; never serialize an exception or private ID."""
    error = PublicError.from_code(code)
    dto = FailedResponse(
        schema_version="operation.v1", request_id=request_id, error=error,
    )
    return JSONResponse(
        dto.model_dump(mode="json", exclude_unset=True),
        status_code=error.http_status,
        headers={"Cache-Control": "no-store", "X-Request-ID": request_id},
    )


class PrivateHttpMiddleware:
    """Assign server IDs and apply cache policy to successes and router errors."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        started = False

        async def private_send(message: Any) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                if message["status"] == 304:
                    # A private route cannot use validators to bypass authorization.
                    raise ValueError("Private conditional responses are unavailable.")
                blocked = {
                    b"cache-control", b"etag", b"last-modified", b"expires",
                    b"age", b"x-request-id",
                }
                headers = [(key, value) for key, value in message.get("headers", [])
                           if key.lower() not in blocked]
                headers.extend([
                    (b"cache-control", b"no-store"),
                    (b"x-request-id", request_id.encode("ascii")),
                ])
                message = {**message, "headers": headers}
                started = True
            await send(message)

        failed = False
        try:
            await self.app(scope, receive, private_send)
        except Exception:
            # Catch inside ServerErrorMiddleware so it cannot log private exceptions.
            failed = True
        if failed and not started:
            response = failure_response(request_id, "INTERNAL_ERROR")
            await response(scope, receive, private_send)
        # This API's JSON responses are materialized before response.start. Once a
        # response starts, do not append an error envelope or expose an exception.


def register_contract_probe(app: FastAPI, token: SecretStr | None) -> None:
    if token is not None and not isinstance(token, SecretStr):
        raise ValueError("Contract test token must be an explicit SecretStr.")
    expected = token.get_secret_value().encode("utf-8") if token is not None else None
    if expected is not None and not 1 <= len(expected) <= 256:
        raise ValueError("Contract test token must contain 1 to 256 UTF-8 bytes.")
    response_models = {
        name: model for name, model in PUBLIC_MODELS.items()
        if {"schema_version", "request_id", "status"} <= model.model_fields.keys()
    }

    @app.post(PROBE_PATH, response_model=None, tags=["isolated-contract-fixtures"])
    async def contract_probe(model_name: str, request: Request):
        request_id = request.state.request_id
        try:
            payload = await read_bounded_json(request)
        except BoundedJsonError as exc:
            return failure_response(request_id, exc.code)

        supplied = [value for key, value in request.scope.get("headers", [])
                    if key.lower() == TOKEN_HEADER]
        if expected is None or len(supplied) != 1:
            return failure_response(request_id, "AUTH_REQUIRED")
        if not compare_digest(supplied[0], expected):
            return failure_response(request_id, "AUTH_REQUIRED")

        model = response_models.get(model_name)
        if model is None:
            return failure_response(request_id, "RESOURCE_UNAVAILABLE")
        try:
            dto = model.model_validate(payload)
        except ValidationError:
            return failure_response(request_id, "VALIDATION_ERROR")
        result = dto.model_dump(mode="json", exclude_unset=True)
        if "request_id" in model.model_fields:
            result["request_id"] = request_id
        status = 200
        if isinstance(dto, AcceptedResponse):
            status = 202
        elif isinstance(dto, OperationResponse):
            status = 200
        elif isinstance(dto, FailedResponse):
            status = dto.error.http_status
        return JSONResponse(result, status_code=status)

    def contract_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        models = list(PUBLIC_MODELS.values())
        references, definitions = models_json_schema(
            [(model, mode) for model in models for mode in ("validation", "serialization")],
            ref_template="#/components/schemas/{model}",
        )
        components = schema.setdefault("components", {}).setdefault("schemas", {})
        components.update(definitions.get("$defs", {}))
        operation = schema["paths"][PROBE_PATH]["post"]
        for parameter in operation.get("parameters", []):
            if parameter["name"] == "model_name" and parameter["in"] == "path":
                parameter["schema"] = {"type": "string", "enum": list(response_models)}
        operation["description"] = (
            "Isolated DTO validation only; requires an explicit in-memory test token "
            "in X-RAG-Contract-Test. Disabled by default. No business authorization, "
            "database access, provider calls, or operation execution. Keep this path "
            "off private/public production gateways. Response-envelope request_id "
            "is replaced by a fresh server ID. Only the five C2 response models "
            "are accepted; helper DTOs are schema components only. "
            "OperationResponse models GET-state projection semantics; this POST "
            "probe does not register a business GET operation endpoint."
        )
        operation["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {
                "oneOf": [references[(model, "validation")]
                          for model in response_models.values()],
            }}},
        }
        serialization = [
            references[(model, "serialization")]
            for model in response_models.values()
            if model not in (AcceptedResponse, FailedResponse)
        ]
        failed_ref = references[(FailedResponse, "serialization")]
        operation["responses"] = {
            "200": {
                "description": "Validated fixture DTO, including operation state projection.",
                "content": {"application/json": {"schema": {"oneOf": serialization}}},
            },
            "202": {
                "description": "Validated AcceptedResponse fixture; no operation is created.",
                "content": {"application/json": {"schema":
                    references[(AcceptedResponse, "serialization")]}},
            },
            "default": {
                "description": "Finite private error or validated FailedResponse fixture.",
                "content": {"application/json": {"schema": failed_ref}},
            },
        }
        app.openapi_schema = schema
        return schema

    app.openapi = contract_openapi
