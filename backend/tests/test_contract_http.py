"""DTO probe HTTP coverage; run on the coordinator's fixed Linux commit."""

from __future__ import annotations

from contextlib import contextmanager
import asyncio
import json
import re
from unittest.mock import Mock

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.testclient import TestClient
from pydantic import SecretStr
import pytest

from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import MESSAGES, SafeError
from rag_app.contracts.public import PUBLIC_MODELS, PublicError
from rag_app.entrypoints import api, contract_probe


TOKEN = "isolated-contract-test-token"
SECRET = "PRIVATE_OPERATION_BODY_PASSWORD_https://private.example/signed"
PATH = "/__maintenance/contracts/"
NOW = "2026-10-17T08:00:00Z"
HEADERS = {"X-RAG-Contract-Test": TOKEN}
RESPONSE_NAMES = {
    "AcceptedResponse", "CompletedResponse", "FailedResponse",
    "OperationResponse", "RetrievalResponse",
}


def fixtures():
    error = PublicError.from_code("DEPENDENCY_TIMEOUT").model_dump(mode="json")
    evidence = {
        "evidence_id": "e1", "chunk_id": "c1", "excerpt": "\U0001f680",
        "start": 0, "end": 1,
    }
    summary = {"text": " \r\nA\u0301\U0001f680 ", "fact_ids": ["f1"]}
    fact = {
        "id": "f1", "kind": "step", "order": 1, "text": "\U0001f680",
        "applicability": "", "evidence_ids": ["e1"],
        "quantity": None, "conflict_sides": None,
    }
    answer = {
        "outcome": "answered", "summary": summary, "facts": [fact],
        "gaps": [], "clarifications": [],
    }
    retrieval_payload = {
        "retrieval_execution_id": "retr-1", "deadline": NOW,
        "evidence_catalog": [evidence],
    }
    return {
        "Usage": {"input_tokens": None, "output_tokens": 0, "unknown": True},
        "Money": {"amount": None, "currency": None, "source": "unknown"},
        "ErrorDetails": {"field": None, "reason": None, "retry_after_seconds": None},
        "PublicError": error,
        "EvidenceBlock": evidence,
        "RetrievalPayload": retrieval_payload,
        "AcceptedResponse": {
            "schema_version": "operation.v1", "request_id": "client-attempt",
            "status": "in_progress", "operation_id": "op-1",
            "operation_state": "accepted", "accepted_at": NOW,
            "status_url": "/operations/op-1", "retry_mode": "same_key_or_status",
        },
        "Summary": summary,
        "Quantity": {"value_text": "5.00", "unit": "V"},
        "ConflictSides": {"side_a": ["e1"], "side_b": ["e2"]},
        "Fact": fact,
        "Gap": {"field": "version", "text": "Which version?"},
        "AnswerPayload": answer,
        "CompletedResponse": {
            **answer, "schema_version": "answer.v1", "request_id": "client-attempt",
            "status": "completed", "operation_id": "op-1", "replayed": False,
            "accepted_at": NOW, "completed_at": NOW, "execution_snapshot_id": "snap-1",
            "evidence_catalog": [evidence],
        },
        "FailedResponse": {
            "schema_version": "operation.v1", "request_id": "client-attempt",
            "status": "failed", "error": error, "operation_id": "private-op",
        },
        "OperationResponse": {
            "schema_version": "operation.v1", "request_id": "client-attempt",
            "status": "failed", "operation_id": "private-op",
            "operation_state": "failed", "error": error,
        },
        "RetrievalResponse": {
            **retrieval_payload, "schema_version": "retrieval.v1",
            "request_id": "client-attempt", "status": "completed",
        },
    }


@contextmanager
def isolated_client(monkeypatch, *, token=SecretStr(TOKEN)):
    runtime = Mock()
    build = Mock(return_value=runtime)
    monkeypatch.setattr(api, "build_runtime", build)
    app = api.create_app(Settings(), contract_test_token=token)
    with TestClient(app) as client:
        yield client
    build.assert_called_once()
    runtime.close.assert_called_once_with()
    runtime.uow.assert_not_called()
    runtime.check_database.assert_not_called()


def assert_private(response):
    assert response.headers["cache-control"] == "no-store"
    assert "etag" not in response.headers
    assert "last-modified" not in response.headers
    assert re.fullmatch(r"[a-f0-9]{32}", response.headers["x-request-id"])
    assert response.status_code != 304


