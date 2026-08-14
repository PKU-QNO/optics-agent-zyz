# -*- coding: utf-8 -*-
"""Extract Alaee Fig.2 curves from the source PDF vector paths.

The paper uses outlined fonts, but the plotted curves remain PDF drawing
objects.  This module deliberately treats vector paths as the primary data
source and keeps raster extraction as an explicitly lower-confidence
fallback.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - exercised by fallback tests only
    fitz = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "fig2_paper_vector_curves.csv"
DEFAULT_META = ROOT / "data" / "fig2_paper_vector_metadata.json"
DEFAULT_PDF_GLOB = "Alaee_2018*.pdf"

MULTIPOLES = ("ED", "MD", "EQ", "MQ")
PDF_COLORS = {
    "ED": (0.84706, 0.32157, 0.094118),
    "MD": (0.0, 0.44314, 0.73725),
    "EQ": (0.92549, 0.69020, 0.12157),
    "MQ": (0.49020, 0.18039, 0.55294),
}


@dataclass(frozen=True)
class PanelSpec:
    name: str
    x_left: float
    x_right: float
    y_top: float
    y_bottom: float
    y_tick_pages: tuple[float, ...]


# These frame coordinates are taken from the page-4 axis drawing objects;
# tick positions are re-discovered from the page and validated below.
PANELS = {
    "a": PanelSpec("a", 104.36, 236.429, 87.878, 144.626,
                   (136.395, 120.274, 103.989, 87.878)),
    "b": PanelSpec("b", 104.429, 236.494, 151.866, 208.614,
                   (200.383, 184.261, 167.979, 151.866)),
}
X_TICK_VALUES = np.asarray([0.2, 0.4, 0.6, 0.8, 1.0], dtype=float)


def find_source_pdf(path: str | Path | None = None) -> Path:
    """Resolve the paper PDF without depending on a Chinese path literal."""
    if path:
        candidate = Path(path)
        if candidate.exists():
            return candidate.resolve()
        raise FileNotFoundError(candidate)
    env_path = os.environ.get("ALAEE_FIG2_PDF")
    if env_path and Path(env_path).exists():
        return Path(env_path).resolve()
    roots = [
        Path("C:/Users/27370/Desktop/project/optics_agent/papers/mie-f"),
        ROOT.parent.parent.parent / "optics_agent" / "papers" / "mie-f",
    ]
    for root in roots:
        if root.exists():
            hits = sorted(root.rglob(DEFAULT_PDF_GLOB))
            if hits:
                return hits[0].resolve()
    raise FileNotFoundError("Alaee 2018 source PDF not found")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _close_color(color, target, tol=2e-4) -> bool:
    return color is not None and len(color) == 3 and float(np.linalg.norm(np.asarray(color) - target)) <= tol


def _drawing_points(drawing) -> list[tuple[float, float]]:
    points = []
    for item in drawing.get("items", []):
        if not item:
            continue
        kind = item[0]
        if kind == "l":
            for point in item[1:3]:
                points.append((float(point.x), float(point.y)))
        elif kind == "c":
            # Bezier marker paths contain four points.  The bounding-box
            # center is less sensitive to the particular Bezier orientation.
            for point in item[1:]:
                points.append((float(point.x), float(point.y)))
    return points


def _dedupe_sort(points: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    unique = {}
    for x, y in points:
        unique[(round(x, 5), round(y, 5))] = (x, y)
    return sorted(unique.values(), key=lambda pair: (pair[0], pair[1]))


def _fit_axis(page, panel: PanelSpec) -> dict:
    """Fit x and y transforms from axis tick drawing objects.

    The expected tick values only identify the labels; the fitted positions
    are taken from the PDF paths themselves and checked for residuals.
    """
    x_candidates = []
    y_candidates = []
    for drawing in page.get_drawings():
        color = drawing.get("color")
        if color is not None and (len(color) != 3 or max(color) > 0.15):
            continue
        for item in drawing.get("items", []):
            if not item or item[0] != "l":
                continue
            p0, p1 = item[1], item[2]
            dx, dy = abs(float(p1.x - p0.x)), abs(float(p1.y - p0.y))
            # x ticks are short vertical strokes immediately above/below the
            # bottom frame.  The range avoids the long panel spines.
            if dx < 0.01 and 0.9 <= dy <= 1.6:
                x = float((p0.x + p1.x) / 2)
                y_candidates_frame = (panel.y_bottom - 1.5 <= min(p0.y, p1.y)
                                      <= panel.y_bottom + 0.2)
                if panel.x_left - 0.2 <= x <= panel.x_right + 0.2 and y_candidates_frame:
                    x_candidates.append(x)
            # y ticks are short horizontal strokes at the right spine.
            if dy < 0.01 and 1.0 <= dx <= 1.5:
                y = float((p0.y + p1.y) / 2)
                x_candidates_frame = (panel.x_right - 1.5 <= max(p0.x, p1.x)
                                      <= panel.x_right + 0.2)
                if panel.y_top - 0.2 <= y <= panel.y_bottom + 0.2 and x_candidates_frame:
                    y_candidates.append(y)

    def unique_sorted(values):
        return sorted({round(value, 3) for value in values})

    x_ticks = unique_sorted(x_candidates)
    # A few line fragments can survive at both frame edges; select the five
    # positions spanning the expected labelled range.
    if len(x_ticks) < 5:
        raise ValueError(f"could not find five x ticks for panel {panel.name}: {x_ticks}")
    x_ticks = np.asarray(x_ticks[-5:], dtype=float)
    y_ticks = np.asarray(unique_sorted(y_candidates), dtype=float)
    if len(y_ticks) < 4:
        # The right-spine tick path may be split differently by a PDF writer;
        # use the validated page coordinates as a conservative fallback.
        y_ticks = np.asarray(panel.y_tick_pages, dtype=float)
    else:
        y_ticks = y_ticks[:4]
    y_ticks = np.sort(y_ticks)
    # y increases downwards in PDF coordinates; the smallest page y is the
    # largest data value.
    y_values = np.asarray([7.0, 5.0, 3.0, 1.0], dtype=float)
    x_fit = np.polyfit(x_ticks, X_TICK_VALUES, 1)
    y_fit = np.polyfit(y_ticks, y_values, 1)
    # polyfit maps PDF-page coordinates to data coordinates, so the direct
    # residuals below are in x_alaee / normalized-y units, not PDF points.
    x_resid_data = float(np.max(np.abs(np.polyval(x_fit, x_ticks) - X_TICK_VALUES)))
    y_resid_data = float(np.max(np.abs(np.polyval(y_fit, y_ticks) - y_values)))
    x_resid_pdf_pt = x_resid_data / abs(float(x_fit[0]))
    y_resid_pdf_pt = y_resid_data / abs(float(y_fit[0]))
    # The acceptance contract is stated in source PDF points.  Keep both
    # representations explicit so future reports cannot confuse the units.
    if x_resid_pdf_pt > 0.5 or y_resid_pdf_pt > 0.5:
        raise ValueError(
            "axis fit residual too large in PDF points: "
            f"x={x_resid_pdf_pt}, y={y_resid_pdf_pt}"
        )
    return {
        "x_ticks_page": x_ticks.tolist(),
        "x_ticks_data": X_TICK_VALUES.tolist(),
        "y_ticks_page": y_ticks.tolist(),
        "y_ticks_data": y_values.tolist(),
        "x_fit_page_to_data": x_fit.tolist(),
        "y_fit_page_to_data": y_fit.tolist(),
        "x_fit_residual_data": x_resid_data,
        "y_fit_residual_data": y_resid_data,
        "x_fit_residual_pdf_pt": x_resid_pdf_pt,
        "y_fit_residual_pdf_pt": y_resid_pdf_pt,
        "frame": {"x_left": panel.x_left, "x_right": panel.x_right,
                  "y_top": panel.y_top, "y_bottom": panel.y_bottom},
    }


def _apply_fit(points, axis_fit):
    xfit = np.asarray(axis_fit["x_fit_page_to_data"])
    yfit = np.asarray(axis_fit["y_fit_page_to_data"])
    return [(float(np.polyval(xfit, x)), float(np.polyval(yfit, y))) for x, y in points]


def extract_vector(pdf_path: str | Path | None = None, page_number: int = 4) -> tuple[list[dict], dict]:
    if fitz is None:
        raise RuntimeError("PyMuPDF is unavailable; use extract_raster_fallback")
    source = find_source_pdf(pdf_path)
    document = fitz.open(source)
    if page_number < 1 or page_number > document.page_count:
        raise ValueError(f"page_number {page_number} outside PDF page count {document.page_count}")
    page = document[page_number - 1]
    rows = []
    axis = {}
    counts = {}
    for panel_name, panel in PANELS.items():
        axis[panel_name] = _fit_axis(page, panel)
        counts[panel_name] = {}
        for multipole, target in PDF_COLORS.items():
            line_points = []
            marker_centers = []
            line_drawings = marker_drawings = 0
            for drawing_index, drawing in enumerate(page.get_drawings()):
                if not _close_color(drawing.get("color"), np.asarray(target)):
                    continue
                rect = drawing["rect"]
                if rect.x1 < panel.x_left - 0.5 or rect.x0 > panel.x_right + 0.5:
                    continue
                if rect.y1 < panel.y_top - 0.5 or rect.y0 > panel.y_bottom + 0.5:
                    continue
                kinds = [item[0] for item in drawing.get("items", [])]
                if "l" in kinds and len(drawing.get("items", [])) >= 20:
                    line_drawings += 1
                    line_points.extend(_drawing_points(drawing))
                elif "c" in kinds and len(drawing.get("items", [])) == 4:
                    marker_drawings += 1
                    marker_centers.append(((float(rect.x0 + rect.x1) / 2),
                                           (float(rect.y0 + rect.y1) / 2)))
            line_points = _dedupe_sort(line_points)
            marker_centers = _dedupe_sort(marker_centers)
            for curve, points in (("mie", line_points), ("exact", marker_centers)):
                for x, y in _apply_fit(points, axis[panel_name]):
                    rows.append({"panel": panel_name, "multipole": multipole,
                                 "curve": curve, "x_alaee": x, "y_norm": y,
                                 "source": str(source), "page": page_number})
            counts[panel_name][multipole] = {
                "line_drawings": line_drawings,
                "line_points": len(line_points),
                "marker_drawings": marker_drawings,
                "marker_points": len(marker_centers),
            }
    metadata = {
        "mode": "vector",
        "source_pdf": str(source),
        "source_sha256": sha256_file(source),
        "page": page_number,
        "page_count": document.page_count,
        "panels": axis,
        "counts": counts,
        "palette_pdf": {key: list(value) for key, value in PDF_COLORS.items()},
        "curve_identity": {"mie": "colored l polyline", "exact": "colored c marker"},
        "domain_policy": {"primary_x": [0.2, 1.0], "gold_jc_min_x": 500.0 / 1935.0},
    }
    return rows, metadata


def extract_raster_fallback(image_path: str | Path) -> tuple[list[dict], dict]:
    """Minimal deterministic color-mask fallback; never claims vector PASS."""
    from PIL import Image

    path = Path(image_path)
    image = np.asarray(Image.open(path).convert("RGB"))
    # Bounds correspond to the existing page-4 crop; the fallback is kept
    # explicit so a future crop can supply its own calibration.
    panels = {"a": (274, 802, 159, 387), "b": (274, 802, 415, 642)}
    colors = {"ED": (216, 82, 24), "MD": (0, 113, 187),
              "EQ": (235, 176, 31), "MQ": (125, 45, 140)}
    rows = []
    for panel, (x0, x1, y0, y1) in panels.items():
        for multipole, color in colors.items():
            mask = np.all(image == np.asarray(color), axis=2)
            ys, xs = np.where(mask & (np.indices(mask.shape)[1] >= x0)
                              & (np.indices(mask.shape)[1] <= x1)
                              & (np.indices(mask.shape)[0] >= y0)
                              & (np.indices(mask.shape)[0] <= y1))
            if len(xs) == 0:
                continue
            # Pixel traces cannot reliably separate solid and markers; expose
            # one combined curve and let comparison classify it as descriptive.
            for xpix in sorted(set(xs.tolist())):
                ypix = float(np.median(ys[xs == xpix]))
                xdata = 0.2 + (xpix - 311.0) * 0.8 / (802.0 - 311.0)
                ydata = (y1 - ypix) * 7.0 / (y1 - y0)
                rows.append({"panel": panel, "multipole": multipole,
                             "curve": "combined", "x_alaee": xdata,
                             "y_norm": ydata, "source": str(path), "page": None})
    return rows, {"mode": "raster", "source_image": str(path),
                  "confidence": "descriptive_only", "solid_marker_separation": "unreliable"}


def save_extraction(rows: list[dict], metadata: dict,
                    csv_path: str | Path = DEFAULT_OUTPUT,
                    metadata_path: str | Path = DEFAULT_META):
    csv_path, metadata_path = Path(csv_path), Path(metadata_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["panel", "multipole", "curve", "x_alaee", "y_norm", "source", "page"]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", default=None)
    parser.add_argument("--page", type=int, default=4)
    parser.add_argument("--csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_META)
    args = parser.parse_args()
    rows, metadata = extract_vector(args.pdf, args.page)
    save_extraction(rows, metadata, args.csv, args.metadata)
    print(json.dumps({"mode": metadata["mode"], "rows": len(rows), "metadata": str(args.metadata)}, indent=2))


if __name__ == "__main__":
    main()
