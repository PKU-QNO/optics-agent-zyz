# -*- coding: utf-8 -*-
"""B2 independent optical-theorem tests.

``test_mie.py::test_optical_theorem`` is intentionally retained as the old
lossless self-consistency check.  These tests exercise the new S(0) module:
the explicit forward-series route and a separate angle-resolved
Legendre-projection route must agree for lossless and absorbing spheres.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[1]
_CODE = _ROOT / "code"
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))

from baseline_mie import cross_sections, wiscombe_nmax  # noqa: E402
from optical_theorem import (  # noqa: E402
    angular_scattering_amplitudes,
    c_ext_dimless_from_s0,
    c_ext_from_s0,
    relative_difference,
    s0_from_angular_quadrature,
    s0_series,
)


def _gold_cases() -> list[tuple[float, complex]]:
    """Use finite Olmon-EV samples already covered by the Fig.2 data contract."""
    rows = list(csv.DictReader((_ROOT / "data" / "gold_epsilon.csv").open(
        newline="", encoding="utf-8"
    )))
    out = []
    for wavelength_nm in (550.0, 1000.0, 1700.0):
        row = next(row for row in rows if float(row["lambda_nm"]) == wavelength_nm)
        m = complex(float(row["olmon_n"]), float(row["olmon_k"]))
        # The Fig.2 geometry is a=250 nm, hence x=2*pi*a/lambda.
        x_mie = np.pi * (500.0 / wavelength_nm)
        out.append((float(x_mie), m))
    return out


def _complex_relative_difference(lhs: complex, rhs: complex) -> float:
    scale = max(abs(lhs), abs(rhs), np.finfo(float).tiny)
    return float(abs(lhs - rhs) / scale)


@pytest.mark.parametrize("x_mie", [0.25, 0.5, 1.0, 1.75, 2.5])
def test_s0_routes_agree_for_lossless_dielectric(x_mie: float):
    m = 2.5 + 0.0j
    n_max = wiscombe_nmax(x_mie)
    s_series = s0_series(x_mie, m, n_max)
    s_angular = s0_from_angular_quadrature(x_mie, m, n_max, n_phi=12)
    assert _complex_relative_difference(s_series, s_angular) < 1e-6


@pytest.mark.parametrize("x_mie,m", _gold_cases())
def test_s0_routes_agree_for_absorbing_gold(x_mie: float, m: complex):
    n_max = wiscombe_nmax(x_mie)
    s_series = s0_series(x_mie, m, n_max)
    s_angular = s0_from_angular_quadrature(x_mie, m, n_max, n_phi=12)
    assert m.imag > 0.0
    assert _complex_relative_difference(s_series, s_angular) < 1e-6


@pytest.mark.parametrize("x_mie", [0.25, 0.5, 1.0, 1.75, 2.5])
def test_s0_extinction_matches_existing_cext_dielectric(x_mie: float):
    m = 2.5 + 0.0j
    n_max = wiscombe_nmax(x_mie)
    _, c_ext, _ = cross_sections(x_mie, m, n_max)
    s_series = s0_series(x_mie, m, n_max)
    s_angular = s0_from_angular_quadrature(x_mie, m, n_max, n_phi=12)
    # baseline_mie returns C'_ext with its common 2*pi/k^2 factor removed.
    c_series = c_ext_dimless_from_s0(s_series)
    c_angular = c_ext_dimless_from_s0(s_angular)
    assert relative_difference(c_series, c_ext) < 1e-8
    assert relative_difference(c_angular, c_ext) < 1e-8


@pytest.mark.parametrize("x_mie,m", _gold_cases())
def test_s0_extinction_matches_existing_cext_gold(x_mie: float, m: complex):
    n_max = wiscombe_nmax(x_mie)
    _, c_ext, c_abs = cross_sections(x_mie, m, n_max)
    s_series = s0_series(x_mie, m, n_max)
    s_angular = s0_from_angular_quadrature(x_mie, m, n_max, n_phi=12)
    c_series = c_ext_dimless_from_s0(s_series)
    c_angular = c_ext_dimless_from_s0(s_angular)
    assert c_abs > 0.0
    assert relative_difference(c_series, c_ext) < 1e-8
    assert relative_difference(c_angular, c_ext) < 1e-8


def test_angle_resolved_amplitude_is_phi_independent_and_forward_limit_is_finite():
    """The explicit angular path respects spherical symmetry and finite S(0)."""
    x_mie, m = 1.1, 0.7 + 1.8j
    theta = np.array([[0.0, 0.4, 1.2], [2.0, 2.5, np.pi]])
    phi = np.array([[0.0, 1.0, 2.0], [0.5, 2.5, 4.0]])
    s1, s2 = angular_scattering_amplitudes(x_mie, m, theta, phi=phi)
    s1_ref, s2_ref = angular_scattering_amplitudes(x_mie, m, theta)
    assert np.allclose(s1, s1_ref, rtol=0.0, atol=1e-14)
    assert np.allclose(s2, s2_ref, rtol=0.0, atol=1e-14)
    assert np.isfinite(s1[0, 0]) and np.isfinite(s2[0, 0])
    assert np.isfinite(s1[1, 1]) and np.isfinite(s2[1, 1])


def test_optical_theorem_physical_k_normalization():
    """Changing k changes physical area but leaves C'_ext invariant."""
    x_mie, m = 0.9, 2.5
    s_k1 = s0_series(x_mie, m, k=1.0)
    s_k3 = s0_series(x_mie, m, k=3.0)
    assert c_ext_from_s0(s_k1, k=1.0) == pytest.approx(
        9.0 * c_ext_from_s0(s_k3, k=3.0), rel=1e-13
    )
    assert c_ext_dimless_from_s0(s_k1, k=1.0) == pytest.approx(
        c_ext_dimless_from_s0(s_k3, k=3.0), rel=1e-13
    )
