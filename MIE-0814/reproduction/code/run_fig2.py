# -*- coding: utf-8 -*-
"""Run Alaee 2018 Fig.2(a,b) with explicit gold-material provenance.

The independent variable is Alaee's ``s = 2a/lambda``.  For the gold
panel ``a=250 nm`` and therefore ``lambda_nm = 500/s``; interpolation is
performed in wavelength space and never extrapolates.  Mie and Table-2
values are computed for the same complex refractive index at every point.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from baseline_mie import mie_coefficients, wiscombe_nmax  # noqa: E402
from multipole_moments import c_sca_from_multipoles, table2_multipole_moments  # noqa: E402

ROOT = _HERE.parent
GOLD_CSV = ROOT / "data" / "gold_epsilon.csv"
DEFAULT_GRID = (40, 41, 80)
MULTIPOLES = ("ED", "MD", "EQ", "MQ")
SOURCES = ("jc", "olmon", "mcpeak")


def _finite_source_rows(source: str):
    source = source.lower()
    if source not in SOURCES:
        raise ValueError(f"unknown gold source: {source!r}")
    with GOLD_CSV.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    out = []
    for row in rows:
        n = float(row[f"{source}_n"])
        k = float(row[f"{source}_k"])
        if math.isfinite(n) and math.isfinite(k):
            out.append((float(row["lambda_nm"]), n, k))
    if len(out) < 2:
        raise ValueError(f"gold source {source} has fewer than two finite samples")
    return np.asarray(out, dtype=float)


def gold_source_range(source: str) -> tuple[float, float]:
    data = _finite_source_rows(source)
    return float(data[0, 0]), float(data[-1, 0])


def interpolate_gold_m(source: str, wavelength_nm: float) -> complex:
    """Linearly interpolate n(lambda), kappa(lambda), rejecting extrapolation."""
    data = _finite_source_rows(source)
    lo, hi = float(data[0, 0]), float(data[-1, 0])
    wavelength_nm = float(wavelength_nm)
    if wavelength_nm < lo - 1e-10 or wavelength_nm > hi + 1e-10:
        raise ValueError(
            f"{source} covers {lo:g}-{hi:g} nm; refusing extrapolation at {wavelength_nm:g} nm"
        )
    n = float(np.interp(wavelength_nm, data[:, 0], data[:, 1]))
    k = float(np.interp(wavelength_nm, data[:, 0], data[:, 2]))
    return complex(n, k)


def mie_multipoles(x_mie: float, m: complex) -> dict[str, float]:
    """Mie per-channel normalized C_sca/(lambda^2/(2 pi))."""
    an, bn = mie_coefficients(x_mie, m, wiscombe_nmax(x_mie))
    return {
        "ED": float(3.0 * abs(an[0]) ** 2),
        "MD": float(3.0 * abs(bn[0]) ** 2),
        "EQ": float(5.0 * abs(an[1]) ** 2),
        "MQ": float(5.0 * abs(bn[1]) ** 2),
    }


def compute_gold_point(x_alaee: float, source: str, grid=DEFAULT_GRID) -> dict:
    """Compute one gold point; both methods use the same interpolated m."""
    x_alaee = float(x_alaee)
    if not 0.2 - 1e-12 <= x_alaee <= 1.0 + 1e-12:
        raise ValueError("Fig.2 x=2a/lambda must lie in [0.2, 1.0]")
    wavelength_nm = 500.0 / x_alaee
    m = interpolate_gold_m(source, wavelength_nm)
    x_mie = math.pi * x_alaee
    mie = mie_multipoles(x_mie, m)
    moments = table2_multipole_moments(
        x_mie, m, wiscombe_nmax(x_mie), *grid, kernel_k="host"
    )
    exact = c_sca_from_multipoles(moments, x_mie)
    row = {
        "x_alaee": x_alaee,
        "lambda_nm": wavelength_nm,
        "source": source.lower(),
        "n": m.real,
        "kappa": m.imag,
    }
    for key in MULTIPOLES:
        row[f"mie_{key}"] = mie[key]
        row[f"table2_{key}"] = exact[key]
        row[f"abs_err_{key}"] = abs(exact[key] - mie[key])
        row[f"rel_err_{key}"] = abs(exact[key] - mie[key]) / max(mie[key], 1e-300)
    return row


def _valid_x_grid(source: str, points: int = 200) -> np.ndarray:
    lo, hi = gold_source_range(source)
    x_lo = max(0.2, 500.0 / hi)
    x_hi = min(1.0, 500.0 / lo)
    if x_lo > x_hi:
        return np.empty(0)
    return np.linspace(x_lo, x_hi, int(points))


def run_source(source: str, points: int = 200, grid=DEFAULT_GRID,
               progress: bool = True) -> list[dict]:
    """Run all valid x points for a source (no out-of-domain extrapolation)."""
    xs = _valid_x_grid(source, points)
    rows = []
    for i, x in enumerate(xs, 1):
        rows.append(compute_gold_point(float(x), source, grid))
        if progress and (i == 1 or i % 10 == 0 or i == len(xs)):
            print(f"[{source}] {i}/{len(xs)} x={x:.6f} lambda={500/x:.2f} nm", flush=True)
    return rows


def summarize(rows: Iterable[dict]) -> dict:
    rows = list(rows)
    result = {"points": len(rows), "channels": {}}
    for key in MULTIPOLES:
        mie = np.asarray([r[f"mie_{key}"] for r in rows], dtype=float)
        abs_err = np.asarray([r[f"abs_err_{key}"] for r in rows], dtype=float)
        rel = np.asarray([r[f"rel_err_{key}"] for r in rows], dtype=float)
        mask = mie >= 1e-4
        result["channels"][key] = {
            "masked_points": int(np.count_nonzero(~mask)),
            "max_relative_percent": float(np.max(rel[mask]) * 100.0) if np.any(mask) else None,
            "p95_relative_percent": float(np.percentile(rel[mask], 95) * 100.0) if np.any(mask) else None,
            "max_absolute": float(np.max(abs_err)) if len(abs_err) else None,
            "passes": bool(
                np.any(mask)
                and np.max(rel[mask]) < 0.01
                and np.percentile(rel[mask], 95) < 0.001
                and np.max(abs_err) < 2e-3
            ),
        }
    result["passes_all_channels"] = all(v["passes"] for v in result["channels"].values())
    return result


def save_rows(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["x_alaee", "lambda_nm", "source", "n", "kappa"]
    for prefix in ("mie", "table2", "abs_err", "rel_err"):
        fields.extend(f"{prefix}_{key}" for key in MULTIPOLES)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=SOURCES, default="olmon")
    parser.add_argument("--points", type=int, default=200)
    parser.add_argument("--grid", nargs=3, type=int, default=DEFAULT_GRID)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args()
    rows = run_source(args.source, args.points, tuple(args.grid))
    output = args.output or (ROOT / "data" / f"fig2_gold_{args.source}.csv")
    summary = args.summary or (ROOT / "data" / f"fig2_gold_{args.source}_summary.json")
    save_rows(output, rows)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(summarize(rows), indent=2), encoding="utf-8")
    print(json.dumps(summarize(rows), indent=2))


if __name__ == "__main__":
    main()
