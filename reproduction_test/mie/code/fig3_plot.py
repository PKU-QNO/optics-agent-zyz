"""Akimov Fig3 复现出图 (step06 T4).

case: 0703-01-akimov-mie-v1 | step06 · T4

只读 T3 六 CSV (data/fig3_loci_{TM,TE}_l{1,2,3}.csv), 不改 fig3_loci.py / scattering.py.
出图:
  - fig3_repro.png     六面板复现图 (红虚 sr / 蓝实 nr, 轴 [0,10]x[-10,15])
  - fig3_overlay.png   复现曲线叠数字化取样点 (需 fig3_digitized.csv)
线型约定 (照原图): sr(a_l=1)=红虚线 dashed red; nr(a_l=0)=蓝实线 solid blue.
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
EPS_LO, EPS_HI = -10.0, 15.0
# 串支时若相邻点 eps 跳变过大 (跨渐近支/极点), 断开不连线
BREAK_DEPS = 3.0


def read_csv(l, pol):
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            rows.append(dict(qe=float(row["q_e"]), eps=float(row["eps_ratio"]),
                             bid=int(row["branch_id"]), type=row["type"]))
    return rows


def segments_of_branch(pts):
    """pts: 同 (type,branch_id) 的点列表, 按 qe 排序. 若相邻 eps 跳变>BREAK_DEPS 断开.

    返回 list of (qe_arr, eps_arr) 连续段.
    """
    pts = sorted(pts, key=lambda p: p["qe"])
    segs = []
    cur_q, cur_e = [], []
    for p in pts:
        if cur_e and abs(p["eps"] - cur_e[-1]) > BREAK_DEPS:
            if len(cur_q) >= 1:
                segs.append((np.array(cur_q), np.array(cur_e)))
            cur_q, cur_e = [], []
        cur_q.append(p["qe"])
        cur_e.append(p["eps"])
    if cur_q:
        segs.append((np.array(cur_q), np.array(cur_e)))
    return segs


def plot_panel(ax, l, pol):
    rows = read_csv(l, pol)
    # 按 (type,branch_id) 分组
    groups = {}
    for r in rows:
        groups.setdefault((r["type"], r["bid"]), []).append(r)
    n_sr_branch = len(set(k[1] for k in groups if k[0] == "sr"))
    n_nr_branch = len(set(k[1] for k in groups if k[0] == "nr"))
    for (typ, bid), pts in groups.items():
        for qa, ea in segments_of_branch(pts):
            if typ == "sr":
                ax.plot(qa, ea, color="red", ls="--", lw=1.0)
            else:
                ax.plot(qa, ea, color="blue", ls="-", lw=1.0)
    ax.set_xlim(QE_LO, QE_HI)
    ax.set_ylim(EPS_LO, EPS_HI)
    ax.set_xlabel(r"$q_e$")
    ax.set_ylabel(r"$\varepsilon_i/\varepsilon_e$")
    ax.text(0.97, 0.95, f"l={l}, {pol}", transform=ax.transAxes,
            ha="right", va="top", fontsize=11,
            bbox=dict(boxstyle="round", fc="white", ec="gray"))
    return n_sr_branch, n_nr_branch


def make_repro():
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    counts = {}
    for ax, (l, pol) in zip(axes.flat, PANELS):
        counts[(pol, l)] = plot_panel(ax, l, pol)
    fig.suptitle("Akimov Fig3 reproduction: sr(a_l=1) red dashed / nr(a_l=0) blue solid",
                 fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = os.path.join(FIG_DIR, "fig3_repro.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("[repro] saved", out)
    for (pol, l), (ns, nn) in counts.items():
        print(f"  panel {pol} l={l}: sr支={ns} nr支={nn}(含平凡线0)")
    return counts


def make_overlay():
    dig_path = os.path.join(DATA_DIR, "fig3_digitized.csv")
    if not os.path.exists(dig_path):
        print("[overlay] 缺 fig3_digitized.csv, 跳过")
        return
    dig = {}
    with open(dig_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["pol"], int(row["l"]))
            dig.setdefault(key, {"sr": [], "nr": []})
            dig[key][row["type"]].append((float(row["q_e"]), float(row["eps_ratio"])))
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, (l, pol) in zip(axes.flat, PANELS):
        plot_panel(ax, l, pol)
        d = dig.get((pol, l), {"sr": [], "nr": []})
        if d["sr"]:
            arr = np.array(d["sr"])
            ax.scatter(arr[:, 0], arr[:, 1], c="darkred", marker="o", s=18,
                       zorder=5, label="dig sr")
        if d["nr"]:
            arr = np.array(d["nr"])
            ax.scatter(arr[:, 0], arr[:, 1], c="navy", marker="s", s=18,
                       zorder=5, label="dig nr")
    fig.suptitle("Fig3 overlay: reproduction curves (lines) vs digitized points (markers)",
                 fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = os.path.join(FIG_DIR, "fig3_overlay.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("[overlay] saved", out)


if __name__ == "__main__":
    import sys
    os.makedirs(FIG_DIR, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "overlay":
        make_overlay()
    else:
        make_repro()
