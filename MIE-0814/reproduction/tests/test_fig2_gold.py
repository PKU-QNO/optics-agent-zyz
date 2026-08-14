# -*- coding: utf-8 -*-
"""Fig.2 金数据契约与复数 Mie 路径的 gate② 回归测试。"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CODE_DIR = _REPO_ROOT / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from baseline_mie import cross_sections, mie_coefficients, wiscombe_nmax  # noqa: E402
from mie_theory import internal_field_coefficients  # noqa: E402

_GOLD_CSV = _REPO_ROOT / "data" / "gold_epsilon.csv"
_SOURCE_DIR = _REPO_ROOT / "data" / "_gold_sources"


def _rows():
    with _GOLD_CSV.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _row_at(wavelength_nm: float):
    return next(row for row in _rows() if float(row["lambda_nm"]) == wavelength_nm)


def _finite_range(rows, prefix: str):
    wavelengths = [
        float(row["lambda_nm"])
        for row in rows
        if row[f"{prefix}_n"].lower() != "nan" and row[f"{prefix}_k"].lower() != "nan"
    ]
    return min(wavelengths), max(wavelengths), len(wavelengths)


def test_gold_table_coverage_contract():
    rows = _rows()
    wavelengths = np.array([float(row["lambda_nm"]) for row in rows])
    assert len(rows) == 421
    assert wavelengths[0] == 400.0
    assert wavelengths[-1] == 2500.0
    assert np.allclose(np.diff(wavelengths), 5.0)
    assert _finite_range(rows, "jc") == (400.0, 1935.0, 308)
    assert _finite_range(rows, "olmon") == (400.0, 2500.0, 421)
    assert _finite_range(rows, "mcpeak") == (400.0, 1700.0, 261)


def test_550nm_spread_metric_is_explicit_pairwise_range_over_mean():
    row = _row_at(550.0)
    epsilon = []
    for source in ("jc", "olmon", "mcpeak"):
        m = float(row[f"{source}_n"]) + 1j * float(row[f"{source}_k"])
        epsilon.append(m ** 2)

    real_abs = np.abs([value.real for value in epsilon])
    imag_abs = np.abs([value.imag for value in epsilon])
    real_spread = 100.0 * np.ptp(real_abs) / np.mean(real_abs)
    imag_spread = 100.0 * np.ptp(imag_abs) / np.mean(imag_abs)
    assert real_spread == pytest.approx(11.34635, rel=1e-5)
    assert imag_spread == pytest.approx(25.74617, rel=1e-5)


@pytest.mark.parametrize("wavelength_nm", [550.0, 1000.0, 1700.0, 1935.0, 2500.0])
def test_complex_gold_mie_matches_miepython_and_is_passive(wavelength_nm):
    miepython = pytest.importorskip("miepython")
    row = _row_at(wavelength_nm)
    m = float(row["olmon_n"]) + 1j * float(row["olmon_k"])
    x_mie = np.pi * (500.0 / wavelength_nm)
    n_max = wiscombe_nmax(x_mie)

    assert m.imag > 0.0
    a_n, b_n = mie_coefficients(x_mie, m, n_max)
    c_n, d_n, _, _ = internal_field_coefficients(x_mie, m, n_max)
    a_ref, b_ref = miepython.an_bn(m, x_mie, n_max)
    c_ref, d_ref = miepython.cn_dn(m, x_mie, n_max)
    assert np.allclose(a_n, a_ref, rtol=1e-11, atol=1e-12)
    assert np.allclose(b_n, b_ref, rtol=1e-11, atol=1e-12)
    assert np.allclose(c_n, c_ref, rtol=1e-11, atol=1e-12)
    assert np.allclose(d_n, d_ref, rtol=1e-11, atol=1e-12)

    _, _, c_abs = cross_sections(x_mie, m, n_max)
    assert c_abs >= -1e-12


def test_raw_source_hashes_match_manifest_values():
    expected = {
        "Johnson.yml": "555C84AF33678F5838BBCA7E7577FDB870C906F72D73B31DD9153D8A0B18A2D3",
        "Olmon-ev.yml": "1102156143D348CD4B223A56FCD2CEDF272E7461B2FEE4509D742C2C63B8D779",
        "McPeak.yml": "E0506DD2B30387EA9BC15CD8DFBD43FF93131684C6417F3077CDB3EE2EEF20AA",
        "Rakic-LD.yml": "4BB9DEB8506D49B0E4C8BFBC71059AE482E8C3E92890DD3836A6AD32AAC8F74E",
    }
    for filename, digest in expected.items():
        actual = hashlib.sha256((_SOURCE_DIR / filename).read_bytes()).hexdigest().upper()
        assert actual == digest
