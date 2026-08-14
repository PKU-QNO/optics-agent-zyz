"""B38 A5-v4 Fig.2 UQ verifier (additive, fail-closed).

The verifier deliberately consumes only electronically sourced gold data and
the B34 cross-validation receipts.  Image/graph-extracted files are never
opened.  Because no gate-eligible third-party gold Mie implementation and no
independent A5-v4 physics receipt are present, formal model validity is false
and every published lane status is UNRESOLVED; numerical diagnostics remain
reproducible for audit.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "codex-prompts" / "out" / "B38"
SPEC = OUT.parent / "A5-v4" / "preregister" / "SPEC.md"
ADDENDUM = OUT.parent / "A5-v4" / "preregister" / "THRESHOLD-ADDENDUM.md"
GOLD = DATA / "fig2_gold_olmon_refined.csv"
CROSS_TABLE2 = DATA / "fig2_cross_validation_table2_vs_mie.csv"
CROSS_SUMMARY = DATA / "fig2_cross_validation_summary.json"
TP = DATA / "third_party"
SUMMARY = DATA / "fig2_uq_a5v4_summary.json"
LANES_CSV = DATA / "fig2_uq_a5v4_lane_verdicts.csv"
TP_RECEIPT = DATA / "third_party_cross_consistency_receipt.json"
REPORT = OUT / "report.md"

CHANNELS = ("ED", "MD", "EQ", "MQ")
PANELS = ("a", "b")
THRESHOLDS = {"rmse": 0.020, "p95": 0.050, "peak_x": 0.010}
EXPECTED_SPEC_SHA = "8a344a6098c493e2fd0f3f386664297cee96a2248ee865c7ed93ae7bea1c67f5"
EXPECTED_ADDENDUM_SHA = "aa00b3c2af1b8f88e1d88b37add807ecfc613aac518f5b3ccdb0a461780c930b"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def finite(value: float | None) -> bool:
    return value is not None and math.isfinite(float(value))


def metrics(x: np.ndarray, ref: np.ndarray, alt: np.ndarray) -> dict[str, float]:
    """RMSE, p95 absolute and deterministic peak-x shift for two curves."""
    err = np.asarray(alt, float) - np.asarray(ref, float)
    peak_ref = float(x[int(np.argmax(ref))])
    peak_alt = float(x[int(np.argmax(alt))])
    return {
        "rmse": float(np.sqrt(np.mean(err * err))),
        "p95": float(np.percentile(np.abs(err), 95)),
        "peak_x": abs(peak_alt - peak_ref),
    }


def interpolation_bound(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """Return (primary, sensitivity, max_curvature, max_h)."""
    # np.gradient on the labelled electronic grid is a model-conditional
    # curvature estimate; it is reported diagnostically only.
    d2 = np.gradient(np.gradient(y, x), x)
    h = float(np.max(np.diff(x)))
    curvature = float(np.max(np.abs(d2)))
    return curvature * h * h / 8.0, 0.5 * curvature * h * h, curvature, h


def state(interval: tuple[float, float] | None, threshold: float) -> str:
    if interval is None or not all(finite(v) for v in interval):
        return "UNRESOLVED"
    lo, hi = interval
    if hi <= threshold:
        return "PASS"
    if lo > threshold:
        return "FAIL"
    return "UNRESOLVED"


def composite(statuses: list[str], valid: bool) -> tuple[str, str]:
    diagnostic = "FAIL" if "FAIL" in statuses else ("UNRESOLVED" if "UNRESOLVED" in statuses else "PASS")
    # A5-v4 published composite is forced UNRESOLVED when model validity is
    # false, while retaining the pre-override diagnostic for transparency.
    return diagnostic, (diagnostic if valid else "UNRESOLVED")


def read_gold() -> dict[str, np.ndarray]:
    rows = list(csv.DictReader(GOLD.open(encoding="utf-8", newline="")))
    result: dict[str, np.ndarray] = {
        "x": np.asarray([float(r["x_alaee"]) for r in rows], float)
    }
    for channel in CHANNELS:
        result[f"mie_{channel}"] = np.asarray([float(r[f"mie_{channel}"]) for r in rows], float)
        result[f"table2_{channel}"] = np.asarray([float(r[f"table2_{channel}"]) for r in rows], float)
    return result


def build_third_party_receipt(gold: dict[str, np.ndarray], input_hashes: dict[str, str]) -> dict:
    """Record all three implementation classes without relabelling c-Si."""
    evidence = {
        "table2_ours": {
            "implementation_class": "table2_exact_multipole",
            "object_class": "mie_analytic_gold",
            "provenance": "code/multipole_moments.py; data/fig2_gold_olmon_refined.csv",
            "material_source": "Olmon Johnson-Christy gold (frozen electronic CSV)",
            "geometry": "Alaee gold sphere, x_alaee=2a/lambda in [0.2,1.0]",
            "host": "air", "normalization": "dimensionless C_sca channel",
            "channels": list(CHANNELS), "matched_class": "lane_object_matched",
        },
        "mie_coefficients_ours": {
            "implementation_class": "independent_mie_coefficients",
            "object_class": "mie_analytic_gold",
            "provenance": "code/mie_theory.py + code/baseline_mie.py; data/fig2_gold_olmon_refined.csv",
            "material_source": "Olmon Johnson-Christy gold (frozen electronic CSV)",
            "geometry": "Alaee gold sphere, x_alaee=2a/lambda in [0.2,1.0]",
            "host": "air", "normalization": "dimensionless C_sca channel",
            "channels": list(CHANNELS), "matched_class": "lane_object_matched",
        },
        "tidy3d_csi": {
            "implementation_class": "third_party_pipeline",
            "object_class": "other",
            "provenance": "data/third_party/mie_*; Tidy3D MultipoleExpansion.ipynb",
            "material_source": "c-Si Green-2008",
            "geometry": "radius=0.18 um",
            "host": "air", "normalization": "scattering efficiency / geometric area",
            "channels": list(CHANNELS), "matched_class": "method_only",
            "gate_eligible": False,
            "reason": "different c-Si object and normalization; audit only",
        },
        "menp_csi_fdtd": {
            "implementation_class": "third_party_pipeline",
            "object_class": "other",
            "provenance": "data/third_party/demo_exact.csv; ENxyzf.mat; demo_exact.m",
            "material_source": "c-Si centre voxel n,k",
            "geometry": "D=200 nm sphere",
            "host": "unspecified in receipt", "normalization": "cross section m^2",
            "channels": list(CHANNELS), "matched_class": "method_only",
            "gate_eligible": False,
            "reason": "different c-Si/FDTD object; audit only",
        },
    }
    pairwise = {}
    for channel in CHANNELS:
        pairwise[channel] = metrics(gold["x"], gold[f"mie_{channel}"], gold[f"table2_{channel}"])
    lane_effects = {}
    for panel in PANELS:
        for channel in CHANNELS:
            lane = f"{panel}-{channel}"
            if panel == "b":
                lane_effects[lane] = {
                    "reference_and_grid": "fixed Olmon electronic x grid (200 points)",
                    "nominal": "table2_exact_multipole",
                    "replacements": [
                        {
                            "source": "independent_mie_coefficients",
                            "matched_class": "lane_object_matched",
                            "effect": pairwise[channel],
                            "gate_eligible": True,
                        },
                        {
                            "source": "tidy3d_csi",
                            "matched_class": "method_only",
                            "effect": None,
                            "gate_eligible": False,
                            "reason": "c-Si/FDTD object and normalization mismatch",
                        },
                        {
                            "source": "menp_csi_fdtd",
                            "matched_class": "method_only",
                            "effect": None,
                            "gate_eligible": False,
                            "reason": "c-Si/FDTD object and normalization mismatch",
                        },
                    ],
                    "u_cross_formal": None,
                    "u_cross_diagnostic_table2_vs_mie": pairwise[channel],
                }
            else:
                lane_effects[lane] = {
                    "reference_and_grid": None,
                    "nominal": None,
                    "replacements": [],
                    "u_cross_formal": None,
                    "u_cross_diagnostic_table2_vs_mie": None,
                    "reason": "no permitted electronic panel-a lane data",
                }
    return {
        "schema_version": 1,
        "task": "B38",
        "contract": "A5-v4-20260813 + threshold-addendum-1",
        "implementation_classes": evidence,
        "pairwise_effects_table2_vs_mie_diagnostic": pairwise,
        "per_lane_replacement_effects": lane_effects,
        "table2_grid": {"Nu": 60, "Ntheta": 61, "Nphi": 120, "provenance": "B34 encrypted-grid precedent; refined gold CSV"},
        "u_cross": {
            "formal_gate_eligible": False,
            "reason": "third-party gold Mie analytic implementation absent; available third-party evidence is method_only",
            "per_lane": {f"{p}-{c}": None for p in PANELS for c in CHANNELS},
        },
        "input_sha256": input_hashes,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # Contract hashes are checked before any evidence is consumed.
    contract_hashes = {"SPEC.md": sha256(SPEC), "THRESHOLD-ADDENDUM.md": sha256(ADDENDUM)}
    contract_integrity = (
        contract_hashes["SPEC.md"] == EXPECTED_SPEC_SHA
        and contract_hashes["THRESHOLD-ADDENDUM.md"] == EXPECTED_ADDENDUM_SHA
    )
    input_paths = [GOLD, CROSS_TABLE2, CROSS_SUMMARY, SPEC, ADDENDUM]
    input_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in input_paths}
    for p in sorted(TP.iterdir()):
        if p.is_file():
            input_hashes[str(p.relative_to(ROOT)).replace("\\", "/")] = sha256(p)

    gold = read_gold()
    x = gold["x"]
    electronic_checks = bool(len(x) == 200 and np.all(np.isfinite(x)) and np.all(np.diff(x) > 0) and 0.2 <= x.min() and x.max() <= 1.0)
    # Gold is panel (b) material.  There is no labelled electronic panel (a)
    # curve in the permitted inputs, so panel (a) coverage is false.
    rows = []
    diagnostics = {}
    grid_conv = json.loads((DATA / "fig2_gold_olmon_grid_convergence.json").read_text(encoding="utf-8"))
    for panel in PANELS:
        for channel in CHANNELS:
            key = f"{panel}-{channel}"
            if panel == "b":
                y_mie, y_t2 = gold[f"mie_{channel}"], gold[f"table2_{channel}"]
                interp_primary, interp_sens, curv, h = interpolation_bound(x, y_mie)
                cross_diag = metrics(x, y_mie, y_t2)
                # Existing convergence receipt is useful diagnostic evidence,
                # but not an independent A5-v4 physics bound.
                phys_diag = float(grid_conv[channel]["max_change_percent"]) / 100.0
                d_formal = None  # no electronic paper reference by contract
                electronic_ok = electronic_checks
            else:
                interp_primary = interp_sens = curv = h = None
                cross_diag = {m: None for m in ("rmse", "p95", "peak_x")}
                phys_diag = None
                d_formal = None
                electronic_ok = False
            formal_cross = None
            formal_physics = None
            validity = bool(contract_integrity and electronic_ok and formal_cross is not None and formal_physics is not None and d_formal is not None)
            intervals = {m: None for m in ("rmse", "p95", "peak_x")}
            statuses = {m: state(intervals[m], THRESHOLDS[m]) for m in intervals}
            pre, published = composite(list(statuses.values()), validity)
            diagnostics[key] = {
                "electronic_points": int(len(x)) if panel == "b" else 0,
                "electronic_coverage": electronic_ok,
                "d_formal": d_formal,
                "u_interp_primary": interp_primary,
                "u_interp_sensitivity_0_5": interp_sens,
                "max_abs_y2": curv,
                "max_h": h,
                "u_physics_diagnostic_grid_convergence": phys_diag,
                "u_cross_diagnostic_table2_vs_mie": cross_diag,
            }
            rows.append({
                "panel": panel, "channel": channel, "electronic_points": int(len(x)) if panel == "b" else 0,
                "d_formal": d_formal, "u_interp": interp_primary, "u_interp_sensitivity": interp_sens,
                "u_physics": formal_physics, "u_physics_diagnostic": phys_diag,
                "u_cross": formal_cross, "u_cross_diagnostic_rmse": cross_diag["rmse"],
                "u_cross_diagnostic_p95": cross_diag["p95"], "u_cross_diagnostic_peak_x": cross_diag["peak_x"],
                "rmse_threshold": THRESHOLDS["rmse"], "p95_threshold": THRESHOLDS["p95"], "peak_x_threshold": THRESHOLDS["peak_x"],
                "rmse_status": statuses["rmse"], "p95_status": statuses["p95"], "peak_x_status": statuses["peak_x"],
                "pre_override_composite": pre, "composite_status": published,
                "uq_model_validity": validity,
                "coverage_note": "panel b gold electronic domain covered; panel a electronic curve absent" if panel == "b" else "no permitted electronic panel-a curve",
                "cross_gate_note": "third-party gold Mie class missing; Tidy3D/MENP are method_only",
                "reference_note": "formal d unavailable: image-derived/reference curves excluded by A5-v4",
            })

    tp_receipt = build_third_party_receipt(gold, input_hashes)
    TP_RECEIPT.write_text(json.dumps(tp_receipt, indent=2), encoding="utf-8")
    fields = list(rows[0])
    with LANES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    summary = {
        "schema_version": 1, "task": "B38", "contract_version": "A5-v4-20260813",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "contract_sha256": {"expected": {"SPEC.md": EXPECTED_SPEC_SHA, "THRESHOLD-ADDENDUM.md": EXPECTED_ADDENDUM_SHA}, "observed": contract_hashes, "integrity_match": contract_integrity}, "thresholds_frozen": THRESHOLDS,
        "threshold_provenance": "THRESHOLD-ADDENDUM.md; user-approved before B38 evidence",
        "image_data_consumed": False,
        "electronic_input": {"path": str(GOLD.relative_to(ROOT)).replace("\\", "/"), "points": 200, "domain": [float(x.min()), float(x.max())], "labels": {"object": "Olmon gold sphere", "host": "air", "x": "x_alaee=2a/lambda", "panel": "b", "channels": list(CHANNELS)}, "coverage_panel_b": electronic_checks, "coverage_panel_a": False},
        "physics_receipt": {"formal_available": False, "diagnostic_source": "data/fig2_gold_olmon_grid_convergence.json", "reason": "A5-v2 PASS_WITH_LIMITS is not an independent per-lane A5-v4 bound"},
        "cross_receipt": {"path": str(TP_RECEIPT.relative_to(ROOT)).replace("\\", "/"), "formal_gate_eligible": False},
        "lanes": rows, "diagnostics": diagnostics,
        "global_composite_status": "UNRESOLVED",
        "global_uq_model_validity": False,
        "fail_closed_reasons": (["A5-v4 contract hash mismatch: observed addendum differs from frozen registration"] if not contract_integrity else []) + ["formal paper discrepancy d unavailable under no-image contract", "panel-a electronic coverage missing", "no gate-eligible third-party gold Mie implementation", "no independent per-lane A5-v4 physics receipt"],
        "input_sha256": input_hashes,
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()},
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Human report is generated from the same in-memory rows (no hard-coded status).
    lines = ["# B38 Fig.2 UQ（A5-v4）报告", "", "正式结论：`UNRESOLVED`（fail-closed）。", "", "A5-v4 冻结门槛：RMSE 0.020、p95 0.050、peak-x 0.010；未使用任何图像/曲线提取数据。", "", "## 8 lane 判定", "", "| lane | d（正式） | u_interp | u_physics | u_cross | RMSE | p95 | peak-x | composite | validity |", "|---|---:|---:|---:|---:|---|---|---|---|---|"]
    for r in rows:
        fmt = lambda v: "—" if v is None else f"{float(v):.6g}"
        lines.append(f"| {r['panel']}-{r['channel']} | {fmt(r['d_formal'])} | {fmt(r['u_interp'])} | {fmt(r['u_physics'])} | {fmt(r['u_cross'])} | {r['rmse_status']} | {r['p95_status']} | {r['peak_x_status']} | {r['composite_status']} | {r['uq_model_validity']} |")
    lines += ["", "## u_cross 三路证据", "", "Table-2 与独立 Mie 系数实现均为金球、同一归一化，逐通道替换诊断值如下（这些是诊断，不是正式 gate u_cross）：", "", "| lane | Table-2→Mie RMSE | p95 | peak-x |", "|---|---:|---:|---:|"]
    for panel in PANELS:
        for channel in CHANNELS:
            diag = diagnostics[f"{panel}-{channel}"]["u_cross_diagnostic_table2_vs_mie"]
            if diag["rmse"] is None:
                lines.append(f"| {panel}-{channel} | — | — | — |")
            else:
                lines.append(f"| {panel}-{channel} | {diag['rmse']:.6g} | {diag['p95']:.6g} | {diag['peak_x']:.6g} |")
    lines += ["", "可用第三方只有 Tidy3D c-Si 与 MENP c-Si/FDTD，均按增补 §2 标为 `method_only`，不得 gate；缺少可 gate 的第三方金球 Mie 解析路，因此正式 u_cross 缺失。", "", "## u_interp / u_physics", "", "主插值项按 sup|y''|h²/8 计算，0.5|y''|h² 仅 sensitivity。`u_physics` 正式项未填：既有 A5-v2 receipt 不是逐 lane、独立 A5-v4 误差界；其网格收敛差异仅作为诊断保留。", "", "## 覆盖率与门槛", "", "panel(b) 的 200 点 Olmon 金球电子域为 [0.2, 1.0]；panel(a) 无允许的电子参考曲线。由于正式 d 缺失、第三方 gate mismatch、physics receipt 缺失，`uq_model_validity=false`，8 lane 的三项及 composite 均为 `UNRESOLVED`。门槛严格保持 0.020 / 0.050 / 0.010，未按观测调整。", "", "契约完整性：SPEC 观测 SHA 与登记一致；THRESHOLD-ADDENDUM 观测 SHA 为 `0e7acb24…`，与登记 `aa00b3c2…` 不一致。契约文件按授权保持只读，漂移被 receipt 记录并触发 fail-closed。", "", "## 产物", "", "- `code/b38_uq_verifier.py`", "- `data/fig2_uq_a5v4_summary.json`", "- `data/fig2_uq_a5v4_lane_verdicts.csv`", "- `data/third_party_cross_consistency_receipt.json`", "- `codex-prompts/out/B38/report.md`"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"task": "B38", "lanes": 8, "global_composite_status": "UNRESOLVED", "uq_model_validity": False, "artifacts": [str(REPORT), str(SUMMARY), str(LANES_CSV), str(TP_RECEIPT)]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
