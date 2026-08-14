"""B34: independent third-party Mie/MENP cross-validation.

This is an additive audit script.  It imports the frozen implementation but
does not modify it; all outputs are new files under ``data``/``codex-prompts``.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TP = ROOT / "data" / "third_party"
OUT = ROOT / "data"
sys_path = str(ROOT / "code")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
from baseline_mie import mie_coefficients  # noqa: E402
from multipole_moments import table2_multipole_moments, c_sca_from_multipoles  # noqa: E402

CHANNELS = ["ED", "MD", "EQ", "MQ"]
TIDY_FILES = {
    "ED": "mie_electric_dipole",
    "MD": "mie_magnetic_dipole",
    "EQ": "mie_electric_quadrupole",
    "MQ": "mie_magnetic_quadrupole",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def green2008() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    pat = re.compile(r"\s*([0-9.]+(?:e[+-]?\d+)?)\s+([0-9.]+(?:e[+-]?\d+)?)\s+([0-9.]+(?:e[+-]?\d+)?)\s*$", re.I)
    for line in (TP / "Si-Green-2008.yml").read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if m:
            rows.append(tuple(map(float, m.groups())))
    a = np.asarray(rows)
    return a[:, 0], a[:, 1], a[:, 2]


def mie_channels(radius_um: float, wavelengths_um: np.ndarray, n: np.ndarray, kappa: np.ndarray):
    vals = {c: [] for c in CHANNELS}
    for wl, nr, ki in zip(wavelengths_um, n, kappa):
        x = 2 * np.pi * radius_um / wl
        an, bn = mie_coefficients(x, complex(nr, ki), 8)
        coeff = [an[0], bn[0], an[1], bn[1]]
        for c, q, order in zip(CHANNELS, coeff, [1, 1, 2, 2]):
            vals[c].append(2.0 / x**2 * (2 * order + 1) * abs(q) ** 2)
    return {c: np.asarray(v) for c, v in vals.items()}


def rel_stats(ours: np.ndarray, ref: np.ndarray, support_floor: float = 0.0):
    denom = np.maximum(np.abs(ref), 1e-30)
    err = np.abs(ours - ref) / denom
    mask = np.abs(ref) >= support_floor
    use = err[mask] if np.any(mask) else err
    return {
        "n": int(err.size),
        "n_support": int(mask.sum()),
        "max": float(err.max()),
        "p95": float(np.percentile(err, 95)),
        "mean": float(err.mean()),
        "support_max": float(use.max()),
        "support_p95": float(np.percentile(use, 95)),
        "support_mean": float(use.mean()),
    }


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    # Tidy3D notebook defines radius=0.18 um, c-Si Green2008, 101 wavelengths.
    wl_tidy = np.linspace(1.4, 0.55, 101)
    wl_src, n_src, k_src = green2008()
    n_tidy = np.interp(wl_tidy, wl_src, n_src)
    k_tidy = np.interp(wl_tidy, wl_src, k_src)
    mie_tidy = mie_channels(0.18, wl_tidy, n_tidy, k_tidy)
    rows = []
    for i, wl in enumerate(wl_tidy):
        row = {"wavelength_um": f"{wl:.12g}", "x_axis": f"{2*np.pi*0.18/wl:.12g}", "n": f"{n_tidy[i]:.12g}", "kappa": f"{k_tidy[i]:.12g}"}
        for c in CHANNELS:
            ref = float(np.loadtxt(TP / TIDY_FILES[c])[i])
            row[f"third_party_{c}"] = f"{ref:.12g}"
            row[f"our_mie_{c}"] = f"{mie_tidy[c][i]:.12g}"
            row[f"rel_err_{c}"] = f"{abs(mie_tidy[c][i]-ref)/max(abs(ref),1e-30):.12g}"
        rows.append(row)
    fields = list(rows[0])
    write_csv(OUT / "fig2_cross_validation_tidy3d.csv", rows, fields)

    tidy_stats = {}
    for c in CHANNELS:
        ref = np.loadtxt(TP / TIDY_FILES[c])
        tidy_stats[c] = rel_stats(mie_tidy[c], ref, support_floor=1e-2)

    # Independent Table-2 integral at 11 common points (higher grid than smoke test).
    idxs = np.linspace(0, 100, 11, dtype=int)
    t2_rows = []
    t2_stats = {c: [] for c in CHANNELS}
    for i in idxs:
        wl, nr, ki = wl_tidy[i], n_tidy[i], k_tidy[i]
        x = 2 * np.pi * 0.18 / wl
        mom = table2_multipole_moments(x, complex(nr, ki), 8, 40, 30, 60)
        c2 = c_sca_from_multipoles(mom, x)
        row = {"wavelength_um": f"{wl:.12g}", "x_axis": f"{x:.12g}"}
        for c in CHANNELS:
            row[f"mie_{c}"] = f"{mie_tidy[c][i]:.12g}"
            q2 = float(c2[c] * 2 / x**2)
            row[f"table2_{c}"] = f"{q2:.12g}"
            err = abs(q2 - mie_tidy[c][i]) / max(abs(mie_tidy[c][i]), 1e-30)
            row[f"rel_err_{c}"] = f"{err:.12g}"
            t2_stats[c].append(err)
        t2_rows.append(row)
    write_csv(OUT / "fig2_cross_validation_table2_vs_mie.csv", t2_rows, list(t2_rows[0]))
    t2_summary = {}
    for c in CHANNELS:
        e = np.asarray(t2_stats[c])
        t2_summary[c] = {
            "n": int(e.size), "n_support": int(e.size), "max": float(e.max()),
            "p95": float(np.percentile(e, 95)), "mean": float(e.mean()),
            "support_max": float(e.max()), "support_p95": float(np.percentile(e, 95)),
            "support_mean": float(e.mean()),
        }

    # MENP exact/approx CSV: use its companion ENxyzf.mat centre refractive index
    # (the CSV itself has no material columns).  Values are cross sections in m².
    menp = np.loadtxt(TP / "demo_exact.csv", delimiter=",")
    approx = np.loadtxt(TP / "demo_approx.csv", delimiter=",")
    try:
        import h5py
        with h5py.File(TP / "ENxyzf.mat", "r") as h5:
            wl_m = 299792458.0 / h5["f"][0] * 1e9
            nr_m = h5["n_x"][()]["real"][:, 15, 15, 15]
            ki_m = h5["n_x"][()]["imag"][:, 15, 15, 15]
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("h5py is required to read MENP's v7.3 field provenance") from exc
    mie_m = mie_channels(0.1, wl_m / 1000.0, nr_m, ki_m)
    # Convert Q-like channels to physical nm² for comparison with MENP CSV.
    area_nm2 = np.pi * 100.0**2
    menp_rows = []
    for i, wl in enumerate(wl_m):
        row = {"wavelength_nm": f"{wl:.12g}"}
        for j, c in enumerate(CHANNELS):
            ref_nm2 = menp[i, j + 1] * 1e18
            ours_nm2 = mie_m[c][i] * area_nm2
            row[f"menp_exact_{c}_nm2"] = f"{ref_nm2:.12g}"
            row[f"our_mie_{c}_nm2"] = f"{ours_nm2:.12g}"
            row[f"rel_err_{c}"] = f"{abs(ours_nm2-ref_nm2)/max(abs(ref_nm2),1e-30):.12g}"
        menp_rows.append(row)
    write_csv(OUT / "fig2_cross_validation_menp_exact.csv", menp_rows, list(menp_rows[0]))
    menp_stats = {c: rel_stats(mie_m[c] * area_nm2, menp[:, j + 1] * 1e18, support_floor=1.0) for j, c in enumerate(CHANNELS)}
    approx_stats = {c: rel_stats(mie_m[c] * area_nm2, approx[:, j + 1] * 1e18, support_floor=1.0) for j, c in enumerate(CHANNELS)}

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "threshold_declared_before_calculation": {"strict_max_relative_error": 0.01, "support_floor": {"tidy3d": 1e-2, "menp_nm2": 1.0}, "decision_rule": "PASS only if every channel strict max <= 1%; support metrics are diagnostic and cannot upgrade a FAIL"},
        "tidy3d": {"source_branch": "develop (main URL returned 404)", "radius_um": 0.18, "wavelength_um": [1.4, 0.55], "n_points": 101, "axis_semantics": "wavelength in um; notebook wls=np.linspace(1.4,0.55,101); values are scattering efficiency divided by geometric cross section", "stats": tidy_stats},
        "table2_vs_our_mie": {"n_points": 11, "grid": [40, 30, 60], "stats": t2_summary},
        "menp": {"radius_nm": 100, "wavelength_nm": [float(wl_m.min()), float(wl_m.max())], "n_points": int(len(wl_m)), "material": "centre voxel n,k from ENxyzf.mat", "stats_exact": menp_stats, "stats_approx": approx_stats},
        "files_sha256": {p.name: sha256(p) for p in sorted(TP.iterdir()) if p.is_file()},
    }
    (OUT / "fig2_cross_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
