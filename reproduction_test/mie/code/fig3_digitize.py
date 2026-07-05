"""Fig3 数字化: 颜色像素提取 (step06 T4 批次3).

case: 0703-01-akimov-mie-v1 | step06 · T4

从矢量渲染图 _fig3_src_render.png (Fig3-eps-converted-to.pdf @ 4x) 按颜色提取:
  红 (dashed) = 超辐射 sr(a_l=1);  蓝 (solid) = 非辐射 nr(a_l=0).
六面板 2x3 各自仿射标定 (q_e∈[0,10], eps∈[-10,15]) -> 像素, 反变换出数据坐标.

方法: 逐面板逐列扫描, 红/蓝像素点 -> (q_e,eps), 收集后按 q_e 网格分箱抽样,
保证覆盖各支且每类型每面板 >=15 点. 落 data/fig3_digitized.csv.

不确定度: 像素->数据标定误差 ~1 像素. 面板 x 跨度 ~595 px 对应 q_e 10 => 0.017/px;
y 跨度 ~508 px 对应 eps 25 => 0.049/px. 叠加线宽(~3px)与帧定位(~2px)误差,
总不确定度估 dq_e~0.05, deps~0.15 (归一化后 ~0.005-0.006 量级, 与 Layer3 阈值同量级).
"""
from __future__ import annotations

import os
import csv
import numpy as np
from PIL import Image

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))
FIG_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "figures"))
SRC = os.path.join(FIG_DIR, "_fig3_src_render.png")

# 面板帧像素 (由 dark-pixel 密度探测, 见报告): x 左右, y 上下
# 列: 三面板 [x_left, x_right]
COL_X = [(130, 725), (868, 1463), (1601, 2197)]
# 行: 两排 [y_top, y_bottom]  (top -> eps=15, bottom -> eps=-10)
ROW_Y = [(42, 550), (673, 1196)]
# 面板逻辑 (row, col) -> (l, pol)
PANEL_MAP = {
    (0, 0): (1, "TM"), (0, 1): (2, "TM"), (0, 2): (3, "TM"),
    (1, 0): (1, "TE"), (1, 1): (2, "TE"), (1, 2): (3, "TE"),
}

QE_LO, QE_HI = 0.0, 10.0
EPS_LO, EPS_HI = -10.0, 15.0
NBIN = 40          # q_e 分箱数, 每箱每支取代表点 (保证 >=15 点/类型/面板)


def load_masks():
    a = np.array(Image.open(SRC).convert("RGB")).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    red = (r > 150) & (g < 110) & (b < 110)
    blue = (b > 120) & (r < 110) & (g < 110)
    return red, blue


def px_to_data(x, y, xl, xr, yt, yb):
    qe = (x - xl) / (xr - xl) * (QE_HI - QE_LO) + QE_LO
    eps = EPS_HI - (y - yt) / (yb - yt) * (EPS_HI - EPS_LO)
    return qe, eps


def digitize_panel(mask, xl, xr, yt, yb):
    """在面板矩形内提取 mask 像素, 返回 (qe,eps) 点数组 (分箱抽样后)."""
    sub = mask[yt:yb + 1, xl:xr + 1]
    ys, xs = np.where(sub)
    if len(xs) == 0:
        return np.empty((0, 2))
    xs_full = xs + xl
    ys_full = ys + yt
    qe, eps = px_to_data(xs_full, ys_full, xl, xr, yt, yb)
    # 只留域内
    m = (qe >= QE_LO) & (qe <= QE_HI) & (eps >= EPS_LO) & (eps <= EPS_HI)
    qe, eps = qe[m], eps[m]
    # 按 q_e 分箱, 每箱内对 eps 聚类抽代表点 (支之间 eps 间隔 -> 分段)
    pts = []
    edges = np.linspace(QE_LO, QE_HI, NBIN + 1)
    for i in range(NBIN):
        sel = (qe >= edges[i]) & (qe < edges[i + 1])
        if not np.any(sel):
            continue
        qc = 0.5 * (edges[i] + edges[i + 1])
        es = np.sort(eps[sel])
        # eps 聚类: 相邻差 >1.0 视为不同支
        cluster = [es[0]]
        reps = []
        for v in es[1:]:
            if v - cluster[-1] > 1.0:
                reps.append(np.mean(cluster)); cluster = [v]
            else:
                cluster.append(v)
        reps.append(np.mean(cluster))
        for e in reps:
            pts.append((qc, e))
    return np.array(pts)


def main():
    red, blue = load_masks()
    rows = []
    stats = []
    for (ri, ci), (l, pol) in PANEL_MAP.items():
        xl, xr = COL_X[ci]
        yt, yb = ROW_Y[ri]
        sr_pts = digitize_panel(red, xl, xr, yt, yb)
        nr_pts = digitize_panel(blue, xl, xr, yt, yb)
        for q, e in sr_pts:
            rows.append((f"{pol}{l}", l, pol, "sr", q, e))
        for q, e in nr_pts:
            rows.append((f"{pol}{l}", l, pol, "nr", q, e))
        stats.append((pol, l, len(sr_pts), len(nr_pts)))
    out = os.path.join(DATA_DIR, "fig3_digitized.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "l", "pol", "type", "q_e", "eps_ratio"])
        for panel, l, pol, typ, q, e in rows:
            w.writerow([panel, l, pol, typ, f"{q:.4f}", f"{e:.4f}"])
    print("[digitize] saved", out, "总点数", len(rows))
    for pol, l, ns, nn in stats:
        print(f"  {pol} l={l}: sr={ns}点 nr={nn}点")
    return stats


if __name__ == "__main__":
    main()
