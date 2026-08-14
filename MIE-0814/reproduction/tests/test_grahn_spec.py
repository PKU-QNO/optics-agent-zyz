"""Contract tests for the Grahn v4 formalization schema."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml


REPRODUCTION_DIR = Path(__file__).resolve().parent.parent
SPEC_PATH = REPRODUCTION_DIR / "formalization" / "grahn.yaml"
VALIDATOR_PATH = REPRODUCTION_DIR / "code" / "validate_grahn_spec.py"


def _run_validator(spec_path: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
    command = [sys.executable, str(VALIDATOR_PATH)]
    if spec_path is not None:
        command.extend(["--spec", str(spec_path)])
    completed = subprocess.run(
        command,
        cwd=REPRODUCTION_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.stdout, completed.stderr
    return completed, json.loads(completed.stdout)


def _mutated_spec(tmp_path: Path, mutate) -> Path:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    mutate(spec)
    path = tmp_path / "grahn-mutated.yaml"
    path.write_text(
        yaml.safe_dump(spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def test_current_v4_spec_passes_and_emits_hash_receipt():
    completed, receipt = _run_validator()

    assert completed.returncode == 0, receipt
    assert receipt["status"] == "PASS"
    assert receipt["version"] == "v4 (2026-08-10, review 12 revised)"
    assert receipt["spec_sha256"] == hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()
    assert len(receipt["schema_sha256"]) == 64
    assert receipt["errors"] == []


def test_missing_required_acceptance_path_fails(tmp_path):
    path = _mutated_spec(
        tmp_path,
        lambda spec: spec["verification"]["acceptance_contract"].pop("path_B_vs_mie"),
    )
    completed, receipt = _run_validator(path)

    assert completed.returncode != 0
    assert receipt["status"] == "FAIL"
    assert any("path_B_vs_mie" in error["message"] for error in receipt["errors"])


def test_meta_version_drift_fails(tmp_path):
    def mutate(spec):
        spec["meta"]["version"] = "v5 (unreviewed drift)"

    path = _mutated_spec(tmp_path, mutate)
    completed, receipt = _run_validator(path)

    assert completed.returncode != 0
    assert receipt["status"] == "FAIL"
    assert receipt["version"] == "v5 (unreviewed drift)"
    assert any(error["path"] == "$.meta.version" for error in receipt["errors"])


def test_numeric_threshold_changed_to_string_fails(tmp_path):
    def mutate(spec):
        gate = spec["verification"]["acceptance_contract"]["path_A_vs_table1"]
        gate["gate_subdomain"]["threshold"] = "0.01"

    path = _mutated_spec(tmp_path, mutate)
    completed, receipt = _run_validator(path)

    assert completed.returncode != 0
    assert receipt["status"] == "FAIL"
    assert any(
        error["path"].endswith("gate_subdomain.threshold")
        and "number" in error["message"]
        for error in receipt["errors"]
    )


def test_legacy_tolerances_are_numbers_and_string_regression_fails(tmp_path):
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    per_m = spec["verification"]["acceptance_contract"]["path_B_vs_mie"]["per_m_tolerances"]
    assert isinstance(per_m["EQ_MQ"]["absolute_floor"], float)
    assert isinstance(per_m["zero_targets"]["absolute_zero"], float)

    def mutate(candidate):
        tolerances = candidate["verification"]["acceptance_contract"]["path_B_vs_mie"]["per_m_tolerances"]
        tolerances["EQ_MQ"]["absolute_floor"] = "1e-6"

    path = _mutated_spec(tmp_path, mutate)
    completed, receipt = _run_validator(path)
    assert completed.returncode != 0
    assert any(
        error["path"].endswith("EQ_MQ.absolute_floor")
        and "number" in error["message"]
        for error in receipt["errors"]
    )


def test_d1_mapping_contract_drift_fails(tmp_path):
    def mutate(spec):
        contract = spec["equations"]["mapping_E2"]["input_contract"]
        contract["allowed_api_values"] = ["stf", "qe"]

    path = _mutated_spec(tmp_path, mutate)
    completed, receipt = _run_validator(path)
    assert completed.returncode != 0
    assert receipt["status"] == "FAIL"
    assert any("allowed_api_values" in error["path"] for error in receipt["errors"])
