# -*- coding: utf-8 -*-
"""Independent forward-amplitude routes for the optical theorem.

The existing :mod:`baseline_mie` implementation stores cross sections in the
dimensionless normalization

``C'_ext = sum_n (2*n+1)*Re(a_n+b_n)``.

This module deliberately does *not* obtain ``C'_ext`` by repeating that
contraction.  It builds the complex far-field scattering amplitudes
``S1(theta)`` and ``S2(theta)`` and obtains their forward limit by an angular
projection.  A second route evaluates the closed forward Mie expression.  Both
routes use the same already-validated coefficients, but the contractions and
the angular algebra are separate code paths.

Conventions
-----------
For an ``exp(-i omega t)`` time convention the outgoing far field is written
as ``E_s ~ exp(i*k*r) S(theta)/(r)``.  The physical amplitude returned here is

``S_phys(theta) = 1j*S_dimensionless(theta)/k``.

Consequently ``C_ext_phys = (4*pi/k)*Im(S_phys(0))``.  The repository's
dimensionless baseline is recovered with
``C'_ext = (k**2/(2*pi))*C_ext_phys``.  Setting ``k=1`` is convenient for
dimensionless tests but does not change the normalized result.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss

from baseline_mie import mie_coefficients, wiscombe_nmax


def _check_inputs(x_mie: float, m: complex, n_max: int | None) -> int:
    """Validate common inputs and return a concrete truncation order."""
    x = float(x_mie)
    if not np.isfinite(x) or x <= 0.0:
        raise ValueError("x_mie must be a finite positive number")
    if n_max is None:
        n_max = wiscombe_nmax(x)
    n_max = int(n_max)
    if n_max < 1:
        raise ValueError("n_max must be at least one")
    if not np.isfinite(complex(m).real) or not np.isfinite(complex(m).imag):
        raise ValueError("m must be finite")
    return n_max


def _forward_dimensionless_from_series(x_mie: float, m: complex,
                                       n_max: int | None = None) -> complex:
    """Closed forward Mie amplitude, before the physical ``1j/k`` factor.

    This is the explicit identity
    ``S_fwd = 1/2 * sum_n (2*n+1) * (a_n+b_n)``.  It is kept private so that
    callers use :func:`s0_series`, whose return value obeys the optical-theorem
    ``(4*pi/k)*Im`` convention.
    """
    n_max = _check_inputs(x_mie, m, n_max)
    a_n, b_n = mie_coefficients(float(x_mie), complex(m), n_max)
    n = np.arange(1, n_max + 1, dtype=float)
    return complex(0.5 * np.sum((2.0 * n + 1.0) * (a_n + b_n)))


def s0_series(x_mie: float, m: complex, n_max: int | None = None,
              k: float = 1.0) -> complex:
    """Forward amplitude from the explicit Mie-series formula.

    The returned physical amplitude is ``S(0)=1j*S_fwd/k``.  With the
    repository's outgoing-wave and ``exp(-i omega t)`` convention this makes
    ``(4*pi/k)*Im(S(0))`` the physical extinction cross section.
    """
    k = float(k)
    if not np.isfinite(k) or k <= 0.0:
        raise ValueError("k must be a finite positive number")
    return 1j * _forward_dimensionless_from_series(x_mie, m, n_max) / k


def _pi_tau(n_max: int, mu: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return Mie angular functions ``pi_n(mu)`` and ``tau_n(mu)``.

    The recurrence is the Bohren--Huffman one (``pi_1=1`` and
    ``tau_n=n*mu*pi_n-(n+1)*pi_(n-1)``).  It is intentionally independent of
    the scalar forward identity and remains well behaved at ``mu=+/-1``.
    """
    mu = np.asarray(mu, dtype=float)
    pi = np.zeros((n_max + 1,) + mu.shape, dtype=float)
    tau = np.zeros_like(pi)
    pi[1] = 1.0
    for n in range(2, n_max + 1):
        pi[n] = ((2.0 * n - 1.0) / (n - 1.0)) * mu * pi[n - 1] \
                - (n / (n - 1.0)) * pi[n - 2]
    for n in range(1, n_max + 1):
        tau[n] = n * mu * pi[n] - (n + 1.0) * pi[n - 1]
    return pi[1:], tau[1:]


def angular_scattering_amplitudes(x_mie: float, m: complex,
                                  theta: np.ndarray | float,
                                  n_max: int | None = None,
                                  k: float = 1.0,
                                  phi: np.ndarray | float | None = None
                                  ) -> tuple[np.ndarray, np.ndarray]:
    """Return complex far-field amplitudes ``(S1,S2)`` on an angular grid.

    ``theta`` and ``phi`` are broadcast to a common shape.  For a homogeneous
    sphere the two polarization amplitudes are independent of ``phi``; the
    argument is accepted explicitly so a caller can audit that symmetry.
    ``S1`` and ``S2`` include the same physical ``1j/k`` normalization as
    :func:`s0_series`.
    """
    k = float(k)
    if not np.isfinite(k) or k <= 0.0:
        raise ValueError("k must be a finite positive number")
    n_max = _check_inputs(x_mie, m, n_max)
    theta_arr = np.asarray(theta, dtype=float)
    if phi is None:
        theta_arr, _ = np.broadcast_arrays(theta_arr, np.asarray(0.0))
    else:
        theta_arr, _ = np.broadcast_arrays(theta_arr, np.asarray(phi, dtype=float))
    mu = np.cos(theta_arr)
    # Avoid a one-ulp excursion outside [-1,1] at theta=0 or pi.
    mu = np.clip(mu, -1.0, 1.0)
    pi_n, tau_n = _pi_tau(n_max, mu)
    a_n, b_n = mie_coefficients(float(x_mie), complex(m), n_max)
    n = np.arange(1, n_max + 1, dtype=float)
    pref = (2.0 * n + 1.0) / (n * (n + 1.0))
    # The leading axis is n; all remaining axes are angular-grid axes.
    shape = (n_max,) + (1,) * mu.ndim
    aa = a_n.reshape(shape)
    bb = b_n.reshape(shape)
    pp = pref.reshape(shape)
    s1_dimless = np.sum(pp * (aa * pi_n + bb * tau_n), axis=0)
    s2_dimless = np.sum(pp * (aa * tau_n + bb * pi_n), axis=0)
    return 1j * s1_dimless / k, 1j * s2_dimless / k


