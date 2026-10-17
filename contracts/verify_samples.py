#!/usr/bin/env python3
"""Run C1/C2/H boundary samples against backend models and the bounded JSON guard.

No business type is defined here. Accepted/rejected samples are checked against
PUBLIC_MODELS, scalars.py and entrypoints/json_guard.py from the backend.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = Path(__file__).resolve().parent
SAMPLES = CONTRACTS / "samples"
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

REQUEST_ID = re.compile(r"^[a-f0-9]{32}$")


def _read(path: str) -> bytes:
    return (SAMPLES / path).read_bytes()


def _request_bytes(request: dict[str, Any]) -> bytes:
    if "file" in request:
        return _read(request["file"])
    if "raw_base64" in request:
        return base64.b64decode(request["raw_base64"])
    if "raw_generate" in request:
        generated = request["raw_generate"]
        prefix = generated["prefix"].encode("utf-8")
        pad = generated.get("pad", " ").encode("utf-8")
        total = int(generated["total_bytes"])
        if len(prefix) > total:
            raise ValueError("raw_generate prefix exceeds total_bytes")
        return prefix + pad * (total - len(prefix))
    raise ValueError("request has no body source")


def _sample_bytes(case: dict[str, Any]) -> bytes:
    if "file" in case:
        return _read(case["file"])
    if "raw_base64" in case:
        return base64.b64decode(case["raw_base64"])
    if "raw_generate" in case:
        generated = case["raw_generate"]
        prefix = generated["prefix"].encode("utf-8")
        pad = generated.get("pad", " ").encode("utf-8")
        total = int(generated["total_bytes"])
        if len(prefix) > total:
            raise ValueError("raw_generate prefix exceeds total_bytes")
        return prefix + pad * (total - len(prefix))
    raise ValueError("sample has no body source")


def _forbidden_check(case: dict[str, Any], text: str) -> None:
    for forbidden in case.get("forbidden_substrings", []):
        if forbidden in text:
            raise AssertionError(f"forbidden substring leaked: {forbidden!r}")


def _lookup(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(path)
            current = current[part]
        elif isinstance(current, list):
            index = int(part)
            if not 0 <= index < len(current):
                raise KeyError(path)
            current = current[index]
        else:
            raise KeyError(path)
    return current


def _expected_error(case: dict[str, Any], error: BaseException) -> None:
    expected = case.get("error")
    if expected is None:
        return
    if expected == "ValidationError":
        from pydantic import ValidationError
        if not isinstance(error, ValidationError):
            raise AssertionError(f"expected ValidationError, got {type(error).__name__}")
        return
    if expected == "ValueError":
        if not isinstance(error, ValueError):
            raise AssertionError(f"expected ValueError, got {type(error).__name__}")
        return
    from rag_app.entrypoints.json_guard import BoundedJsonError
    if not isinstance(error, BoundedJsonError):
        raise AssertionError(f"expected BoundedJsonError, got {type(error).__name__}")
    if error.code != expected:
        raise AssertionError(f"expected {expected}, got {error.code}")


def _accept(case: dict[str, Any]) -> None:
    _forbidden_check(case, "")


def _reject(case: dict[str, Any], error: BaseException) -> None:
    _expected_error(case, error)
    rendered = " ".join([
        str(error), repr(error), repr(vars(error)) if hasattr(error, "__dict__") else "",
    ])
    _forbidden_check(case, rendered)
    needle = case.get("error_contains")
    if needle is not None and needle not in rendered:
        raise AssertionError(
            f"rejection did not match {needle!r}: {rendered[:500]}"
        )


def _run_model(case: dict[str, Any]) -> None:
    from rag_app.contracts.public import PUBLIC_MODELS

    model = PUBLIC_MODELS[case["model"]]
    raw = _sample_bytes(case)
    if case["operation"] == "model_validate_json":
        try:
            dto = model.model_validate_json(raw)
        except BaseException as error:
            if case["expect"] != "reject":
                raise
            _reject(case, error)
            return
        if case["expect"] != "accept":
            raise AssertionError("sample was accepted but expected reject")
        wire = dto.model_dump(mode="json", exclude_unset=True)
        for path, expected in case.get("expected_fields", {}).items():
            try:
                actual = _lookup(wire, path)
            except (KeyError, ValueError):
                raise AssertionError(f"serialized field is missing: {path}") from None
            if actual != expected:
                raise AssertionError(
                    f"serialized field {path} = {actual!r} != {expected!r}"
                )
        for path in case.get("serialized_absent_fields", []):
            parent, _, last = path.rpartition(".")
            try:
                container = wire if not parent else _lookup(wire, parent)
            except (KeyError, ValueError):
                continue
            if isinstance(container, dict) and last in container:
                raise AssertionError(f"serialized field must be absent: {path}")
        _accept(case)
        return
    raise ValueError(f"unsupported model operation: {case['operation']}")


def _run_scalar(case: dict[str, Any]) -> None:
    from rag_app.contracts.scalars import scalar_length, scalar_slice

    value = json.loads(_read(case["file"]).decode("utf-8"))
    if case["operation"] == "scalar_length":
        actual = scalar_length(value["text"])
        if actual != value["expected_length"]:
            raise AssertionError(
                f"scalar length {actual} != {value['expected_length']}"
            )
    elif case["operation"] == "scalar_slice":
        actual = scalar_slice(value["text"], value["start"], value["end"])
        if actual != value["expected_slice"]:
            raise AssertionError(
                f"scalar slice {actual!r} != {value['expected_slice']!r}"
            )
    else:
        raise ValueError(f"unsupported scalar operation: {case['operation']}")
    _accept(case)


def _run_json(case: dict[str, Any]) -> None:
    from rag_app.contracts.scalars import stable_json_bytes, strict_json_loads
    from rag_app.entrypoints.json_guard import JsonLimits, parse_json_bytes

    raw = _sample_bytes(case)
    limits = JsonLimits(**case["limits"]) if "limits" in case else JsonLimits()
    if case["operation"] == "stable_json_bytes":
        # The sample is a JSON object dumped with stable_json_bytes, not text.
        value = strict_json_loads(raw)
        actual = stable_json_bytes(value).decode("utf-8")
        if actual != case["expected_text"]:
            raise AssertionError(
                f"stable JSON {actual!r} != {case['expected_text']!r}"
            )
        _accept(case)
        return
    try:
        if case["operation"] == "strict_json_loads":
            strict_json_loads(raw)
        elif case["operation"] == "parse_json_bytes":
            parse_json_bytes(raw, limits)
        else:
            raise ValueError(f"unsupported JSON operation: {case['operation']}")
    except BaseException as error:
        if case["expect"] != "reject":
            raise
        _reject(case, error)
        return
    if case["expect"] != "accept":
        raise AssertionError("sample was accepted but expected reject")
    _accept(case)


def _run_enum_set(case: dict[str, Any]) -> None:
    from pydantic import TypeAdapter, ValidationError

    from rag_app.contracts.public import PUBLIC_ENUMS

    field_enums = {
        "status": "Status",
        "outcome": "Outcome",
        "operation_state": "OperationState",
        "job_state": "JobState",
        "retry_mode": "RetryMode",
    }
    value = json.loads(_sample_bytes(case).decode("utf-8"))
    if set(value) != set(field_enums):
        raise AssertionError("enum sample must contain the five separate state fields")
    if set(field_enums.values()) - set(PUBLIC_ENUMS):
        raise AssertionError("enum sample references a missing PUBLIC_ENUMS entry")
    invalid_fields = set(case.get("invalid_fields", ()))
    if not invalid_fields <= set(field_enums):
        raise AssertionError("invalid_fields must name sample fields")
    rejected: list[str] = []
    rendered: list[str] = []
    for field, enum_name in field_enums.items():
        adapter = TypeAdapter(PUBLIC_ENUMS[enum_name])
        try:
            adapter.validate_python(value[field])
        except ValidationError as error:
            rejected.append(field)
            rendered.append(f"{field}: {error!s} {error!r}")
        else:
            if field in invalid_fields:
                raise AssertionError(
                    f"{field} unexpectedly accepted {value[field]!r}"
                )
    _forbidden_check(case, " ".join(rendered))
    if case["expect"] == "accept":
        if rejected:
            raise AssertionError(f"valid enum sample rejected fields: {rejected}")
        if invalid_fields:
            raise AssertionError("accept sample must not declare invalid_fields")
        _accept(case)
        return
    if case["expect"] != "reject":
        raise ValueError(f"unsupported enum expectation: {case['expect']}")
    if not rejected:
        raise AssertionError("reject sample accepted every enum value")
    if invalid_fields and set(rejected) != invalid_fields:
        raise AssertionError(
            f"rejected fields {sorted(rejected)} != declared "
            f"{sorted(invalid_fields)}"
        )
    if case.get("error", "ValidationError") != "ValidationError":
        raise AssertionError(
            f"enum rejection must declare ValidationError, got {case['error']!r}"
        )


async def _run_http(case: dict[str, Any], token: str) -> None:
    import httpx
    from pydantic import SecretStr

    from rag_app.bootstrap.config import Settings
    from rag_app.contracts.public import FailedResponse, PUBLIC_MODELS, PublicError
    from rag_app.entrypoints.api import create_app

    request = case["request"]
    headers = dict(request.get("headers", {}))
    for name, size in request.get("headers_generate", {}).items():
        headers[name] = "x" * int(size)
    body = _request_bytes(request)
    response_model = case.get("response_model")
    if response_model not in PUBLIC_MODELS:
        raise ValueError(f"unknown response_model: {response_model!r}")
    expected_error = case.get("expected_error")
    attempts = int(case.get("attempts", 1))
    if not 1 <= attempts <= 3:
        raise ValueError("HTTP attempts must be between 1 and 3")
    app = create_app(
        Settings(environment="development"), contract_test_token=SecretStr(token),
    )
    transport = httpx.ASGITransport(app=app)
    request_ids: list[str] = []
    async with httpx.AsyncClient(
        transport=transport, base_url="http://contracts.local",
    ) as client:
        for _ in range(attempts):
            response = await client.request(
                request.get("method", "POST"), request["path"],
                content=body, headers=headers,
            )
            if response.status_code != case["expected_status"]:
                raise AssertionError(
                    f"HTTP {response.status_code} != {case['expected_status']}"
                )
            if response.status_code == 304:
                raise AssertionError("private HTTP response must not be 304")
            content_type = response.headers.get(
                "content-type", "",
            ).split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                raise AssertionError(
                    f"private response content-type {content_type!r} is not JSON"
                )
            if response.headers.get("cache-control") != "no-store":
                raise AssertionError(
                    "private response is missing Cache-Control: no-store"
                )
            if "etag" in response.headers or "last-modified" in response.headers:
                raise AssertionError("private response exposed a cache validator")
            try:
                payload: Any = response.json()
            except ValueError:
                raise AssertionError(
                    "private HTTP response body is not JSON"
                ) from None
            if not isinstance(payload, dict):
                raise AssertionError(
                    "private HTTP response body is not a JSON object"
                )
            for field in ("schema_version", "request_id", "status"):
                if field not in payload:
                    raise AssertionError(f"private HTTP response lacks {field}")
            header_id = response.headers.get("x-request-id")
            if not header_id or not REQUEST_ID.fullmatch(header_id):
                raise AssertionError(
                    "X-Request-ID is missing or not a server 32-hex ID"
                )
            if payload["request_id"] != header_id:
                raise AssertionError(
                    "response body request_id differs from X-Request-ID"
                )
            dto = PUBLIC_MODELS[response_model].model_validate(payload)
            request_ids.append(header_id)
            if expected_error is not None:
                expected = PublicError.from_code(expected_error)
                if not isinstance(dto, FailedResponse):
                    raise AssertionError(
                        "error sample did not produce FailedResponse"
                    )
                if dto.error != expected:
                    raise AssertionError(
                        f"error policy mismatch: {dto.error!r} != {expected!r}"
                    )
                if dto.error.http_status != response.status_code:
                    raise AssertionError(
                        "error.http_status differs from the HTTP status"
                    )
            elif isinstance(dto, FailedResponse):
                raise AssertionError(
                    "accepted HTTP sample returned FailedResponse"
                )
            _forbidden_check(case, response.text)
            for field in case.get("absent_fields", []):
                if field in payload:
                    raise AssertionError(f"field must be absent: {field}")
    if len(set(request_ids)) != len(request_ids):
        raise AssertionError("different HTTP attempts reused X-Request-ID")


async def _run_case(
    case: dict[str, Any], token: str, *, run_control: bool = True,
) -> tuple[str, str]:
    if run_control and "control" in case and not case.get("_is_control"):
        control = {
            **case["control"],
            "expect": "accept",
            "_is_control": True,
            "id": case["id"] + ".control",
        }
        outcome, detail = await _run_case(control, token, run_control=False)
        if outcome != "passed":
            raise AssertionError(
                f"control {control['id']} was not accepted: {outcome} {detail}"
            )
    operation = case["operation"]
    if operation == "blocked":
        return "blocked", case.get("reason", "blocked")
    if operation == "note":
        return "note", case.get("text", "")
    if operation == "http_probe":
        await _run_http(case, token)
        return "passed", ""
    if operation in {"model_validate_json"}:
        _run_model(case)
        return "passed", ""
    if operation in {"scalar_length", "scalar_slice"}:
        _run_scalar(case)
        return "passed", ""
    if operation in {"strict_json_loads", "parse_json_bytes", "stable_json_bytes"}:
        _run_json(case)
        return "passed", ""
    if operation == "enum_set":
        _run_enum_set(case)
        return "passed", ""
    raise ValueError(f"unsupported operation: {operation}")


async def _main_async(arguments: argparse.Namespace) -> int:
    manifest = json.loads((SAMPLES / "manifest.json").read_text(encoding="utf-8"))
    for name, text in manifest.get("boundaries", {}).items():
        print(f"boundary {name}: {text}")

    passed = failed = blocked = noted = 0
    for case in manifest["cases"]:
        try:
            outcome, detail = await _run_case(case, arguments.token)
        except BaseException as error:
            failed += 1
            print(f"FAIL {case['id']}: {type(error).__name__}: {error}")
            continue
        if outcome == "passed":
            passed += 1
            print(f"PASS {case['id']}")
        elif outcome == "blocked":
            blocked += 1
            print(f"BLOCKED {case['id']}: {detail}")
        elif outcome == "note":
            noted += 1
            print(f"NOTE {case['id']}: {detail}")

    print(
        f"RESULT passed={passed} failed={failed} "
        f"blocked={blocked} notes={noted}"
    )
    if failed:
        return 1
    if blocked:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--token", default="contracts-samples-token",
        help="Explicit in-memory token for the isolated HTTP probe.",
    )
    return asyncio.run(_main_async(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
