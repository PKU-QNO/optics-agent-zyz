# -*- coding: utf-8 -*-
"""Build the JC/Olmon/McPeak common-domain material envelope."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHANNELS = ("ED", "MD", "EQ", "MQ")
INPUTS = {
    "jc": DATA / "fig2_gold_jc_sensitivity.csv",
    "olmon": DATA / "fig2_gold_olmon_refined.csv",
    "mcpeak": DATA / "fig2_gold_mcpeak_sensitivity.csv",
}
OUT_CSV = DATA / "fig2_gold_material_envelope.csv"
OUT_PNG = ROOT / "figs" / "fig2_gold_material_sensitivity.png"


def read(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main():
    raw = {name: read(path) for name, path in INPUTS.items()}
    x = np.linspace(500.0 / 1700.0, 1.0, 200)
    series = {}
    for name, rows in raw.items():
        xp = np.asarray([float(row["x_alaee"]) for row in rows])
        series[name] = {}
        for method in ("mie", "table2"):
            for key in CHANNELS:
                yp = np.asarray([float(row[f"{method}_{key}"]) for row in rows])
                series[name][f"{method}_{key}"] = np.interp(x, xp, yp)

    fields = ["x_alaee", "lambda_nm"]
    for method in ("mie", "table2"):
        for key in CHANNELS:
            fields += [f"{method}_{key}_min", f"{method}_{key}_max"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for i, value in enumerate(x):
            row = {"x_alaee": value, "lambda_nm": 500.0 / value}
            for method in ("mie", "table2"):
                for key in CHANNELS:
                    vals = [series[name][f"{method}_{key}"][i] for name in INPUTS]
                    row[f"{method}_{key}_min"] = min(vals)
                    row[f"{method}_{key}_max"] = max(vals)
            writer.writerow(row)

    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True, constrained_layout=True)
    for ax, key in zip(axes.flat, CHANNELS):
        for name, color in zip(INPUTS, ("#1f77b4", "#d62728", "#2ca02c")):
            ax.plot(x, series[name][f"mie_{key}"], color=color, lw=1.2, label=name)
            ax.plot(x, series[name][f"table2_{key}"], color=color, lw=0.7, ls="--")
        lower = np.min([series[n][f"mie_{key}"] for n in INPUTS], axis=0)
        upper = np.max([series[n][f"mie_{key}"] for n in INPUTS], axis=0)
        ax.fill_between(x, lower, upper, color="0.5", alpha=0.12, label="Mie min-max envelope")
        ax.set_title(key)
        ax.set_xlim(x[0], 1.0)
        ax.grid(alpha=0.18)
    axes[0, 0].set_ylabel(r"$C_{\rm sca}/(\lambda^2/2\pi)$")
    axes[1, 0].set_ylabel(r"$C_{\rm sca}/(\lambda^2/2\pi)$")
    axes[1, 0].set_xlabel(r"$2a/\lambda$")
    axes[1, 1].set_xlabel(r"$2a/\lambda$")
    axes[0, 0].legend(fontsize=7)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=220)
    print(OUT_CSV)
    print(OUT_PNG)


if __name__ == "__main__":
    main()