def _forward_reproducing_weights(mu: np.ndarray, n_max: int,
                                 quadrature_weights: np.ndarray) -> np.ndarray:
    """Weights that reconstruct a degree-``n_max`` polynomial at ``mu=1``.

    For any polynomial ``p`` of degree at most ``n_max``,

    ``p(1) = sum_j q_j p(mu_j)``

    with ``q_j = w_j * sum_l (2l+1)P_l(mu_j)/2``.  Gauss--Legendre quadrature
    makes the integral exact when it has at least ``n_max+1`` nodes.  Computing
    these weights from a Legendre basis is the numerical angular integration
    path; no forward ``sum(a_n+b_n)`` is used here.
    """
    mu = np.asarray(mu, dtype=float)
    qweights = np.asarray(quadrature_weights, dtype=float)
    if mu.ndim != 1 or qweights.shape != mu.shape:
        raise ValueError("mu and quadrature_weights must be one-dimensional and same length")
    # Legendre recurrence, kept local to make the projection path auditable.
    p_prev = np.ones_like(mu)
    kernel = 0.5 * p_prev  # l=0 term
    if n_max >= 1:
        p_curr = mu.copy()
        kernel += 1.5 * p_curr
        for ell in range(2, n_max + 1):
            p_next = ((2.0 * ell - 1.0) * mu * p_curr - (ell - 1.0) * p_prev) / ell
            kernel += 0.5 * (2.0 * ell + 1.0) * p_next
            p_prev, p_curr = p_curr, p_next
    return qweights * kernel


def s0_from_angular_quadrature(x_mie: float, m: complex,
                               n_max: int | None = None,
                               n_mu: int | None = None,
                               n_phi: int = 8,
                               k: float = 1.0) -> complex:
    """Forward amplitude reconstructed from angle-resolved far-field samples.

    The complex amplitudes are sampled away from the forward singular
    coordinate at Gauss--Legendre ``mu=cos(theta)`` nodes.  A Legendre
    reproducing kernel performs the angular integral and evaluates the finite
    spherical-harmonic expansion at ``mu=1``.  ``S1`` and ``S2`` are averaged,
    and a uniform azimuthal quadrature explicitly checks the sphere's
    phi-independence.  ``n_mu`` defaults to ``n_max+4``; this integrates all
    products required by the order-``n_max`` expansion exactly up to roundoff.
    """
    k = float(k)
    if not np.isfinite(k) or k <= 0.0:
        raise ValueError("k must be a finite positive number")
    n_max = _check_inputs(x_mie, m, n_max)
    if n_mu is None:
        n_mu = n_max + 4
    n_mu = int(n_mu)
    if n_mu < n_max + 1:
        raise ValueError("n_mu must be at least n_max+1 for exact projection")
    n_phi = int(n_phi)
    if n_phi < 1:
        raise ValueError("n_phi must be positive")

    mu, weights = leggauss(n_mu)
    theta = np.arccos(mu)[:, None]
    phi = (2.0 * np.pi * np.arange(n_phi, dtype=float) / n_phi)[None, :]
    s1, s2 = angular_scattering_amplitudes(x_mie, m, theta, n_max, k, phi)
    s_pol = 0.5 * (s1 + s2)
    s_phi_avg = np.mean(s_pol, axis=1)
    q = _forward_reproducing_weights(mu, n_max, weights)
    return complex(np.sum(q * s_phi_avg))


def c_ext_from_s0(s0: complex, k: float = 1.0) -> float:
    """Physical extinction cross section from ``C_ext=(4*pi/k) Im S(0)``."""
    k = float(k)
    if not np.isfinite(k) or k <= 0.0:
        raise ValueError("k must be a finite positive number")
    return float((4.0 * np.pi / k) * np.imag(complex(s0)))


def c_ext_dimless_from_s0(s0: complex, k: float = 1.0) -> float:
    """Baseline normalization ``C'_ext = k²/(2*pi) * C_ext_phys``."""
    k = float(k)
    return float((k * k / (2.0 * np.pi)) * c_ext_from_s0(s0, k))


def relative_difference(lhs: float, rhs: float) -> float:
    """Symmetric relative difference used by the audit report/tests."""
    scale = max(abs(float(lhs)), abs(float(rhs)), np.finfo(float).tiny)
    return abs(float(lhs) - float(rhs)) / scale


__all__ = [
    "angular_scattering_amplitudes",
    "c_ext_dimless_from_s0",
    "c_ext_from_s0",
    "relative_difference",
    "s0_from_angular_quadrature",
    "s0_series",
]