def assert_failure(response, code):
    assert_private(response)
    dto = PUBLIC_MODELS["FailedResponse"].model_validate(response.json())
    assert dto.error == PublicError.from_code(code)
    assert response.status_code == dto.error.http_status
    assert dto.request_id == response.headers["x-request-id"]
    assert "operation_id" not in response.json()
    assert SECRET not in response.text
    return dto


def test_five_public_response_models_have_authorized_dto_roundtrips(monkeypatch):
    samples = fixtures()
    assert set(samples) == set(PUBLIC_MODELS)
    with isolated_client(monkeypatch) as client:
        request_ids = set()
        for name in sorted(RESPONSE_NAMES):
            payload = samples[name]
            response = client.post(PATH + name, json=payload, headers=HEADERS)
            assert_private(response)
            expected_status = {"AcceptedResponse": 202, "FailedResponse": 504}.get(name, 200)
            assert response.status_code == expected_status
            dto = PUBLIC_MODELS[name].model_validate(response.json())
            expected = PUBLIC_MODELS[name].model_validate(payload)
            if "request_id" in type(expected).model_fields:
                expected = expected.model_copy(update={"request_id": dto.request_id})
                assert dto.request_id == response.headers["x-request-id"]
                assert dto.request_id != payload["request_id"]
            assert dto == expected
            request_ids.add(response.headers["x-request-id"])
        assert len(request_ids) == len(RESPONSE_NAMES)


def test_helper_dtos_are_not_bare_http_responses(monkeypatch):
    with isolated_client(monkeypatch) as client:
        for name in PUBLIC_MODELS.keys() - RESPONSE_NAMES:
            assert_failure(client.post(PATH + name, json=fixtures()[name],
                                       headers=HEADERS), "RESOURCE_UNAVAILABLE")
            assert_failure(client.post(PATH + name, json=fixtures()[name]),
                           "AUTH_REQUIRED")


def test_default_none_and_production_settings_never_enable_probe(monkeypatch):
    monkeypatch.setenv("RAG_CONTRACT_TEST_TOKEN", TOKEN)
    monkeypatch.setenv("RAG_ENVIRONMENT", "production")
    with isolated_client(monkeypatch, token=None) as client:
        for headers in ({}, HEADERS):
            response = client.post(PATH + "RetrievalResponse",
                                   json=fixtures()["RetrievalResponse"], headers=headers)
            assert_failure(response, "AUTH_REQUIRED")
    app = api.create_app()
    assert app.openapi()["paths"][PATH + "{model_name}"]["post"]
    with isolated_client(monkeypatch) as client:
        assert_failure(client.post(PATH + "RetrievalResponse",
                                   json=fixtures()["RetrievalResponse"],
                                   headers=HEADERS), "AUTH_REQUIRED")


def test_token_must_be_an_explicit_nonempty_secretstr():
    for invalid in ("plaintext-token", SecretStr(""), SecretStr("x" * 257)):
        with pytest.raises(ValueError) as caught:
            api.create_app(Settings(), contract_test_token=invalid)
        assert "plaintext-token" not in str(caught.value)
        assert "x" * 257 not in str(caught.value)


def test_missing_wrong_duplicate_token_and_unknown_model_reveal_no_fixture(monkeypatch):
    payload = {**fixtures()["OperationResponse"], "operation_id": SECRET}
    with isolated_client(monkeypatch) as client:
        for headers in ({}, {"X-RAG-Contract-Test": "wrong"}, [
            ("X-RAG-Contract-Test", TOKEN), ("X-RAG-Contract-Test", TOKEN),
        ]):
            response = client.post(PATH + "OperationResponse", json=payload, headers=headers)
            assert_failure(response, "AUTH_REQUIRED")
        assert_failure(client.post(PATH + "UnknownModel", json=payload),
                       "AUTH_REQUIRED")
        assert_failure(client.post(PATH + "UnknownModel", json=payload, headers=HEADERS),
                       "RESOURCE_UNAVAILABLE")


def test_constant_time_comparison_is_used(monkeypatch):
    original = contract_probe.compare_digest
    compare = Mock(side_effect=original)
    monkeypatch.setattr(contract_probe, "compare_digest", compare)
    with isolated_client(monkeypatch) as client:
        client.post(PATH + "RetrievalResponse", json=fixtures()["RetrievalResponse"],
                    headers=HEADERS)
    compare.assert_called_once_with(TOKEN.encode(), TOKEN.encode())


