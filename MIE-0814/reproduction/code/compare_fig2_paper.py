# -*- coding: utf-8 -*-
"""Compare extracted Alaee Fig.2 vector curves with local reproduction data."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

from extract_fig2_vector import MULTIPOLES, ROOT
from run_fig2 import interpolate_gold_m, mie_multipoles

DATA = ROOT / "data"
FIGS = ROOT / "figs"
EXTRACTED_CSV = DATA / "fig2_paper_vector_curves.csv"
EXTRACTED_META = DATA / "fig2_paper_vector_metadata.json"
SUMMARY_JSON = DATA / "fig2_layer3_summary.json"
OVERLAY_PNG = FIGS / "fig2_layer3_overlay.png"
METHOD_SUMMARY_JSON = DATA / "fig2_gold_olmon_refined_summary.json"
JC_MIN_X = 500.0 / 1935.0
VECTOR_THRESHOLDS = {"rmse": 0.02, "p95_abs": 0.05, "peak_x": 0.01}
Q_FACTOR_RELATIVE_TOLERANCE = 0.05
RASTER_DESCRIPTIVE_RMSE = 0.08
COLORS = {"ED": "#d85218", "MD": "#0071bb", "EQ": "#ebb01f", "MQ": "#7d2d8c"}
REQUIRED_FIG2_DOMAIN = (0.2, 1.0)


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_local_curves() -> dict:
    mie_a = _read_csv(DATA / "fig1a_multipole_mie.csv")
    t2_a = _read_csv(DATA / "fig1a_multipole_table2.csv")
    jc = _read_csv(DATA / "fig2_gold_jc_sensitivity.csv")
    result = {"a": {}, "b": {}}
    dense_a_x = np.linspace(0.2, 1.0, 4000)
    dense_b_x = np.linspace(JC_MIN_X, 1.0, 4000)
    dense_a = {key: [] for key in MULTIPOLES}
    dense_b = {key: [] for key in MULTIPOLES}
    for x in dense_a_x:
        values = mie_multipoles(np.pi * x, 2.5)
        for key in MULTIPOLES:
            dense_a[key].append(values[key])
    for x in dense_b_x:
        wavelength_nm = 500.0 / x
        values = mie_multipoles(np.pi * x, interpolate_gold_m("jc", wavelength_nm))
        for key in MULTIPOLES:
            dense_b[key].append(values[key])
    for key in MULTIPOLES:
        result["a"][(key, "mie")] = (
            dense_a_x, np.asarray(dense_a[key]),
        )
        result["a"][(key, "exact")] = (
            np.asarray([float(row["2a_over_lambda"]) for row in t2_a]),
            np.asarray([float(row[key]) for row in t2_a]),
        )
        result["b"][(key, "mie")] = (
            dense_b_x, np.asarray(dense_b[key]),
        )
        result["b"][(key, "exact")] = (
            np.asarray([float(row["x_alaee"]) for row in jc]),
            np.asarray([float(row[f"table2_{key}"]) for row in jc]),
        )
    return result


def load_paper_curves(path: Path = EXTRACTED_CSV) -> dict:
    rows = _read_csv(path)
    grouped = {}
    for panel in ("a", "b"):
        for key in MULTIPOLES:
            for curve in ("mie", "exact", "combined"):
                subset = [row for row in rows if row["panel"] == panel
                          and row["multipole"] == key and row["curve"] == curve]
                if not subset:
                    continue
                points = sorted((float(row["x_alaee"]), float(row["y_norm"])) for row in subset)
                # Collapse repeated PDF x coordinates using the median path y.
                by_x = {}
                for x, y in points:
                    by_x.setdefault(round(x, 7), []).append(y)
                x = np.asarray(sorted(by_x), dtype=float)
                y = np.asarray([float(np.median(by_x[value])) for value in x], dtype=float)
                grouped[panel, key, curve] = (x, y)
    return grouped


def estimate_peak(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    if len(x) == 0:
        return math.nan, math.nan
    prominence = max(0.01, 0.01 * float(np.ptp(y)))
    indices = find_peaks(y, prominence=prominence)[0].tolist()
    if not indices or y[-1] >= 0.99 * float(np.max(y)):
        indices.append(len(y) - 1)
    if y[0] >= 0.99 * float(np.max(y)):
        indices.append(0)
    estimates = []
    for index in sorted(set(indices)):
        if index == 0 or index == len(x) - 1:
            estimates.append((float(x[index]), float(y[index])))
            continue
        # Three points are deliberately used for sparse exact markers.  A
        # five-point fit smears the narrow dielectric resonances.
        xs, ys = x[index - 1:index + 2], y[index - 1:index + 2]
        coeff = np.polyfit(xs, ys, 2)
        if coeff[0] >= 0:
            estimates.append((float(x[index]), float(y[index])))
            continue
        vertex = float(-coeff[1] / (2 * coeff[0]))
        vertex = min(max(vertex, float(xs.min())), float(xs.max()))
        estimates.append((vertex, float(np.polyval(coeff, vertex))))
    maximum = max(value for _, value in estimates)
    # If two resonances reach the same single-channel limit, use the first
    # one consistently instead of allowing endpoint rounding to switch peaks.
    near_max = [item for item in estimates if item[1] >= 0.99 * maximum]
    return min(near_max, key=lambda item: item[0])


def estimate_fwhm_q(x: np.ndarray, y: np.ndarray, max_gap: float = 0.03) -> dict:
    """Estimate FWHM and Q for the first dominant peak.

    A crossing separated by a large PDF-path gap is deliberately rejected.
    Boundary peaks and curves missing either half-height crossing are reported
    as NOT_EVALUABLE rather than being counted as passes.
    """
    peak_x, peak_y = estimate_peak(x, y)
    if not np.isfinite(peak_x) or not np.isfinite(peak_y) or peak_y <= 0:
        return {"status": "NOT_EVALUABLE", "reason": "no finite positive peak"}
    peak_index = int(np.argmin(np.abs(x - peak_x)))
    half_y = peak_y / 2.0

    def crossing(start: int, stop: int, step: int):
        for index in range(start, stop, step):
            left, right = index, index + 1
            if float(x[right] - x[left]) > max_gap:
                continue
            y0, y1 = float(y[left] - half_y), float(y[right] - half_y)
            if y0 * y1 <= 0 and y1 != y0:
                return float(x[left] - y0 * (x[right] - x[left]) / (y1 - y0))
        return None

    left_x = crossing(peak_index - 1, -1, -1)
    right_x = crossing(peak_index, len(x) - 1, 1)
    result = {"peak_x": peak_x, "peak_y": peak_y, "half_max_y": half_y,
              "left_half_x": left_x, "right_half_x": right_x}
    if left_x is None or right_x is None or right_x <= left_x:
        result.update({"status": "NOT_EVALUABLE",
                       "reason": "both in-domain half-height crossings are not available"})
        return result
    fwhm = right_x - left_x
    result.update({"status": "EVALUATED", "fwhm": fwhm,
                   "q_factor": peak_x / fwhm})
    return result


def compare_q_factor(paper_x: np.ndarray, paper_y: np.ndarray,
                     local_x: np.ndarray, local_y: np.ndarray,
                     domain: tuple[float, float]) -> dict:
    lower = max(domain[0], float(local_x.min()), float(paper_x.min()))
    upper = min(domain[1], float(local_x.max()), float(paper_x.max()))
    paper_mask = (paper_x >= lower) & (paper_x <= upper)
    local_mask = (local_x >= lower) & (local_x <= upper)
    paper_q = estimate_fwhm_q(paper_x[paper_mask], paper_y[paper_mask])
    local_q = estimate_fwhm_q(local_x[local_mask], local_y[local_mask])
    result = {"paper": paper_q, "local": local_q,
              "relative_error_tolerance": Q_FACTOR_RELATIVE_TOLERANCE,
              "supplemental_only": True, "promotion_eligible": False}
    if paper_q["status"] != "EVALUATED" or local_q["status"] != "EVALUATED":
        result.update({"status": "NOT_EVALUABLE",
                       "reason": "paper or local curve lacks two reliable in-domain half-height crossings"})
        return result
    relative_error = abs(local_q["q_factor"] - paper_q["q_factor"]) / abs(paper_q["q_factor"])
    result["relative_error"] = float(relative_error)
    result["status"] = "PASS" if relative_error <= Q_FACTOR_RELATIVE_TOLERANCE else "UNRESOLVED"
    return result


def graphical_floor_metrics(paper_line_x: np.ndarray, paper_line_y: np.ndarray,
                            marker_x: np.ndarray, marker_y: np.ndarray,
                            local_x: np.ndarray, local_y: np.ndarray,
                            domain: tuple[float, float]) -> dict:
    """Compare local fidelity with the paper's own line/marker discrepancy.

    The exact-marker x positions are used for both comparisons, so the two
    error samples have identical support.  This is a diagnostic measurement
    floor and never supersedes the pre-registered strict vector gate.
    """
    lower = max(domain[0], float(paper_line_x.min()), float(marker_x.min()), float(local_x.min()))
    upper = min(domain[1], float(paper_line_x.max()), float(marker_x.max()), float(local_x.max()))
    mask = (marker_x >= lower) & (marker_x <= upper)
    x = marker_x[mask]
    exact_y = marker_y[mask]
    paper_line_at_x = np.interp(x, paper_line_x, paper_line_y)
    local_at_x = np.interp(x, local_x, local_y)
    paper_internal_error = paper_line_at_x - exact_y
    local_to_paper_error = local_at_x - paper_line_at_x

    def summarize(error: np.ndarray) -> dict:
        return {"rmse": float(np.sqrt(np.mean(error ** 2))),
                "mae": float(np.mean(np.abs(error))),
                "p95_absolute_error": float(np.percentile(np.abs(error), 95)),
                "max_absolute_error": float(np.max(np.abs(error)))}

    paper_internal = summarize(paper_internal_error)
    local_to_paper = summarize(local_to_paper_error)
    consistent = (local_to_paper["rmse"] <= paper_internal["rmse"]
                  and local_to_paper["p95_absolute_error"] <= paper_internal["p95_absolute_error"])
    return {"same_marker_points": int(len(x)),
            "paper_internal_mie_vs_exact": paper_internal,
            "local_mie_vs_paper_mie": local_to_paper,
            "assessment": ("CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR"
                           if consistent else "UNRESOLVED"),
            "overrides_strict_gate": False}


def curve_spacing_diagnostics(x: np.ndarray) -> dict:
    diff = np.diff(x)
    maximum_index = int(np.argmax(diff))

    def window_max(lower: float, upper: float) -> float:
        mask = (x[:-1] > lower) & (x[:-1] < upper)
        return float(np.max(diff[mask])) if np.any(mask) else math.nan

    return {"source_curve_points": int(len(x)),
            "source_max_x_gap": float(diff[maximum_index]),
            "source_max_x_gap_interval": [float(x[maximum_index]), float(x[maximum_index + 1])],
            "primary_peak_window": [0.50, 0.58],
            "primary_peak_window_max_x_gap": window_max(0.50, 0.58),
            "secondary_peak_window": [0.90, 0.98],
            "secondary_peak_window_max_x_gap": window_max(0.90, 0.98)}


def classify_metrics(metrics: dict, mode: str) -> str:
    if mode != "vector":
        return "DESCRIPTIVE_ONLY"
    passed = (
        metrics["rmse"] <= VECTOR_THRESHOLDS["rmse"]
        and metrics["p95_absolute_error"] <= VECTOR_THRESHOLDS["p95_abs"]
        and metrics["peak_x_difference"] <= VECTOR_THRESHOLDS["peak_x"]
    )
    return "PASS_VECTOR_CONSISTENT" if passed else "UNRESOLVED"


def derive_panel_coverage(local_panel: dict,
                          required_domain: tuple[float, float] = REQUIRED_FIG2_DOMAIN) -> dict:
    """Derive material-domain coverage from the actual local curve support.

    The paper comparison may be restricted to the common source domain, but
    the returned status records whether that support covers the full Fig.2
    plotting domain.  This keeps a future material-data extension from
    leaving a stale ``MATERIAL_DOMAIN_LIMITED`` label behind.
    """
    lower_required, upper_required = map(float, required_domain)
    ranges = []
    missing = []
    for key in MULTIPOLES:
        curve = local_panel.get((key, "mie"))
        if curve is None:
            missing.append(key)
            continue
        x = np.asarray(curve[0], dtype=float)
        x = x[np.isfinite(x)]
        if not len(x):
            missing.append(key)
            continue
        ranges.append((float(x.min()), float(x.max())))

    if missing:
        return {
            "status": "UNRESOLVED",
            "comparison_domain": [lower_required, upper_required],
            "masked_x_range": [lower_required, upper_required],
            "masked_reason": "missing finite local curve support for: " + ", ".join(missing),
        }

    # All channels must be present over the common domain.  Intersect their
    # supports before clipping to the required plotting range.
    available_lower = max(item[0] for item in ranges)
    available_upper = min(item[1] for item in ranges)
    comparison_lower = max(lower_required, available_lower)
    comparison_upper = min(upper_required, available_upper)
    limited = (available_lower > lower_required
               or available_upper < upper_required)
    masked = []
    if available_lower > lower_required:
        masked.extend([lower_required, min(available_lower, upper_required)])
    elif available_upper < upper_required:
        masked.extend([max(available_upper, lower_required), upper_required])
    return {
        "status": "MATERIAL_DOMAIN_LIMITED" if limited else "PASS",
        "comparison_domain": [comparison_lower, comparison_upper],
        "masked_x_range": masked or None,
        "masked_reason": (
            "local material source does not cover the required Fig.2 x domain; "
            "out-of-domain interval is masked (Olmon substitution forbidden)"
            if limited else "local material source covers the required Fig.2 x domain"
        ),
    }


def derive_final_statuses(strict_status: str,
                          panel_coverage_statuses: list[str],
                          method_passes: bool) -> dict:
    """Derive machine-facing final statuses from the computed gate inputs."""
    strict_pass = strict_status == "PASS_VECTOR_CONSISTENT"
    coverage_limited = any(status == "MATERIAL_DOMAIN_LIMITED"
                           for status in panel_coverage_statuses)
    coverage_unresolved = any(status not in {"PASS", "MATERIAL_DOMAIN_LIMITED"}
                              for status in panel_coverage_statuses)
    if coverage_limited:
        coverage_status = "MATERIAL_DOMAIN_LIMITED"
    elif coverage_unresolved:
        coverage_status = "UNRESOLVED"
    else:
        coverage_status = "PASS"

    all_gates_pass = method_passes and strict_pass and coverage_status == "PASS"
    return {
        "paper_fidelity_status": "PASS" if strict_pass else "UNRESOLVED",
        "coverage_status": coverage_status,
        "gate4_decision": (
            "PASS" if all_gates_pass
            else "PASS_WITH_LIMITATIONS" if method_passes
            else "DENIED"
        ),
        "result_class": (
            "physical_reproduction_success" if all_gates_pass
            else "partial_physical_match" if method_passes
            else "diagnostic_only"
        ),
        "promotion_to_physical_reproduction_success": (
            "physical_reproduction_success" if all_gates_pass else "DENIED"
        ),
    }


def compare_curve(paper_x: np.ndarray, paper_y: np.ndarray,
                  local_x: np.ndarray, local_y: np.ndarray,
                  domain: tuple[float, float], mode: str) -> dict:
    lower = max(domain[0], float(local_x.min()), float(paper_x.min()))
    upper = min(domain[1], float(local_x.max()), float(paper_x.max()))
    mask = (paper_x >= lower) & (paper_x <= upper)
    px, py = paper_x[mask], paper_y[mask]
    if len(px) < 3 or lower >= upper:
        return {"status": "UNRESOLVED", "reason": "insufficient common-domain points",
                "paper_points": int(len(px)), "domain": [lower, upper]}
    local_at_paper = np.interp(px, local_x, local_y)
    error = local_at_paper - py
    over_005 = np.abs(error) > 0.05
    paper_peak_x, paper_peak_y = estimate_peak(px, py)
    dense_x = np.linspace(lower, upper, 4000)
    dense_local_y = np.interp(dense_x, local_x, local_y)
    local_peak_x, local_peak_y = estimate_peak(dense_x, dense_local_y)
    metrics = {
        "paper_points": int(len(px)),
        "paper_x_range": [float(px.min()), float(px.max())],
        "domain": [lower, upper],
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "mae": float(np.mean(np.abs(error))),
        "p95_absolute_error": float(np.percentile(np.abs(error), 95)),
        "max_absolute_error": float(np.max(np.abs(error))),
        "mean_signed_error": float(np.mean(error)),
        "absolute_error_gt_0_05_count": int(np.sum(over_005)),
        "absolute_error_gt_0_05_x": [float(value) for value in px[over_005]],
        "paper_peak_x": paper_peak_x,
        "paper_peak_y": paper_peak_y,
        "local_peak_x": local_peak_x,
        "local_peak_y": local_peak_y,
        "peak_x_difference": abs(local_peak_x - paper_peak_x),
        "peak_height_difference": abs(local_peak_y - paper_peak_y),
    }
    metrics["status"] = classify_metrics(metrics, mode)
    return metrics


def compare_all(extracted_csv: Path = EXTRACTED_CSV,
                metadata_path: Path = EXTRACTED_META) -> tuple[dict, dict, dict]:
    paper = load_paper_curves(extracted_csv)
    local = load_local_curves()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    method_summary = json.loads(METHOD_SUMMARY_JSON.read_text(encoding="utf-8"))
    method_passes = bool(method_summary.get("passes_all_channels", False))
    mode = metadata.get("mode", "raster")
    result = {"mode": mode,
              "thresholds": VECTOR_THRESHOLDS,
              "strict_vector_fidelity_gate": {"thresholds": VECTOR_THRESHOLDS},
              "raster_descriptive_rmse": RASTER_DESCRIPTIVE_RMSE,
              "panels": {}, "attribution_order": [
                  "axis_or_curve_identity", "solid_marker_overlap", "JC_domain_or_interpolation",
                  "paper_COMSOL_numerics", "gold_material_sample", "local_physics_candidate"
              ]}
    panel_coverage_statuses = []
    for panel in ("a", "b"):
        coverage = derive_panel_coverage(local[panel])
        domain = tuple(coverage["comparison_domain"])
        panel_result = {"comparison_domain": list(domain), "curves": {},
                        "graphical_floor": {}, "q_factor_diagnostics": {}}
        panel_coverage_statuses.append(coverage["status"])
        if coverage["status"] != "PASS":
            panel_result["coverage_status"] = coverage["status"]
            panel_result["masked_x_range"] = coverage["masked_x_range"]
            panel_result["masked_reason"] = coverage["masked_reason"]
        for key in MULTIPOLES:
            panel_result["curves"][key] = {}
            curve_names = ("mie", "exact") if mode == "vector" else ("combined",)
            for curve in curve_names:
                if (panel, key, curve) not in paper:
                    panel_result["curves"][key][curve] = {
                        "status": "UNRESOLVED", "reason": "curve not extracted"}
                    continue
                local_curve = "mie" if curve == "combined" else curve
                panel_result["curves"][key][curve] = compare_curve(
                    *paper[panel, key, curve], *local[panel][key, local_curve], domain, mode)
                metrics = panel_result["curves"][key][curve]
                if curve == "exact" and "paper_x_range" in metrics:
                    marker_x = paper[panel, key, curve][0]
                    marker_x = marker_x[(marker_x >= domain[0]) & (marker_x <= domain[1])]
                    spacing = float(np.median(np.diff(marker_x))) if len(marker_x) > 1 else math.nan
                    metrics["marker_x_spacing_median"] = spacing
                    metrics["strict_metrics_status"] = metrics["status"]
                    metrics["shape_metrics_status"] = (
                        "PASS_VECTOR_CONSISTENT"
                        if metrics.get("rmse", math.inf) <= VECTOR_THRESHOLDS["rmse"]
                        and metrics.get("p95_absolute_error", math.inf) <= VECTOR_THRESHOLDS["p95_abs"]
                        else "UNRESOLVED"
                    )
                    metrics["independent_peak_verdict"] = bool(spacing <= VECTOR_THRESHOLDS["peak_x"])
                    metrics["peak_verdict"] = (
                        "PASS" if metrics["independent_peak_verdict"]
                        and metrics.get("peak_x_difference", math.inf) <= VECTOR_THRESHOLDS["peak_x"]
                        else "DESCRIPTIVE_ONLY"
                    )
                    if not metrics["independent_peak_verdict"]:
                        metrics["status"] = "DESCRIPTIVE_ONLY"
                        metrics["reason"] = (
                            "exact-marker spacing is coarser than the 0.01 peak-location gate; "
                            "shape metrics are retained but cannot independently decide peak fidelity"
                        )

            if mode == "vector" and ((panel, key, "mie") in paper
                                      and (panel, key, "exact") in paper):
                panel_result["graphical_floor"][key] = graphical_floor_metrics(
                    *paper[panel, key, "mie"], *paper[panel, key, "exact"],
                    *local[panel][key, "mie"], domain,
                )
                panel_result["q_factor_diagnostics"][key] = compare_q_factor(
                    *paper[panel, key, "mie"], *local[panel][key, "mie"], domain,
                )

            if panel == "a" and key == "MQ" and (panel, key, "mie") in paper:
                mie_metrics = panel_result["curves"][key]["mie"]
                mie_metrics["spacing_diagnostics"] = curve_spacing_diagnostics(
                    paper[panel, key, "mie"][0]
                )
        # The solid vector path is the primary paper-fidelity gate.  Exact
        # markers remain a separate audit channel but are too sparse to veto
        # an otherwise passing solid-path comparison.
        statuses = [panel_result["curves"][key]["mie"]["status"] for key in MULTIPOLES]
        panel_result["consistency_status"] = (
            "PASS_VECTOR_CONSISTENT" if statuses and all(s == "PASS_VECTOR_CONSISTENT" for s in statuses)
            else "DESCRIPTIVE_ONLY" if mode != "vector" else "UNRESOLVED"
        )
        result["panels"][panel] = panel_result
    strict_status = (
        "PASS_VECTOR_CONSISTENT" if result["panels"]["a"]["consistency_status"] == "PASS_VECTOR_CONSISTENT"
        and result["panels"]["b"]["consistency_status"] == "PASS_VECTOR_CONSISTENT"
        else "UNRESOLVED"
    )
    floor_statuses = [
        result["panels"][panel]["graphical_floor"][key]["assessment"]
        for panel in ("a", "b") for key in MULTIPOLES
    ]
    graphical_floor_assessment = (
        "CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR"
        if floor_statuses and all(status == "CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR"
                                  for status in floor_statuses)
        else "UNRESOLVED"
    )
    result["strict_vector_fidelity_status"] = strict_status
    result["strict_vector_fidelity_gate"]["status"] = strict_status
    result["graphical_floor_assessment"] = graphical_floor_assessment
    result["method_claim_status"] = "PASS" if method_passes else "UNRESOLVED"
    result.update(derive_final_statuses(strict_status, panel_coverage_statuses, method_passes))
    result["overall_status"] = strict_status
    result["overall_note"] = (
        "Computed statuses: method_claim_status={method}, strict_vector_fidelity_status={strict}, "
        "paper_fidelity_status={paper}, coverage_status={coverage}, gate4_decision={gate4}, "
        "result_class={result_class}. The paper's own line/marker discrepancy is a graphical-floor "
        "diagnostic and does not override the strict gate."
    ).format(
        method=result["method_claim_status"], strict=strict_status,
        paper=result["paper_fidelity_status"], coverage=result["coverage_status"],
        gate4=result["gate4_decision"], result_class=result["result_class"],
    )
    return result, paper, local


def save_overlay(summary: dict, paper: dict, local: dict, path: Path = OVERLAY_PNG):
    fig, axes = plt.subplots(2, 1, figsize=(9, 8.5), sharex=True, constrained_layout=True)
    for panel, ax in zip(("a", "b"), axes):
        domain = (0.2, 1.0) if panel == "a" else (JC_MIN_X, 1.0)
        for key in MULTIPOLES:
            color = COLORS[key]
            lx, ly = local[panel][key, "mie"]
            mask = (lx >= domain[0]) & (lx <= domain[1])
            ax.plot(lx[mask], ly[mask], color=color, lw=1.6, label=f"{key} local Mie")
            if (panel, key, "mie") in paper:
                px, py = paper[panel, key, "mie"]
                pm = (px >= domain[0]) & (px <= domain[1])
                ax.plot(px[pm], py[pm], color=color, lw=0.8, ls="--", alpha=0.9,
                        label=f"{key} paper vector")
            if (panel, key, "exact") in paper:
                px, py = paper[panel, key, "exact"]
                pm = (px >= domain[0]) & (px <= domain[1])
                ax.scatter(px[pm], py[pm], facecolors="none", edgecolors=color,
                           s=16, linewidths=0.7)
        ax.set_xlim(0.2, 1.0)
        ax.set_ylim(0.0, 7.0)
        ax.set_ylabel(r"$C_{\rm sca}/(\lambda^2/2\pi)$")
        ax.set_title("(a) dielectric sphere" if panel == "a" else "(b) gold sphere - JC common domain")
        ax.grid(alpha=0.18)
        if panel == "b":
            ax.axvspan(0.2, JC_MIN_X, color="0.7", alpha=0.25)
            ax.text((0.2 + JC_MIN_X) / 2, 6.7, "JC out of domain", ha="center", va="top", fontsize=8)
    axes[-1].set_xlabel(r"$2a/\lambda$")
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].legend(handles, labels, ncol=2, fontsize=7, loc="upper left")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main():
    summary, paper, local = compare_all()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_overlay(summary, paper, local)
    print(json.dumps({"overall_status": summary["overall_status"],
                      "summary": str(SUMMARY_JSON), "overlay": str(OVERLAY_PNG)}, indent=2))


if __name__ == "__main__":
    main()
