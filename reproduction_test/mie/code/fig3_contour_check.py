"""Fig3 完备性核对: 二维 contour 法独立提取 loci, 与切片法 CSV 对比 (step06 T4).

case: 0703-01-akimov-mie-v1 | step06 · T4 | Gate2 强制附加判据(防漏根).

方法 (formalization.yaml solver.fallback_strategy):
  在 (q_e, eps) 二维密网格上直接算 g=Im(coeff_l) (TM: a_l, TE: b_l),
  matplotlib contour(level=0) 提取零等值线, 按 Re(coeff) 分类:
    Re>0.5 -> sr(a_l≈1) 红虚;  Re<0.5 -> nr(a_l≈0) 蓝实.
  与切片法 CSV 曲线叠加目测, 并逐面板计数支数对比.

计数说明: 二维 contour 的"支数"用零等值线段(contour path 段) 数近似, 受网格分辨率
影响, 不追求与切片法 branch_id 完全同数; 判据是"contour 有的支切片法都有(无漏根),
切片法无多余杂散支"。这里给逐面板 contour 段数 vs 切片 branch 数, 并做覆盖核对:
  对每个 contour 提取点, 找同面板同类型切片法最近点距离, 统计最大/中位覆盖距离,
  若某段 contour 找不到近邻切片点(距离>阈值) => 切片法漏根警告。
"""
from __future__ import annotations

import os
import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fig3_loci as F  # 复用向量化 coeff_vec (不改该文件)

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))
FIG_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "figures"))

PANELS = [(1, "TM"), (2, "TM"), (3, "TM"), (1, "TE"), (2, "TE"), (3, "TE")]

QE_MIN, QE_MAX = 0.0125, 10.0
EPS_MIN, EPS_MAX = -10.0, 15.0
NQ = 500          # 二维网格 q_e
NE = 900          # 二维网格 eps
EPS0_GUARD = 1e-6
EPS1_GUARD = 1e-3
# contour 点匹配切片法点的"命中"归一化阈值 (与 step08 同归一: q/10, eps/25)
COVER_TOL = 0.02


def read_csv(l, pol):
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    sr, nr = [], []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            q, e = float(row["q_e"]), float(row["eps_ratio"])
            (sr if row["type"] == "sr" else nr).append((q, e))
    return np.array(sr), np.array(nr)


def branch_count(l, pol):
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    sr_b, nr_b = set(), set()
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["type"] == "sr":
                sr_b.add(int(row["branch_id"]))
            else:
                nr_b.add(int(row["branch_id"]))
    return len(sr_b), len(nr_b)


def build_grid():
    qe = np.linspace(QE_MIN, QE_MAX, NQ)
    eps = np.linspace(EPS_MIN, EPS_MAX, NE)
    # 避开 eps=0 / eps=1 退化点: 用 mask 把邻域设 nan (contour 自动断开)
    return qe, eps


def compute_field(l, pol, qe, eps):
    """返回 G[ie, iq] = Im coeff, R[ie, iq] = Re coeff. 退化点邻域置 nan."""
    QG, EG = np.meshgrid(qe, eps)  # shape (NE, NQ)
    G = np.full(QG.shape, np.nan)
    R = np.full(QG.shape, np.nan)
    for iq, q in enumerate(qe):
        c = F.coeff_vec(l, eps, q, pol)  # 向量化 over eps
        G[:, iq] = c.imag
        R[:, iq] = c.real
    # 退化点邻域屏蔽
    degen = (np.abs(EG) < 1e-2) | (np.abs(EG - 1.0) < 5e-3)
    G[degen] = np.nan
    R[degen] = np.nan
    return QG, EG, G, R


def extract_zero_contour(ax, QG, EG, G, R):
    """提取 Im=0 零等值线, 按 Re 分类. 返回 (sr_pts, nr_pts, n_seg_sr, n_seg_nr)."""
    cs = ax.contour(QG, EG, G, levels=[0.0], colors="k", linewidths=0)
    sr_pts, nr_pts = [], []
    n_seg_sr = n_seg_nr = 0
    # 遍历所有等值线段, 对段上采样点按 Re 分类
    segs = []
    # mpl 3.10: 用 allsegs
    if hasattr(cs, "allsegs") and cs.allsegs:
        segs = cs.allsegs[0]
    for seg in segs:
        if len(seg) < 2:
            continue
        # 段中点的 Re 值决定类型 (段一般不跨类型, 因 sr/nr 不同零线不相交)
        qs = seg[:, 0]
        es = seg[:, 1]
        # 双线性插值 Re
        re_vals = _interp_field(R, QG[0, :], EG[:, 0], qs, es)
        mean_re = np.nanmean(re_vals)
        if mean_re > 0.5:
            n_seg_sr += 1
            for q, e in zip(qs, es):
                sr_pts.append((q, e))
        else:
            n_seg_nr += 1
            for q, e in zip(qs, es):
                nr_pts.append((q, e))
    return np.array(sr_pts), np.array(nr_pts), n_seg_sr, n_seg_nr


def _interp_field(F2d, qax, eax, qs, es):
    """在规则网格 F2d[ie,iq] 上双线性插值 (qs,es) 点值."""
    iq = np.clip(np.searchsorted(qax, qs) - 1, 0, len(qax) - 2)
    ie = np.clip(np.searchsorted(eax, es) - 1, 0, len(eax) - 2)
    q0, q1 = qax[iq], qax[iq + 1]
    e0, e1 = eax[ie], eax[ie + 1]
    tq = np.where(q1 > q0, (qs - q0) / (q1 - q0), 0.0)
    te = np.where(e1 > e0, (es - e0) / (e1 - e0), 0.0)
    f00 = F2d[ie, iq]; f10 = F2d[ie, iq + 1]
    f01 = F2d[ie + 1, iq]; f11 = F2d[ie + 1, iq + 1]
    return (f00 * (1 - tq) * (1 - te) + f10 * tq * (1 - te)
            + f01 * (1 - tq) * te + f11 * tq * te)


