# -*- coding: utf-8 -*-
"""
Analytic Fig.3 surrogate: gold Mie channels and an explicit interference
diagnostic.

The Alaee Fig.3 target is a *coupled, non-spherical pair of gold disks*.
There is no closed-form Mie solution for that object and the paper's curves
come from a COMSOL current distribution.  This module therefore deliberately
implements a ``surrogate_fallback`` path:

* an equivalent isolated sphere (radius ``a``) is evaluated with the validated
  Lorenz--Mie coefficients in :mod:`baseline_mie`;
* a transparent two-particle retardation factor and weak channel coupling are
  applied to make a reproducible coupled-particle proxy;
* Table-1-like values are the Rayleigh (small-``x``) continuation of the same
  coefficients, while Table-2-like values retain the full Mie coefficients;
* angle-resolved Mie amplitudes are retained as complex numbers.  Their sum
  exposes the ED/MD/EQ/MQ cross term, whereas the angle-integrated channel
  powers are the positive, orthogonal contributions used by Alaee Eq.(1).

No claim in this file is an FEM reproduction of Fig.3.  The module is useful
for regression, a deterministic analytic baseline, and Fano/Kerker diagnostic
tests.  The material loader refuses to extrapolate Johnson--Christy data.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

try:  # tests add ``code`` to sys.path
    from baseline_mie import mie_coefficients, wiscombe_nmax
except ImportError:  # pragma: no cover - package-style import
    from .baseline_mie import mie_coefficients, wiscombe_nmax


CHANNELS = ("ED", "MD", "EQ", "MQ")
_CHANNEL_TO_L_KIND = {"ED": (1, "a", 3), "MD": (1, "b", 5),
                      "EQ": (2, "a", 5), "MQ": (2, "b", 7)}


@dataclass(frozen=True)
class Fig3Parameters:
    """Geometry and sampling inherited from the A4 Fig.3 draft.

    ``x=2a/lambda`` is the plotted abscissa.  A JC-faithful run uses the
    covered sub-domain ``x >= 2a/1935 nm``; points below it are represented as
    NaN by :func:`spectrum` rather than silently extrapolated.
    """

    radius_nm: float = 250.0
    thickness_nm: float = 80.0
    gap_nm: float = 120.0
    host_n: float = 1.0
    x_min: float = 0.25
    x_max: float = 1.0
    n_points: int = 301

    @property
    def center_distance_nm(self) -> float:
        return self.thickness_nm + self.gap_nm

    @property
    def lambda_nm_min(self) -> float:
        return 2.0 * self.radius_nm / self.x_max

    @property
    def lambda_nm_max(self) -> float:
        return 2.0 * self.radius_nm / self.x_min


def _read_jc(path: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Read finite Johnson--Christy ``lambda_nm,jc_n,jc_k`` rows."""
    lam, n, k = [], [], []
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                vals = (float(row["lambda_nm"]), float(row["jc_n"]), float(row["jc_k"]))
            except (TypeError, ValueError):
                continue
            if np.all(np.isfinite(vals)):
                lam.append(vals[0]); n.append(vals[1]); k.append(vals[2])
    if len(lam) < 2:
        raise ValueError("Johnson--Christy table has fewer than two finite rows")
    order = np.argsort(lam)
    return np.asarray(lam)[order], np.asarray(n)[order], np.asarray(k)[order]


def jc_refractive_index(lambda_nm: float | np.ndarray, data_path: str | Path) -> np.ndarray:
    """Interpolate complex JC ``n+i*k``; raise instead of extrapolating."""
    lam_src, n_src, k_src = _read_jc(data_path)
    lam = np.asarray(lambda_nm, dtype=float)
    if np.any(lam < lam_src[0]) or np.any(lam > lam_src[-1]):
        raise ValueError(
            f"Johnson--Christy coverage is [{lam_src[0]:g}, {lam_src[-1]:g}] nm; "
            "requested wavelength is outside the source domain (no extrapolation)."
        )
    return np.interp(lam, lam_src, n_src) + 1j * np.interp(lam, lam_src, k_src)


def x_to_lambda_nm(x: float | np.ndarray, radius_nm: float = 250.0) -> np.ndarray:
    """Convert the plotted ``x=2a/lambda`` to wavelength in nm."""
    x = np.asarray(x, dtype=float)
    if np.any(x <= 0):
        raise ValueError("x=2a/lambda must be positive")
    return 2.0 * radius_nm / x


def _rayleigh_coefficients(x: float, m: complex, x_ref: float = 1.0e-4) -> tuple[complex, complex]:
    """Leading small-x continuation of one Mie channel.

    The coefficient at ``x_ref`` is divided by its known power (x^3 for a1,
    x^5 for b1/a2, x^7 for b2) and then scaled to ``x``.  This avoids relying
    on a fragile hand-transcribed prefactor for absorbing gold while retaining
    the correct Rayleigh limit and phase.
    """
    a_ref, b_ref = mie_coefficients(x_ref, m, 2)
    return a_ref[0] * (x / x_ref) ** 3, b_ref[0] * (x / x_ref) ** 5


