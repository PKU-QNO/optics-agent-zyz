# -*- coding: utf-8 -*-
"""Emit the nine-point Table-2/Mie ratio table for Fig.2."""
from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_fig2 import MULTIPOLES, compute_gold_point  # noqa: E402

POINTS = (0.2, 0.3, 0.385, 0.5, 0.6, 0.65, 0.7, 0.8, 1.0)
OUT_CSV = DATA / "fig2_nine_point_ratios.csv"
OUT_MD = ROOT / "notes" / "fig2-nine-point-ratios.md"


def dielectric_rows():
    def load(path):
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))
    mie = load(DATA / "fig1a_multipole_mie.csv")
    exact = load(DATA / "fig1a_multipole_table2.csv")
    out = []
    for target in POINTS:
        i = min(range(len(mie)), key=lambda j: abs(float(mie[j]["2a_over_lambda"]) - target))
        row = {"material": "dielectric_eps6.25", "x_alaee": target}
        for key in MULTIPOLES:
            row[f"ratio_{key}"] = float(exact[i][key]) / float(mie[i][key])
        out.append(row)
    return out


def gold_rows():
    out = []
    for target in POINTS:
        row = compute_gold_point(target, "olmon", (60, 61, 120))
        item = {"material": "gold_olmon_ev", "x_alaee": target}
        for key in MULTIPOLES:
            item[f"ratio_{key}"] = row[f"table2_{key}"] / row[f"mie_{key}"]
        out.append(item)
    return out


def main():
    rows = dielectric_rows() + gold_rows()
    fields = ["material", "x_alaee"] + [f"ratio_{key}" for key in MULTIPOLES]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Fig.2 九个指定点 Table2/Mie 比值", "", "比值定义：`C_table2 / C_Mie`；每个方法使用同一材料源与同一 $m(λ)$。", ""]
    for material, label in (("dielectric_eps6.25", "介电球 εᵣ=6.25"), ("gold_olmon_ev", "金球 Olmon-EV（加密网格）")):
        lines += [f"## {label}", "", "| 2a/λ | ED | MD | EQ | MQ |", "|---:|---:|---:|---:|---:|"]
        for row in rows:
            if row["material"] != material:
                continue
            lines.append("| " + " | ".join([f"{row['x_alaee']:.3f}"] + [f"{row[f'ratio_{key}']:.6f}" for key in MULTIPOLES]) + " |")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_CSV)
    print(OUT_MD)


if __name__ == "__main__":
    main()
