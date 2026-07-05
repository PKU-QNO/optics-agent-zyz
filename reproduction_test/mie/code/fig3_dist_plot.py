#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fig3_dist_plot.py — Layer3 归一化距离分布图 + 长尾点位置诊断.
六面板 sr/nr 归一化距离箱线+直方, 标阈值线 0.01/0.03, 供 Gate4 目测.
另诊断 sr 大偏差点的 q_e 分布 (判断长尾是端点/急弯还是系统偏移)."""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fig3_compare as fc

FIG_DIR = fc.FIG_DIR
os.makedirs(FIG_DIR, exist_ok=True)


def main():
    fig, axes = plt.subplots(2, 6, figsize=(20, 7))
    diag_lines = []
    diag_lines.append("=== sr/nr 归一化距离长尾诊断 (阈值 median<0.01, p95<0.03) ===")

    for col, (pol, l) in enumerate(fc.PANELS):
        pm = fc.panel_metrics(pol, l)
        key = f"{pol}{l}"
        for row, typ in enumerate(fc.TYPES):
            ax = axes[row, col]
            d = pm[typ]["_dist"]
            d = d[np.isfinite(d)]
            ax.hist(d, bins=30, color=("#c44" if typ == "sr" else "#48c"),
                    alpha=0.75, edgecolor="k", linewidth=0.3)
            ax.axvline(0.01, color="k", ls="--", lw=1, label="med thr 0.01")
            ax.axvline(0.03, color="gray", ls=":", lw=1, label="p95 thr 0.03")
            med = np.median(d)
            p95 = np.percentile(d, 95)
            ax.axvline(med, color="green", ls="-", lw=1.2)
            ax.set_title(f"{key} {typ}\nmed={med:.4f} p95={p95:.4f}", fontsize=8)
            ax.set_xlabel("norm dist", fontsize=7)
            if col == 0:
                ax.set_ylabel(f"{typ} count", fontsize=8)
            ax.tick_params(labelsize=6)
            if row == 0 and col == 0:
                ax.legend(fontsize=6)

            # 长尾诊断: sr 超阈值点的 q_e 分布
            if typ == "sr":
                dig = fc.load_digitized(pol, l, typ)
                over_mask = d > 0.03
                n_over = int(over_mask.sum())
                if n_over > 0:
                    qe_over = dig[over_mask, 0]
                    diag_lines.append(
                        f"[{key} sr] p95超阈(>0.03)点数={n_over}/{len(d)} "
                        f"({100*n_over/len(d):.1f}%), 这些点 q_e 范围="
                        f"[{qe_over.min():.2f},{qe_over.max():.2f}] "
                        f"中位={np.median(qe_over):.2f}; 全体 q_e 范围="
                        f"[{dig[:,0].min():.2f},{dig[:,0].max():.2f}]")
                else:
                    diag_lines.append(f"[{key} sr] 无 p95 超阈点")

    fig.suptitle("Fig3 Layer3 归一化距离分布 (数字化点->复现曲线族), 绿线=median, 黑虚=0.01 灰点=0.03",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(FIG_DIR, "fig3_dist_hist.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)
    print("\n".join(diag_lines))
    # 落盘诊断文本供报告引用 (工作区绝对路径, 避免 junction 解析歧义)
    diag_path = (r"C:\Users\27370\Desktop\project\self-evo-paper-repro"
                 r"\.work\.todo\2401.04146\0703-01-akimov-mie-v1"
                 r"\08-physical_verification\sr_tail_diagnosis.txt")
    with open(diag_path, "w", encoding="utf-8") as f:
        f.write("\n".join(diag_lines))
    print("wrote", diag_path)


if __name__ == "__main__":
    main()
