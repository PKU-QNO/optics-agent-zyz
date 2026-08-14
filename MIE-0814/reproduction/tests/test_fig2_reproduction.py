# -*- coding: utf-8 -*-
"""Fig.2 formalization and numerical acceptance tests.

The full 200-point volume-integral gate is opt-in because it takes several
minutes on a laptop; the generated CSV/JSON artifacts are the auditable
evidence for that gate.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from baseline_mie import cross_sections, wiscombe_nmax  # noqa: E402
from run_fig2 import (  # noqa: E402
    MULTIPOLES,
    _valid_x_grid,
    compute_gold_point,
    gold_source_range,
    interpolate_gold_m,
    run_source,
    summarize,
)


def test_gold_interpolation_is_wavelength_domain_and_no_extrapolation():
    assert gold_source_range("jc") == (400.0, 1935.0)
    assert gold_source_range("olmon") == (400.0, 2500.0)
    assert gold_source_range("mcpeak") == (400.0, 1700.0)
    assert interpolate_gold_m("olmon", 550.0).imag > 0
    with pytest.raises(ValueError):
        interpolate_gold_m("jc", 2000.0)


def test_valid_x_grid_respects_source_domains():
    # x=500/lambda, so shorter data coverage means a larger lower x bound.
    assert _valid_x_grid("olmon", 200)[0] == pytest.approx(0.2)
    assert _valid_x_grid("mcpeak", 200)[0] == pytest.approx(500.0 / 1700.0)
    assert _valid_x_grid("jc", 200)[0] == pytest.approx(500.0 / 1935.0)


@pytest.mark.parametrize("wavelength_nm", [550.0, 1000.0, 1700.0, 1935.0, 2500.0])
def test_gold_mie_passivity_at_required_wavelengths(wavelength_nm):
    # This is intentionally the fast independent Mie check; Table-2 volume
    # integration is covered by the opt-in slow gate below.
    source = "olmon"
    m = interpolate_gold_m(source, wavelength_nm)
    x = np.pi * 500.0 / wavelength_nm
    _, _, c_abs = cross_sections(x, m, wiscombe_nmax(x))
    assert m.imag > 0
    assert c_abs >= -1e-12


def test_gold_point_uses_same_material_for_mie_and_table2():
    row = compute_gold_point(0.5, "olmon", grid=(24, 25, 48))
    assert row["source"] == "olmon"
    assert row["lambda_nm"] == pytest.approx(1000.0)
    assert row["n"] + 1j * row["kappa"] == interpolate_gold_m("olmon", 1000.0)
    assert all(np.isfinite(row[f"table2_{key}"]) for key in MULTIPOLES)


def test_gold_olmon_full_range_contract():
    artifact = ROOT / "data" / "fig2_gold_olmon_refined_summary.json"
    if artifact.exists() and os.environ.get("RUN_FIG2_SLOW") != "1":
        report = json.loads(artifact.read_text(encoding="utf-8"))
        assert report["points"] == 200
        assert report["passes_all_channels"], report
        return
    if os.environ.get("RUN_FIG2_SLOW") != "1":
        pytest.skip("未找到加密 200 点产物；设置 RUN_FIG2_SLOW=1 现场重算")
    rows = run_source("olmon", 200, grid=(60, 61, 120), progress=False)
    report = summarize(rows)
    assert report["points"] == 200
    assert report["passes_all_channels"], report


def test_gold_grid_convergence_high_signal():
    artifact = ROOT / "data" / "fig2_gold_olmon_grid_convergence.json"
    if artifact.exists() and os.environ.get("RUN_FIG2_SLOW") != "1":
        report = json.loads(artifact.read_text(encoding="utf-8"))
        assert max(item["max_change_percent"] for item in report.values()) < 0.1
        return
    if os.environ.get("RUN_FIG2_SLOW") != "1":
        pytest.skip("未找到网格收敛产物；设置 RUN_FIG2_SLOW=1 现场重算")
    x = 0.5
    coarse = compute_gold_point(x, "olmon", grid=(40, 41, 80))
    refined = compute_gold_point(x, "olmon", grid=(60, 61, 120))
    for key in MULTIPOLES:
        base = refined[f"mie_{key}"]
        if base < 1e-4:
            continue
        change = abs(refined[f"table2_{key}"] - coarse[f"table2_{key}"]) / base
        assert change < 1e-3, (key, change)