def test_h_precedes_token_model_and_dto_validation(monkeypatch):
    with isolated_client(monkeypatch) as client:
        for token_headers in ({}, {"X-RAG-Contract-Test": "wrong"}, HEADERS):
            response = client.post(
                PATH + "UnknownModel", content=b'{"a":1,"\\u0061":2}',
                headers={**token_headers, "Content-Type": "application/json"},
            )
            assert_failure(response, "VALIDATION_ERROR")
        response = client.post(PATH + "UnknownModel", content=b"x" * 1048577,
                               headers={"Content-Type": "application/json"})
        assert_failure(response, "REQUEST_BODY_LIMIT_EXCEEDED")


def test_real_http_h_error_dictionary(monkeypatch):
    cases = [
        (b'{"a":"\xff"}', {}, "VALIDATION_ERROR"),
        (b'{"a":"\\ud800"}', {}, "VALIDATION_ERROR"),
        (b'{"a":NaN}', {}, "VALIDATION_ERROR"),
        (b'{"a":1e309}', {}, "VALIDATION_ERROR"),
        (b"{}", {"Content-Type": "text/plain"}, "UNSUPPORTED_MEDIA_TYPE"),
        (b"{}", {"Content-Type": "application/json;charset=latin1"},
         "UNSUPPORTED_MEDIA_TYPE"),
        (b"{}", {"Content-Encoding": "gzip"}, "UNSUPPORTED_CONTENT_ENCODING"),
        (b"{}", {"Content-Length": "3"}, "VALIDATION_ERROR"),
        (b"{}", {"Content-Length": "1048577"}, "REQUEST_BODY_LIMIT_EXCEEDED"),
        (b"{}", {"X-Large": "x" * 16384}, "REQUEST_HEADERS_LIMIT_EXCEEDED"),
        (b'{"a":' * 8 + b"0" + b"}" * 8, {}, "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED"),
        (b'{"a":"' + b"x" * 65537 + b'"}', {}, "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED"),
    ]
    with isolated_client(monkeypatch) as client:
        for raw, extra, code in cases:
            headers = {**HEADERS, "Content-Type": "application/json", **extra}
            assert_failure(client.post(PATH + "RetrievalResponse", content=raw, headers=headers),
                           code)


def test_unknown_fields_versions_and_private_validation_inputs_are_finite(monkeypatch):
    with isolated_client(monkeypatch) as client:
        for name, patch in (
            ("RetrievalResponse", {"private": SECRET}),
            ("CompletedResponse", {"schema_version": "unknown.v9"}),
            ("CompletedResponse", {"schema_version": None}),
            ("CompletedResponse", {"request_id": SECRET}),
            ("CompletedResponse", {"summary": {"text": SECRET, "fact_ids": ["f99"]}}),
        ):
            payload = {**fixtures()[name], **patch}
            assert_failure(client.post(PATH + name, json=payload, headers=HEADERS),
                           "VALIDATION_ERROR")


