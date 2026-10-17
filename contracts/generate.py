#!/usr/bin/env python3
"""Generate public contract artifacts from the backend source of truth.

Only PUBLIC_MODELS, create_app().openapi() and the locked backend environment are
used. No business type, field, enum or error policy is hand-written here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import re
import sys
from importlib import metadata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = Path(__file__).resolve().parent
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

REF_TEMPLATE = "#/$defs/{model}"
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

SOURCE_FILES = (
    "backend/src/rag_app/contracts/public.py",
    "backend/src/rag_app/contracts/scalars.py",
    "backend/src/rag_app/contracts/errors.py",
    "backend/src/rag_app/entrypoints/api.py",
    "backend/src/rag_app/entrypoints/contract_probe.py",
    "backend/src/rag_app/entrypoints/json_guard.py",
    "backend/src/rag_app/bootstrap/config.py",
    "backend/src/rag_app/bootstrap/runtime.py",
    "backend/src/rag_app/application/health.py",
)

ENUM_MODES = ("validation", "serialization")

CAPABILITY_MODELS: dict[str, tuple[str, ...]] = {
    "answer.v1": (
        "AnswerPayload",
        "CompletedResponse",
        "ConflictSides",
        "EvidenceBlock",
        "Fact",
        "Gap",
        "Quantity",
        "Summary",
    ),
    "retrieval.v1": (
        "EvidenceBlock",
        "RetrievalPayload",
        "RetrievalResponse",
    ),
    "operation.v1": (
        "AcceptedResponse",
        "ErrorDetails",
        "FailedResponse",
        "Money",
        "OperationResponse",
        "PublicError",
        "Usage",
    ),
}

NOT_GENERATED = {
    "comparison.v1": (
        "PUBLIC_MODELS has no comparison.v1 response or payload model; "
        "no hand-written substitute is generated."
    ),
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False,
    ) + "\n"


def _bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _source_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in SOURCE_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"contract source file is missing: {relative}")
        result[relative] = _sha256(path.read_bytes())
    return result


def _package_versions() -> dict[str, str]:
    result: dict[str, str] = {}
    for name in ("fastapi", "pydantic"):
        try:
            result[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            raise SystemExit(f"required backend package is not installed: {name}")
    return result


def _raw_schema(model: type[Any], mode: str) -> dict[str, Any]:
    schema = model.model_json_schema(mode=mode, ref_template=REF_TEMPLATE)
    definitions = schema.pop("$defs", {})
    result: dict[str, Any] = {"$schema": JSON_SCHEMA_DIALECT, **schema}
    if definitions:
        result["$defs"] = definitions
    return result


def _raw_enum_schema(enum: type[Any], mode: str) -> dict[str, Any]:
    from pydantic import TypeAdapter

    # TypeAdapter exports the existing backend enum; values are never retyped.
    schema = TypeAdapter(enum).json_schema(mode=mode)
    return {"$schema": JSON_SCHEMA_DIALECT, **schema}


def _core(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value for key, value in schema.items()
        if key not in {"$schema", "$id"}
    }


def _ts_identifier(name: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_$]", "_", name)
    if not result:
        result = "_"
    if result[0].isdigit():
        result = "_" + result
    return result


def _ts_key(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name):
        return name
    return json.dumps(name, ensure_ascii=False)


def _ts_literal(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise ValueError("unsupported TS literal")


def _ts_expr(schema: dict[str, Any], level: int = 0) -> str:
    if not isinstance(schema, dict):
        return "unknown"
    if "$ref" in schema:
        return _ts_identifier(str(schema["$ref"]).rsplit("/", 1)[-1])
    if "const" in schema:
        return _ts_literal(schema["const"])
    if "enum" in schema:
        return " | ".join(_ts_literal(item) for item in schema["enum"])
    for key in ("anyOf", "oneOf"):
        if key in schema:
            return " | ".join(_ts_expr(item, level) for item in schema[key])
    if "allOf" in schema:
        return " & ".join(_ts_expr(item, level) for item in schema["allOf"])

    kind = schema.get("type")
    if isinstance(kind, list):
        return " | ".join(
            _ts_expr({**schema, "type": item}, level) for item in kind
        )
    if kind == "null":
        return "null"
    if kind == "string":
        return "string"
    if kind in {"integer", "number"}:
        return "number"
    if kind == "boolean":
        return "boolean"
    if kind == "array":
        return f"Array<{_ts_expr(schema.get('items', {}), level)}>"
    if kind == "object" or "properties" in schema:
        properties = schema.get("properties")
        if not properties:
            additional = schema.get("additionalProperties", False)
            if additional is False:
                return "Record<string, never>"
            if isinstance(additional, dict):
                return f"Record<string, {_ts_expr(additional, level)}>"
            return "Record<string, unknown>"
        required = set(schema.get("required", []))
        pad = "  " * level
        lines = ["{"]
        for name in sorted(properties):
            optional = "" if name in required else "?"
            lines.append(
                f"{pad}  {_ts_key(name)}{optional}: "
                f"{_ts_expr(properties[name], level + 1)};"
            )
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    return "unknown"


def _collect_named(schemas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    named: dict[str, dict[str, Any]] = {}
    roots: dict[str, dict[str, Any]] = {}
    for name, raw in schemas.items():
        body = _core(copy.deepcopy(raw))
        definitions = body.pop("$defs", {})
        roots[name] = body
        for definition_name, definition in definitions.items():
            normalized = _core(definition)
            existing = named.get(definition_name)
            if existing is not None and canonical_json(existing) != canonical_json(normalized):
                raise ValueError(f"conflicting schema definition: {definition_name}")
            named[definition_name] = normalized
    for name, body in roots.items():
        existing = named.get(name)
        if existing is not None and canonical_json(existing) != canonical_json(body):
            raise ValueError(f"conflicting root schema definition: {name}")
        named[name] = body
    return named


def _render_typescript(
    schemas: dict[str, dict[str, Any]], *, header: str,
) -> str:
    named = _collect_named(schemas)
    identifiers: dict[str, str] = {}
    for name in named:
        identifier = _ts_identifier(name)
        if identifier in identifiers.values():
            raise ValueError(f"TypeScript identifier collision: {name}")
        identifiers[name] = identifier

    lines = [header, ""]
    for name in sorted(named):
        schema = named[name]
        identifier = identifiers[name]
        if (
            schema.get("type") == "object"
            and "properties" in schema
            and not any(key in schema for key in ("anyOf", "oneOf", "allOf"))
        ):
            required = set(schema.get("required", []))
            lines.append(f"export interface {identifier} {{")
            for property_name in sorted(schema["properties"]):
                optional = "" if property_name in required else "?"
                lines.append(
                    f"  {_ts_key(property_name)}{optional}: "
                    f"{_ts_expr(schema['properties'][property_name], 1)};"
                )
            lines.append("}")
        else:
            lines.append(f"export type {identifier} = {_ts_expr(schema)};")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_artifacts() -> dict[str, bytes]:
    from rag_app.contracts.public import PUBLIC_ENUMS, PUBLIC_MODELS

    missing = sorted({
        name
        for names in CAPABILITY_MODELS.values()
        for name in names
        if name not in PUBLIC_MODELS
    })
    if missing:
        raise SystemExit(
            "PUBLIC_MODELS is missing required models: " + ", ".join(missing)
        )
    expected_enums = {"Status", "Outcome", "OperationState", "JobState", "RetryMode"}
    missing_enums = sorted(expected_enums - set(PUBLIC_ENUMS))
    if missing_enums:
        raise SystemExit(
            "PUBLIC_ENUMS is missing required enums: " + ", ".join(missing_enums)
        )

    schemas: dict[tuple[str, str, str], dict[str, Any]] = {}
    enum_schemas: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, bytes] = {}
    for capability, names in CAPABILITY_MODELS.items():
        for name in names:
            model = PUBLIC_MODELS[name]
            for mode in ("validation", "serialization"):
                raw = _raw_schema(model, mode)
                schema = copy.deepcopy(raw)
                schema["$id"] = (
                    f"https://rag.local/contracts/schemas/{capability}/"
                    f"{name}.{mode}.schema.json"
                )
                relative = (
                    f"schemas/{capability}/{name}.{mode}.schema.json"
                )
                artifacts[relative] = _bytes(schema)
                schemas[(capability, name, mode)] = raw

    for name, enum in sorted(PUBLIC_ENUMS.items()):
        for mode in ENUM_MODES:
            raw = _raw_enum_schema(enum, mode)
            schema = copy.deepcopy(raw)
            schema["$id"] = (
                f"https://rag.local/contracts/schemas/enums/"
                f"{name}.{mode}.schema.json"
            )
            artifacts[f"schemas/enums/{name}.{mode}.schema.json"] = _bytes(schema)
            enum_schemas.setdefault(name, {})[mode] = raw
            if not isinstance(raw.get("enum"), list) or raw.get("type") != "string":
                raise SystemExit(
                    f"PUBLIC_ENUMS export did not produce a string enum: {name}"
                )
            if raw["enum"] != [item.value for item in enum]:
                raise SystemExit(
                    f"PUBLIC_ENUMS export does not match backend order: {name}"
                )

    capabilities: dict[str, Any] = {
        "schema_version": "contracts-capabilities.v1",
        "capabilities": {
            capability: {
                "models": sorted(names),
                "validation_schemas": [
                    f"schemas/{capability}/{name}.validation.schema.json"
                    for name in sorted(names)
                ],
                "serialization_schemas": [
                    f"schemas/{capability}/{name}.serialization.schema.json"
                    for name in sorted(names)
                ],
            }
            for capability, names in CAPABILITY_MODELS.items()
        },
        "enums": {
            name: {
                "values": [item.value for item in PUBLIC_ENUMS[name]],
                "validation_schema": f"schemas/enums/{name}.validation.schema.json",
                "serialization_schema": f"schemas/enums/{name}.serialization.schema.json",
            }
            for name in sorted(PUBLIC_ENUMS)
        },
        "not_generated": NOT_GENERATED,
    }
    artifacts["schemas/capabilities.json"] = _bytes(capabilities)

    serialization = {
        name: schemas[(capability, name, "serialization")]
        for capability, names in CAPABILITY_MODELS.items()
        for name in names
    }
    validation = {
        name: schemas[(capability, name, "validation")]
        for capability, names in CAPABILITY_MODELS.items()
        for name in names
    }
    for name, modes in enum_schemas.items():
        serialization[name] = modes["serialization"]
        validation[name] = modes["validation"]
    artifacts["typescript/contracts.ts"] = _render_typescript(
        serialization,
        header=(
            "// Generated by contracts/generate.py. Do not edit by hand.\n"
            "// Source: rag_app.contracts.public.PUBLIC_MODELS, "
            "serialization schemas.\n"
        ),
    ).encode("utf-8")
    artifacts["typescript/contracts.input.ts"] = _render_typescript(
        validation,
        header=(
            "// Generated by contracts/generate.py. Do not edit by hand.\n"
            "// Source: rag_app.contracts.public.PUBLIC_MODELS, "
            "validation schemas.\n"
        ),
    ).encode("utf-8")

    from rag_app.entrypoints.api import create_app

    openapi = create_app().openapi()
    artifacts["openapi.json"] = _bytes(openapi)

    manifest = {
        "schema_version": "contracts-export.v1",
        "generator": {
            "path": "generate.py",
            "sha256": _sha256(Path(__file__).read_bytes()),
        },
        "runtime": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
        },
        "packages": _package_versions(),
        "openapi": {
            "version": openapi.get("openapi"),
            "title": openapi.get("info", {}).get("title"),
            "api_version": openapi.get("info", {}).get("version"),
        },
        "models": sorted(PUBLIC_MODELS),
        "enums": {
            name: [item.value for item in enum]
            for name, enum in sorted(PUBLIC_ENUMS.items())
        },
        "capabilities": {
            name: sorted(models) for name, models in CAPABILITY_MODELS.items()
        },
        "not_generated": NOT_GENERATED,
        "source_files": _source_hashes(),
        "artifacts": {
            relative: _sha256(data)
            for relative, data in sorted(artifacts.items())
        },
    }
    artifacts["manifest.json"] = _bytes(manifest)
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="Verify generated files match the backend source; do not write.",
    )
    arguments = parser.parse_args()
    artifacts = build_artifacts()

    if arguments.check:
        failures: list[str] = []
        for relative in sorted(artifacts):
            path = CONTRACTS / relative
            if not path.exists():
                failures.append(f"missing: {relative}")
            elif path.read_bytes() != artifacts[relative]:
                failures.append(f"diff: {relative}")
        for directory in ("schemas", "typescript"):
            root = CONTRACTS / directory
            if not root.exists():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(CONTRACTS).as_posix()
                if relative not in artifacts:
                    failures.append(f"unexpected: {relative}")
        if failures:
            print("contracts check FAILED")
            for failure in failures:
                print(f"  {failure}")
            return 1
        print(f"contracts check OK ({len(artifacts)} files)")
        return 0

    for relative in sorted(artifacts):
        path = CONTRACTS / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(artifacts[relative])
    print(f"generated {len(artifacts)} contract files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
