# -*- coding: utf-8 -*-
"""Run the Fig.2 Layer3 uncertainty-aware promotion audit.

The original B3 task named the first A5 preregistration as its contract.  A
newer A5-v2 contract was frozen before this recovered execution and explicitly
supersedes the earlier trial's statistical semantics.  This runner therefore:

* computes the original fixed 4000 x 401 x 401 envelope for every Fig.2 solid
  Mie channel as a fully reproducible diagnostic;
* also reports the A5-v2 ``M h^2 / 8`` sensitivity;
* fail-closes the promotion status to UNRESOLVED when A5-v2 model validity or
  dense-mode thresholds are absent; and
* never rewrites the historical Layer3 receipt.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from compare_fig2_paper import estimate_peak, load_local_curves, load_paper_curves


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
NOTES = ROOT / "notes"
OUT = ROOT / "codex-prompts" / "out"

OLD_SPEC = OUT / "A5-recompute" / "preregister" / "MQ-uncertainty-preregistration.md"
LATEST_SPEC = OUT / "A5-v2" / "preregister" / "SPEC.md"
EXTRACTION_RECEIPT = OUT / "A5-v2" / "extraction" / "receipt.json"
PHYSICS_RECEIPT = OUT / "A5-v2" / "physics" / "receipt.json"
LATEST_UQ_RECEIPT = OUT / "A5-v2" / "preregister" / "uq_receipt.json"
LATEST_WEIGHTING_RECEIPT = OUT / "A5-v2" / "preregister" / "weighting_sensitivity.csv"
PAPER_CSV = DATA / "fig2_paper_vector_curves.csv"
PAPER_METADATA = DATA / "fig2_paper_vector_metadata.json"
HISTORICAL_SUMMARY = DATA / "fig2_layer3_summary.json"

RESULTS_CSV = DATA / "fig2_uq_channel_results.csv"
POINTWISE_CSV = DATA / "fig2_uq_pointwise.csv"
SUMMARY_JSON = DATA / "fig2_uq_summary.json"
WEIGHTING_CSV = DATA / "fig2_uq_weighting_sensitivity.csv"
NOTE_MD = NOTES / "fig2-uq-promotion.md"
VERDICT_MD = OUT / "B3-promotion-verdict.md"
DISCREPANCIES_MD = OUT / "B3-discrepancies.md"

CHANNELS = ("ED", "MD", "EQ", "MQ")
PANELS = ("a", "b")
PANEL_DOMAINS = {"a": (0.2, 1.0), "b": (500.0 / 1935.0, 1.0)}

# These values are frozen by the original named preregistration.  They remain
# diagnostic sensitivities under A5-v2, not calibrated uncertainty bounds.
DX = 0.00044298097784123414
DY = 0.006570147109485447
AXIS_POINTS = 401
UQ_POINTS = 4000
HISTORICAL_THRESHOLDS = {"rmse": 0.02, "p95_abs": 0.05, "peak_x": 0.01}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_recorded_hashes(summary: dict, root: Path = ROOT) -> None:
    """Fail closed if any input hash in the receipt no longer matches."""
    for relative, expected in summary.get("input_sha256", {}).items():
        path = root / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"input hash mismatch: {relative}")


def verify_external_hash_map(hash_map: dict[str, str]) -> None:
    """Verify an upstream receipt's own absolute-path hash map."""
    for path_text, expected in hash_map.items():
        path = Path(path_text)
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"upstream input hash mismatch: {path_text}")


def interval_state(interval: tuple[float, float], threshold: float | None,
                   model_validity: bool = True) -> str:
    """A5-v2 three-state interval rule, including fail-closed validity."""
    if threshold is None or not model_validity or not all(math.isfinite(v) for v in interval):
        return "UNRESOLVED"
    lower, upper = interval
    if upper <= threshold:
        return "PASS"
    if lower > threshold:
        return "FAIL"
    return "UNRESOLVED"


def old_composite(statuses: tuple[str, str, str]) -> str:
    """Composite exactly as stated by the original MQ preregistration."""
    if all(value == "PASS" for value in statuses):
        return "PASS"
    if "UNRESOLVED" in statuses:
        return "UNRESOLVED"
    return "FAIL"


def latest_composite(statuses: tuple[str, str, str], model_validity: bool) -> str:
    """A5-v2 truth table plus its published model-invalid override."""
    diagnostic = "FAIL" if "FAIL" in statuses else (
        "UNRESOLVED" if "UNRESOLVED" in statuses else "PASS"
    )
    return diagnostic if model_validity else "UNRESOLVED"


def _weighted_p95(values: np.ndarray, weights: np.ndarray) -> float:
    order = np.argsort(values)
    ordered_values = values[order]
    cumulative = np.cumsum(weights[order])
    cumulative /= cumulative[-1]
    return float(ordered_values[int(np.searchsorted(cumulative, 0.95, side="left"))])


