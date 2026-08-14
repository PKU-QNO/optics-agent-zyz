#!/usr/bin/env python3
"""Validate the Grahn formalization YAML against its v4 JSON Schema."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml


REPRODUCTION_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPRODUCTION_DIR / "formalization" / "grahn.yaml"
DEFAULT_SCHEMA = Path(__file__).resolve().parent / "schemas" / "grahn_schema.json"


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _json_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _failure_payload(
    *,
    spec_sha256: str | None,
    schema_sha256: str | None,
    version: Any,
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "spec_sha256": spec_sha256,
        "schema_sha256": schema_sha256,
        "version": version,
        "errors": errors,
    }


def validate(spec_path: Path, schema_path: Path) -> tuple[int, dict[str, Any]]:
    """Return an exit code and a JSON-serializable validation receipt."""

    spec_sha256: str | None = None
    schema_sha256: str | None = None
    version: Any = None

    try:
        spec_bytes = spec_path.read_bytes()
        spec_sha256 = _sha256(spec_bytes)
    except OSError as exc:
        return 2, _failure_payload(
            spec_sha256=None,
            schema_sha256=None,
            version=None,
            errors=[{"path": "$", "message": f"cannot read spec: {exc}"}],
        )

    try:
        schema_bytes = schema_path.read_bytes()
        schema_sha256 = _sha256(schema_bytes)
    except OSError as exc:
        return 2, _failure_payload(
            spec_sha256=spec_sha256,
            schema_sha256=None,
            version=None,
            errors=[{"path": "$", "message": f"cannot read schema: {exc}"}],
        )

    try:
        spec = yaml.safe_load(spec_bytes.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        return 2, _failure_payload(
            spec_sha256=spec_sha256,
            schema_sha256=schema_sha256,
            version=None,
            errors=[{"path": "$", "message": f"invalid YAML: {exc}"}],
        )

    if isinstance(spec, dict):
        meta = spec.get("meta")
        if isinstance(meta, dict):
            version = meta.get("version")

    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
    except (UnicodeDecodeError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        return 2, _failure_payload(
            spec_sha256=spec_sha256,
            schema_sha256=schema_sha256,
            version=version,
            errors=[{"path": "$", "message": f"invalid JSON Schema: {exc}"}],
        )

    validator = validator_class(schema)
    failures = sorted(
        validator.iter_errors(spec),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    errors = [
        {"path": _json_path(error.absolute_path), "message": error.message}
        for error in failures
    ]
    if errors:
        return 1, _failure_payload(
            spec_sha256=spec_sha256,
            schema_sha256=schema_sha256,
            version=version,
            errors=errors,
        )

    return 0, {
        "status": "PASS",
        "spec_sha256": spec_sha256,
        "schema_sha256": schema_sha256,
        "version": version,
        "errors": [],
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    exit_code, receipt = validate(args.spec.resolve(), args.schema.resolve())
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
