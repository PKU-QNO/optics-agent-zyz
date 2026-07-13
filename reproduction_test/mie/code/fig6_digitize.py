"""Fig6 数字化: 颜色像素提取 (step06 T4).

case: 0707-02-akimov-mie-v1 | step06 · T4

**诚实边界声明 (与 Fig3 数字化的本质区别，务必读)**：
Fig3 数字化能按颜色 (红虚=sr / 蓝实=nr) 把像素分成 2 类，再在每类内用"eps 相邻差
>阈值"聚类出各分支代表点，分支间用求根结果的 branch_id 对齐——因为 Fig3 每个
面板只有 2 类曲线且分支稀疏可分。

Fig6 每个 (l,偏振) 面板有 ~10-12 条**同色**曲线密集分布 (Re 子图全蓝色实线，
Im 子图全红色实线，颜色不区分分支)，且论文图上的数字标签 (1-12) 才是真正的分支
标识，但数字标签本身是图像里的文字，无法通过纯颜色阈值可靠 OCR/分割。

因此本脚本**只做粗粒度数字化**：对每个面板的 Re/Im 子图分别提取曲线像素、按
q_e 像素列分箱、箱内按 eps 值聚类得到代表点，输出 (l, pol, subplot, q_e,
value) 点集 —— **不保证这些点与论文原图数字标签 1-12 的分支编号一一对应**，
也**不保证 Re 子图某点与 Im 子图某点属于同一条物理曲线** (两者是独立数字化的，
没有跨子图关联的凭据)。这是本方法相对 Fig3 的明确降级，适合后续 step08 做
"曲线包络/密度形貌"层面的粗对比，不适合逐分支的精确 RMSE 定量对比。

标定 (2026-07-09 修复, 从 figs/Fig6.png, 1716x2442px @3x 用 5px 粒度扫描精确探测):
  上一版行边界用"4行均分整张2442px高度"的占位假设 (_row_h~=550px/行)，但图像
  实际内容只在上方约37.7%区域 (y<=905px)，下方62%是空白边距。TM两行(row0/row1)
  恰好因累积偏移不够大而蒙对非零点，TE两行(row2/row3)完全偏出到空白区、采样到
  0点。main-agent 用 5px 粒度扫描 Fig6.png 得到精确边界 (见下方 ROW_Y/COL_X 常量
  注释)，本脚本已替换为硬编码精确值，不再依赖"均分公式"假设。
"""
from __future__ import annotations

import os
import csv
import numpy as np

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))
FIG_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "figures"))
# 注意: reproduction_test/ 是到 optics_agent/reproduction_test 的 filesystem junction,
# __file__ 的 abspath 解析落在 optics_agent 侧, 相对路径拼接 ../../../ 无法回到
# self-evo-paper-repro 侧真实 case 目录 —— 这里改用写死绝对路径规避该 junction 陷阱
# (与 fig6_verify.py 同一坑, 同一修法)。
CASE_DIR = r"C:\Users\27370\Desktop\project\self-evo-paper-repro\.work\.todo\2401.04146\0707-02-akimov-mie-v1"
SRC = os.path.join(CASE_DIR, "figs", "Fig6.png")

QE_LO, QE_HI = 0.0, 10.0

# ---- 面板像素边界 (main-agent 用 5px 粒度扫描 figs/Fig6.png 精确探测, 2026-07-09 修复) ----
# 图像整体 1716x2442px。4 行(TM-Re,TM-Im,TE-Re,TE-Im) x 3 列(l=1,2,3)。
# 旧版 bug: 假设 4 行均分整张 2442px 高度 (_row_h~=550px/行), 但图像实际内容只在
# 上方约 37.7% 区域 (y<=905), 下方是空白边距, 导致 TE 两行 (row2/row3) 算出的坐标
# 完全偏出到空白区、采样到 0 点。TM 两行恰好因累积偏移不够大而蒙对。
# 现直接硬编码 main-agent 精确扫描给出的 8(行)+6(列) 边界值, 不再用"均分公式"假设。
IMG_W, IMG_H = 1716, 2442

ROW_Y = [
    (15, 195),    # row0: TM, Re (蓝色)
    (240, 420),   # row1: TM, Im (红色)
    (500, 645),   # row2: TE, Re (蓝色)
    (715, 905),   # row3: TE, Im (红色)
]
COL_X = [
    (100, 565),   # col0: l=1
    (650, 1115),  # col1: l=2
    (1200, 1665), # col2: l=3
]

