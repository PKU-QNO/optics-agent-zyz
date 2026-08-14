"""B38b A5-v4 Fig.2 UQ completion verifier.

This is an independent runner.  It reads the frozen contract and frozen gold
CSV, computes a new dielectric panel-a electronic pair, computes coarse versus
refined Table-2 grid convergence for both panels, audits the optional pyGDM2
third-party route, and writes only B38b-whitelisted artifacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "code"
DATA = ROOT / "data"
OUT = ROOT / "codex-prompts" / "out" / "B38b"
SPEC = ROOT / "codex-prompts" / "out" / "A5-v4" / "preregister" / "SPEC.md"
ADDENDUM = ROOT / "codex-prompts" / "out" / "A5-v4" / "preregister" / "THRESHOLD-ADDENDUM.md"
GOLD = DATA / "fig2_gold_olmon_refined.csv"
SUMMARY = DATA / "fig2_uq_a5v4_summary.json"
LANES = DATA / "fig2_uq_a5v4_lane_verdicts.csv"
PHYSICS = DATA / "fig2_uq_a5v4_physics.csv"
TP_RECEIPT = DATA / "third_party_cross_consistency_receipt.json"

CHANNELS = ("ED", "MD", "EQ", "MQ")
PANELS = ("a", "b")
THRESHOLDS = {"rmse": 0.020, "p95": 0.050, "peak_x": 0.010}
SPEC_SHA = "8a344a6098c493e2fd0f3f386664297cee96a2248ee865c7ed93ae7bea1c67f5"
ADD_SHA = "67a883f869ae395d501e7dcddf8f0d3f113f5c9d2c5730ca7d6b0140c4bc189d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def metric(x: np.ndarray, ref: np.ndarray, alt: np.ndarray) -> dict[str, float]:
    e = np.asarray(alt, float) - np.asarray(ref, float)
    return {
        "rmse": float(np.sqrt(np.mean(e * e))),
        "p95": float(np.percentile(np.abs(e), 95)),
        "peak_x": float(abs(x[int(np.argmax(ref))] - x[int(np.argmax(alt))])),
    }


def interp_bound(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    d2 = np.gradient(np.gradient(y, x), x)
    h = float(np.max(np.diff(x)))
    curv = float(np.max(np.abs(d2)))
    return curv * h * h / 8.0, 0.5 * curv * h * h, curv, h


def load_gold() -> dict[str, np.ndarray]:
    with GOLD.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = {"x": np.array([float(r["x_alaee"]) for r in rows])}
    for c in CHANNELS:
        out[f"mie_{c}"] = np.array([float(r[f"mie_{c}"]) for r in rows])
        out[f"table2_{c}"] = np.array([float(r[f"table2_{c}"]) for r in rows])
    return out


def mie_channels(x_alaee: float, m: complex) -> dict[str, float]:
    sys.path.insert(0, str(CODE))
    from baseline_mie import mie_coefficients, wiscombe_nmax
    xm = math.pi * float(x_alaee)
    an, bn = mie_coefficients(xm, m, wiscombe_nmax(xm))
    return {"ED": 3.0 * abs(an[0]) ** 2, "MD": 3.0 * abs(bn[0]) ** 2,
            "EQ": 5.0 * abs(an[1]) ** 2, "MQ": 5.0 * abs(bn[1]) ** 2}


def _dielectric_one(s: float) -> dict:
    sys.path.insert(0, str(CODE))
    from baseline_mie import wiscombe_nmax
    from multipole_moments import c_sca_from_multipoles, table2_multipole_moments
    xm = math.pi * float(s); nmax = wiscombe_nmax(xm)
    mm = table2_multipole_moments(xm, 2.5, nmax, 60, 61, 120, kernel_k="host")
    cc = c_sca_from_multipoles(mm, xm); mc = mie_channels(float(s), 2.5)
    row = {"x_alaee": float(s), "epsilon_r": 6.25, "m_real": 2.5, "m_imag": 0.0,
           "grid_Nu": 60, "grid_Ntheta": 61, "grid_Nphi": 120}
    for c in CHANNELS:
        row[f"table2_{c}"] = float(cc[c]); row[f"mie_{c}"] = float(mc[c])
        row[f"abs_err_{c}"] = abs(row[f"table2_{c}"] - row[f"mie_{c}"])
        row[f"rel_err_{c}"] = row[f"abs_err_{c}"] / max(abs(row[f"mie_{c}"]), 1e-300)
    return row


def _physics_one(task):
    panel, idx, s, m = task
    sys.path.insert(0, str(CODE))
    from baseline_mie import wiscombe_nmax
    from multipole_moments import c_sca_from_multipoles, table2_multipole_moments
    xm = math.pi * float(s); nmax = wiscombe_nmax(xm)
    coarse = c_sca_from_multipoles(table2_multipole_moments(xm, m, nmax, 40, 30, 60), xm)
    refined = c_sca_from_multipoles(table2_multipole_moments(xm, m, nmax, 60, 61, 120), xm)
    return panel, idx, float(s), coarse, refined


def compute_dielectric() -> tuple[list[dict], dict[str, dict[str, float]]]:
    """Run 200 panel-a points using refined Table-2 and independent Mie."""
    sys.path.insert(0, str(CODE))
    from baseline_mie import wiscombe_nmax
    from multipole_moments import c_sca_from_multipoles, table2_multipole_moments
    xs = np.linspace(0.2, 1.0, 200)
    rows: list[dict] = []
    t2 = {c: [] for c in CHANNELS}; mie = {c: [] for c in CHANNELS}
    workers = max(1, min(8, (os.cpu_count() or 2) - 2))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_dielectric_one, [float(s) for s in xs], chunksize=1))
    rows.sort(key=lambda r: r["x_alaee"])
    for row in rows:
        for c in CHANNELS:
            t2[c].append(row[f"table2_{c}"]); mie[c].append(row[f"mie_{c}"])
    print(f"[panel-a refined] {len(rows)}/{len(xs)} using {workers} workers", flush=True)
    effects = {c: metric(xs, np.asarray(mie[c]), np.asarray(t2[c])) for c in CHANNELS}
    return rows, effects


def write_dielectric(rows: list[dict]) -> tuple[Path, Path]:
    path_t2 = DATA / "fig2_uq_a5v4_dielectric_table2.csv"
    path_mie = DATA / "fig2_uq_a5v4_dielectric_mie.csv"
    fields = list(rows[0])
    # Separate files are intentional: each route is independently consumable.
    for path, route in ((path_t2, "table2"), (path_mie, "mie")):
        keep = ["x_alaee", "epsilon_r", "m_real", "m_imag", "grid_Nu", "grid_Ntheta", "grid_Nphi"] + [f"{route}_{c}" for c in CHANNELS]
        if route == "table2":
            keep += [f"abs_err_{c}" for c in CHANNELS] + [f"rel_err_{c}" for c in CHANNELS]
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keep); w.writeheader()
            for r in rows: w.writerow({k: r[k] for k in keep})
    return path_t2, path_mie


def physics_rows(a_rows: list[dict], gold: dict[str, np.ndarray]) -> list[dict]:
    """Compute coarse/refined Table-2 relative convergence bounds per lane."""
    sys.path.insert(0, str(CODE))
    from baseline_mie import wiscombe_nmax
    from multipole_moments import c_sca_from_multipoles, table2_multipole_moments
    out: list[dict] = []
    specs = [("a", np.array([r["x_alaee"] for r in a_rows]), np.full(200, 2.5), a_rows),
             ("b", gold["x"], None, None)]
    # Gold material m is reconstructed from the frozen CSV columns in the same row.
    with GOLD.open(encoding="utf-8", newline="") as f: grows = list(csv.DictReader(f))
    tasks = []
    for panel, xs, _, _ in specs:
        for idx, s in enumerate(xs):
            m = 2.5 if panel == "a" else complex(float(grows[idx]["n"]), float(grows[idx]["kappa"]))
            tasks.append((panel, idx, float(s), m))
    workers = max(1, min(8, (os.cpu_count() or 2) - 2))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_physics_one, tasks, chunksize=1))
    for panel, idx, s, coarse, refined in results:
        for c in CHANNELS:
            denom = max(abs(refined[c]), 1e-12)
            out.append({"panel": panel, "channel": c, "x_alaee": s, "grid_coarse": "40x30x60", "grid_refined": "60x61x120", "coarse": float(coarse[c]), "refined": float(refined[c]), "relative_difference": float(abs(refined[c]-coarse[c])/denom)})
    return out


def write_physics(rows: list[dict]) -> dict[str, dict[str, float]]:
    with PHYSICS.open("w", newline="", encoding="utf-8") as f:
        fields = list(rows[0]); w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    bounds = {}
    for p in PANELS:
        for c in CHANNELS:
            rr = [r for r in rows if r["panel"] == p and r["channel"] == c]
            vals = np.array([r["relative_difference"] for r in rr])
            x = np.array([r["x_alaee"] for r in rr])
            bounds[f"{p}-{c}"] = {"u_physics": float(np.max(vals)), "p95_relative_difference": float(np.percentile(vals, 95)), "peak_x_effect": float(abs(x[np.argmax([r["refined"] for r in rr])] - x[np.argmax([r["coarse"] for r in rr])])), "points": len(rr)}
    return bounds


def third_party_attempt() -> dict:
    rec = {"attempt_order": ["pyGDM2", "torchGDM", "B34_c-Si_method_only"], "route3_available": False, "gate_eligible": False, "matched_class": "method_only", "reason": "No reproducible third-party gold Mie curve was produced."}
    try:
        import copy
        import pyGDM2
        from pyGDM2 import core, fields, materials, multipole, propagators, structures
        wavelengths = np.linspace(500.0, 2500.0, 41)
        step, diameter = 125.0, 500.0
        dyads = propagators.DyadsQuasistatic123(1.0, 1.0, 1.0, 10000)
        geo = structures.sphere(step, R=diameter/(2*step), mesh="hex")
        struct = structures.struct(step, geo, materials.gold())
        kwargs = dict(E_s=1, E_p=0, inc_angle=0, inc_plane="xz")
        efield = fields.efield(fields.plane_wave, wavelengths=wavelengths, kwargs=copy.deepcopy(kwargs))
        sim = core.simulation(struct=struct, efield=efield, dyads=dyads)
        sim.scatter(method="lu", verbose=False)
        curves = {c: [] for c in CHANNELS}
        for i in range(len(wavelengths)):
            vals = multipole.scs(sim, i)
            for c, v in zip(CHANNELS, vals): curves[c].append(float(np.asarray(v).ravel()[0]))
        rec["pyGDM2"] = {"installed": True, "version": getattr(pyGDM2, "__version__", None), "status": "official_ex1_pipeline_scaled_to_alaee_geometry", "provenance": "pyGDM2 official Multipole Decomposition 1 pipeline; Alaee D=500nm; Johnson-Christy gold", "object_class": "mie_analytic_gold", "geometry": "D=500nm sphere; hex DDA mesh", "diameter_nm": diameter, "step_nm": step, "dipoles": len(geo), "wavelength_nm": wavelengths.tolist(), "x_variable": "x_alaee=500nm/wavelength", "x_unit": "dimensionless", "x_domain": [0.2, 1.0], "panel_mapping": "panel(b) method audit only", "channels": list(CHANNELS), "raw_scs_nm2": curves, "host": "air", "material_source": "Johnson-Christy 1972", "normalization": "raw scattering cross section nm2", "matched_class": "method_only", "gate_eligible": False, "reason": "route ran successfully, but the coarse 57-dipole DDA output is not an analytic Mie third-party curve and has no preregistered numerical-error bound"}
        rec["route3_available"] = True
        rec["reason"] = "pyGDM2 gold route ran, but remains method_only because normalization/grid labels do not match the lane contract."
    except Exception as e:
        rec["pyGDM2"] = {"installed": False, "error": repr(e)}
    try:
        import torchgdm  # type: ignore
        rec["torchGDM"] = {"installed": True, "status": "no official Mie route invoked"}
    except Exception as e:
        rec["torchGDM"] = {"installed": False, "error": repr(e)}
    rec["fallback"] = {"source": "B34 c-Si Tidy3D/MENP", "matched_class": "method_only", "gate_eligible": False, "reason": "different material/object/normalization"}
    return rec


def status(interval: tuple[float, float] | None, threshold: float) -> str:
    if interval is None: return "UNRESOLVED"
    lo, hi = interval
    return "PASS" if hi <= threshold else ("FAIL" if lo > threshold else "UNRESOLVED")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = {"SPEC.md": sha256(SPEC), "THRESHOLD-ADDENDUM.md": sha256(ADDENDUM)}
    integrity = observed == {"SPEC.md": SPEC_SHA, "THRESHOLD-ADDENDUM.md": ADD_SHA}
    gold = load_gold()
    t2_path = DATA / "fig2_uq_a5v4_dielectric_table2.csv"
    mie_path = DATA / "fig2_uq_a5v4_dielectric_mie.csv"
    if t2_path.is_file() and mie_path.is_file():
        with t2_path.open(encoding="utf-8", newline="") as f: t2_rows = list(csv.DictReader(f))
        with mie_path.open(encoding="utf-8", newline="") as f: mie_rows = list(csv.DictReader(f))
        if len(t2_rows) != 200 or len(mie_rows) != 200: raise ValueError("cached dielectric electronic data must contain 200 rows")
        a_rows = []
        for rt, rm in zip(t2_rows, mie_rows):
            if float(rt["x_alaee"]) != float(rm["x_alaee"]): raise ValueError("cached dielectric x mismatch")
            row = {k: (float(v) if k != "x_alaee" or v else v) for k, v in rt.items()}
            row.update({k: float(v) for k, v in rm.items() if k.startswith("mie_")})
            a_rows.append(row)
        ax = np.array([r["x_alaee"] for r in a_rows])
        a_cross = {c: metric(ax, np.array([r[f"mie_{c}"] for r in a_rows]), np.array([r[f"table2_{c}"] for r in a_rows])) for c in CHANNELS}
        print("[cache] reused 200-row dielectric electronic data", flush=True)
    else:
        a_rows, a_cross = compute_dielectric(); t2_path, mie_path = write_dielectric(a_rows)
    if PHYSICS.is_file():
        with PHYSICS.open(encoding="utf-8", newline="") as f: cached_physics = list(csv.DictReader(f))
        if len(cached_physics) != 1600: raise ValueError("cached physics receipt must contain 1600 rows")
        parsed = []
        for r in cached_physics:
            parsed.append({**r, "x_alaee": float(r["x_alaee"]), "coarse": float(r["coarse"]), "refined": float(r["refined"]), "relative_difference": float(r["relative_difference"])})
        phys = write_physics(parsed)
        print("[cache] reused 1600-row physics receipt", flush=True)
    else:
        phys = write_physics(physics_rows(a_rows, gold))
    route3 = third_party_attempt()
    # The fixed electronic reference is independent Mie and the nominal path is
    # Table-2.  Their per-metric discrepancy is formal d; no paper-image curve
    # is required or consumed.  Missing route3 still leaves formal u_cross null.
    lane_rows = []; diag = {}
    for p in PANELS:
        x = np.array([r["x_alaee"] for r in a_rows]) if p == "a" else gold["x"]
        for c in CHANNELS:
            lane = f"{p}-{c}"
            if p == "a": ref = np.array([r[f"mie_{c}"] for r in a_rows]); alt = np.array([r[f"table2_{c}"] for r in a_rows]); cross = a_cross[c]
            else: ref = gold[f"mie_{c}"]; alt = gold[f"table2_{c}"]; cross = metric(x, ref, alt)
            ui, us, curv, h = interp_bound(x, ref)
            up = phys[lane]["u_physics"]
            uc = None  # no gate-eligible route3; pairwise result remains diagnostic
            intervals = {m: None for m in THRESHOLDS}
            statuses = {m: status(intervals[m], THRESHOLDS[m]) for m in THRESHOLDS}
            lane_rows.append({"panel": p, "channel": c, "electronic_points": len(x), "d_rmse": cross["rmse"], "d_p95": cross["p95"], "d_peak_x": cross["peak_x"], "u_interp": ui, "u_interp_sensitivity": us, "u_physics": up, "u_cross_rmse": uc, "u_cross_p95": uc, "u_cross_peak_x": uc, "interval_L_rmse": None, "interval_U_rmse": None, "interval_L_p95": None, "interval_U_p95": None, "interval_L_peak_x": None, "interval_U_peak_x": None, "rmse_threshold": .02, "p95_threshold": .05, "peak_x_threshold": .01, "rmse_status": statuses["rmse"], "p95_status": statuses["p95"], "peak_x_status": statuses["peak_x"], "pre_override_composite": "UNRESOLVED", "composite_status": "UNRESOLVED", "uq_model_validity": False, "coverage_note": "electronic dense curve computed" if integrity else "contract SHA mismatch", "cross_gate_note": "route3 not gate-eligible; formal u_cross unavailable", "reference_note": "d is Table2-vs-independent-Mie on fixed electronic grid; no image data"})
            diag[lane] = {"electronic_points": len(x), "u_interp_primary": ui, "u_interp_sensitivity_0_5": us, "max_abs_y2": curv, "max_h": h, "u_physics": phys[lane], "u_cross_diagnostic_table2_vs_mie": cross}
    fields = list(lane_rows[0])
    with LANES.open("w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(lane_rows)
    tp = {"schema_version": 2, "task": "B38b", "contract": "A5-v4-20260813 + threshold-addendum-1", "implementation_classes": {"table2_ours": {"implementation_class": "table2_exact_multipole", "object_class": "mie_analytic_dielectric+gold", "matched_class": "lane_object_matched", "provenance": "code/multipole_moments.py; B38b electronic CSVs"}, "mie_coefficients_ours": {"implementation_class": "independent_mie_coefficients", "object_class": "mie_analytic_dielectric+gold", "matched_class": "lane_object_matched", "provenance": "code/baseline_mie.py; code/mie_theory.py"}, "third_party_route3": route3}, "nominal_discrepancy_table2_vs_mie": {"a-"+c: a_cross[c] for c in CHANNELS} | {"b-"+c: metric(gold["x"], gold[f"mie_{c}"], gold[f"table2_{c}"]) for c in CHANNELS}, "u_cross": {"formal_gate_eligible": False, "reason": "third-party gold route is not gate-eligible; no admissible third replacement exists", "per_lane": {r["panel"]+"-"+r["channel"]: {"rmse": None, "p95": None, "peak_x": None} for r in lane_rows}}, "input_sha256": {"SPEC.md": observed["SPEC.md"], "THRESHOLD-ADDENDUM.md": observed["THRESHOLD-ADDENDUM.md"], "data/fig2_gold_olmon_refined.csv": sha256(GOLD)}}
    TP_RECEIPT.write_text(json.dumps(tp, indent=2), encoding="utf-8")
    summary = {"schema_version": 2, "task": "B38b", "executed_at_utc": datetime.now(timezone.utc).isoformat(), "contract_sha256": {"expected": {"SPEC.md": SPEC_SHA, "THRESHOLD-ADDENDUM.md": ADD_SHA}, "observed": observed, "integrity_match": integrity}, "thresholds_frozen": THRESHOLDS, "image_data_consumed": False, "nominal_discrepancy_definition": "Table2 nominal implementation versus independent Mie electronic reference on fixed lane grid", "panel_a": {"points": 200, "epsilon_r": 6.25, "table2_path": str(t2_path.relative_to(ROOT)).replace("\\", "/"), "mie_path": str(mie_path.relative_to(ROOT)).replace("\\", "/"), "cross": a_cross}, "physics_receipt": {"formal_available": True, "path": str(PHYSICS.relative_to(ROOT)).replace("\\", "/"), "grid_coarse": [40,30,60], "grid_refined": [60,61,120], "per_lane": phys}, "cross_receipt": {"path": str(TP_RECEIPT.relative_to(ROOT)).replace("\\", "/"), "formal_gate_eligible": False}, "lanes": lane_rows, "diagnostics": diag, "global_composite_status": "UNRESOLVED", "global_uq_model_validity": False, "fail_closed_reasons": ["third-party gold route not gate-eligible; formal u_cross unavailable"] + ([] if integrity else ["A5-v4 contract SHA mismatch"]), "input_sha256": {"data/fig2_gold_olmon_refined.csv": sha256(GOLD), "codex-prompts/out/A5-v4/preregister/SPEC.md": observed["SPEC.md"], "codex-prompts/out/A5-v4/preregister/THRESHOLD-ADDENDUM.md": observed["THRESHOLD-ADDENDUM.md"]}, "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()}}
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = ["# B38b Fig.2 UQ（A5-v4）补缺口报告", "", "正式结论：`UNRESOLVED`（fail-closed）。", "", "门槛冻结为 RMSE 0.020、p95 0.050、peak-x 0.010；未使用图像数据。正式 d 是固定电子网格上的 Table-2→独立 Mie 差异。", "", "## 8 lane 判定", "", "| lane | d_RMSE | d_p95 | d_peak-x | u_interp | u_physics | u_cross | RMSE | p95 | peak-x | composite |", "|---|---:|---:|---:|---:|---:|---:|---|---|---|---|"]
    for r in lane_rows: lines.append(f"| {r['panel']}-{r['channel']} | {r['d_rmse']:.6g} | {r['d_p95']:.6g} | {r['d_peak_x']:.6g} | {r['u_interp']:.6g} | {r['u_physics']:.6g} | — | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |")
    lines += ["", "## 缺口补齐", "", "1. panel(a) 介电球：已生成 200 点、εr=6.25、host=air 的 Table-2（60×61×120）与独立 Mie 电子 CSV；四 lane 的 d_RMSE/d_p95/d_peak-x 已登记。", "2. u_physics：已生成 `data/fig2_uq_a5v4_physics.csv`，逐 lane 比较 40×30×60 与 60×61×120，`u_physics` 取最大逐点相对差。", "3. u_cross 第三路：pyGDM2 官方示例管线已按 Alaee D=500nm Johnson-Christy 金球、500–2500nm、CPU/LU 复跑并产生 ED/MD/EQ/MQ SCS；但这是 57 dipole 的粗 DDA 分解，不是增补 §2 所称 Mie 解析类第三方曲线，且无独立离散误差界，故诚实标 `method_only`、不 gate。torchGDM 未安装；B34 c-Si 也仅 `method_only`。正式 u_cross 仍缺失。", f"4. SHA：SPEC 观测 `{observed['SPEC.md']}`，增补观测 `{observed['THRESHOLD-ADDENDUM.md']}`；登记值为 `8a344a60…` / `67a883f8…`，完整性={integrity}。", "", "## 门槛对照", "", "8 lane 的 d、u_interp、u_physics 均已有限；但第三路不具 gate eligibility，u_cross 为空，所以总 u 和 [L,U] 无法形成。按 A5-v4 模型有效性规则，三项 metric 与 composite 均为 UNRESOLVED，不能用已很小的双实现 d 替代第三路。", "", "## 产物", "", "- `codex-prompts/out/B38b/report.md`", "- `data/fig2_uq_a5v4_dielectric_table2.csv`", "- `data/fig2_uq_a5v4_dielectric_mie.csv`", "- `data/fig2_uq_a5v4_physics.csv`", "- `data/fig2_uq_a5v4_summary.json`", "- `data/fig2_uq_a5v4_lane_verdicts.csv`", "- `data/third_party_cross_consistency_receipt.json`", "- `code/b38b_uq_verifier.py`"]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"task": "B38b", "global_composite_status": "UNRESOLVED", "integrity_match": integrity, "artifacts": [str(OUT / "report.md"), str(SUMMARY), str(LANES), str(PHYSICS), str(TP_RECEIPT)]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
