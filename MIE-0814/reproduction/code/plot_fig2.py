# -*- coding: utf-8 -*-
"""Render the two-panel Fig.2 reproduction from auditable CSV artifacts."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figs" / "fig2_reproduction.png"
CHANNELS = ("ED", "MD", "EQ", "MQ")
COLORS = {"ED": "#1f77b4", "MD": "#d62728", "EQ": "#2ca02c", "MQ": "#9467bd"}


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def plot_panel(ax, rows, title, source_label=""):
    x = [float(row["x_alaee"] if "x_alaee" in row else row["2a_over_lambda"]) for row in rows]
    for key in CHANNELS:
        color = COLORS[key]
        if f"mie_{key}" in rows[0]:
            mie = [float(row[f"mie_{key}"]) for row in rows]
            exact = [float(row[f"table2_{key}"]) for row in rows]
        else:
            mie = [float(row[key]) for row in rows]
            exact = None
        ax.plot(x, mie, color=color, lw=1.6, label=f"{key} Mie")
        if exact is not None:
            ax.plot(x, exact, color=color, lw=0.9, ls="--", marker=".", ms=2.0,
                    markevery=max(1, len(x) // 25), label=f"{key} Table 2")
    ax.set_xlim(0.2, 1.0)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel(r"$C_{\rm sca}/(\lambda^2/2\pi)$")
    ax.set_title(title)
    ax.grid(alpha=0.18)
    if source_label:
        ax.text(0.99, 0.03, source_label, transform=ax.transAxes,
                ha="right", va="bottom", fontsize=8, color="0.35")


def main():
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 8.4), sharex=True, constrained_layout=True)
    panel_a = read_csv(DATA / "fig1a_multipole_mie.csv")
    # Figure 1 CSV uses the same normalized x column and is the dielectric
    # panel's independently validated Mie/Table-2 data.
    a_rows = read_csv(DATA / "fig1a_multipole_table2.csv")
    joined = []
    for mie, exact in zip(panel_a, a_rows):
        row = {"x_alaee": mie["2a_over_lambda"]}
        for key in CHANNELS:
            row[f"mie_{key}"] = mie[key]
            row[f"table2_{key}"] = exact[key]
        joined.append(row)
    plot_panel(axes[0], joined, "(a) dielectric sphere, $\\varepsilon_r=2.5^2$")

    gold_path = DATA / "fig2_gold_olmon_refined.csv"
    if not gold_path.exists():
        gold_path = DATA / "fig2_gold_olmon.csv"
    plot_panel(axes[1], read_csv(gold_path), "(b) gold sphere, $a=250$ nm", "Olmon-EV")
    axes[1].set_xlabel(r"$2a/\lambda$")
    handles, labels = axes[1].get_legend_handles_labels()
    axes[1].legend(handles, labels, ncol=2, fontsize=7, loc="upper left", frameon=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220)
    print(OUT)


if __name__ == "__main__":
    main()