# 纵轴范围 (目视估读, figures.md): TM Re[-5,15], TM Im 随l而变, TE Re[-5,15], TE Im 随l而变
Y_RANGES = {
    (0, "TM_Re"): (-5, 15), (1, "TM_Im_1"): (0, 3), (1, "TM_Im_2"): (0, 4), (1, "TM_Im_3"): (0, 4),
    (2, "TE_Re"): (-5, 15), (3, "TE_Im_1"): (0, 1.2), (3, "TE_Im_2"): (0, 0.8), (3, "TE_Im_3"): (0, 0.6),
}

ROW_MAP = {0: ("TM", "Re"), 1: ("TM", "Im"), 2: ("TE", "Re"), 3: ("TE", "Im")}


def y_range_for(row, col):
    l = col + 1
    pol, comp = ROW_MAP[row]
    if comp == "Re":
        return (-5, 15)
    imranges = {"TM": {1: (0, 3), 2: (0, 4), 3: (0, 4)},
               "TE": {1: (0, 1.2), 2: (0, 0.8), 3: (0, 0.6)}}
    return imranges[pol][l]


def load_masks():
    a = np.array(Image.open(SRC).convert("RGB")).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    blue = (b > 120) & (r < 110) & (g < 110)
    red = (r > 150) & (g < 110) & (b < 110)
    return blue, red


def px_to_data(x, y, xl, xr, yt, yb, y_lo, y_hi):
    qe = (x - xl) / (xr - xl) * (QE_HI - QE_LO) + QE_LO
    val = y_hi - (y - yt) / (yb - yt) * (y_hi - y_lo)
    return qe, val


def digitize_panel(mask, xl, xr, yt, yb, y_lo, y_hi, nbin=50):
    sub = mask[yt:yb + 1, xl:xr + 1]
    ys, xs = np.where(sub)
    if len(xs) == 0:
        return np.empty((0, 2))
    xs_full, ys_full = xs + xl, ys + yt
    qe, val = px_to_data(xs_full, ys_full, xl, xr, yt, yb, y_lo, y_hi)
    m = (qe >= QE_LO) & (qe <= QE_HI) & (val >= y_lo) & (val <= y_hi)
    qe, val = qe[m], val[m]
    pts = []
    edges = np.linspace(QE_LO, QE_HI, nbin + 1)
    for i in range(nbin):
        sel = (qe >= edges[i]) & (qe < edges[i + 1])
        if not np.any(sel):
            continue
        qc = 0.5 * (edges[i] + edges[i + 1])
        vs = np.sort(val[sel])
        cluster = [vs[0]]
        reps = []
        gap = (y_hi - y_lo) * 0.03  # 聚类间距阈值 (值域3%)
        for v in vs[1:]:
            if v - cluster[-1] > gap:
                reps.append(np.mean(cluster)); cluster = [v]
            else:
                cluster.append(v)
        reps.append(np.mean(cluster))
        for v in reps:
            pts.append((qc, v))
    return np.array(pts)


def main():
    if not HAS_PIL:
        print("[digitize] PIL 不可用，跳过数字化 (blocked_by: missing PIL)")
        return None
    if not os.path.exists(SRC):
        print(f"[digitize] 源图不存在: {SRC}，跳过")
        return None
    blue, red = load_masks()
    rows = []
    stats = []
    for row in range(4):
        pol, comp = ROW_MAP[row]
        yt, yb = ROW_Y[row]
        mask = blue if comp == "Re" else red
        for col in range(3):
            l = col + 1
            xl, xr = COL_X[col]
            y_lo, y_hi = y_range_for(row, col)
            pts = digitize_panel(mask, xl, xr, yt, yb, y_lo, y_hi)
            for q, v in pts:
                rows.append((pol, l, comp, f"{q:.4f}", f"{v:.4f}"))
            stats.append((pol, l, comp, len(pts)))
    out = os.path.join(DATA_DIR, "fig6_digitized.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pol", "l", "component", "q_e", "value"])
        w.writerows(rows)
    print("[digitize] saved", out, "总点数", len(rows))
    for pol, l, comp, n in stats:
        print(f"  {pol} l={l} {comp}: {n} 点 (粗粒度, 无跨Re/Im配对, 无分支编号对齐)")
    return stats


if __name__ == "__main__":
    main()
