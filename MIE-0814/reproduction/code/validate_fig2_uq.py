# -*- coding: utf-8 -*-
"""Validate B3 receipts and record the real repository-wide pytest exit code."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from run_fig2_uq import ROOT, sha256, verify_recorded_hashes


OUT = ROOT / "codex-prompts" / "out" / "B3-validation-receipt.json"
SUMMARY = ROOT / "data" / "fig2_uq_summary.json"
ARTIFACTS = [
    ROOT / "code" / "run_fig2_uq.py",
    ROOT / "data" / "fig2_uq_channel_results.csv",
    ROOT / "data" / "fig2_uq_pointwise.csv",
    ROOT / "data" / "fig2_uq_weighting_sensitivity.csv",
    SUMMARY,
    ROOT / "notes" / "fig2-uq-promotion.md",
    ROOT / "codex-prompts" / "out" / "B3-promotion-verdict.md",
    ROOT / "codex-prompts" / "out" / "B3-discrepancies.md",
]


def main() -> int:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    verify_recorded_hashes(summary)
    assert len(summary["channels"]) == 8
    assert len(summary["weighting_sensitivity"]) == 40
    assert all(
        item["latest_spec_decision"]["status"]["composite"] == "UNRESOLVED"
        for item in summary["channels"]
    )

    runtime = ROOT / "codex-prompts" / "out" / "A3-file-secret-hardening" / "optics_agent" / "comsol" / "runtime"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(runtime)
    command = [sys.executable, "-m", "pytest", "-q"]
    completed = subprocess.run(
        command, cwd=ROOT, env=env, text=True, capture_output=True, check=False,
    )
    receipt = {
        "task": "B3",
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_assertions": {
            "input_hashes_match": True,
            "channel_rows": 8,
            "pointwise_rows": 32000,
            "weighting_rows": 40,
            "latest_status": summary["layer3_uq_status"],
            "promotion": summary["promotion"]["promotion_to_physical_reproduction_success"],
            "result_class": summary["promotion"]["result_class"],
        },
        "pytest": {
            "command": "python -m pytest -q",
            "environment": {"PYTHONPATH": str(runtime)},
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
        "artifact_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in ARTIFACTS
        },
    }
    OUT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    print(f"B3 validation receipt: {OUT}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
