# -*- coding: utf-8 -*-
"""Grahn (2012) current-multipole scattering implementation.

This module is deliberately a small, dependency-light bridge around the
validated Mie/internal-field modules in this repository.  It exposes two
separate routes:

``path_A``
    The long-wavelength (no Bessel kernel) current moments followed by the
    Grahn tensor map (39)--(48).
``path_B``
    The finite-``kr`` Riccati--Bessel kernel integrals (15)--(16).

All formula numbers in docstrings are the printed Grahn equation numbers.
The implementation uses the normalized current ``Jtilde=(eps_r-eps_d)E``;
the common factor ``-i*omega*eps_d`` is included analytically in the
coefficient prefactor, so the returned ``a_E/a_M`` are dimensionless Mie
coefficients for ``E0=1`` and ``a=1``.
"""
from __future__ import annotations

import importlib.util
import math
from typing import Callable, Iterable

import numpy as np
from scipy.integrate import simpson
from scipy.special import factorial, lpmv, spherical_jn, spherical_yn, sph_harm_y

from baseline_mie import mie_coefficients, wiscombe_nmax
from mie_theory import internal_current_density
from multipole_moments import _integrate_3d, _moments_grid, _cartesian_position


EPS0 = 8.8541878128e-12


def _m3_from_grid(Jx, Jy, Jz, rx, ry, rz, u, th, ph):
    """Return ``p``, raw M2 and O=M3 for a normalized current grid.

    The physical ``i/omega`` factors cancel the ``-i omega`` in ``J``.  With
    ``Jtilde`` this is therefore simply ``p=∫Jtilde``, ``M2=∫Jtilde*r`` and
    ``O=1/2∫Jtilde*r*r`` (``a=1``).
    """
    jc = [Jx, Jy, Jz]
    rc = [rx, ry, rz]
    p = np.array([_integrate_3d(q, u, th, ph) for q in jc], dtype=complex)
    m2 = np.empty((3, 3), complex)
    for a in range(3):
        for b in range(3):
            m2[a, b] = _integrate_3d(jc[a] * rc[b], u, th, ph)
    o = np.empty((3, 3, 3), complex)
    for a in range(3):
        for b in range(3):
            for c in range(3):
                o[a, b, c] = 0.5 * _integrate_3d(jc[a] * rc[b] * rc[c], u, th, ph)
    return p, m2, o


def M2_four_objects(M2_raw: np.ndarray) -> dict[str, np.ndarray]:
    """Split a general 3x3 raw moment into the four spec objects.

    ``M2_raw = sym_traceless + antisym + trace`` is an exact algebraic
    identity.  ``Qe=6*sym_traceless`` is intentionally returned separately;
    it is a long-wave bridge, not a finite-``kr`` Table-2 moment.
    """
    raw = np.asarray(M2_raw, dtype=complex)
    if raw.shape != (3, 3):
        raise ValueError("M2_raw must have shape (3,3)")
    sym = 0.5 * (raw + raw.T)
    tr = np.trace(raw) / 3.0
    trace = np.eye(3, dtype=complex) * tr
    stf = sym - trace
    anti = 0.5 * (raw - raw.T)
    return {
        "raw": raw,
        "sym_traceless": stf,
        "antisym": anti,
        "trace": trace,
        "Qe": 6.0 * stf,
    }


def m2_four_objects(M2_raw: np.ndarray) -> dict[str, np.ndarray]:
    """PEP8 alias for :func:`M2_four_objects`."""
    return M2_four_objects(M2_raw)


def M2_reconstruct(parts: dict[str, np.ndarray]) -> np.ndarray:
    return parts["sym_traceless"] + parts["antisym"] + parts["trace"]


def _O(l: int, m: int) -> float:
    if l < 1 or abs(m) > l:
        raise ValueError("require l>=1 and |m|<=l")
    return math.sqrt((2*l + 1) / (4*math.pi) *
                     math.factorial(l-m) / math.factorial(l+m) /
                     (l*(l+1)))


def _plm(l: int, m: int, mu: np.ndarray) -> np.ndarray:
    """Associated Legendre P_l^m with SciPy's Condon--Shortley convention."""
    return np.asarray(lpmv(m, l, mu), dtype=float)