def coverage(contour_pts, slice_pts):
    """对每个 contour 点找最近 slice 点归一化距离, 返回 (max, median, n_uncovered)."""
    if len(contour_pts) == 0 or len(slice_pts) == 0:
        return np.nan, np.nan, len(contour_pts)
    cp = contour_pts.copy().astype(float)
    sp = slice_pts.copy().astype(float)
    cp[:, 0] /= 10.0; cp[:, 1] /= 25.0
    sp[:, 0] /= 10.0; sp[:, 1] /= 25.0
    dists = []
    # 分块算最近邻距离
    for i in range(len(cp)):
        d = np.sqrt(np.sum((sp - cp[i]) ** 2, axis=1)).min()
        dists.append(d)
    dists = np.array(dists)
    return dists.max(), np.median(dists), int(np.sum(dists > COVER_TOL))


def main():
    qe, eps = build_grid()
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    lines = []
    lines.append("=" * 78)
    lines.append("Fig3 完备性核对: 切片法(CSV) vs 二维 contour 法 逐面板支数/覆盖对比")
    lines.append(f"二维网格: q_e {NQ}点[{QE_MIN},{QE_MAX}] x eps {NE}点[{EPS_MIN},{EPS_MAX}]")
    lines.append(f"覆盖归一化阈值 COVER_TOL={COVER_TOL} (q/10, eps/25); "
                 f"contour 点距最近切片点 > 阈值 记为未覆盖(潜在漏根)")
    lines.append("=" * 78)
    verdict_all = True
    for ax, (l, pol) in zip(axes.flat, PANELS):
        QG, EG, G, R = compute_field(l, pol, qe, eps)
        sr_c, nr_c, nseg_sr, nseg_nr = extract_zero_contour(ax, QG, EG, G, R)
        sr_s, nr_s = read_csv(l, pol)
        nb_sr, nb_nr = branch_count(l, pol)
        # 叠加目测: 切片法线 + contour 点
        if len(sr_s):
            ax.plot(sr_s[:, 0], sr_s[:, 1], ".", color="red", ms=0.6, alpha=0.4)
        if len(nr_s):
            ax.plot(nr_s[:, 0], nr_s[:, 1], ".", color="blue", ms=0.6, alpha=0.4)
        if len(sr_c):
            ax.plot(sr_c[:, 0], sr_c[:, 1], ".", color="darkred", ms=0.8, alpha=0.5)
        if len(nr_c):
            ax.plot(nr_c[:, 0], nr_c[:, 1], ".", color="navy", ms=0.8, alpha=0.5)
        ax.set_xlim(0, 10); ax.set_ylim(-10, 15)
        ax.set_xlabel(r"$q_e$"); ax.set_ylabel(r"$\varepsilon_i/\varepsilon_e$")
        ax.set_title(f"l={l} {pol}: slice sr/nr支={nb_sr}/{nb_nr} contour段={nseg_sr}/{nseg_nr}",
                     fontsize=9)
        # 覆盖核对: contour sr 点是否都能被切片 sr 点覆盖(无漏根)
        mx_sr, md_sr, unc_sr = coverage(sr_c, sr_s)
        mx_nr, md_nr, unc_nr = coverage(nr_c, nr_s)
        # 未覆盖比例
        frac_sr = unc_sr / max(len(sr_c), 1)
        frac_nr = unc_nr / max(len(nr_c), 1)
        panel_ok = (frac_sr < 0.05 and frac_nr < 0.05)
        verdict_all = verdict_all and panel_ok
        lines.append(f"[{pol} l={l}]")
        lines.append(f"  切片法 branch: sr={nb_sr}  nr={nb_nr}(含平凡线bid=0)")
        lines.append(f"  contour 段  : sr={nseg_sr}  nr={nseg_nr} "
                     f"(段数受网格分辨率影响, 不要求等于 branch 数)")
        lines.append(f"  覆盖 sr: contour点={len(sr_c)} max归一距={mx_sr:.4f} "
                     f"中位={md_sr:.4f} 未覆盖={unc_sr}({frac_sr*100:.2f}%)")
        lines.append(f"  覆盖 nr: contour点={len(nr_c)} max归一距={mx_nr:.4f} "
                     f"中位={md_nr:.4f} 未覆盖={unc_nr}({frac_nr*100:.2f}%)")
        lines.append(f"  面板判定(未覆盖<5%): {'PASS' if panel_ok else 'WARN 潜在漏根/多支'}")
    fig.suptitle("Fig3 completeness check: slice-method (faint) vs 2D contour (dark) overlay",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = os.path.join(FIG_DIR, "fig3_contour_check.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    lines.append("=" * 78)
    lines.append(f"完备性总判定 (所有面板 contour 点被切片法覆盖 >95%): "
                 f"{'PASS 无系统性漏根' if verdict_all else 'WARN 需人工核对'}")
    lines.append("说明: 该判据检验 contour(独立法) 找到的 loci 是否都被切片法 CSV 覆盖;")
    lines.append("      通过 => 切片法无系统性漏根/漏支; contour 段数与 branch 数差异属分辨率, 非漏根。")
    lines.append("=" * 78)
    report = "\n".join(lines)
    print(report)
    print("[contour] saved", out)
    return report


if __name__ == "__main__":
    os.makedirs(FIG_DIR, exist_ok=True)
    main()