def _rayleigh_channel(x: float, m: complex, channel: str, x_ref: float = 1.0e-4) -> complex:
    a_ref, b_ref = mie_coefficients(x_ref, m, 3)
    l, kind, power = _CHANNEL_TO_L_KIND[channel]
    ref = a_ref[l - 1] if kind == "a" else b_ref[l - 1]
    return ref * (x / x_ref) ** power


def _pi_tau(n_max: int, cos_theta: float) -> tuple[np.ndarray, np.ndarray]:
    """Bohren--Huffman angular functions pi_l and tau_l."""
    pi = np.zeros(n_max + 1, dtype=float)
    tau = np.zeros(n_max + 1, dtype=float)
    pi[1] = 1.0
    for l in range(2, n_max + 1):
        pi[l] = ((2 * l - 1) / (l - 1)) * cos_theta * pi[l - 1] - (l / (l - 1)) * pi[l - 2]
    for l in range(1, n_max + 1):
        tau[l] = l * cos_theta * pi[l] - (l + 1) * pi[l - 1]
    return pi[1:], tau[1:]


def _pair_factor(lambda_nm: float, theta: float, distance_nm: float) -> complex:
    """Retarded symmetric two-centre factor for an axial pair."""
    phase = 2.0 * np.pi * distance_nm / lambda_nm * np.cos(theta)
    return 1.0 + np.exp(1j * phase)


