"""Small regression guards for B15 review-critical frozen summaries."""

from __future__ import annotations

import json
from pathlib import Path


REPRODUCTION_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPRODUCTION_DIR / "data"


def _load_json(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def test_fig3_surrogate_coverage_and_tribelsky_extrema_contract() -> None:
    summary = _load_json("fig3_mie_surrogate_summary.json")

    assert summary["result_class"] == "surrogate_fallback"
    assert (summary["covered_points"], summary["n_points"]) == (297, 301)
    assert summary["uncovered_points"] == 4

    feature = summary["tribelsky_feature"]
    extrema = summary["tribelsky_numeric_extrema"]
    assert extrema["peak_grid"] == 1.32002
    assert extrema["valley_grid"] == 1.35998
    assert abs(extrema["peak_grid"] - feature["x_peak"]) <= 2.1e-5
    assert abs(extrema["valley_grid"] - feature["x_valley"]) <= 2.1e-5


def test_fig2_latest_uq_all_eight_formal_lanes_fail_closed() -> None:
    summary = _load_json("fig2_uq_summary.json")

    assert summary["layer3_uq_status"] == "UNRESOLVED"
    assert summary["promotion"]["promotion_to_physical_reproduction_success"] == "DENIED"

    lanes = summary["channels"]
    assert {(lane["panel"], lane["channel"]) for lane in lanes} == {
        (panel, channel)
        for panel in ("a", "b")
        for channel in ("ED", "MD", "EQ", "MQ")
    }
    for lane in lanes:
        status = lane["latest_spec_decision"]["status"]
        assert status == {
            "rmse": "UNRESOLVED",
            "p95_abs": "UNRESOLVED",
            "peak_x": "UNRESOLVED",
            "composite": "UNRESOLVED",
        }
