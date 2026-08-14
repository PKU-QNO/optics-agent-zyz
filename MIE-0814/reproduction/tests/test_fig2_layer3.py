# -*- coding: utf-8 -*-
"""Layer3 paper-vector extraction and comparison regression tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from compare_fig2_paper import (  # noqa: E402
    JC_MIN_X,
    classify_metrics,
    compare_all,
)
from extract_fig2_vector import (  # noqa: E402
    MULTIPOLES,
    extract_raster_fallback,
    extract_vector,
    find_source_pdf,
    sha256_file,
)

EXPECTED_PDF_SHA256 = "c79e243e9b0d05e2800223dea8552df03bbbf0318c134839e9e7ebcc8dda973e"


@pytest.fixture(scope="module")
def vector_data():
    return extract_vector()


def test_source_pdf_hash_is_fixed():
    assert sha256_file(find_source_pdf()) == EXPECTED_PDF_SHA256


def test_page4_has_expected_colored_vector_paths(vector_data):
    rows, metadata = vector_data
    assert metadata["mode"] == "vector"
    assert metadata["page"] == 4
    for panel in ("a", "b"):
        for key in MULTIPOLES:
            counts = metadata["counts"][panel][key]
            assert counts["line_drawings"] >= 1
            assert counts["line_points"] >= 40
            assert counts["marker_drawings"] >= 20
            assert counts["marker_points"] >= 20
    assert len(rows) > 1000


def test_axis_fit_and_round_trip(vector_data):
    _, metadata = vector_data
    for panel in ("a", "b"):
        axis = metadata["panels"][panel]
        assert axis["x_fit_residual_data"] < 0.001
        assert axis["y_fit_residual_data"] < 0.01
        assert axis["x_fit_residual_pdf_pt"] < 0.5
        assert axis["y_fit_residual_pdf_pt"] < 0.5
        assert axis["x_fit_residual_pdf_pt"] == pytest.approx(
            axis["x_fit_residual_data"] / abs(axis["x_fit_page_to_data"][0])
        )
        assert axis["y_fit_residual_pdf_pt"] == pytest.approx(
            axis["y_fit_residual_data"] / abs(axis["y_fit_page_to_data"][0])
        )
        xfit = np.asarray(axis["x_fit_page_to_data"])
        yfit = np.asarray(axis["y_fit_page_to_data"])
        for value in [0.2, 0.4, 0.6, 0.8, 1.0]:
            page_x = (value - xfit[1]) / xfit[0]
            assert np.polyval(xfit, page_x) == pytest.approx(value, abs=1e-12)
        for value in [1.0, 3.0, 5.0, 7.0]:
            page_y = (value - yfit[1]) / yfit[0]
            assert np.polyval(yfit, page_y) == pytest.approx(value, abs=1e-12)


def test_extracted_curves_are_monotonic_and_bounded(vector_data):
    rows, _ = vector_data
    for panel in ("a", "b"):
        for key in MULTIPOLES:
            for curve in ("mie", "exact"):
                xs = sorted({float(row["x_alaee"]) for row in rows
                             if row["panel"] == panel and row["multipole"] == key
                             and row["curve"] == curve})
                assert len(xs) >= 20
                assert np.all(np.diff(xs) > 0)
                # The physical frame extends a little left of the first
                # labelled tick, but no extracted point may leave the frame.
                assert min(xs) > 0.1
                assert max(xs) <= 1.01


def test_vector_extraction_is_deterministic(vector_data):
    rows1, metadata1 = vector_data
    rows2, metadata2 = extract_vector()
    assert rows1 == rows2
    assert metadata1 == metadata2


def test_gold_jc_domain_mask_and_no_olmon_substitution():
    summary, _, _ = compare_all()
    panel = summary["panels"]["b"]
    assert panel["coverage_status"] == "MATERIAL_DOMAIN_LIMITED"
    assert panel["masked_x_range"] == pytest.approx([0.2, JC_MIN_X])
    assert "Olmon substitution forbidden" in panel["masked_reason"]


def test_vector_and_raster_have_different_result_classes():
    passing = {"rmse": 0.01, "p95_absolute_error": 0.02, "peak_x_difference": 0.005}
    assert classify_metrics(passing, "vector") == "PASS_VECTOR_CONSISTENT"
    assert classify_metrics(passing, "raster") == "DESCRIPTIVE_ONLY"


def test_raster_fallback_is_explicitly_descriptive():
    image = ROOT / "figs" / "_fig2_panels.png"
    rows, metadata = extract_raster_fallback(image)
    assert rows
    assert metadata["mode"] == "raster"
    assert metadata["confidence"] == "descriptive_only"


def test_dielectric_and_gold_primary_vector_gates():
    summary, _, _ = compare_all()
    a = summary["panels"]["a"]
    b = summary["panels"]["b"]
    assert a["curves"]["ED"]["mie"]["status"] == "PASS_VECTOR_CONSISTENT"
    assert a["curves"]["MD"]["mie"]["status"] == "PASS_VECTOR_CONSISTENT"
    assert a["curves"]["EQ"]["mie"]["status"] == "PASS_VECTOR_CONSISTENT"
    # The sharp MQ vector trace misses the pre-registered 0.02 RMSE gate by a
    # small amount; keep this unresolved instead of loosening the threshold.
    assert a["curves"]["MQ"]["mie"]["status"] == "UNRESOLVED"
    for key in MULTIPOLES:
        assert b["curves"][key]["mie"]["status"] == "PASS_VECTOR_CONSISTENT"


def test_mq_point_count_and_spacing_diagnostics_are_not_stale():
    summary, _, _ = compare_all()
    mq = summary["panels"]["a"]["curves"]["MQ"]["mie"]
    spacing = mq["spacing_diagnostics"]
    assert mq["paper_points"] == 212
    assert mq["absolute_error_gt_0_05_count"] == 14
    assert all(0.52 <= value <= 0.97 for value in mq["absolute_error_gt_0_05_x"])
    assert spacing["source_curve_points"] == 214
    assert spacing["source_max_x_gap"] == pytest.approx(0.2302626)
    assert spacing["source_max_x_gap_interval"] == pytest.approx([0.1394499, 0.3697125])
    assert spacing["primary_peak_window_max_x_gap"] == pytest.approx(0.0022529)
    assert spacing["secondary_peak_window_max_x_gap"] == pytest.approx(0.0087895)


def test_paper_internal_graphical_floor_is_separate_from_strict_gate():
    summary, _, _ = compare_all()
    floor = summary["panels"]["a"]["graphical_floor"]["MQ"]
    internal = floor["paper_internal_mie_vs_exact"]
    local = floor["local_mie_vs_paper_mie"]
    assert floor["same_marker_points"] == 23
    assert internal["rmse"] == pytest.approx(0.024302105943257324)
    assert internal["p95_absolute_error"] == pytest.approx(0.06186587951829785)
    assert local["rmse"] == pytest.approx(0.009326519191935317)
    assert local["p95_absolute_error"] == pytest.approx(0.02104180392780459)
    assert floor["assessment"] == "CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR"
    assert floor["overrides_strict_gate"] is False
    assert summary["strict_vector_fidelity_status"] == "UNRESOLVED"


def test_sparse_exact_markers_never_make_an_independent_peak_verdict():
    summary, _, _ = compare_all()
    for panel in ("a", "b"):
        for key in MULTIPOLES:
            exact = summary["panels"][panel]["curves"][key]["exact"]
            assert exact["marker_x_spacing_median"] > 0.01
            assert exact["independent_peak_verdict"] is False
            assert exact["peak_verdict"] == "DESCRIPTIVE_ONLY"
            assert exact["status"] == "DESCRIPTIVE_ONLY"
            assert exact["shape_metrics_status"] in {"PASS_VECTOR_CONSISTENT", "UNRESOLVED"}


def test_q_factor_diagnostic_is_supplemental_and_never_fabricates_boundary_passes():
    summary, _, _ = compare_all()
    for key in MULTIPOLES:
        diagnostic = summary["panels"]["a"]["q_factor_diagnostics"][key]
        assert diagnostic["status"] == "PASS"
        assert diagnostic["relative_error"] <= 0.05
        assert diagnostic["supplemental_only"] is True
        assert diagnostic["promotion_eligible"] is False
    assert summary["panels"]["b"]["q_factor_diagnostics"]["ED"]["status"] == "PASS"
    for key in ("MD", "EQ", "MQ"):
        assert summary["panels"]["b"]["q_factor_diagnostics"][key]["status"] == "NOT_EVALUABLE"


def test_gate4_machine_contract_uses_only_valid_sepr_result_class():
    summary, _, _ = compare_all()
    assert summary["method_claim_status"] == "PASS"
    assert summary["paper_fidelity_status"] == "UNRESOLVED"
    assert summary["coverage_status"] == "MATERIAL_DOMAIN_LIMITED"
    assert summary["graphical_floor_assessment"] == "CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR"
    assert summary["gate4_decision"] == "PASS_WITH_LIMITATIONS"
    assert summary["result_class"] == "partial_physical_match"
    assert summary["promotion_to_physical_reproduction_success"] == "DENIED"


def test_saved_layer3_summary_is_machine_readable():
    path = ROOT / "data" / "fig2_layer3_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["mode"] == "vector"
    assert data["overall_status"] in {"PASS_VECTOR_CONSISTENT", "UNRESOLVED"}
    assert data["result_class"] == "partial_physical_match"