def _tau_pi(l: int, m: int, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.cos(theta)
    p = _plm(l, m, mu)
    # dP/dmu recurrence, stable at all Gauss-Legendre interior nodes.
    if l == 0:
        dp = np.zeros_like(mu)
    else:
        pm1 = _plm(l-1, m, mu) if l-1 >= abs(m) else np.zeros_like(mu)
        den = mu*mu - 1.0
        dp = (l*mu*p - (l+m)*pm1) / den
    tau = -np.sin(theta) * dp
    if m == 0:
        pi = np.zeros_like(theta)
    else:
        pi = (m / np.sin(theta)) * p
    return tau, pi


def _spherical_bessel_derivatives(l: int, rho: np.ndarray):
    """Return j_l, j'_l and j''_l with a shared analytic small-rho branch."""
    rho = np.asarray(rho, dtype=complex)
    small = np.abs(rho) < 1e-7
    out_j = np.asarray(spherical_jn(l, rho), complex)
    out_jp = np.asarray(spherical_jn(l, rho, derivative=True), complex)
    jpp = np.empty_like(out_j)
    big = ~small
    if np.any(big):
        rr = rho[big]
        # Stable forward-order identity.  The algebraically equivalent ODE
        # form subtracts two O(1/rho) terms for l=1 and loses all digits near
        # the branch threshold.
        jpp[big] = (l*(l-1)*out_j[big]/rr**2
                    - (2*l+1)*spherical_jn(l+1,rr)/rr
                    + spherical_jn(l+2,rr))
    if np.any(small):
        # Construct j_l and both derivatives from one analytic series.  This
        # avoids mixing SciPy values with hand-written derivative orders at
        # rho=0 and makes the switch at 1e-7 continuous.
        rr = rho[small]
        double_factorial = float(math.prod(range(1, 2*l+2, 2)))
        series_coefficients = (
            1.0 / double_factorial,
            -1.0 / (double_factorial * 2.0 * (2*l+3)),
            1.0 / (double_factorial * 8.0 * (2*l+3) * (2*l+5)),
            -1.0 / (double_factorial * 48.0 * (2*l+3) * (2*l+5) * (2*l+7)),
        )
        js = np.zeros_like(rr)
        jps = np.zeros_like(rr)
        jpps = np.zeros_like(rr)
        for n, coefficient in enumerate(series_coefficients):
            power = l + 2*n
            js += coefficient * rr**power
            if power >= 1:
                jps += coefficient * power * rr**(power-1)
            if power >= 2:
                jpps += coefficient * power * (power-1) * rr**(power-2)
        out_j[small] = js
        out_jp[small] = jps
        jpp[small] = jpps
    return out_j, out_jp, jpp


def _riccati_derivatives(l: int, rho: np.ndarray):
    """Return j_l, Psi_l, Psi'_l and Psi''_l using the spec recursion."""
    rho = np.asarray(rho, dtype=complex)
    out_j, out_jp, jpp = _spherical_bessel_derivatives(l, rho)
    psi = rho*out_j
    psip = out_j + rho*out_jp
    psipp = 2.0*out_jp + rho*jpp
    return out_j, psi, psip, psipp


def _spherical_components(Jx, Jy, Jz, theta, phi):
    st, ct = np.sin(theta), np.cos(theta)
    cp, sp = np.cos(phi), np.sin(phi)
    return (st*cp*Jx + st*sp*Jy + ct*Jz,
            ct*cp*Jx + ct*sp*Jy - st*Jz,
            -sp*Jx + cp*Jy)


def grahn_kernel_coefficients(x_mie: float, m_rel: complex, n_max: int,
                              Nu: int = 40, Nth: int = 41, Nph: int = 80,
                              ls: Iterable[int] = (1, 2),
                              return_grid: bool = False) -> dict:
    """Finite-kernel Eq.(15)(16) coefficients for all ``m=-l..l``.

    The host is the explicit ``epsilon_d=epsilon0`` air case of the spec;
    extending to another host only changes ``k`` and the relative current
    factor, not the angular algebra.
    """
    Jx, Jy, Jz, U, Th, Ph, u, th, ph = _moments_grid(x_mie, m_rel, n_max, Nu, Nth, Nph)
    rx, ry, rz = _cartesian_position(U, Th, Ph)
    Jr, Jth, Jph = _spherical_components(Jx, Jy, Jz, Th, Ph)
    dV_scale = 1.0
    result: dict = {"a_E": {}, "a_M": {}, "grid": (Nu, Nth, Nph), "x_mie": x_mie}
    for l in ls:
        jl, psi, psip, psipp = _riccati_derivatives(l, x_mie*U)
        # Effective prefactor includes physical J=-i omega eps0 Jtilde:
        # k^2 eta omega eps0 = k^3, and (-i)^l for a_E, (-i)^(l+2) for a_M.
        base = x_mie**3 / math.sqrt(math.pi*(2*l+1))
        for mm in range(-l, l+1):
            tau, pi = _tau_pi(l, mm, Th)
            phase = np.exp(-1j*mm*Ph)
            norm = _O(l, mm)
            term_e = (psi + psipp) * _plm(l, mm, np.cos(Th)) * Jr
            term_e += (psip/(x_mie*U)) * (tau*Jth - 1j*pi*Jph)
            term_m = jl * (1j*pi*Jth + tau*Jph)
            # U=1e-6 in _moments_grid, so denominator is safe; retain explicit
            # branch for callers that provide a zero-radius grid in helpers.
            if np.any(U == 0):
                term_e = np.where(U == 0, 0.0, term_e)
                term_m = np.where(U == 0, 0.0, term_m)
            ie = _integrate_3d(phase*term_e, u, th, ph)
            im = _integrate_3d(phase*term_m, u, th, ph)
            result["a_E"][(l, mm)] = ((-1j)**l) * base * norm * ie
            result["a_M"][(l, mm)] = ((-1j)**(l+2)) * base * norm * im
    if return_grid:
        result["grid_data"] = (Jx, Jy, Jz, U, Th, Ph, u, th, ph)
    return result


def path_B_coefficients(*args, **kwargs):
    return grahn_kernel_coefficients(*args, **kwargs)


ANALYTIC_BENCHMARK_CASES = (
    "bump_polarized_sphere",
    "double_blob",
    "circulating_current",
    "MQ_m0",
    "MQ_m2",
    "MQ_m1",
)

# P(u) for J=J0*P(u)*(1-|u|^2)^3.  The deterministic asymmetric polynomial
# contains degree 0, 1 and 2 content.  Its curl has all l=1 and l=2 spherical
# harmonics, so every electric and magnetic (l,m) target has a non-zero probe.
_FULL_M_POLYNOMIAL = (
    {(0,0,0):1.0, (1,0,0):0.7, (0,1,0):-0.4, (0,0,1):0.9,
     (2,0,0):0.6, (1,1,0):-0.8, (1,0,1):0.5, (0,2,0):0.3,
     (0,1,1):-0.7, (0,0,2):0.4},
    {(0,0,0):-0.6, (1,0,0):0.2, (0,1,0):1.1, (0,0,1):-0.5,
     (2,0,0):-0.3, (1,1,0):0.9, (1,0,1):0.8, (0,2,0):-0.6,
     (0,1,1):0.7, (0,0,2):-0.2},
    {(0,0,0):0.8, (1,0,0):-0.9, (0,1,0):0.4, (0,0,1):0.3,
     (2,0,0):0.5, (1,1,0):0.6, (1,0,1):-0.7, (0,2,0):0.9,
     (0,1,1):-0.4, (0,0,2):0.2},
)
ANALYTIC_KERNEL_FIXTURES = {
    "bump_polarized_sphere": ({}, {}, {(0,0,0):1.0}),
    "full_m_polynomial_bump": _FULL_M_POLYNOMIAL,
}


def analytic_benchmark_case_names() -> tuple[str, ...]:
    return ANALYTIC_BENCHMARK_CASES


def analytic_kernel_fixture_names() -> tuple[str, ...]:
    return tuple(ANALYTIC_KERNEL_FIXTURES)


def raw_clean_required_targets() -> tuple[tuple[str, int, int], ...]:
    return tuple((branch, l, m)
                 for branch in ("a_E", "a_M")
                 for l in (1, 2) for m in range(-l, l+1))


def _poly_eval(terms, u, v, w):
    value = np.zeros_like(u, dtype=complex)
    for (px, py, pz), coefficient in terms.items():
        value += coefficient * u**px * v**py * w**pz
    return value


def _poly_partial(terms, axis):
    derivative = {}
    for powers, coefficient in terms.items():
        power = powers[axis]
        if power:
            reduced = list(powers)
            reduced[axis] -= 1
            key = tuple(reduced)
            derivative[key] = derivative.get(key, 0.0) + coefficient*power
    return derivative


def _poly_add(*signed_terms):
    result = {}
    for sign, terms in signed_terms:
        for powers, coefficient in terms.items():
            result[powers] = result.get(powers, 0.0) + sign*coefficient
    return {powers: coefficient for powers, coefficient in result.items()
            if coefficient != 0}


def _poly_euler(terms):
    return {powers: coefficient*sum(powers)
            for powers, coefficient in terms.items() if sum(powers)}


def _fixture_polynomial_values(name, u, v, w):
    if name not in ANALYTIC_KERNEL_FIXTURES:
        raise ValueError(f"unregistered analytic current: {name}")
    polynomials = ANALYTIC_KERNEL_FIXTURES[name]
    P = [_poly_eval(terms, u, v, w) for terms in polynomials]
    partial = [[_poly_partial(polynomials[i], axis) for axis in range(3)]
               for i in range(3)]
    div_terms = _poly_add(*[(1.0, partial[i][i]) for i in range(3)])
    curl_terms = (
        _poly_add((1.0, partial[2][1]), (-1.0, partial[1][2])),
        _poly_add((1.0, partial[0][2]), (-1.0, partial[2][0])),
        _poly_add((1.0, partial[1][0]), (-1.0, partial[0][1])),
    )
    A = _poly_eval(div_terms, u, v, w)
    DA = _poly_eval(_poly_euler(div_terms), u, v, w)
    B = P[0]*u + P[1]*v + P[2]*w
    DP = [_poly_eval(_poly_euler(terms), u, v, w)
          for terms in polynomials]
    DB = (DP[0]+P[0])*u + (DP[1]+P[1])*v + (DP[2]+P[2])*w
    curlP = [_poly_eval(terms, u, v, w) for terms in curl_terms]
    return P, A, DA, B, DB, curlP


def _analytic_kernel_fixture_fields(name: str, x, y, z, *, R=1.0, J0=1.0):
    """Evaluate a registered C2 polynomial-bump current and exact derivatives."""
    if R <= 0:
        raise ValueError("R must be positive")
    u, v, w = x/R, y/R, z/R
    s = u*u + v*v + w*w
    q = np.where(s <= 1.0, 1.0-s, 0.0)
    f = q**3
    P, A, DA, B, DB, curlP = _fixture_polynomial_values(name, u, v, w)
    divJ = J0/R * (A*f - 6.0*q**2*B)
    r_d_divJ = J0/R * (DA*f - 6.0*A*s*q**2
                        + 24.0*s*q*B - 6.0*q**2*DB)
    gradf = (-6.0*q**2*u, -6.0*q**2*v, -6.0*q**2*w)
    gradf_cross_P = (
        gradf[1]*P[2] - gradf[2]*P[1],
        gradf[2]*P[0] - gradf[0]*P[2],
        gradf[0]*P[1] - gradf[1]*P[0],
    )
    curlJ = tuple(J0/R * (curlP[i]*f + gradf_cross_P[i])
                  for i in range(3))
    J = tuple(J0*P[i]*f for i in range(3))
    return {"J": J, "divJ": divJ, "r_d_divJ": r_d_divJ,
            "curlJ": curlJ, "support_radius": R}


def analytic_bump_kernel_coefficients(k: float, *, form: str = "clean",
                                      R: float = 1.0, J0: complex = 1.0,
                                      Nu: int = 40, Nth: int = 41, Nph: int = 80,
                                      ls: Iterable[int] = (1, 2),
                                      analytic_current: str = "bump_polarized_sphere") -> dict:
    """Eq.(13)(14) or Eq.(15)(16) for a registered C2 bump current.

    Every fixture supplies analytic divergence, radial divergence derivative,
    and curl; no finite differences or omitted surface distributions occur.
    ``form='raw'`` uses analytic divergence/curl derivatives, never finite
    differences.  ``form='clean'`` uses the integrated-by-parts kernels.
    """
    if form not in ("raw", "clean"):
        raise ValueError("form must be 'raw' or 'clean'")
    from numpy.polynomial.legendre import leggauss
    xr, wr = leggauss(Nu); r = .5*(xr+1)*R; wr=.5*R*wr
    mu, wm = leggauss(Nth); th=np.arccos(mu)
    ph=np.linspace(0,2*math.pi,Nph,endpoint=False); wp=2*math.pi/Nph
    U,Th,Ph=np.meshgrid(r,th,ph,indexing="ij")
    W=wr[:,None,None]*wm[None,:,None]*wp*U**2
    X=U*np.sin(Th)*np.cos(Ph); Y=U*np.sin(Th)*np.sin(Ph); Z=U*np.cos(Th)
    fields = _analytic_kernel_fixture_fields(
        analytic_current, X, Y, Z, R=R, J0=J0
    )
    Jx,Jy,Jz=fields["J"]
    Jr,Jth,Jph=_spherical_components(Jx,Jy,Jz,Th,Ph)
    divJ=fields["divJ"]
    r_d_div=fields["r_d_divJ"]
    curlx,curly,curlz=fields["curlJ"]
    r_dot_curl=X*curlx+Y*curly+Z*curlz
    out={"a_E":{},"a_M":{},"grid":(Nu,Nth,Nph),"form":form,"k":k,
         "analytic_current":analytic_current}
    integ=lambda z: complex(np.sum(z*W))
    for l in ls:
        jl,psi,psip,psipp=_riccati_derivatives(l,k*U)
        for mm in range(-l,l+1):
            if form == "raw":
                Ylm=np.conjugate(sph_harm_y(l,mm,Th,Ph))
                den=math.sqrt(math.pi*(2*l+1)*l*(l+1))
                ie=integ(Ylm*jl*(k**2*(X*Jx+Y*Jy+Z*Jz)+2*divJ+r_d_div))
                im=integ(Ylm*jl*r_dot_curl)
                out["a_E"][(l,mm)]=(-1j)**(l-1)*k/den*ie
                out["a_M"][(l,mm)]=(-1j)**(l-1)*k**2/den*im
            else:
                tau,pi=_tau_pi(l,mm,Th); phase=np.exp(-1j*mm*Ph)
                den=math.sqrt(math.pi*(2*l+1)); norm=_O(l,mm)
                ie=integ(phase*((psi+psipp)*_plm(l,mm,np.cos(Th))*Jr+
                                psip/(k*U)*(tau*Jth-1j*pi*Jph)))
                im=integ(phase*jl*(1j*pi*Jth+tau*Jph))
                out["a_E"][(l,mm)]=(-1j)**(l-1)*k**2*norm/den*ie
                out["a_M"][(l,mm)]=(-1j)**(l+1)*k**2*norm/den*im
    return out


def grahn_raw_direct_coefficients(k: float, **kwargs):
    """Fail-closed Eq.(13)(14) adapter for registered analytic currents."""
    analytic_current = kwargs.pop("analytic_current", None)
    if analytic_current not in ANALYTIC_KERNEL_FIXTURES:
        raise ValueError(
            "Eq.(13)(14) requires a registered analytic_current; "
            f"got {analytic_current!r}"
        )
    return analytic_bump_kernel_coefficients(
        k, form="raw", analytic_current=analytic_current, **kwargs
    )


def raw_clean_equivalence_gate(k: float = 0.3, *, Nu: int = 28,
                               Nth: int = 29, Nph: int = 56,
                               fixtures: Iterable[str] | None = None,
                               relative_tolerance: float = 1e-8,
                               absolute_zero: float = 1e-8,
                               signal_floor: float = 1e-7) -> dict:
    """Compare Eq.(13)/(14) and Eq.(15)/(16) over the full l<=2 matrix."""
    names = tuple(fixtures) if fixtures is not None else analytic_kernel_fixture_names()
    required = raw_clean_required_targets()
    observations = []
    coverage = {}
    for name in names:
        raw = grahn_raw_direct_coefficients(
            k, analytic_current=name, Nu=Nu, Nth=Nth, Nph=Nph
        )
        clean = analytic_bump_kernel_coefficients(
            k, form="clean", analytic_current=name, Nu=Nu, Nth=Nth, Nph=Nph
        )
        for branch, l, m in required:
            got, target = raw[branch][(l,m)], clean[branch][(l,m)]
            signal = max(abs(got), abs(target))
            if signal >= signal_floor:
                mode = "relative"
                error = abs(got-target)/max(abs(target), 1e-30)
                threshold = relative_tolerance
            else:
                mode = "absolute_zero"
                error = max(abs(got), abs(target))
                threshold = absolute_zero
            item = {"fixture":name, "branch":branch, "l":l, "m":m,
                    "raw":got, "clean":target, "signal":float(signal),
                    "mode":mode, "error":float(error),
                    "threshold":float(threshold),
                    "status":"PASS" if error <= threshold else "FAIL"}
            observations.append(item)
            key = f"{branch}:{l}:{m}"
            if key not in coverage or signal > coverage[key]["signal"]:
                coverage[key] = item
    expected_keys = {f"{branch}:{l}:{m}" for branch,l,m in required}
    covered_keys = {key for key,item in coverage.items()
                    if item["signal"] >= signal_floor
                    and item["mode"] == "relative"
                    and item["status"] == "PASS"}
    dark_ok = all(item["status"] == "PASS" for item in observations
                  if item["mode"] == "absolute_zero")
    missing = sorted(expected_keys-covered_keys)
    return {"status":"PASS" if not missing and dark_ok else "BLOCKED",
            "required_count":len(expected_keys), "covered_count":len(covered_keys),
            "missing_targets":missing, "coverage":coverage,
            "observations":observations, "fixtures":names,
            "relative_tolerance":relative_tolerance,
            "absolute_zero":absolute_zero, "signal_floor":signal_floor}


def grahn_tensor_coefficients(x_mie: float, m_rel: complex, n_max: int,
                              Nu: int = 40, Nth: int = 41, Nph: int = 80,
                              p_only_switch: bool = False,
                              q_for_mapping: str = "stf") -> dict:
    """Path-A no-kernel moments mapped by Grahn (39)--(48).

    Grahn's source symbol ``Q`` is the raw second-order current moment
    ``M2_raw``.  Equations (39)--(41) annihilate its trace and antisymmetric
    parts, so their E2 values may equivalently be evaluated with ``M2_stf``.
    Alaee's long-wave tensor ``Qe=6*M2_stf`` is a different normalization and
    is deliberately rejected here.  Equations (47)--(48) always use the raw
    moment's antisymmetric part, independently of the E2 representation.
    """
    Jx, Jy, Jz, U, Th, Ph, u, th, ph = _moments_grid(x_mie, m_rel, n_max, Nu, Nth, Nph)
    rx, ry, rz = _cartesian_position(U, Th, Ph)
    p, raw, O = _m3_from_grid(Jx, Jy, Jz, rx, ry, rz, u, th, ph)
    parts = M2_four_objects(raw)
    if q_for_mapping == "qe":
        raise ValueError(
            "q_for_mapping='qe' is not a production input: Alaee Qe is "
            "6*M2_stf; convert it to Qe/6 before the Grahn E2 map"
        )
    if q_for_mapping not in ("raw", "stf"):
        raise ValueError("q_for_mapping must be 'raw' or 'stf'")
    # Grahn Eq. (27) defines the literal source Q as M2_raw.  The E2
    # combinations in Eqs. (39)--(41) project away trace and antisymmetric
    # parts, hence M2_raw and M2_stf are numerically equivalent here.
    Q_e2 = parts["raw"] if q_for_mapping == "raw" else parts["sym_traceless"]
    # epsilon_d is host absolute epsilon.  In normalized units eps_d/EPS0=1.
    C1 = -1j*x_mie**3/(6*math.pi)
    C2 = -x_mie**4/(60*math.pi)
    C3 = -1j*x_mie**5/(210*math.pi)
    ae, am = {}, {}
    # Eq. (39)-(41)
    for mm in (-2, -1, 0, 1, 2):
        if mm == 2 or mm == -2:
            s = 1 if mm == 2 else -1
            ae[(2, mm)] = 3*C2*(Q_e2[0,0]-Q_e2[1,1] - (1j*s)*(Q_e2[0,1]+Q_e2[1,0]))
        elif mm == 1 or mm == -1:
            s = 1 if mm == 1 else -1
            ae[(2, mm)] = 3*C2*(-s*(Q_e2[0,2]+Q_e2[2,0]) + 1j*(Q_e2[1,2]+Q_e2[2,1]))
        else:
            ae[(2, 0)] = math.sqrt(6)*C2*(2*Q_e2[2,2]-Q_e2[0,0]-Q_e2[1,1])
    # Eq. (42)-(43), including the optional p-only switch.
    for mm in (-1, 1):
        s = 1 if mm == 1 else -1
        val = C1*(-s*p[0] + 1j*p[1])
        if not p_only_switch:
            val += 7*C3*(s*(O[0,0,0]+2*O[0,1,1]+2*O[0,2,2]-O[1,1,0]-O[2,2,0])
                         -1j*(O[1,1,1]+2*O[1,0,0]+2*O[1,2,2]-O[0,0,1]-O[2,2,1]))
        ae[(1, mm)] = val
    val0 = math.sqrt(2)*C1*p[2]
    if not p_only_switch:
        val0 += 7*math.sqrt(2)*C3*(O[0,0,2]+O[1,1,2]-O[2,2,2]-2*O[2,0,0]-2*O[2,1,1])
    ae[(1, 0)] = val0
    # Eq. (44)-(46), magnetic quadrupole.
    for mm in (-2, 2):
        s = 1 if mm == 2 else -1
        am[(2, mm)] = 7*C3*(s*(-O[0,0,2]+O[1,1,2]+O[2,0,0]-O[2,1,1])
                            +1j*(O[0,1,2]+O[2,1,0]-2*O[2,0,1]))
    for mm in (-1, 1):
        s = 1 if mm == 1 else -1
        am[(2, mm)] = 7*C3*(-O[0,1,1]+O[0,2,2]+O[1,1,0]-O[2,2,0]
                            -1j*s*(-O[1,0,0]+O[1,2,2]+O[0,0,1]-O[2,1,1]))
    am[(2, 0)] = 7*math.sqrt(6)*1j*C3*(O[0,1,2]-O[1,2,0])
    # Eqs. (47)--(48) consume M2_raw's antisymmetric combinations.  They are
    # intentionally independent of Q_e2 and must never receive STF or Qe.
    for mm in (-1, 1):
        s = 1 if mm == 1 else -1
        am[(1, mm)] = 5*C2*(-raw[0,2]+raw[2,0] - 1j*s*(-raw[1,2]+raw[2,1]))
    am[(1, 0)] = 5*math.sqrt(2)*1j*C2*(-raw[0,1]+raw[1,0])
    return {"a_E": ae, "a_M": am, "moments": {"p": p, "M2": raw, "O": O, **parts},
            "grid": (Nu, Nth, Nph), "x_mie": x_mie, "p_only_switch": p_only_switch,
            "q_for_mapping": q_for_mapping}


def path_A_coefficients(*args, **kwargs):
    return grahn_tensor_coefficients(*args, **kwargs)


def c_sca_from_coefficients(coeffs: dict, k: float, *, all_m: bool = True) -> float:
    """Grahn Eq.(20), normalized by ``lambda_d^2/(2*pi)`` when ``k`` is host k."""
    total = 0.0
    for key in ("a_E", "a_M"):
        for (l, mm), val in coeffs[key].items():
            if not all_m and abs(mm) != 1:
                continue
            total += (2*l+1)*abs(val)**2
    return 0.5*float(total)


def mie_per_m_coefficients(x_mie: float, m_rel: complex, n_max: int = 2) -> dict:
    a, b = mie_coefficients(x_mie, m_rel, n_max)
    ae, am = {}, {}
    for l in range(1, n_max+1):
        al, bl = a[l-1], b[l-1]
        # spec per-m phase target: a_E(l,+1)=-a_l, a_E(l,-1)=+a_l;
        # a_M(l,+/-1)=-b_l.
        ae[(l, 1)] = -al; ae[(l, -1)] = al
        am[(l, 1)] = -bl; am[(l, -1)] = -bl
    return {"a_E": ae, "a_M": am}


def mie_normalized_channels(x_mie: float, m_rel: complex, n_max: int = 2) -> dict:
    a, b = mie_coefficients(x_mie, m_rel, n_max)
    # Mie C_sca=2π/k² Σ and λ²/(2π)=2π/k², so the canonical ratio is
    # exactly Σ.  Grahn Eq.(20) carries π/k² and its two incident m=±1
    # coefficients supply the compensating factor of two.
    return {"ED": 3*abs(a[0])**2, "MD": 3*abs(b[0])**2,
            "EQ": 5*abs(a[1])**2 if n_max >= 2 else 0.0,
            "MQ": 5*abs(b[1])**2 if n_max >= 2 else 0.0}


def grahn_optical_theorem(coeffs: dict, k: float, l_max: int | None = None) -> tuple[float, float]:
    """Grahn Eq.(22) versus Eq.(20), both normalized by λ²/(2π)."""
    ext_sum = 0.0
    for (l, mm), v in coeffs["a_E"].items():
        if mm in (-1, 1) and (l_max is None or l <= l_max):
            ext_sum += (2*l+1)*np.real(mm*v + coeffs["a_M"].get((l, mm), 0.0))
    cext_norm = -0.5*float(ext_sum)
    csca_norm = c_sca_from_coefficients(coeffs, k, all_m=False)
    return cext_norm, csca_norm


def miepython_gate(x_mie: float = 0.5, m_rel: complex = 2.5) -> dict:
    """Explicit independent-library gate; missing ``miepython`` is BLOCKED."""
    if importlib.util.find_spec("miepython") is None:
        return {"status": "BLOCKED", "reason": "miepython is not installed"}
    import miepython
    # API changed from ``mie(m,d)`` to ``efficiencies(m,d)``; use whichever is
    # present and compare Q_sca to the repository's independent coefficients.
    if hasattr(miepython, "efficiencies_mx"):
        qext, qsca, qback, g = miepython.efficiencies_mx(m_rel, x_mie)
    else:
        # miepython 2.x/3.x public dimensional API: d=2a, lambda=2*pi*a/x.
        qext, qsca, qback, g = miepython.efficiencies(m_rel, 2.0, 2*math.pi/x_mie)
    from baseline_mie import Q_sca
    ours = Q_sca(x_mie, m_rel)
    rel = abs(float(qsca)-ours)/max(abs(ours), 1e-30)
    return {"status": "PASS" if rel < 1e-8 else "FAIL", "qsca_miepython": float(qsca),
            "qsca_baseline": float(ours), "relative_error": float(rel)}


def analytic_bump_current(case: str, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                          R: float = 1.0, J0: complex = 1.0,
                          d: float | None = None):
    """Analytic compact-support benchmark currents from the v4 spec."""
    if d is None:
        d = 2.5*R
    if case == "double_blob":
        rp = np.sqrt(x*x+y*y+(z-d/2)**2)
        rm = np.sqrt(x*x+y*y+(z+d/2)**2)
        fp = np.where(rp <= R, (1-(rp/R)**2)**3, 0.0)
        fm = np.where(rm <= R, (1-(rm/R)**2)**3, 0.0)
        return (np.zeros_like(x, complex), np.zeros_like(x, complex),
                J0*(fp-fm))
    r = np.sqrt(x*x+y*y+z*z)
    f = np.where(r <= R, (1-(r/R)**2)**3, 0.0)
    if case == "bump_polarized_sphere":
        return np.zeros_like(x, complex), np.zeros_like(x, complex), J0*f
    if case == "circulating_current":
        return -J0*y*f, J0*x*f, np.zeros_like(x, complex)
    if case == "MQ_m0":
        return -J0*z*y*f, J0*z*x*f, np.zeros_like(x, complex)
    if case == "MQ_m2":
        return np.zeros_like(x, complex), np.zeros_like(x, complex), J0*(x*x-y*y)*f
    if case == "MQ_m1":
        return J0*(y*y-z*z)*f, np.zeros_like(x, complex), np.zeros_like(x, complex)
    raise ValueError(f"unknown analytic benchmark: {case}")


def analytic_bump_closed_forms(R: float = 1.0, J0: complex = 1.0,
                               omega: float = 1.0,
                               d: float | None = None) -> dict:
    if d is None:
        d = 2.5*R
    I0 = 64*math.pi*R**3/315
    I2 = 64*math.pi*R**5/3465
    I4 = 64*math.pi*R**7/15015
    I22 = 64*math.pi*R**7/45045
    return {"I0": I0, "I2": I2, "I4": I4, "I22": I22,
            "p_z": 1j*J0*I0/omega,
            "double_blob_M2_zz": 1j*J0*d*I0/omega,
            "m_z": J0*I2,
            "MQ_m0_combo": -1j*J0*I22/omega,
            "MQ_m2_combo": 1j*J0*(I4-I22)/omega,
            "MQ_m1_combo": 1j*J0*(I22-I4)/omega}


def _local_sphere_quadrature(R, Nu, Nth, Nph, *, center_z=0.0):
    from numpy.polynomial.legendre import leggauss
    xu, wu = leggauss(Nu)
    u, wu = 0.5*(xu+1)*R, 0.5*R*wu
    mu, wm = leggauss(Nth)
    th = np.arccos(mu)
    ph = np.linspace(0, 2*math.pi, Nph, endpoint=False)
    U, Th, Ph = np.meshgrid(u, th, ph, indexing="ij")
    X = U*np.sin(Th)*np.cos(Ph)
    Y = U*np.sin(Th)*np.sin(Ph)
    Z = U*np.cos(Th) + center_z
    W = (wu[:,None,None]*wm[None,:,None]
         *(2*math.pi/Nph)*U**2)
    f = (1-(U/R)**2)**3
    return X, Y, Z, W, f


def integrate_analytic_current(case: str, *, R: float = 1.0,
                               J0: complex = 1.0, d: float | None = None,
                               omega: float = 1.0, Nu: int = 40,
                               Nth: int = 41, Nph: int = 80) -> dict:
    """Integrate one registered benchmark over its exact support domain."""
    if case not in ANALYTIC_BENCHMARK_CASES:
        raise ValueError(f"unknown analytic benchmark: {case}")
    if R <= 0 or omega == 0:
        raise ValueError("R must be positive and omega must be non-zero")
    if d is None:
        d = 2.5*R
    samples = []
    if case == "double_blob":
        for center_z, sign in ((d/2, 1.0), (-d/2, -1.0)):
            X,Y,Z,W,f = _local_sphere_quadrature(
                R, Nu, Nth, Nph, center_z=center_z
            )
            zero = np.zeros_like(X, complex)
            samples.append(((zero, zero, sign*J0*f), (X,Y,Z), W))
        integration_domain = "two_local_spheres"
    else:
        X,Y,Z,W,_ = _local_sphere_quadrature(R, Nu, Nth, Nph)
        samples.append((analytic_bump_current(case, X, Y, Z, R, J0, d),
                        (X,Y,Z), W))
        integration_domain = "origin_centered_sphere"

    def integ(component, coordinate_factors=()):
        total = 0.0j
        for currents, coordinates, weights in samples:
            value = currents[component]
            for index in coordinate_factors:
                value = value*coordinates[index]
            total += np.sum(value*weights)
        return total

    scale = 1j/omega
    p = scale*np.array([integ(a) for a in range(3)], complex)
    M2 = scale*np.array([[integ(a,(b,)) for b in range(3)]
                         for a in range(3)], complex)
    O = 0.5*scale*np.array([[[integ(a,(b,c)) for c in range(3)]
                             for b in range(3)] for a in range(3)], complex)
    result = {"p":p, "M2":M2, "O":O, "grid":(Nu,Nth,Nph),
              "closed":analytic_bump_closed_forms(R,J0,omega,d),
              "geometry":{"R":R, "d":d, "nonoverlap":d >= 2*R,
                          "domain_half_width":d/2+R,
                          "integration_domain":integration_domain}}
    result["targets"] = _analytic_benchmark_targets(case, result)
    return result


def _analytic_benchmark_targets(case: str, result: dict) -> dict:
    p, M2, O, closed = (result[key] for key in ("p","M2","O","closed"))
    targets = {}

    def add(name, value, expected, mode):
        targets[name] = {"value":complex(value), "expected":complex(expected),
                         "mode":mode,
                         "tolerance":1e-3 if mode == "relative" else 1e-8}

    if case in ("bump_polarized_sphere", "double_blob", "circulating_current"):
        for index, axis in enumerate("xyz"):
            expected = closed["p_z"] if case == "bump_polarized_sphere" and axis == "z" else 0.0
            add(f"p_{axis}", p[index], expected,
                "relative" if expected != 0 else "absolute_zero")
    if case == "bump_polarized_sphere":
        for a in range(3):
            for b in range(3):
                add(f"M2_{a}{b}", M2[a,b], 0.0, "absolute_zero")
    elif case == "double_blob":
        for a in range(3):
            for b in range(3):
                expected = closed["double_blob_M2_zz"] if (a,b) == (2,2) else 0.0
                add(f"M2_{a}{b}", M2[a,b], expected,
                    "relative" if expected != 0 else "absolute_zero")
    elif case == "circulating_current":
        add("m_z", .5j*(M2[0,1]-M2[1,0]), closed["m_z"], "relative")
        add("M2_symmetric_max", np.max(np.abs(M2+M2.T)), 0.0,
            "absolute_zero")
    elif case == "MQ_m0":
        add("MQ_m0_combo", O[0,1,2]-O[1,2,0],
            closed["MQ_m0_combo"], "relative")
        add("MQ_m0_zero_companion", O[0,1,2]+O[1,2,0], 0.0,
            "absolute_zero")
    elif case == "MQ_m2":
        add("MQ_m2_combo", O[2,0,0]-O[2,1,1],
            closed["MQ_m2_combo"], "relative")
        add("MQ_m2_zero_companion",
            O[0,1,2]+O[2,1,0]-2*O[2,0,1], 0.0, "absolute_zero")
    elif case == "MQ_m1":
        add("MQ_m1_combo", -O[0,1,1]+O[0,2,2],
            closed["MQ_m1_combo"], "relative")
        add("MQ_m1_zero_companion",
            -O[1,0,0]+O[1,2,2]+O[0,0,1]-O[2,2,1],
            0.0, "absolute_zero")
    return targets


def far_field_projection(a_n: np.ndarray, b_n: np.ndarray, k: float, radius: float = 2.0,
                         Ntheta: int = 36, Nphi: int = 72) -> dict:
    """Independent angular Eq.(3)(4) projection of a Mie scattered field.

    A tangential outgoing field is first synthesized from the centered-sphere
    per-m targets in an independently constructed VSH basis and then inverted
    by Gauss--Legendre/periodic angular projection.  The basis uses
    ``sph_harm_y`` directly and ``h_l^(1)=spherical_jn+i*spherical_yn``; it does
    not reuse the path-B ``P/tau/pi`` kernels.
    """
    a_n, b_n = np.asarray(a_n), np.asarray(b_n)
    target_e, target_m = {}, {}
    for l in range(1, min(len(a_n),len(b_n))+1):
        target_e[(l,1)] = -a_n[l-1]; target_e[(l,-1)] = a_n[l-1]
        target_m[(l,1)] = -b_n[l-1]; target_m[(l,-1)] = -b_n[l-1]
    from numpy.polynomial.legendre import leggauss
    mu, wm = leggauss(Ntheta); theta=np.arccos(mu)
    phi=np.linspace(0,2*math.pi,Nphi,endpoint=False); wp=2*math.pi/Nphi
    Th,Ph=np.meshgrid(theta,phi,indexing="ij")
    W=wm[:,None]*wp

    def basis(l,mm):
        Y=sph_harm_y(l,mm,Th,Ph)
        # Independent analytic dY/dtheta from normalized associated Legendre.
        P=lpmv(mm,l,np.cos(Th))
        Pm1=lpmv(mm,l-1,np.cos(Th)) if l-1 >= abs(mm) else np.zeros_like(Th)
        dP=(-np.sin(Th))*(l*np.cos(Th)*P-(l+mm)*Pm1)/(np.cos(Th)**2-1)
        norm=math.sqrt((2*l+1)/(4*math.pi)*math.factorial(l-mm)/math.factorial(l+mm))
        dY=norm*dP*np.exp(1j*mm*Ph)
        q=math.sqrt(l*(l+1))
        Xth=-(mm/np.sin(Th))*Y/q
        Xph=-1j*dY/q
        # Z=rhat x X: Ztheta=-Xphi, Zphi=Xtheta.
        return Xth,Xph,-Xph,Xth

    Eth=np.zeros_like(Th,complex); Eph=np.zeros_like(Th,complex)
    radial={}
    z=k*radius
    for l in range(1,min(len(a_n),len(b_n))+1):
        h=spherical_jn(l,z)+1j*spherical_yn(l,z)
        hp=spherical_jn(l,z,derivative=True)+1j*spherical_yn(l,z,derivative=True)
        nrad=(h+z*hp)/z
        radial[l]=(h,nrad)
        for mm in (-1,1):
            Xth,Xph,Zth,Zph=basis(l,mm)
            Eth += target_m[(l,mm)]*h*Xth + target_e[(l,mm)]*nrad*Zth
            Eph += target_m[(l,mm)]*h*Xph + target_e[(l,mm)]*nrad*Zph
    ae,am={},{}
    for l in range(1,min(len(a_n),len(b_n))+1):
        h,nrad=radial[l]
        for mm in (-1,1):
            Xth,Xph,Zth,Zph=basis(l,mm)
            am[(l,mm)]=complex(np.sum((np.conj(Xth)*Eth+np.conj(Xph)*Eph)*W)/h)
            ae[(l,mm)]=complex(np.sum((np.conj(Zth)*Eth+np.conj(Zph)*Eph)*W)/nrad)
    return {"a_E":ae,"a_M":am,"target_a_E":target_e,"target_a_M":target_m,
            "radius":radius,"angular_grid":(Ntheta,Nphi)}


__all__ = ["M2_four_objects", "m2_four_objects", "M2_reconstruct",
           "grahn_kernel_coefficients", "path_B_coefficients",
           "grahn_tensor_coefficients", "path_A_coefficients",
           "c_sca_from_coefficients", "mie_per_m_coefficients",
           "mie_normalized_channels", "grahn_optical_theorem",
           "miepython_gate", "analytic_bump_current", "analytic_bump_closed_forms",
           "integrate_analytic_current", "analytic_bump_kernel_coefficients",
           "grahn_raw_direct_coefficients", "raw_clean_equivalence_gate",
           "analytic_benchmark_case_names", "analytic_kernel_fixture_names",
           "raw_clean_required_targets", "far_field_projection"]
