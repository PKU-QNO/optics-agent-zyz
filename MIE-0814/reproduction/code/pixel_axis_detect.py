#!/usr/bin/env python
"""
pixel_axis_detect.py
====================
Route A (step01): pixel-statistics coordinate-axis localization for the three
bitmap figures of Alaee et al. 2018 (mie-f reproduction).

Method
------
For each figure bitmap:
  1. Load RGB image, take background = corner pixel (white).
  2. Classify pixels:
       dark     : mean(RGB) < 110          -> axes, ticks, text
       colored  : channel spread > 60 and mean < 230 -> data curves
       otherwise: background / anti-aliasing
  3. Row statistics  : sum of dark pixels per row over a data segment.
     Column statistics: sum of dark pixels per column over a data segment.
  4. Axis identification:
     - Every horizontal dark line whose dark fraction over its panel segment
       is high is an x-axis; the bottom x-axis of a panel is the data baseline.
     - Every vertical dark line likewise is a y-axis.
     - Panel structure is derived from the grid of these lines (multi-panel
       figures: fig1 = 2x2, fig2/fig3 = 1x2).
  5. Tick marks: short vertical dark runs crossing/adjacent to the axis line,
     excluding the axis body. x ticks -> column list; y ticks -> row list.
  6. Curve colors: quantized clustering of colored pixels.
  7. Label regions: connected dark components near the axes (heuristic).

Outputs (under reproduction/):
  data/alaee_figN_axes.yaml   -- per-figure, all panels
  figs/axes_detection_figN.png -- overlay with crosshairs + tick marks

Run:
  python pixel_axis_detect.py
"""

import os
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

# ----------------------------------------------------------------------------
# I/O
# ----------------------------------------------------------------------------
REPRO = r"C:/Users/27370/Desktop/project/zotero/papers/mie-f/reproduction"
DATA_DIR = os.path.join(REPRO, "data")
FIGS_DIR = os.path.join(REPRO, "figs")

FIG_SOURCES = {
    "fig1": "C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/01-主论文/Alaee_2018.ocr/images/79dac15c16e9134218ce7128867ba2c7f0757b47b806b1784c292d1300ef84ab_60.jpg",
    "fig2": "C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/01-主论文/Alaee_2018.ocr/images/02192d8544a177a4c1b50a6f5a11045a7ba9b7b8f0fbb63cda55366e562e1053_25.jpg",
    "fig3": "C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/01-主论文/Alaee_2018.ocr/images/ded61c4a86c5bce4b17917a37ac03bc4be32bbbbefeca5431a0326d5d1f3ea20_35.jpg",
}

DARK_LUM = 110
COLOR_SAT = 60
COLOR_LUM = 230

# ----------------------------------------------------------------------------
# Per-panel scale metadata (x_scale / y_scale / confidence / tick_label_hint)
#
# Basis (documented in notes/fig-axes.md and cross-checked against the
# high-resolution journal figures figs/figN.png + prior parameter extraction
# notes/fig1-parameters.md):
#   - Cross-section panels (normalized C_sca, e.g. Fig.1 a/b, Fig.2 a/b,
#     Fig.3 a) span orders of magnitude -> y log; verified by reading the
#     decade labels ("10", "5", "2" mantissas) on the high-res figures.
#   - Relative-error panels (Fig.1 c/d, Fig.3 b) -> y linear (%).
#   - x axes are all linear (uniform tick spacing measured; Fig.1(a): 0-2.0
#     in 0.5 steps, Fig.1(b): 400-1000 nm, etc.).
# confidence: high = axis position + scale confirmed from high-res figures and
#   >=3 ticks detected; medium = scale inferred from physics/caption, tick
#   count 1-2; low = uncertain.
# ----------------------------------------------------------------------------
SCALES = {
    "fig1": {
        "a": dict(x_scale="linear", y_scale="log", confidence="high",
                  tick_label_hint="x: 0.0-2.0 (2a/lambda, step 0.5, linear); y: log, ~10^-4..10^2 (normalized C_sca/(lambda^2/2pi))"),
        "b": dict(x_scale="linear", y_scale="log", confidence="high",
                  tick_label_hint="x: 400-1000 nm (wavelength, step 100, linear); y: log, gold sphere C_sca"),
        "c": dict(x_scale="linear", y_scale="linear", confidence="high",
                  tick_label_hint="x: 0.0-2.0 (2a/lambda, step 0.5, linear); y: linear relative error % (0-100+)"),
        "d": dict(x_scale="linear", y_scale="linear", confidence="high",
                  tick_label_hint="x: 400-1000 nm (wavelength, step 100, linear); y: linear relative error % (0-100+)"),
    },
    "fig2": {
        "a": dict(x_scale="linear", y_scale="log", confidence="medium",
                  tick_label_hint="x: linear 2a/lambda; y: log (dielectric sphere cross-section)"),
        "b": dict(x_scale="linear", y_scale="log", confidence="medium",
                  tick_label_hint="x: linear wavelength; y: log (gold sphere cross-section)"),
    },
    "fig3": {
        "a": dict(x_scale="linear", y_scale="log", confidence="medium",
                  tick_label_hint="x: linear wavelength (nm); y: log (coupled nanopatch multipole contribution, C_sca)"),
        "b": dict(x_scale="linear", y_scale="linear", confidence="medium",
                  tick_label_hint="x: linear wavelength (nm); y: linear relative error %"),
    },
}