def test_original_null_missing_and_nonbmp_values_survive_http(monkeypatch):
    with isolated_client(monkeypatch) as client:
        payload = fixtures()["CompletedResponse"]
        response = client.post(PATH + "CompletedResponse", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["facts"] == payload["facts"]
        assert response.json()["summary"] == payload["summary"]
        assert response.json()["facts"][0]["quantity"] is None
        del payload["facts"][0]["quantity"]
        assert_failure(client.post(PATH + "CompletedResponse", json=payload, headers=HEADERS),
                       "VALIDATION_ERROR")
        data = fixtures()["FailedResponse"]
        del data["operation_id"]
        absent = client.post(PATH + "FailedResponse", json=data, headers=HEADERS)
        assert "operation_id" not in absent.json()
        explicit = client.post(PATH + "FailedResponse", json={**data, "operation_id": None},
                               headers=HEADERS)
        assert explicit.json()["operation_id"] is None


def test_operation_failed_get_projection_stays_200_and_does_not_register_get(monkeypatch):
    with isolated_client(monkeypatch) as client:
        data = fixtures()["OperationResponse"]
        result = client.post(PATH + "OperationResponse", json=data, headers=HEADERS)
        assert result.status_code == 200
        assert result.json()["error"]["http_status"] == 504
        assert result.json()["operation_state"] == "failed"
        assert_failure(client.get("/operations/private-op"), "RESOURCE_UNAVAILABLE")
        assert_failure(client.get(PATH + "OperationResponse"), "METHOD_NOT_ALLOWED")


def test_every_attempt_gets_a_new_server_id_including_errors(monkeypatch):
    with isolated_client(monkeypatch) as client:
        ids = []
        for _ in range(3):
            result = client.post(PATH + "AcceptedResponse",
                                 json=fixtures()["AcceptedResponse"],
                                 headers={**HEADERS, "X-Request-ID": "client-attempt"})
            assert result.status_code == 202
            assert result.json()["request_id"] != "client-attempt"
            ids.append(result.json()["request_id"])
            rejected = client.post(PATH + "AcceptedResponse",
                                   json=fixtures()["AcceptedResponse"])
            ids.append(assert_failure(rejected, "AUTH_REQUIRED").request_id)
        assert len(ids) == len(set(ids))


def test_router_errors_health_and_conditionals_are_private(monkeypatch):
    with isolated_client(monkeypatch) as client:
        headers = {"If-None-Match": "*", "If-Modified-Since": "Sat, 17 Oct 2026 08:00:00 GMT"}
        for method, path, code in (
            ("get", "/unknown/" + SECRET, "RESOURCE_UNAVAILABLE"),
            ("get", PATH + "Usage", "METHOD_NOT_ALLOWED"),
            ("put", PATH + "Usage", "METHOD_NOT_ALLOWED"),
            ("post", PATH + "Usage/", "RESOURCE_UNAVAILABLE"),
        ):
            assert_failure(getattr(client, method)(path, headers=headers), code)
        alive = client.get("/health", headers=headers)
        assert alive.json() == {"status": "alive", "service": "rag-api", "check": "liveness"}
        assert_private(alive)


def test_all_safeerror_codes_keep_503_and_public_envelope(monkeypatch, caplog, capsys):
    with isolated_client(monkeypatch) as client:
        app = client.app

        @app.get("/_test_safe/{code}")
        def safe_error(code: str):
            raise SafeError(code, diagnostic_cause=RuntimeError(SECRET),
                            cleanup_errors=(RuntimeError(SECRET),))

        for code in MESSAGES:
            response = client.get("/_test_safe/" + code)
            assert_failure(response, code)
            assert response.status_code == 503
            assert response.json()["error"]["message"] == MESSAGES[code]
    assert SECRET not in caplog.text + "".join(capsys.readouterr())


def test_unexpected_framework_and_validation_exceptions_never_leak(monkeypatch, caplog, capsys):
    with isolated_client(monkeypatch) as client:
        @client.app.get("/_test_unexpected")
        def unexpected():
            raise RuntimeError(SECRET)

        @client.app.get("/_test_framework")
        def framework():
            raise HTTPException(status_code=404, detail=SECRET,
                                headers={"X-Secret": SECRET, "ETag": SECRET})

        @client.app.get("/_test_typed")
        def typed(count: int):
            return {"count": count}

        assert_failure(client.get("/_test_unexpected"), "INTERNAL_ERROR")
        response = client.get("/_test_framework")
        assert_failure(response, "RESOURCE_UNAVAILABLE")
        assert "x-secret" not in response.headers
        assert_failure(client.get("/_test_typed", params={"count": SECRET}),
                       "VALIDATION_ERROR")
        assert_failure(client.post(PATH + "RetrievalResponse", json={"private": SECRET},
                                   headers=HEADERS), "VALIDATION_ERROR")
    assert SECRET not in caplog.text + "".join(capsys.readouterr())


def test_private_validators_and_304_are_removed(monkeypatch):
    with isolated_client(monkeypatch) as client:
        @client.app.get("/_test_validators")
        def validators():
            return JSONResponse({"ok": True}, headers={
                "ETag": "private", "Last-Modified": NOW,
                "Cache-Control": "public,max-age=999", "Expires": NOW,
                "Age": "100", "X-Request-ID": "spoofed",
            })

        @client.app.get("/_test_304")
        def not_modified():
            return Response(status_code=304, headers={"ETag": "private"})

        response = client.get("/_test_validators")
        assert_private(response)
        assert "expires" not in response.headers and "age" not in response.headers
        assert_failure(client.get("/_test_304"), "INTERNAL_ERROR")


def test_no_unbounded_request_loader_or_provider_calls(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected unbounded input or external transport")

    monkeypatch.setattr(Request, "json", forbidden)
    monkeypatch.setattr(Request, "body", forbidden)
    monkeypatch.setattr("httpx.HTTPTransport.handle_request", forbidden)
    monkeypatch.setattr("httpx.AsyncHTTPTransport.handle_async_request", forbidden)
    with isolated_client(monkeypatch) as client:
        response = client.post(PATH + "RetrievalResponse",
                               json=fixtures()["RetrievalResponse"], headers=HEADERS)
        assert response.status_code == 200
        assert_private(response)


def test_openapi_is_model_derived_and_has_no_token_or_business_routes():
    schema = api.create_app(contract_test_token=SecretStr(TOKEN)).openapi()
    default_schema = api.create_app().openapi()
    assert schema == default_schema
    raw = json.dumps(schema)
    assert TOKEN not in raw and SECRET not in raw
    assert set(schema["paths"]) == {"/health", PATH + "{model_name}"}
    operation = schema["paths"][PATH + "{model_name}"]["post"]
    assert set(next(p for p in operation["parameters"] if p["name"] == "model_name")
               ["schema"]["enum"]) == RESPONSE_NAMES
    assert set(operation["responses"]) == {"200", "202", "default"}
    refs = operation["requestBody"]["content"]["application/json"]["schema"]["oneOf"]
    assert len(refs) == len(RESPONSE_NAMES)
    components = schema["components"]["schemas"]
    assert set(PUBLIC_MODELS) <= {item.get("title") for item in components.values()}
    for reference in refs:
        model_schema = components[reference["$ref"].split("/")[-1]]
        model = PUBLIC_MODELS[model_schema["title"]]
        expected = model.model_json_schema(ref_template="#/components/schemas/{model}")
        assert model_schema["additionalProperties"] is False
        assert set(model_schema["properties"]) == set(expected["properties"])
        assert model_schema.get("required", []) == expected.get("required", [])

    def assert_refs_exist(value):
        if isinstance(value, dict):
            if "$ref" in value:
                assert value["$ref"].startswith("#/components/schemas/")
                assert value["$ref"].split("/")[-1] in components
            for nested in value.values():
                assert_refs_exist(nested)
        elif isinstance(value, list):
            for nested in value:
                assert_refs_exist(nested)

    assert_refs_exist(schema)


def test_asgi_small_chunks_and_disconnect_are_bounded(monkeypatch, caplog):
    app = api.create_app(Settings(), contract_test_token=SecretStr(TOKEN))

    async def attempt(messages):
        captured = []
        pending = iter(messages)

        async def receive():
            return next(pending)

        async def send(message):
            captured.append(message)

        path = PATH + "CompletedResponse"
        await app({
            "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
            "method": "POST", "scheme": "http", "root_path": "",
            "path": path, "raw_path": path.encode(), "query_string": b"",
            "server": ("testserver", 80), "client": ("fixture", 1),
            "headers": [(b"content-type", b"application/json"),
                        (b"x-rag-contract-test", TOKEN.encode())],
        }, receive, send)
        start = next(message for message in captured if message["type"] == "http.response.start")
        body = b"".join(message.get("body", b"") for message in captured
                        if message["type"] == "http.response.body")
        return start, json.loads(body)

    raw = json.dumps(fixtures()["CompletedResponse"], ensure_ascii=False).encode()
    start, body = asyncio.run(attempt([
        {"type": "http.request", "body": raw[index:index + 1],
         "more_body": index + 1 < len(raw)} for index in range(len(raw))
    ]))
    assert start["status"] == 200
    assert body["facts"][0]["text"] == "\U0001f680"
    assert dict(start["headers"])[b"cache-control"] == b"no-store"
    start, body = asyncio.run(attempt([
        {"type": "http.request", "body": b'{"private":"' + SECRET.encode(),
         "more_body": True},
        {"type": "http.disconnect"},
    ]))
    assert start["status"] == 400
    assert body["error"]["code"] == "REQUEST_STREAM_ERROR"
    assert "operation_id" not in body
    assert SECRET not in json.dumps(body) + caplog.text
