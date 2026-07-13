"""Akimov Fig6 复现出图 (step06 T4).

case: 0707-02-akimov-mie-v1 | step06 · T4

只读 fig6_loci.py 输出的六 CSV (data/fig6_loci_{TM,TE}_l{1,2,3}.csv)，不改
fig6_loci.py / scattering.py。

布局 (照 figures.md 判定): Fig6 每个 (l,偏振) 对应两个纵向堆叠子图 (上 Re / 下
Im)，与 Fig3 单子图布局不同。整图排成 4 行 x 3 列:
  行1 = TM, Re(eps_ratio)   行2 = TM, Im(eps_ratio)
  行3 = TE, Re(eps_ratio)   行4 = TE, Im(eps_ratio)
  列 = l=1,2,3
"""
from __future__ import annotations

import os
import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))
FIG_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "figures"))

PANELS = [(1, "TM"), (2, "TM"), (3, "TM"), (1, "TE"), (2, "TE"), (3, "TE")]

QE_LO, QE_HI = 0.0, 10.0
BREAK_D = 3.0  # 相邻点跳变超过此阈值断开不连线 (跨分支/极点)


def read_csv(l, pol):
    path = os.path.join(DATA_DIR, f"fig6_loci_{pol}_l{l}.csv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            rows.append(dict(qe=float(row["q_e"]), bid=int(row["branch_id"]),
                             x=float(row["eps_re"]), y=float(row["eps_im"])))
    return rows


def segments_of_branch(pts, key):
    """pts: 同 branch_id 的点, 按 qe 排序. key='x' 或 'y'. 跳变>BREAK_D 断开."""
    pts = sorted(pts, key=lambda p: p["qe"])
    segs = []
    cur_q, cur_v = [], []
    for p in pts:
        if cur_v and abs(p[key] - cur_v[-1]) > BREAK_D:
            if cur_q:
                segs.append((np.array(cur_q), np.array(cur_v)))
            cur_q, cur_v = [], []
        cur_q.append(p["qe"])
        cur_v.append(p[key])
    if cur_q:
        segs.append((np.array(cur_q), np.array(cur_v)))
    return segs


def plot_re_im(ax_re, ax_im, l, pol):
    rows = read_csv(l, pol)
    groups = {}
    for r in rows:
        groups.setdefault(r["bid"], []).append(r)
    for bid, pts in groups.items():
        for qa, va in segments_of_branch(pts, "x"):
            ax_re.plot(qa, va, color="blue", ls="-", lw=0.8)
        for qa, va in segments_of_branch(pts, "y"):
            ax_im.plot(qa, va, color="red", ls="-", lw=0.8)
    ax_re.set_xlim(QE_LO, QE_HI)
    ax_im.set_xlim(QE_LO, QE_HI)
    ax_re.set_ylabel(r"Re$(\varepsilon_i/\varepsilon_e)$")
    ax_im.set_ylabel(r"Im$(\varepsilon_i/\varepsilon_e)$")
    ax_re.text(0.97, 0.92, f"l={l}, {pol}", transform=ax_re.transAxes,
              ha="right", va="top", fontsize=9,
              bbox=dict(boxstyle="round", fc="white", ec="gray"))
    n_branch = len(groups)
    return n_branch


def make_repro():
    fig, axes = plt.subplots(4, 3, figsize=(14, 12), sharex=True)
    counts = {}
    row_pairs = [(0, 1, "TM"), (2, 3, "TE")]
    for row_re, row_im, pol in row_pairs:
        for col, l in enumerate([1, 2, 3]):
            n = plot_re_im(axes[row_re, col], axes[row_im, col], l, pol)
            counts[(pol, l)] = n
    for col in range(3):
        axes[3, col].set_xlabel(r"$q_e$")
    fig.suptitle("Akimov Fig6 reproduction: super-absorbing states "
                 "(Re/Im of eps_ratio vs q_e, stacked)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = os.path.join(FIG_DIR, "fig6_repro.png")
    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("[repro] saved", out)
    for (pol, l), n in counts.items():
        print(f"  panel {pol} l={l}: 分支数={n}")
    return counts


if __name__ == "__main__":
    make_repro()