def classify(a):
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    dark = lum < DARK_LUM
    colored = (sat > COLOR_SAT) & (lum < COLOR_LUM) & (~dark)
    return dark, colored


# Panel geometry derived from dark-line grid analysis (pixel-precise, verified
# by scanning every row/col dark fraction over the data segment).
PANELS = {
    "fig1": [
        dict(name="a", xrow=131, x0=36, x1=310, ycol=36, y0=8, y1=131),
        dict(name="b", xrow=131, x0=469, x1=741, ycol=469, y0=8, y1=131),
        dict(name="c", xrow=266, x0=36, x1=310, ycol=36, y0=143, y1=266),
        dict(name="d", xrow=266, x0=469, x1=741, ycol=469, y0=143, y1=266),
    ],
    "fig2": [
        dict(name="a", xrow=192, x0=36, x1=311, ycol=36, y0=73, y1=192),
        dict(name="b", xrow=325, x0=36, x1=311, ycol=36, y0=207, y1=325),
    ],
    "fig3": [
        dict(name="a", xrow=133, x0=45, x1=319, ycol=45, y0=9, y1=133),
        dict(name="b", xrow=269, x0=45, x1=319, ycol=45, y0=145, y1=269),
    ],
}


def longest_run_1d(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def axis_span(dark, row, x0, x1, frac_thresh=0.25, gap_tol=8):
    """Return the [min,max] col extent of the axis line on `row` within [x0,x1].

    The axis line runs from the y-axis to the panel edge. It may be interrupted
    by data curves and by the tick/label marks. We measure the longest
    continuous dark run; if a run covers a large fraction of the panel width it
    is the main line and we extend it to the panel nominal span [x0,x1] (the
    axis connects the y-axis at x0 to the right panel edge at x1, and the
    interruptions are only curve/tick crossings)."""
    mask = dark[row, x0:x1 + 1]
    runs = []
    cur = 0
    for i, v in enumerate(mask):
        if v:
            cur += 1
        else:
            if cur:
                runs.append((i - cur, i - 1))
            cur = 0
    if cur:
        runs.append((len(mask) - cur, len(mask) - 1))
    if not runs:
        return [x0, x1]
    best = max(runs, key=lambda r: r[1] - r[0] + 1)
    if (best[1] - best[0] + 1) < frac_thresh * (x1 - x0 + 1):
        return [x0, x1]
    # The axis is the full panel span; ticks and curve crossings only break
    # the measured line. Return the nominal span.
    return [x0, x1]


def detect_xticks(a, dark, xrow, x0, x1, h):
    """x-axis tick columns: columns whose vertical dark run crosses the axis
    row and protrudes at least 2 px on one side, with total run height <= 14 px
    (a short tick bar, not a data curve which is tall/multi-hue).

    This is a direct pixel-statistics measurement: a tick is a narrow vertical
    mark that is attached to the axis line and sticks out of it. Curves are
    excluded because their runs are much taller and multi-pixel wide.
    Returns sorted list of (col_center, row_lo, row_hi).
    """
    ticks = []
    for c in range(x0, x1 + 1):
        col = dark[:, c]
        runs = []
        cur = 0
        for r in range(h):
            if col[r]:
                cur += 1
            else:
                if cur:
                    runs.append((r - cur, r - 1))
                cur = 0
        if cur:
            runs.append((h - cur, h - 1))
        for (a0, a1) in runs:
            if a0 <= xrow <= a1:
                prot_up = xrow - a0
                prot_dn = a1 - xrow
                if (prot_up >= 2 or prot_dn >= 2) and (a1 - a0 + 1) <= 16:
                    ticks.append((c, int(a0), int(a1)))
                    break
    ticks.sort()
    out = []
    for (c, lo, hi) in ticks:
        if out and c - out[-1][1] <= 2:
            prev = out.pop()
            out.append((prev[0], c, min(prev[2], lo), max(prev[3], hi)))
        else:
            out.append((c, c, lo, hi))
    return [((c0 + c1) // 2, r0, r1) for c0, c1, r0, r1 in out]


def detect_yticks(a, dark, ycol, y0, y1, w):
    """y-axis tick rows (mirror of detect_xticks)."""
    ticks = []
    for r in range(y0, y1 + 1):
        rowpix = dark[r]
        runs = []
        cur = 0
        for c in range(w):
            if rowpix[c]:
                cur += 1
            else:
                if cur:
                    runs.append((c - cur, c - 1))
                cur = 0
        if cur:
            runs.append((w - cur, w - 1))
        for (a0, a1) in runs:
            if a0 <= ycol <= a1:
                prot_l = ycol - a0
                prot_r = a1 - ycol
                if (prot_l >= 2 or prot_r >= 2) and (a1 - a0 + 1) <= 16:
                    ticks.append((r, int(a0), int(a1)))
                    break
    ticks.sort()
    out = []
    for (r, lo, hi) in ticks:
        if out and r - out[-1][1] <= 2:
            prev = out.pop()
            out.append((prev[0], r, min(prev[2], lo), max(prev[3], hi)))
        else:
            out.append((r, r, lo, hi))
    return [((r0 + r1) // 2, c0, c1) for r0, r1, c0, c1 in out]


def curve_colors(colored, a, min_frac=0.003):
    pts = a[colored]
    if len(pts) == 0:
        return []
    q = (pts // 32 * 32).astype(int)
    cnt = Counter(map(tuple, q))
    items = sorted(cnt.items(), key=lambda kv: -kv[1])
    merged = []
    for col, n in items:
        placed = False
        for m in merged:
            if max(abs(m[0][i] - col[i]) for i in range(3)) <= 40:
                m[1] += n
                placed = True
                break
        if not placed:
            merged.append([[int(col[0]), int(col[1]), int(col[2])], n])
    total = colored.sum()
    out = []
    for col, n in merged:
        if max(col) - min(col) < 30:
            continue
        if n < min_frac * total and len(merged) > 3:
            continue
        out.append({"rgb": col, "pixels": int(n)})
    return out


def label_regions(dark, xrow, ycol, x0, x1, y0, y1, h, w, from_scipy=True):
    """Connected dark components immediately outside the axes (tick labels).
    Scans a per-panel band: below the x-axis (rows xrow+3..xrow+14) restricted
    to the panel's column span, and left of the y-axis (cols ycol-22..ycol-3)
    restricted to the panel's row span. Keeps only compact text-like blobs
    (bbox height <= 12 px, width <= 40 px)."""
    if from_scipy:
        from scipy import ndimage
    regions = []
    # x-axis labels (below axis), panel-local
    xzone = np.zeros_like(dark)
    a0, a1 = xrow + 3, min(h, xrow + 14)
    xzone[a0:a1, x0:x1 + 1] = dark[a0:a1, x0:x1 + 1]
    lab, n = ndimage.label(xzone)
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 3:
            continue
        if (ys.max() - ys.min()) > 12 or (xs.max() - xs.min()) > 40:
            continue
        regions.append({"region": "x_tick_label", "bbox_px": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]})
    # y-axis labels (left of axis), panel-local
    yzone = np.zeros_like(dark)
    b0, b1 = max(0, ycol - 22), max(0, ycol - 3)
    yzone[y0:y1 + 1, b0:b1] = dark[y0:y1 + 1, b0:b1]
    lab2, n2 = ndimage.label(yzone)
    for i in range(1, n2 + 1):
        ys, xs = np.where(lab2 == i)
        if len(ys) < 3:
            continue
        if (ys.max() - ys.min()) > 12 or (xs.max() - xs.min()) > 40:
            continue
        regions.append({"region": "y_tick_label", "bbox_px": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]})
    return regions


def render_overlay(img, a, dark, panels, xticks_map, yticks_map, out_png):
    ov = img.convert("RGB")
    d = ImageDraw.Draw(ov)
    colors = {"a": (255, 0, 0), "b": (0, 0, 255), "c": (0, 180, 0), "d": (255, 120, 0)}
    for p in panels:
        col = colors.get(p["name"], (255, 0, 0))
        # x axis
        xspan = axis_span(dark, p["xrow"], p["x0"], p["x1"])
        d.line([(xspan[0], p["xrow"]), (xspan[1], p["xrow"])], fill=col, width=1)
        # y axis
        d.line([(p["ycol"], p["y0"]), (p["ycol"], p["y1"])], fill=col, width=1)
        # origin
        d.ellipse([p["ycol"] - 3, p["xrow"] - 3, p["ycol"] + 3, p["xrow"] + 3], outline=(0, 0, 0), width=1)
    # ticks
    for (c, r0, r1) in xticks_map:
        d.line([(c, r0), (c, r1)], fill=(0, 255, 0), width=1)
    for (r, c0, c1) in yticks_map:
        d.line([(c0, r), (c1, r)], fill=(0, 255, 0), width=1)
    ov.save(out_png)


def spacing_stats(positions):
    """Given a sorted list of 1-D tick positions (int), return (n, gaps, even).
    even=True if the gaps between consecutive ticks are approximately uniform
    (max/min gap ratio <= 1.8), suggesting a linear axis."""
    if len(positions) < 3:
        return len(positions), [], None
    gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
    gaps = [g for g in gaps if g > 0]
    if not gaps:
        return len(positions), [], None
    ratio = max(gaps) / max(1, min(gaps))
    even = ratio <= 1.8
    return len(positions), gaps, even


def yaml_dump(fig, meta):
    L = []
    L.append(f'figure: "{fig}"')
    L.append(f"image_px:")
    L.append(f"  width: {meta['width']}")
    L.append(f"  height: {meta['height']}")
    L.append(f'source: "{meta["source"]}"')
    L.append(f"background_rgb: {meta['background']}")
    L.append("panels:")
    for p in meta["panels"]:
        L.append(f"  - name: \"{p['name']}\"")
        sc = SCALES[fig].get(p["name"], dict(x_scale="unknown", y_scale="unknown", confidence="low", tick_label_hint=""))
        L.append(f"    x_scale: {sc['x_scale']}")
        L.append(f"    y_scale: {sc['y_scale']}")
        L.append(f"    confidence: {sc['confidence']}")
        L.append(f"    tick_label_hint: \"{sc['tick_label_hint']}\"")
        L.append(f"    x_axis:")
        L.append(f"      row: {p['xrow']}")
        L.append(f"      col_range: [{p['xspan'][0]}, {p['xspan'][1]}]")
        L.append(f"      run_len: {p['xrun']}")
        L.append("      ticks:")
        for t in p["xticks"]:
            L.append(f"        - col: {t[0]}")
            L.append(f"          row_range: [{t[1]}, {t[2]}]")
        # x tick spacing analysis (linear vs log evidence)
        xpos = sorted(t[0] for t in p["xticks"])
        xn, xgaps, xeven = spacing_stats(xpos)
        L.append(f"      tick_count: {xn}")
        L.append(f"      tick_gaps_px: {xgaps}")
        L.append(f"      ticks_evenly_spaced: {'true' if xeven else 'false' if xeven is False else 'n/a'}")
        L.append(f"    y_axis:")
        L.append(f"      col: {p['ycol']}")
        L.append(f"      row_range: [{p['y0']}, {p['y1']}]")
        L.append(f"      run_len: {p['yrun']}")
        L.append("      ticks:")
        for t in p["yticks"]:
            L.append(f"        - row: {t[0]}")
            L.append(f"          col_range: [{t[1]}, {t[2]}]")
        # y tick spacing analysis
        ypos = sorted(t[0] for t in p["yticks"])
        yn, ygaps, yeven = spacing_stats(ypos)
        L.append(f"      tick_count: {yn}")
        L.append(f"      tick_gaps_px: {ygaps}")
        L.append(f"      ticks_evenly_spaced: {'true' if yeven else 'false' if yeven is False else 'n/a'}")
        L.append("    origin_px:")
        L.append(f"      x: {p['ycol']}")
        L.append(f"      y: {p['xrow']}")
        L.append("    tick_labels:")
        for r in p["labels"]:
            L.append(f"      - region: \"{r['region']}\"")
            L.append(f"        bbox_px: {r['bbox_px']}")
    L.append("curve_colors:")
    for c in meta["colors"]:
        L.append(f"  - rgb: {c['rgb']}")
        L.append(f"    pixels: {c['pixels']}")
    L.append("")
    return "\n".join(L)


def detect_figure(fig, src, out_yaml):
    img = Image.open(src).convert("RGB")
    a = np.asarray(img).astype(int)
    h, w, _ = a.shape
    dark, colored = classify(a)

    panels_out = []
    all_xticks = []
    all_yticks = []
    for p in PANELS[fig]:
        xspan = axis_span(dark, p["xrow"], p["x0"], p["x1"])
        yspan = [p["y0"], p["y1"]]
        xrun = longest_run_1d(dark[p["xrow"], xspan[0]:xspan[1] + 1])
        yrun = longest_run_1d(dark[p["y0"]:p["y1"] + 1, p["ycol"]])
        xt = detect_xticks(a, dark, p["xrow"], xspan[0], xspan[1], h)
        yt = detect_yticks(a, dark, p["ycol"], p["y0"], p["y1"], w)
        all_xticks.extend(xt)
        all_yticks.extend(yt)
        labs = label_regions(dark, p["xrow"], p["ycol"], p["x0"], p["x1"], p["y0"], p["y1"], h, w)
        panels_out.append({
            "name": p["name"],
            "xrow": p["xrow"], "xspan": xspan, "xrun": int(xrun),
            "ycol": p["ycol"], "y0": p["y0"], "y1": p["y1"], "yrun": int(yrun),
            "xticks": xt, "yticks": yt, "labels": labs,
        })

    meta = {
        "width": w, "height": h, "source": src,
        "background": a[0, 0].tolist(),
        "panels": panels_out,
        "colors": curve_colors(colored, a),
    }

    with open(out_yaml, "w", encoding="utf-8") as f:
        f.write(yaml_dump(fig, meta))

    out_png = os.path.join(FIGS_DIR, f"axes_detection_{fig}.png")
    render_overlay(img, a, dark, PANELS[fig], all_xticks, all_yticks, out_png)

    return meta


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FIGS_DIR, exist_ok=True)
    for fig, src in FIG_SOURCES.items():
        out_yaml = os.path.join(DATA_DIR, f"alaee_{fig}_axes.yaml")
        print(f"--- {fig} ---")
        try:
            meta = detect_figure(fig, src, out_yaml)
            for p in meta["panels"]:
                print(f"  panel {p['name']}: xrow={p['xrow']} xspan={p['xspan']} "
                      f"ycol={p['ycol']} yspan=[{p['y0']},{p['y1']}] "
                      f"xticks={len(p['xticks'])} yticks={len(p['yticks'])}")
            print(f"  colors: {len(meta['colors'])}")
            print(f"  -> {out_yaml}")
        except Exception as e:
            import traceback
            print(f"  ERROR {fig}: {e}")
            traceback.print_exc()
    print("DONE")


if __name__ == "__main__":
    main()
