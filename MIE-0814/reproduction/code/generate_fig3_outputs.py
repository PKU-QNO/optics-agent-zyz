# -*- coding: utf-8 -*-
"""Generate the auditable B7 Fig.3 surrogate artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fig3_mie_fano import (
    CHANNELS,
    Fig3Parameters,
    fu2013_forward_backward_ratio,
    mie_directional_interference,
    rayleigh_limit_check,
    relative_error,
    spectrum,
    tribelsky_feature_profile,
)
from baseline_mie import cross_sections, mie_coefficients, wiscombe_nmax


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    params = Fig3Parameters(n_points=301)
    x = np.linspace(params.x_min, params.x_max, params.n_points)
    rows = spectrum(x, DATA / "gold_epsilon.csv", params)
    out_csv = DATA / "fig3_mie_surrogate.csv"
    fields = ["x_2a_over_lambda", "lambda_nm", "material_covered"]
    for c in CHANNELS:
        fields += [f"{c}_exact", f"{c}_approx", f"{c}_error_percent"]
    fields += ["total_exact", "total_approx"]
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for row in rows:
            row = dict(row)
            for c in CHANNELS:
                row[f"{c}_error_percent"] = relative_error(row[f"{c}_exact"], row[f"{c}_approx"])
            wr.writerow({key: row.get(key, "") for key in fields})

    # Direction-resolved complex interference at a fixed transverse angle.
    drows = []
    for row in rows:
        if not row["material_covered"]:
            continue
        val = mie_directional_interference(row["lambda_nm"], np.pi / 2, DATA / "gold_epsilon.csv", params)
        drows.append({"x_2a_over_lambda": row["x_2a_over_lambda"], "lambda_nm": row["lambda_nm"],
                      "total": val["total"], "incoherent": val["incoherent"],
                      "cross_term": val["cross_term"], "S1_real": val["S1"].real,
                      "S1_imag": val["S1"].imag, "S2_real": val["S2"].real,
                      "S2_imag": val["S2"].imag})
    with (DATA / "fig3_directional_interference.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(drows[0]))
        wr.writeheader(); wr.writerows(drows)

    # Strict analytic Fano comparator (Tribelsky feature positions).
    xt = np.linspace(1.25, 1.43, 1001)
    profile, meta = tribelsky_feature_profile(xt)
    with (DATA / "fig3_tribelsky_fano.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["x", "fano_profile"])
        wr.writerows(zip(xt, profile))

    # Independent Layer-1/2 receipts.  ``n_max`` is the only discretisation
    # in the analytic path; a spatial FEM mesh is intentionally not claimed.
    x_conv, m_conv = 2.0 * np.pi * 250.0 / 800.0, complex(0.15, 4.9)
    conv_vals = []
    for nmax in (2, 4, 6, 8, wiscombe_nmax(x_conv)):
        aa, bb = mie_coefficients(x_conv, m_conv, nmax)
        l = np.arange(1, nmax + 1)
        conv_vals.append(float(np.sum((2 * l + 1) * (abs(aa) ** 2 + abs(bb) ** 2))))
    optical = cross_sections(0.7, complex(1.5), n_max=8)
    # Deliberate phase-sign mutation: the cross term must change in a fixed
    # direction-resolved channel, while the angle-integrated positive powers
    # remain non-negative.
    d_ok = mie_directional_interference(800.0, np.pi / 2, DATA / "gold_epsilon.csv", params)
    d_wrong = mie_directional_interference(800.0, 0.7, DATA / "gold_epsilon.csv", params)
    fano_peak_x = float(xt[np.argmax(profile)])
    fano_valley_x = float(xt[np.argmin(profile)])

    # Main plot: retain readable exact Mie channels, expose the direction-
    # resolved cross term, and show the independent Tribelsky comparator.
    xx = np.array([r["x_2a_over_lambda"] for r in rows])
    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(14.5, 4.2), constrained_layout=True)
    colors = {"ED": "#d62728", "MD": "#1f77b4", "EQ": "#e6b800", "MQ": "#7f3fbf"}
    for c in CHANNELS:
        exact = np.array([r[f"{c}_exact"] for r in rows], dtype=float)
        ax0.plot(xx, exact, color=colors[c], label=c)
    xd = np.array([r["x_2a_over_lambda"] for r in drows])
    ax1.plot(xd, [r["total"] for r in drows], color="black", label="coherent total")
    ax1.plot(xd, [r["incoherent"] for r in drows], color="#777777", ls="--", label="incoherent sum")
    ax1.plot(xd, [r["cross_term"] for r in drows], color="#2ca02c", label="cross term")
    ax1.axhline(0, color="black", lw=.6)
    ax2.plot(xt, profile, color="#9467bd", label=r"$q=-1$")
    ax2.axvline(meta["x_peak"], color="#d62728", ls="--", lw=1, label="peak 1.32")
    ax2.axvline(meta["x_valley"], color="#1f77b4", ls=":", lw=1.2, label="valley 1.36")
    ax0.set(xlabel=r"$2a/\lambda$", ylabel=r"$C_{sca}/(\lambda^2/2\pi)$",
            title="Mie channel surrogate (not FEM)", xlim=(.25, 1.0))
    ax1.set(xlabel=r"$2a/\lambda$", ylabel="directional intensity (arb.)",
            title=r"Interference at $\theta=\pi/2$", xlim=(.25, 1.0))
    ax2.set(xlabel=r"$x=kR$", ylabel=r"$F(\epsilon)$",
            title="Tribelsky strict-feature comparator", xlim=(1.25, 1.43))
    for ax in (ax0, ax1, ax2):
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.savefig(DATA / "fig3_mie_surrogate.png", dpi=180)
    plt.close(fig)

    # Wide-range Rayleigh-vs-Mie diagnostic is kept separately on log axes so
    # the exact curves are not visually crushed by the deliberately invalid
    # large-x continuation of the leading terms.
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    for c in CHANNELS:
        exact = np.array([r[f"{c}_exact"] for r in rows], dtype=float)
        approx = np.array([r[f"{c}_approx"] for r in rows], dtype=float)
        ax0.semilogy(xx, exact, color=colors[c], label=f"{c} exact")
        ax0.semilogy(xx, approx, color=colors[c], ls="--", alpha=.75, label=f"{c} leading")
        err = np.array([relative_error(e, a) for e, a in zip(exact, approx)])
        ax1.semilogy(xx, err, color=colors[c], label=c)
    ax0.set(xlabel=r"$2a/\lambda$", ylabel=r"$C_{sca}/(\lambda^2/2\pi)$",
            title="Full Mie vs Rayleigh leading terms", xlim=(.25, 1.0))
    ax1.set(xlabel=r"$2a/\lambda$", ylabel="relative error (%)",
            title="Exact-denominator diagnostic", xlim=(.25, 1.0))
    ax0.grid(alpha=.2); ax1.grid(alpha=.2); ax0.legend(ncol=2, fontsize=8); ax1.legend(fontsize=8)
    fig.savefig(DATA / "fig3_mie_approx_diagnostic.png", dpi=180)
    plt.close(fig)

    summary = {
        "result_class": "surrogate_fallback",
        "material_source": "data/gold_epsilon.csv: jc_n,jc_k; finite coverage 400-1935 nm",
        "x_domain_requested": [params.x_min, params.x_max],
        "n_points": params.n_points,
        "covered_points": int(sum(r["material_covered"] for r in rows)),
        "uncovered_points": int(sum(not r["material_covered"] for r in rows)),
        "rayleigh_limit": rayleigh_limit_check(DATA / "gold_epsilon.csv"),
        "tribelsky_feature": meta,
        "fu2013_forward_backward_at_660nm_n3p5": fu2013_forward_backward_ratio(),
        "directional_cross_term_min": float(np.nanmin([r["cross_term"] for r in drows])),
        "directional_cross_term_max": float(np.nanmax([r["cross_term"] for r in drows])),
        "layer1_optical_theorem_residual": float(optical[1] - optical[0] - optical[2]),
        "nmax_convergence": {
            "x_mie": x_conv, "values": conv_vals,
            "relative_last_vs_wiscombe": float(abs(conv_vals[-1] - conv_vals[-2]) / max(abs(conv_vals[-1]), 1e-30)),
        },
        "error_injection": {
            "mutation": "replace transverse angle pi/2 by 0.7 rad (phase/cross-term path)",
            "cross_term_control": float(d_ok["cross_term"]),
            "cross_term_mutated": float(d_wrong["cross_term"]),
            "expected_failure_code": "INTERFERENCE_PHASE_FAIL",
        },
        "tribelsky_numeric_extrema": {"peak_grid": fano_peak_x, "valley_grid": fano_valley_x,
                                      "peak_error": abs(fano_peak_x - meta["x_peak"]),
                                      "valley_error": abs(fano_valley_x - meta["x_valley"])},
    }
    (DATA / "fig3_mie_surrogate_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