def _coupled_coefficients(x: float, lambda_nm: float, m: complex, params: Fig3Parameters,
                          a_n: np.ndarray, b_n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Weak, bounded channel coupling used only by the surrogate path."""
    phase = np.exp(1j * 2.0 * np.pi * params.center_distance_nm / lambda_nm)
    # Dimensionless geometry factors; signs distinguish bright and subradiant
    # channels and create a reproducible, not fitted, phase-sensitive proxy.
    strength = {"ED": 0.10, "MD": -0.07, "EQ": 0.14, "MQ": -0.10}
    aa, bb = a_n.copy(), b_n.copy()
    for channel, (l, kind, _) in _CHANNEL_TO_L_KIND.items():
        raw = aa[l - 1] if kind == "a" else bb[l - 1]
        beta = strength[channel] * (params.radius_nm / params.center_distance_nm) ** (2 * l + 1)
        dressed = raw / (1.0 - beta * raw * phase)
        if kind == "a":
            aa[l - 1] = dressed
        else:
            bb[l - 1] = dressed
    return aa, bb


def _channel_values(a_n: np.ndarray, b_n: np.ndarray) -> dict[str, float]:
    return {
        "ED": float(3.0 * abs(a_n[0]) ** 2),
        "MD": float(3.0 * abs(b_n[0]) ** 2),
        "EQ": float(5.0 * abs(a_n[1]) ** 2),
        "MQ": float(5.0 * abs(b_n[1]) ** 2),
    }


def spectrum(x_values: Iterable[float], data_path: str | Path,
             params: Fig3Parameters | None = None) -> list[dict[str, float]]:
    """Generate exact/approximate channel spectra and wavelength coverage flags."""
    params = params or Fig3Parameters()
    out: list[dict[str, float]] = []
    for x in np.asarray(list(x_values), dtype=float):
        lam = float(x_to_lambda_nm(x, params.radius_nm))
        row: dict[str, float] = {"x_2a_over_lambda": float(x), "lambda_nm": lam}
        try:
            m = complex(jc_refractive_index(lam, data_path).item())
        except ValueError:
            row["material_covered"] = 0.0
            for channel in CHANNELS:
                row[f"{channel}_exact"] = np.nan
                row[f"{channel}_approx"] = np.nan
            row["total_exact"] = np.nan; row["total_approx"] = np.nan
            out.append(row)
            continue
        row["material_covered"] = 1.0
        x_mie = 2.0 * np.pi * params.radius_nm / lam
        n_max = max(2, wiscombe_nmax(x_mie))
        a_n, b_n = mie_coefficients(x_mie, m / params.host_n, n_max)
        a_exact, b_exact = _coupled_coefficients(x_mie, lam, m, params, a_n, b_n)
        # Quasi-static (Table-1-like) amplitudes; same static two-disc factor.
        pair_static = 2.0
        for channel in CHANNELS:
            l, kind, _ = _CHANNEL_TO_L_KIND[channel]
            raw_approx = _rayleigh_channel(x_mie, m / params.host_n, channel)
            raw_exact = a_exact[l - 1] if kind == "a" else b_exact[l - 1]
            row[f"{channel}_exact"] = float((2 * l + 1) * abs(raw_exact * pair_static) ** 2)
            row[f"{channel}_approx"] = float((2 * l + 1) * abs(raw_approx * pair_static) ** 2)
        row["total_exact"] = float(sum(row[f"{c}_exact"] for c in CHANNELS))
        row["total_approx"] = float(sum(row[f"{c}_approx"] for c in CHANNELS))
        out.append(row)
    return out


def relative_error(exact: float, approx: float, floor: float = 1e-14) -> float:
    """Percentage error with the exact value as denominator (diagnostic only)."""
    if not np.isfinite(exact) or not np.isfinite(approx):
        return float("nan")
    return float(abs(approx - exact) / max(abs(exact), floor) * 100.0)


def mie_directional_interference(lambda_nm: float, theta: float, data_path: str | Path,
                                 params: Fig3Parameters | None = None) -> dict[str, float | complex]:
    """Angle-resolved Mie amplitude and explicit incoherent/cross-term split."""
    params = params or Fig3Parameters()
    m = complex(jc_refractive_index(lambda_nm, data_path).item())
    x = 2.0 * np.pi * params.radius_nm / lambda_nm
    n_max = max(2, wiscombe_nmax(x))
    a_n, b_n = mie_coefficients(x, m / params.host_n, n_max)
    a_n, b_n = _coupled_coefficients(x, lambda_nm, m, params, a_n, b_n)
    pi, tau = _pi_tau(n_max, float(np.cos(theta)))
    l = np.arange(1, n_max + 1, dtype=float)
    pref = (2.0 * l + 1.0) / (l * (l + 1.0))
    pair = _pair_factor(lambda_nm, theta, params.center_distance_nm)
    s1_l = pair * pref * (a_n * pi + b_n * tau)
    s2_l = pair * pref * (a_n * tau + b_n * pi)
    s1 = complex(np.sum(s1_l)); s2 = complex(np.sum(s2_l))
    total = float(abs(s1) ** 2 + abs(s2) ** 2)
    incoherent = float(np.sum(abs(s1_l) ** 2 + abs(s2_l) ** 2))
    return {"S1": s1, "S2": s2, "total": total,
            "incoherent": incoherent, "cross_term": total - incoherent}


def fano_profile(epsilon: float | np.ndarray, q: float) -> np.ndarray:
    """Normalized Miroshnichenko--Flach--Kivshar Fano profile."""
    e = np.asarray(epsilon, dtype=float)
    return (e + q) ** 2 / (1.0 + e ** 2)


def tribelsky_feature_profile(x_values: Iterable[float]) -> tuple[np.ndarray, dict[str, float]]:
    """Strict-feature comparator calibrated to Tribelsky 2016 Fig.3.

    The literature reports a directional maximum near ``x=1.32`` and minimum
    near ``x=1.36``.  ``q=-1`` and ``Gamma=0.04`` place the analytic Fano
    extrema at those coordinates exactly; this is a comparator unit, not an
    Alaee-geometry fit.
    """
    x = np.asarray(list(x_values), dtype=float)
    x0, gamma, q = 1.34, 0.04, -1.0
    eps = 2.0 * (x - x0) / gamma
    return fano_profile(eps, q), {"x_peak": 1.32, "x_valley": 1.36,
                                  "x0": x0, "gamma": gamma, "q": q}


def fu2013_forward_backward_ratio(lambda_nm: float = 660.0, radius_nm: float = 75.0,
                                  refractive_index: float = 3.5) -> float:
    """Mie ED/MD forward-to-backward sanity comparator for Fu et al. (2013)."""
    x = 2.0 * np.pi * radius_nm / lambda_nm
    n_max = max(2, wiscombe_nmax(x))
    a_n, b_n = mie_coefficients(x, complex(refractive_index), n_max)
    l = np.arange(1, n_max + 1, dtype=float)
    fwd = np.sum((2.0 * l + 1.0) * (a_n + b_n))
    back = np.sum((2.0 * l + 1.0) * ((-1.0) ** l) * (a_n - b_n))
    return float(abs(fwd) ** 2 / max(abs(back) ** 2, 1e-30))


def rayleigh_limit_check(data_path: str | Path) -> dict[str, float]:
    """Compare exact and Rayleigh amplitudes at ``x=0.02``.

    The gold source starts at a finite wavelength and cannot provide a
    meaningful ``x→0`` limit without extrapolation.  Consequently this Layer-2
    regression intentionally uses a lossless dielectric ``m=1.5`` and reports
    the source path only as provenance (the argument is retained for a stable
    caller API).
    """
    del data_path
    x, m = 0.02, complex(1.5)
    a_n, b_n = mie_coefficients(x, m, 3)
    errs: dict[str, float] = {}
    for channel, (l, kind, _) in _CHANNEL_TO_L_KIND.items():
        exact = a_n[l - 1] if kind == "a" else b_n[l - 1]
        approx = _rayleigh_channel(x, m, channel)
        errs[channel] = relative_error(abs(exact), abs(approx), floor=1e-30)
    return {"x": x, "max_relative_error_percent": float(max(errs.values())), **errs}


__all__ = ["CHANNELS", "Fig3Parameters", "jc_refractive_index", "x_to_lambda_nm",
           "spectrum", "relative_error", "mie_directional_interference",
           "fano_profile", "tribelsky_feature_profile", "fu2013_forward_backward_ratio",
           "rayleigh_limit_check"]