def _weighted_metrics(error: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    absolute = np.abs(error)
    return {
        "rmse": float(np.sqrt(np.sum(weights * error * error) / np.sum(weights))),
        "p95_abs": _weighted_p95(absolute, weights),
        "max_abs": float(np.max(absolute)),
    }


def _arc_length_resample(
    paper_x: np.ndarray, paper_y: np.ndarray,
    local_x: np.ndarray, local_y: np.ndarray,
    count: int,
    use_source_vertices: bool = False,
    thresholds: dict[str, float | None] | None = None,
    model_validity: bool = False,
    threshold_provenance: str = "none_by_A5_v2_spec",
) -> dict[str, object]:
    """A5-v2 deterministic cumulative-polyline-arc resampling receipt row."""
    if use_source_vertices:
        sample_x, sample_paper = paper_x.copy(), paper_y.copy()
    else:
        segment_length = np.hypot(np.diff(paper_x), np.diff(paper_y))
        cumulative = np.concatenate(([0.0], np.cumsum(segment_length)))
        target = np.linspace(0.0, float(cumulative[-1]), count)
        sample_x = np.interp(target, cumulative, paper_x)
        sample_paper = np.interp(target, cumulative, paper_y)
    sample_local = np.interp(sample_x, local_x, local_y)
    error = sample_local - sample_paper
    if use_source_vertices:
        arc = np.hypot(np.diff(sample_x), np.diff(sample_paper))
        weights = np.empty(len(sample_x), dtype=float)
        weights[0], weights[-1] = arc[0] / 2.0, arc[-1] / 2.0
        if len(weights) > 2:
            weights[1:-1] = (arc[:-1] + arc[1:]) / 2.0
    else:
        step = 1.0 / max(1, len(sample_x) - 1)
        weights = np.full(len(sample_x), step, dtype=float)
        weights[0] = weights[-1] = step / 2.0
    metrics = _weighted_metrics(error, weights)
    thresholds = thresholds or {"rmse": None, "p95_abs": None, "peak_x": None}
    status_rmse = interval_state((metrics["rmse"], metrics["rmse"]), thresholds["rmse"], model_validity)
    status_p95 = interval_state((metrics["p95_abs"], metrics["p95_abs"]), thresholds["p95_abs"], model_validity)
    return {
        "scheme": "strict_vertex_212" if use_source_vertices and count == 212 else f"dense_{count}",
        "effective_count": int(len(sample_x)),
        **metrics,
        "threshold_rmse": thresholds["rmse"],
        "threshold_p95_abs": thresholds["p95_abs"],
        "status": latest_composite((status_rmse, status_p95, "PASS"), model_validity),
        "rmse_status": status_rmse,
        "p95_status": status_p95,
        "threshold_provenance": threshold_provenance,
        "model_validity": model_validity,
        "resampling": "cumulative_polyline_arc_length_trapezoidal",
    }


def _equal_segment_row(
    paper_x: np.ndarray, paper_y: np.ndarray,
    local_x: np.ndarray, local_y: np.ndarray,
    thresholds: dict[str, float | None] | None = None,
    model_validity: bool = False,
    threshold_provenance: str = "none_by_A5_v2_spec",
) -> dict[str, object]:
    mids_x = (paper_x[:-1] + paper_x[1:]) / 2.0
    mids_paper = (paper_y[:-1] + paper_y[1:]) / 2.0
    error = np.interp(mids_x, local_x, local_y) - mids_paper
    metrics = {
        "rmse": float(np.sqrt(np.mean(error * error))),
        "p95_abs": float(np.percentile(np.abs(error), 95)),
        "max_abs": float(np.max(np.abs(error))),
    }
    thresholds = thresholds or {"rmse": None, "p95_abs": None, "peak_x": None}
    status_rmse = interval_state((metrics["rmse"], metrics["rmse"]), thresholds["rmse"], model_validity)
    status_p95 = interval_state((metrics["p95_abs"], metrics["p95_abs"]), thresholds["p95_abs"], model_validity)
    return {
        "scheme": "equal_segment",
        "effective_count": int(len(mids_x)),
        **metrics,
        "threshold_rmse": thresholds["rmse"],
        "threshold_p95_abs": thresholds["p95_abs"],
        "status": latest_composite((status_rmse, status_p95, "PASS"), model_validity),
        "rmse_status": status_rmse,
        "p95_status": status_p95,
        "threshold_provenance": threshold_provenance,
        "model_validity": model_validity,
        "resampling": "source_segment_midpoints_equal_weight",
    }


def _extreme(values: np.ndarray, mode: str) -> tuple[float, int]:
    index = int(np.argmin(values) if mode == "min" else np.argmax(values))
    return float(values[index]), index


def enumerate_axis_grid(
    x: np.ndarray,
    paper_line: np.ndarray,
    local_x: np.ndarray,
    local_y: np.ndarray,
    bands: dict[str, np.ndarray],
) -> tuple[dict, dict]:
    """Enumerate the inclusive 401 x 401 correlated global-shift grid."""
    sx_grid = np.linspace(-DX, DX, AXIS_POINTS)
    sy_grid = np.linspace(-DY, DY, AXIS_POINTS)
    extrema: dict[str, dict[str, dict]] = {
        "axis_only": {
            "rmse_min": {"value": math.inf}, "rmse_max": {"value": -math.inf},
            "p95_min": {"value": math.inf}, "p95_max": {"value": -math.inf},
        }
    }
    for name in bands:
        extrema[name] = {
            "rmse_lower_min": {"value": math.inf},
            "rmse_upper_max": {"value": -math.inf},
            "p95_lower_min": {"value": math.inf},
            "p95_upper_max": {"value": -math.inf},
        }

    clipped_x_evaluations = 0
    sx_values_with_clipping = 0

    def update(bucket: dict, key: str, value: float, sx: float, sy: float, choose_min: bool) -> None:
        previous = float(bucket[key]["value"])
        if (choose_min and value < previous) or ((not choose_min) and value > previous):
            bucket[key] = {"value": value, "delta_x": sx, "delta_y": sy}

    for sx in sx_grid:
        shifted_x = x + sx
        outside = (shifted_x < local_x[0]) | (shifted_x > local_x[-1])
        outside_count = int(np.sum(outside))
        clipped_x_evaluations += outside_count
        sx_values_with_clipping += int(outside_count > 0)

        shifted_local = np.interp(np.clip(shifted_x, local_x[0], local_x[-1]), local_x, local_y)
        signed = shifted_local - paper_line
        signed_grid = signed[:, None] - sy_grid[None, :]
        absolute = np.abs(signed_grid)

        raw_rmse = np.sqrt(np.mean(signed_grid * signed_grid, axis=0))
        raw_p95 = np.percentile(absolute, 95, axis=0)
        for metric, values in (("rmse", raw_rmse), ("p95", raw_p95)):
            low, low_i = _extreme(values, "min")
            high, high_i = _extreme(values, "max")
            update(extrema["axis_only"], f"{metric}_min", low, float(sx), float(sy_grid[low_i]), True)
            update(extrema["axis_only"], f"{metric}_max", high, float(sx), float(sy_grid[high_i]), False)

        for name, band in bands.items():
            lower = np.maximum(absolute - band[:, None], 0.0)
            upper = absolute + band[:, None]
            lower_rmse = np.sqrt(np.mean(lower * lower, axis=0))
            upper_rmse = np.sqrt(np.mean(upper * upper, axis=0))
            lower_p95 = np.percentile(lower, 95, axis=0)
            upper_p95 = np.percentile(upper, 95, axis=0)
            for key, values, choose_min in (
                ("rmse_lower_min", lower_rmse, True),
                ("rmse_upper_max", upper_rmse, False),
                ("p95_lower_min", lower_p95, True),
                ("p95_upper_max", upper_p95, False),
            ):
                value, sy_i = _extreme(values, "min" if choose_min else "max")
                update(extrema[name], key, value, float(sx), float(sy_grid[sy_i]), choose_min)

    coverage = {
        "coverage_warning": bool(clipped_x_evaluations),
        "shifted_x_clipped_point_evaluations": clipped_x_evaluations,
        "sx_values_with_clipping": sx_values_with_clipping,
        "shift_combinations_with_clipping": sx_values_with_clipping * AXIS_POINTS,
        "total_shift_combinations": AXIS_POINTS * AXIS_POINTS,
    }
    return extrema, coverage


def channel_uq(panel: str, channel: str, paper: dict, local: dict,
               historical: dict, dense_thresholds: dict[str, float | None],
               model_validity: bool, strict_thresholds: dict[str, float | None],
               strict_model_validity: bool, strict_threshold_provenance: str) -> tuple[dict, list[dict]]:
    paper_x_all, paper_y_all = paper[panel, channel, "mie"]
    local_x, local_y = local[panel][channel, "mie"]
    domain_lower, domain_upper = PANEL_DOMAINS[panel]
    keep = (
        (paper_x_all >= max(domain_lower, float(local_x.min())))
        & (paper_x_all <= min(domain_upper, float(local_x.max())))
    )
    paper_x = paper_x_all[keep]
    paper_y = paper_y_all[keep]
    if len(paper_x) < 3:
        raise RuntimeError(f"{panel}/{channel}: fewer than three common-domain paper vertices")

    # The fixed dense grid uses the retained paper support endpoints.  This is
    # the rule that gives the named MQ support [0.3697125, 0.9991572].
    lower = float(paper_x.min())
    upper = float(paper_x.max())
    x = np.linspace(lower, upper, UQ_POINTS)
    paper_line = np.interp(x, paper_x, paper_y)
    local_line = np.interp(x, local_x, local_y)

    widths = np.diff(paper_x)
    segment_h = widths.copy()
    if len(segment_h) > 1:
        segment_h[1:] = np.maximum(widths[:-1], widths[1:])
    segment_index = np.clip(np.searchsorted(paper_x, x, side="right") - 1, 0, len(widths) - 1)
    h = segment_h[segment_index]

    # Match the frozen trial's three-point finite-difference construction.
    curvature_local = np.abs(np.gradient(np.gradient(local_y, local_x), local_x))
    curvature = np.interp(x, local_x, curvature_local)
    conservative_band = 0.5 * curvature * h * h
    # A5-v2 changes the primary theorem sensitivity to a segment supremum and
    # the segment's own width.  It is intentionally distinct from the older
    # pointwise 0.5*M(x)*max-adjacent-h^2 envelope above.
    segment_curvature_sup = np.empty(len(widths), dtype=float)
    for segment in range(len(widths)):
        left, right = paper_x[segment], paper_x[segment + 1]
        support = curvature_local[(local_x >= left) & (local_x <= right)]
        endpoint_values = np.interp([left, right], local_x, curvature_local)
        segment_curvature_sup[segment] = float(np.max(np.concatenate((support, endpoint_values))))
    theorem_band = 0.125 * segment_curvature_sup[segment_index] * widths[segment_index] ** 2

    # Directly measured local-curve interpolation proxy.  It is diagnostic and
    # cannot replace either fixed coefficient after seeing the result.
    local_at_paper_vertices = np.interp(paper_x, local_x, local_y)
    local_reinterpolated = np.interp(x, paper_x, local_at_paper_vertices)
    interpolation_proxy = np.abs(local_line - local_reinterpolated)

    extrema, coverage = enumerate_axis_grid(
        x, paper_line, local_x, local_y,
        {"conservative_0_5": conservative_band, "theorem_0_125": theorem_band},
    )

    paper_peak_x, paper_peak_y = estimate_peak(paper_x, paper_y)
    local_peak_x, local_peak_y = estimate_peak(x, local_line)
    peak_vertex = int(np.argmin(np.abs(paper_x - paper_peak_x)))
    left_gap = float(paper_x[peak_vertex] - paper_x[max(0, peak_vertex - 1)])
    right_gap = float(paper_x[min(len(paper_x) - 1, peak_vertex + 1)] - paper_x[peak_vertex])
    peak_u = 0.5 * max(left_gap, right_gap) + DX
    peak_delta = abs(float(local_peak_x) - float(paper_peak_x))
    peak_interval = (max(0.0, peak_delta - peak_u), peak_delta + peak_u)

    legacy_rmse = (
        extrema["conservative_0_5"]["rmse_lower_min"]["value"],
        extrema["conservative_0_5"]["rmse_upper_max"]["value"],
    )
    legacy_p95 = (
        extrema["conservative_0_5"]["p95_lower_min"]["value"],
        extrema["conservative_0_5"]["p95_upper_max"]["value"],
    )
    theorem_rmse = (
        extrema["theorem_0_125"]["rmse_lower_min"]["value"],
        extrema["theorem_0_125"]["rmse_upper_max"]["value"],
    )
    theorem_p95 = (
        extrema["theorem_0_125"]["p95_lower_min"]["value"],
        extrema["theorem_0_125"]["p95_upper_max"]["value"],
    )
    legacy_states = {
        "rmse": interval_state(legacy_rmse, HISTORICAL_THRESHOLDS["rmse"]),
        "p95_abs": interval_state(legacy_p95, HISTORICAL_THRESHOLDS["p95_abs"]),
        "peak_x": interval_state(peak_interval, HISTORICAL_THRESHOLDS["peak_x"]),
    }
    legacy_states["composite"] = old_composite(tuple(
        legacy_states[key] for key in ("rmse", "p95_abs", "peak_x")
    ))

    strict = historical["panels"][panel]["curves"][channel]["mie"]
    weighting_212 = _arc_length_resample(
        paper_x, paper_y, local_x, local_y, 212,
        use_source_vertices=(len(paper_x) == 212),
        thresholds=(strict_thresholds if panel == "a" and channel == "MQ" and len(paper_x) == 212 else dense_thresholds),
        model_validity=(strict_model_validity if panel == "a" and channel == "MQ" and len(paper_x) == 212 else model_validity),
        threshold_provenance=(strict_threshold_provenance if panel == "a" and channel == "MQ" and len(paper_x) == 212 else "none_by_A5_v2_spec"),
    )
    if panel == "a" and channel == "MQ" and len(paper_x) == 212:
        strict_receipt = historical["panels"]["a"]["curves"]["MQ"]["mie"]
        weighting_212.update({
            "rmse": strict_receipt["rmse"],
            "p95_abs": strict_receipt["p95_absolute_error"],
            "max_abs": strict_receipt["max_absolute_error"],
            "resampling": "historical_212_vertex_receipt",
        })

    result = {
        "panel": panel,
        "channel": channel,
        "curve": "mie",
        "paper_vertices": int(len(paper_x)),
        "uq_points": UQ_POINTS,
        "domain": [lower, upper],
        "axis_shift_bounds": {"delta_x": DX, "delta_y": DY},
        "axis_grid": {"points_per_axis": AXIS_POINTS, "inclusive": True},
        "spacing": {
            "median_dx": float(np.median(widths)),
            "max_dx": float(np.max(widths)),
            "h_definition": "max(previous_segment_dx, current_segment_dx); first segment uses its own dx",
        },
        "nominal_dense": {
            "rmse": float(np.sqrt(np.mean((local_line - paper_line) ** 2))),
            "p95_abs": float(np.percentile(np.abs(local_line - paper_line), 95)),
            "peak_x_delta": peak_delta,
            "paper_peak": [float(paper_peak_x), float(paper_peak_y)],
            "local_peak": [float(local_peak_x), float(local_peak_y)],
        },
        "historical_strict": {
            "rmse": strict["rmse"],
            "p95_abs": strict["p95_absolute_error"],
            "peak_x_delta": strict["peak_x_difference"],
            "status": strict["status"],
        },
        "axis_only_interval": {
            "rmse": [extrema["axis_only"]["rmse_min"]["value"], extrema["axis_only"]["rmse_max"]["value"]],
            "p95_abs": [extrema["axis_only"]["p95_min"]["value"], extrema["axis_only"]["p95_max"]["value"]],
        },
        "interpolation": {
            "conservative_0_5": {
                "rmse": float(np.sqrt(np.mean(conservative_band ** 2))),
                "p95": float(np.percentile(conservative_band, 95)),
                "max": float(np.max(conservative_band)),
            },
            "theorem_0_125": {
                "rmse": float(np.sqrt(np.mean(theorem_band ** 2))),
                "p95": float(np.percentile(theorem_band, 95)),
                "max": float(np.max(theorem_band)),
            },
            "direct_proxy": {
                "rmse": float(np.sqrt(np.mean(interpolation_proxy ** 2))),
                "p95": float(np.percentile(interpolation_proxy, 95)),
                "max": float(np.max(interpolation_proxy)),
            },
        },
        "legacy_named_spec_diagnostic": {
            "promotion_eligible": False,
            "reason": "superseded by A5-v2 statistical semantics",
            "rmse_interval": list(legacy_rmse),
            "p95_abs_interval": list(legacy_p95),
            "peak_x_interval": list(peak_interval),
            "status": legacy_states,
        },
        "latest_spec_diagnostic": {
            "promotion_eligible": False,
            "reason": (
                "axis and interpolation components are proxy/conditional and the independent "
                "physics uncertainty bound is absent"
            ),
            "theorem_rmse_interval": list(theorem_rmse),
            "theorem_p95_abs_interval": list(theorem_p95),
            "peak_x_interval": list(peak_interval),
        },
        "weighting_sensitivity": [
            weighting_212,
            _arc_length_resample(paper_x, paper_y, local_x, local_y, 1000,
                                 thresholds=dense_thresholds, model_validity=model_validity,
                                 threshold_provenance="none_by_A5_v2_spec"),
            _arc_length_resample(paper_x, paper_y, local_x, local_y, 4000,
                                 thresholds=dense_thresholds, model_validity=model_validity,
                                 threshold_provenance="none_by_A5_v2_spec"),
            _arc_length_resample(paper_x, paper_y, local_x, local_y, 16000,
                                 thresholds=dense_thresholds, model_validity=model_validity,
                                 threshold_provenance="none_by_A5_v2_spec"),
            _equal_segment_row(paper_x, paper_y, local_x, local_y,
                               thresholds=dense_thresholds, model_validity=model_validity,
                               threshold_provenance="none_by_A5_v2_spec"),
        ],
        "coverage": coverage,
        "extrema_receipt": extrema,
    }

    pointwise = []
    for index in range(UQ_POINTS):
        pointwise.append({
            "panel": panel,
            "channel": channel,
            "grid_index": index,
            "x_alaee": float(x[index]),
            "paper_y": float(paper_line[index]),
            "local_y": float(local_line[index]),
            "nominal_abs_error": float(abs(local_line[index] - paper_line[index])),
            "segment_index": int(segment_index[index]),
            "h_adjacent": float(h[index]),
            "curvature_abs": float(curvature[index]),
            "segment_curvature_sup": float(segment_curvature_sup[segment_index[index]]),
            "theorem_segment_width": float(widths[segment_index[index]]),
            "u_conservative_0_5": float(conservative_band[index]),
            "u_theorem_0_125": float(theorem_band[index]),
            "interpolation_proxy_abs": float(interpolation_proxy[index]),
        })
    return result, pointwise


def _fmt_interval(values: list[float]) -> str:
    return f"[{values[0]:.8g}, {values[1]:.8g}]"


def write_markdown(summary: dict) -> None:
    rows = []
    for item in summary["channels"]:
        legacy = item["legacy_named_spec_diagnostic"]
        rows.append(
            f"| {item['panel']} | {item['channel']} | "
            f"{_fmt_interval(legacy['rmse_interval'])} | {legacy['status']['rmse']} | "
            f"{_fmt_interval(legacy['p95_abs_interval'])} | {legacy['status']['p95_abs']} | "
            f"{_fmt_interval(legacy['peak_x_interval'])} | {legacy['status']['peak_x']} | "
            f"{legacy['status']['composite']} | "
            f"{_fmt_interval(item['latest_spec_diagnostic']['theorem_rmse_interval'])} | "
            f"{_fmt_interval(item['latest_spec_diagnostic']['theorem_p95_abs_interval'])} | "
            f"{item['latest_spec_decision']['pre_override_diagnostic_if_historical_thresholds_were_applied']['composite']} | "
            f"{item['latest_spec_decision']['status']['composite']} |"
        )
    table = "\n".join(rows)
    command = 'python "code/run_fig2_uq.py"'
    pytest_path = (
        "$env:PYTHONPATH = (Resolve-Path "
        "'codex-prompts/out/A3-file-secret-hardening/optics_agent/comsol/runtime').Path"
    )

    note = f"""# Fig.2 Layer3 UQ 晋级轮

## 执行结论

恢复执行时发现原 B3 指定的 A5 预注册之后，`A5-v2/preregister/SPEC.md` 已冻结并明确
supersede 旧试运行的统计语义。故下表保留旧 4000 点、401×401 平移、$0.5Mh^2$ 数值作为
`diagnostic_only`，正式 `layer3_uq_status` 按最新 spec fail-closed：全部 `UNRESOLVED`。

| panel | channel | legacy RMSE interval | state | legacy p95 interval | state | peak-x interval | state | legacy composite | latest theorem RMSE proxy | latest theorem p95 proxy | pre-override diagnostic | latest layer3 UQ |
|---|---|---:|---|---:|---|---:|---|---|---:|---:|---|---|
{table}

历史 strict 门槛 0.02 / 0.05 / 0.01 仍原样保留，但 A5-v2 禁止把它们继承为 dense UQ
门槛。当前轴项仍标为 sensitivity proxy，插值 coverage 未被校准为未知论文曲线 coverage，
physics receipt 也没有独立 uncertainty bound；因此 `uq_model_validity=false`。
最新 theorem proxy 区间已逐通道列出，但其阈值来源为 `none_by_A5_v2_spec`，不能裁决。

## 晋级裁决

- method gate: `{summary['promotion']['method_claim_status']}`
- required-domain coverage: `{summary['promotion']['coverage_status']}`
- layer3 UQ: `{summary['layer3_uq_status']}`
- promotion: `{summary['promotion']['promotion_to_physical_reproduction_success']}`
- result_class: `{summary['promotion']['result_class']}`

金球 panel-b 的 JC 域外缺口仍为独立 blocker；UQ 不得隐藏该缺口。既有第 2 轮 strict
receipt 未被改写。

## 复现

```powershell
{command}
{pytest_path}
python -m pytest -q
```

逐点输入、曲率、相邻间距和两种插值带见 `data/fig2_uq_pointwise.csv`；212/1000/4000/
16000/equal-segment 五种权重敏感性见 `data/fig2_uq_weighting_sensitivity.csv`；逐通道平移
网格极值参数与 input SHA-256 见 `data/fig2_uq_summary.json`。
"""

    verdict = f"""# B3 promotion verdict

## Verdict

`promotion_to_physical_reproduction_success: {summary['promotion']['promotion_to_physical_reproduction_success']}`

`result_class: {summary['promotion']['result_class']}`

`layer3_uq_status: {summary['layer3_uq_status']}`

| panel | channel | legacy RMSE interval vs 0.02 | state | legacy p95 interval vs 0.05 | state | peak-x interval vs 0.01 | state | diagnostic composite | latest theorem RMSE proxy | latest theorem p95 proxy | pre-override diagnostic | gate-eligible status |
|---|---|---:|---|---:|---|---:|---|---|---:|---:|---|---|
{table}

表中 `legacy` 区间是为完成原 B3 全通道要求而逐点、逐平移组合实跑的敏感性结果；它们
不具晋级资格。最新 A5-v2 spec 要求 calibrated axis/interpolation/physics uncertainty、有效
coverage，以及 dense-mode 专属门槛。当前 receipts 不满足这些条件，因此所有正式逐通道
状态均为 `UNRESOLVED`，不能用旧 strict 阈值把任一 dense lane 判为 PASS 或 FAIL。

最新 theorem proxy 区间与 five-scheme weighting 数值也写入
`data/fig2_uq_channel_results.csv`、`data/fig2_uq_weighting_sensitivity.csv`；dense threshold
字段保持 `null`，不是遗漏。

此外，历史 strict 总状态仍为 `{summary['promotion']['strict_vector_fidelity_status']}`，panel-b
required-domain coverage 仍为 `{summary['promotion']['coverage_status']}`。任一条件都足以阻止
promotion；最终裁决为 `{summary['promotion']['promotion_to_physical_reproduction_success']}`，不得美化。

复算命令：`{command}`。
"""

    discrepancies = f"""# B3 discrepancies

## D1 — UQ spec supersession (blocking)

- 原任务明确指定 `A5-recompute/preregister/MQ-uncertainty-preregistration.md` 为唯一权威，
  其中 dense UQ 使用 $0.5Mh^2$、401×401 平移网格和历史 0.02/0.05/0.01 门槛。
- 后写入的 `A5-v2/preregister/SPEC.md` 及 `A5-mq-rootcause.md` supersession 声明改为
  $Mh^2/8$ primary、$0.5Mh^2$ sensitivity-only、dense mode 禁止继承历史门槛，并在
  model invalid 时强制 `UNRESOLVED`。
- 恢复指令要求以最新 spec 为准。因此本轮把旧方法完整实跑但只作 diagnostic，正式裁决
  按 A5-v2 fail-closed。未修改任何 spec。

## D2 — 原 spec 文本与其 dense trial 的 h 定义不一致

- 文本定义每段 $h_i=\\max(x_i-x_{{i-1}},x_{{i+1}}-x_i)$。
- 随附 `mq_uncertainty_dense_trial.py` 实际只用当前段宽 $x_{{i+1}}-x_i$。
- 本轮数字遵循文本公式（相邻段最大值），未为复现试运行表格而追溯性改公式。

## D3 — 原 spec 的注册对象与 B3 扩展范围

- 原预注册只明确 panel-a / MQ / Mie 实线和 panel-a 轴残差。
- B3 另要求 ED/MD/EQ/MQ × panel a/b。为给出可审计数值，本轮对八条实线统一应用冻结的
  panel-a 残差；扩展通道不宣称被原预注册覆盖，且在 A5-v2 下均 fail-closed。

## D4 — Grahn v4 relevance

`formalization/grahn.yaml` v4（含 D1 归一化合同修复）属于 Grahn mapping 工作流，不是
Fig.2 Layer3 的 UQ 输入。本轮只核对其存在与版本，未消费其物理合同，也未修改该文件。

## D5 — repository-wide pytest import path

根目录直接运行 `python -m pytest -q` 会在既有 A3 hardening 测试收集阶段因
`case_importer` 不在 `sys.path` 而失败；该模块实际位于
`codex-prompts/out/A3-file-secret-hardening/optics_agent/comsol/runtime/`。本轮未修改 A3
产物或测试，而是仅在验证命令中临时设置 `PYTHONPATH`；随后全量回归通过。
"""

    NOTE_MD.write_text(note, encoding="utf-8")
    VERDICT_MD.write_text(verdict, encoding="utf-8")
    DISCREPANCIES_MD.write_text(discrepancies, encoding="utf-8")


def _run_channel_task(args: tuple[str, str, dict, dict, dict, dict, bool, dict, bool, str]) -> tuple[dict, list[dict]]:
    """Top-level worker wrapper for Windows spawn multiprocessing."""
    return channel_uq(*args)


def main() -> int:
    for required in (
        OLD_SPEC, LATEST_SPEC, EXTRACTION_RECEIPT, PHYSICS_RECEIPT,
        LATEST_UQ_RECEIPT, LATEST_WEIGHTING_RECEIPT,
        PAPER_CSV, PAPER_METADATA, HISTORICAL_SUMMARY,
    ):
        if not required.is_file():
            raise FileNotFoundError(required)

    paper = load_paper_curves()
    local = load_local_curves()
    historical = json.loads(HISTORICAL_SUMMARY.read_text(encoding="utf-8"))
    extraction = json.loads(EXTRACTION_RECEIPT.read_text(encoding="utf-8"))
    physics = json.loads(PHYSICS_RECEIPT.read_text(encoding="utf-8"))
    latest_uq = json.loads(LATEST_UQ_RECEIPT.read_text(encoding="utf-8"))
    verify_external_hash_map(latest_uq.get("input_sha256", {}))

    extraction_valid = bool(extraction.get("decision", {}).get("uq_model_validity", False))
    physics_bound = physics.get("uncertainty_bound")
    physics_semantics = physics.get("uncertainty_bound_semantics")
    physics_valid = (
        isinstance(physics_bound, (int, float))
        and math.isfinite(float(physics_bound))
        and isinstance(physics_semantics, str)
        and "independent" in physics_semantics.lower()
    )
    dense_thresholds = {"rmse": None, "p95_abs": None, "peak_x": None}
    strict_thresholds = {
        "rmse": latest_uq.get("thresholds", {}).get("rmse"),
        "p95_abs": latest_uq.get("thresholds", {}).get("p95_abs"),
        "peak_x": latest_uq.get("thresholds", {}).get("peak_x"),
    }
    strict_threshold_provenance = latest_uq.get("thresholds", {}).get(
        "provenance", "historical strict only"
    )
    strict_model_validity = bool(latest_uq.get("model_validity", False))
    global_model_validity = extraction_valid and physics_valid

    tasks = [
        (
            panel, channel, paper, local, historical, dense_thresholds,
            global_model_validity, strict_thresholds, strict_model_validity,
            strict_threshold_provenance,
        )
        for panel in PANELS for channel in CHANNELS
    ]
    with ProcessPoolExecutor(max_workers=min(4, len(tasks))) as pool:
        completed = list(pool.map(_run_channel_task, tasks))

    channel_results: list[dict] = []
    all_pointwise: list[dict] = []
    for result, pointwise in completed:
        coverage_valid = not result["coverage"]["coverage_warning"]
        finite_valid = all(
            math.isfinite(float(row[key]))
            for row in pointwise
            for key in (
                "x_alaee", "paper_y", "local_y", "nominal_abs_error",
                "curvature_abs", "segment_curvature_sup", "u_conservative_0_5",
                "u_theorem_0_125", "interpolation_proxy_abs",
            )
        )
        channel_model_validity = global_model_validity and coverage_valid and finite_valid
        latest_diag = result["latest_spec_diagnostic"]
        latest_intervals = {
            "rmse": tuple(latest_diag["theorem_rmse_interval"]),
            "p95_abs": tuple(latest_diag["theorem_p95_abs_interval"]),
            "peak_x": tuple(latest_diag["peak_x_interval"]),
        }
        latest_states = {
            name: interval_state(latest_intervals[name], dense_thresholds[name], channel_model_validity)
            for name in ("rmse", "p95_abs", "peak_x")
        }
        diagnostic_states_if_historical_thresholds = {
            name: interval_state(latest_intervals[name], HISTORICAL_THRESHOLDS[name], True)
            for name in ("rmse", "p95_abs", "peak_x")
        }
        latest_states["composite"] = latest_composite(tuple(
            latest_states[key] for key in ("rmse", "p95_abs", "peak_x")
        ), channel_model_validity)
        result["latest_spec_decision"] = {
            "mode": "dense_curve_uq",
            "thresholds": dense_thresholds,
            "threshold_provenance": "none_by_A5_v2_spec",
            "model_validity": channel_model_validity,
            "coverage_valid": coverage_valid,
            "finite_data": finite_valid,
            "validity_reasons": [
                "axis evidence is labelled sensitivity proxy rather than calibrated nuisance coverage",
                "interpolation coverage for the unknown paper curve is not established",
                "independent physics uncertainty bound is absent",
                "dense-mode thresholds are absent and may not inherit historical strict thresholds",
                "A5-v2 receipts are MQ-specific and do not validate the scope extension to every channel",
            ],
            "status": latest_states,
            "pre_override_diagnostic_if_historical_thresholds_were_applied": {
                **diagnostic_states_if_historical_thresholds,
                "composite": latest_composite(tuple(
                    diagnostic_states_if_historical_thresholds[key]
                    for key in ("rmse", "p95_abs", "peak_x")
                ), True),
                "promotion_eligible": False,
            },
        }
        channel_results.append(result)
        all_pointwise.extend(pointwise)

    channel_composites = [item["latest_spec_decision"]["status"]["composite"] for item in channel_results]
    layer3_status = (
        "PASS" if channel_composites and all(value == "PASS" for value in channel_composites)
        else "UNRESOLVED" if any(value == "UNRESOLVED" for value in channel_composites)
        else "FAIL"
    )
    all_uq_pass = bool(channel_composites) and all(value == "PASS" for value in channel_composites)
    mq_result = next(item for item in channel_results if item["panel"] == "a" and item["channel"] == "MQ")
    other_results = [item for item in channel_results if not (
        item["panel"] == "a" and item["channel"] == "MQ"
    )]
    other_channels_clear = all(
        item["historical_strict"]["status"] == "PASS_VECTOR_CONSISTENT"
        and item["latest_spec_decision"]["status"]["composite"] == "PASS"
        for item in other_results
    )
    promotion_eligible = (
        historical["method_claim_status"] == "PASS"
        and historical["coverage_status"] == "PASS"
        and mq_result["latest_spec_decision"]["status"]["composite"] == "PASS"
        and other_channels_clear
    )
    promotion = {
        "method_claim_status": historical["method_claim_status"],
        "strict_vector_fidelity_status": historical["strict_vector_fidelity_status"],
        "coverage_status": historical["coverage_status"],
        "mq_uq_composite": next(
            item["latest_spec_decision"]["status"]["composite"]
            for item in channel_results if item["panel"] == "a" and item["channel"] == "MQ"
        ),
        "other_channels_have_unresolved": any(value == "UNRESOLVED" for value in channel_composites),
        "promotion_to_physical_reproduction_success": (
            "physical_reproduction_success" if promotion_eligible else "DENIED"
        ),
        "result_class": (
            "physical_reproduction_success"
            if promotion_eligible
            else historical.get("result_class", "partial_physical_match")
        ),
    }
    consumed = [
        OLD_SPEC, LATEST_SPEC, EXTRACTION_RECEIPT, PHYSICS_RECEIPT,
        LATEST_UQ_RECEIPT, LATEST_WEIGHTING_RECEIPT,
        PAPER_CSV, PAPER_METADATA, HISTORICAL_SUMMARY,
        DATA / "fig1a_multipole_mie.csv", DATA / "fig1a_multipole_table2.csv",
        DATA / "fig2_gold_jc_sensitivity.csv",
        Path(__file__).resolve(),
    ]
    summary = {
        "schema_version": 1,
        "task": "B3",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "authoritative_spec": str(LATEST_SPEC.relative_to(ROOT)).replace("\\", "/"),
        "named_original_spec": str(OLD_SPEC.relative_to(ROOT)).replace("\\", "/"),
        "spec_resolution": "A5-v2 governs formal status; original named method is retained as diagnostic only",
        "grid": {"uq_points": UQ_POINTS, "axis_points_per_axis": AXIS_POINTS, "inclusive": True},
        "historical_thresholds": HISTORICAL_THRESHOLDS,
        "strict_vertex_212_thresholds_from_latest_receipt": strict_thresholds,
        "dense_thresholds": dense_thresholds,
        "global_model_validity": global_model_validity,
        "latest_uq_receipt_input_hashes_verified": True,
        "layer3_uq_status": layer3_status,
        "promotion": promotion,
        "channels": channel_results,
        "weighting_sensitivity": [
            {"panel": item["panel"], "channel": item["channel"], **row}
            for item in channel_results
            for row in item["weighting_sensitivity"]
        ],
        "input_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in consumed},
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }
    verify_recorded_hashes(summary)

    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "panel", "channel", "paper_vertices", "domain_lower", "domain_upper",
            "legacy_rmse_lower", "legacy_rmse_upper", "legacy_rmse_status",
            "legacy_p95_lower", "legacy_p95_upper", "legacy_p95_status",
            "peak_x_lower", "peak_x_upper", "peak_x_status", "legacy_composite",
            "theorem_band_rmse", "theorem_band_p95", "theorem_band_max",
            "theorem_rmse_lower", "theorem_rmse_upper", "theorem_p95_lower", "theorem_p95_upper",
            "latest_rmse_status", "latest_p95_status", "latest_peak_status",
            "latest_pre_override_composite", "layer3_uq_status", "model_validity", "dense_threshold_provenance",
            "historical_strict_status", "coverage_warning",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in channel_results:
            legacy = item["legacy_named_spec_diagnostic"]
            latest = item["latest_spec_decision"]
            writer.writerow({
                "panel": item["panel"], "channel": item["channel"],
                "paper_vertices": item["paper_vertices"],
                "domain_lower": item["domain"][0], "domain_upper": item["domain"][1],
                "legacy_rmse_lower": legacy["rmse_interval"][0],
                "legacy_rmse_upper": legacy["rmse_interval"][1],
                "legacy_rmse_status": legacy["status"]["rmse"],
                "legacy_p95_lower": legacy["p95_abs_interval"][0],
                "legacy_p95_upper": legacy["p95_abs_interval"][1],
                "legacy_p95_status": legacy["status"]["p95_abs"],
                "peak_x_lower": legacy["peak_x_interval"][0],
                "peak_x_upper": legacy["peak_x_interval"][1],
                "peak_x_status": legacy["status"]["peak_x"],
                "legacy_composite": legacy["status"]["composite"],
                "theorem_band_rmse": item["interpolation"]["theorem_0_125"]["rmse"],
                "theorem_band_p95": item["interpolation"]["theorem_0_125"]["p95"],
                "theorem_band_max": item["interpolation"]["theorem_0_125"]["max"],
                "theorem_rmse_lower": item["latest_spec_diagnostic"]["theorem_rmse_interval"][0],
                "theorem_rmse_upper": item["latest_spec_diagnostic"]["theorem_rmse_interval"][1],
                "theorem_p95_lower": item["latest_spec_diagnostic"]["theorem_p95_abs_interval"][0],
                "theorem_p95_upper": item["latest_spec_diagnostic"]["theorem_p95_abs_interval"][1],
                "latest_rmse_status": latest["status"]["rmse"],
                "latest_p95_status": latest["status"]["p95_abs"],
                "latest_peak_status": latest["status"]["peak_x"],
                "latest_pre_override_composite": latest["pre_override_diagnostic_if_historical_thresholds_were_applied"]["composite"],
                "layer3_uq_status": latest["status"]["composite"],
                "model_validity": latest["model_validity"],
                "dense_threshold_provenance": latest["threshold_provenance"],
                "historical_strict_status": item["historical_strict"]["status"],
                "coverage_warning": item["coverage"]["coverage_warning"],
            })

    with POINTWISE_CSV.open("w", newline="", encoding="utf-8") as stream:
        fields = list(all_pointwise[0])
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_pointwise)

    with WEIGHTING_CSV.open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "panel", "channel", "scheme", "effective_count", "rmse", "p95_abs", "max_abs",
            "threshold_rmse", "threshold_p95_abs", "rmse_status", "p95_status", "status", "threshold_provenance",
            "model_validity", "resampling",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary["weighting_sensitivity"])

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary)
    print(json.dumps({
        "task": "B3",
        "layer3_uq_status": layer3_status,
        "promotion": promotion["promotion_to_physical_reproduction_success"],
        "result_class": promotion["result_class"],
        "channels": [
            {
                "panel": item["panel"], "channel": item["channel"],
                "legacy": item["legacy_named_spec_diagnostic"]["status"]["composite"],
                "latest": item["latest_spec_decision"]["status"]["composite"],
            }
            for item in channel_results
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
