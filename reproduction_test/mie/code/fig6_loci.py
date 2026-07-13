"""Akimov Fig6 超吸收态 loci 复数域求根 (step04+06 合并).

case: 0707-02-akimov-mie-v1 | step04 T1 + step06 T3

物理 spec 唯一来源: .work/.todo/2401.04146/0707-02-akimov-mie-v1/formalization.yaml
（本代码消费该 spec，不消费论文 prose）。

核心方法（严格照 formalization.yaml solver.recommended_strategy）:
  超吸收条件 a_l(q_e,z)=1/2 (TM) 或 b_l(q_e,z)=1/2 (TE)，z=eps_ratio∈C 是待求未知数
  （q_e 固定实数扫描）。一个复数方程 = 2 个实自由度方程：
     F1(x,y) = Re[coeff(l,x+iy,q_e,pol)] - 0.5 = 0
     F2(x,y) = Im[coeff(l,x+iy,q_e,pol)]       = 0
  用 scipy.optimize.root(method='hybr') 做二维非线性方程组求根。

复用: coeff() 直接调用 case 0703-01 已 Gate3 通过的 scattering.mie_ab(l, m, x)，
m = sqrt(eps_ratio) 取主值 (Im eps_ratio>=0 时 Im m>=0，与 spec 一致)。
零新增物理代码 —— 只新增"复数域求根+多起点+延拓"这层数值方法。

延拓策略:
  q_e 由小到大扫描 (N_QE 切片)。每个切片起点 = 上一切片收敛根 (warm start，跟踪
  已知分支连续变化) + 周期性补充稀疏网格新起点 (防止漏掉在某个 q_e 处新生成的分支，
  spec solver.recommended_strategy 第6条)。首切片额外做一次密集网格多起点扫描
  (发现初始分支集合)。

验证判据: 解出 z 后代回 mie_ab 断言 |coeff(q_e,z)-0.5| < TOL（写入 CSV 的
residual 列，供 step07 verifier 独立复核）。
"""
from __future__ import annotations

import os
import sys
import time
import numpy as np
from scipy.optimize import root

import scattering  # 审计过的 BH 核 (case 0703-01 Gate3 通过); 唯一物理系数来源

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))

# ---------------------------------------------------------------- 域与网格
# 复数域范围: formalization.yaml materials.effective_parameter.eps_ratio.range
RE_MIN, RE_MAX = -10.0, 20.0
IM_MIN, IM_MAX = 0.0, 10.0
QE_MIN, QE_MAX = 0.05, 10.0   # q_e->0 极限避开 (spec special_cases)
N_QE = 100                     # q_e 切片数 (延拓意义下比 Fig3 的 800 点密网格扫描少很多)

TOL = 1e-8              # 断言判据 |coeff-0.5|<tol (spec solver 第5条)
DEDUP_THR = 5e-3        # 同切片去重欧氏距离阈值 (eps_ratio 平面, x-y 单位一致)
CONT_MATCH_THR = 2.0    # 相邻 q_e 切片串支匹配阈值 (eps_ratio 平面距离)
REFRESH_EVERY = 4       # 每隔几个切片补充一次稀疏新起点网格 (防漏新分支)
EPS0_GUARD = 1e-6       # eps_ratio=0 邻域退化点避开半径

PANELS = [(1, "TM"), (2, "TM"), (3, "TM"), (1, "TE"), (2, "TE"), (3, "TE")]


# ---------------------------------------------------------------- 复系数求值
def coeff(l, z, qe, pol):
    """z=eps_ratio(complex) -> a_l 或 b_l，经 scattering.mie_ab (唯一物理源)。

    m = sqrt(z) 主值 (numpy/cmath principal branch: Re(m)>=0，Im(z)>=0 时 Im(m)>=0，
    与 formalization.yaml materials.effective_parameter.m_rel 定义一致)。
    """
    m = np.sqrt(complex(z))
    a, b = scattering.mie_ab(l, m, qe)
    return a if pol == "TM" else b


def residual_vec(v, l, qe, pol):
    x, y = v
    c = coeff(l, complex(x, y), qe, pol)
    return [c.real - 0.5, c.imag]


def try_root(l, qe, pol, x0, y0):
    """从起点 (x0,y0) 求根，返回 (x,y,residual) 或 None（不收敛/超域/断言未过）。"""
    if abs(x0) < EPS0_GUARD and abs(y0) < EPS0_GUARD:
        x0 = x0 + EPS0_GUARD * 10  # 避开 eps_ratio=0 退化点
    try:
        sol = root(residual_vec, [x0, y0], args=(l, qe, pol), method="hybr",
                   tol=1e-12)
    except Exception:
        return None
    if not sol.success:
        return None
    x, y = float(sol.x[0]), float(sol.x[1])
    # 放宽域判断 (允许略超出标定范围, 供后续判断是否要收紧坐标轴), 但不接受发散解
    if not (RE_MIN - 5 <= x <= RE_MAX + 5 and IM_MIN - 1.0 <= y <= IM_MAX + 5):
        return None
    c = coeff(l, complex(x, y), qe, pol)
    resid = abs(c - 0.5)
    if resid > TOL or not np.isfinite(resid):
        return None
    if y < 0.0:
        y = 0.0 if y > -1e-6 else y  # 数值噪声夹紧; 真负值仍保留供 verifier 检查
    return (x, y, resid)


def dedup(points, thr=DEDUP_THR):
    kept = []
    for p in points:
        dup = False
        for k in kept:
            if (p[0] - k[0]) ** 2 + (p[1] - k[1]) ** 2 < thr ** 2:
                dup = True
                break
        if not dup:
            kept.append(p)
    return kept


def multistart_grid(nx, ny, re_lo=RE_MIN, re_hi=RE_MAX, im_lo=IM_MIN, im_hi=IM_MAX):
    xs = np.linspace(re_lo, re_hi, nx)
    ys = np.linspace(im_lo + 1e-3, im_hi, ny)
    return [(x, y) for x in xs for y in ys]


# ---------------------------------------------------------------- 单面板求根
def compute_panel(l, pol, verbose=True, n_qe=None):
    n_qe = n_qe or N_QE
    qe_grid = np.linspace(QE_MIN, QE_MAX, n_qe)
    t0 = time.time()
    all_rows = []
    prev_roots = []  # list of (x,y)  上一切片收敛根 (warm start)

    dense_grid = multistart_grid(28, 16)      # 首切片密集网格
    sparse_grid = multistart_grid(10, 6)      # 周期性补充稀疏网格

    for i, qe in enumerate(qe_grid):
        candidates = list(prev_roots)
        if i == 0:
            candidates += dense_grid
        elif i % REFRESH_EVERY == 0:
            candidates += sparse_grid

        found = []
        for x0, y0 in candidates:
            r = try_root(l, qe, pol, x0, y0)
            if r is not None:
                found.append(r)
        found = dedup(found)
        for x, y, resid in found:
            all_rows.append(dict(qe=qe, x=x, y=y, residual=resid))
        prev_roots = [(x, y) for x, y, _ in found]

        if verbose and (i % 20 == 0 or i == len(qe_grid) - 1):
            print(f"  [{pol} l={l}] qe={qe:.3f} ({i + 1}/{len(qe_grid)}) "
                  f"根数={len(found)} 累计耗时={time.time() - t0:.1f}s")

    if verbose:
        print(f"[panel {pol} l={l}] 完成, 总点数={len(all_rows)}, "
              f"耗时={time.time() - t0:.1f}s")
    return all_rows


# ---------------------------------------------------------------- 串支 (2D)
def stitch_branches(rows, thr=CONT_MATCH_THR):
    """按 q_e 递增，在 (eps_re, eps_im) 平面用最近邻串支。返回同结构+branch_id。"""
    from collections import defaultdict
    by_qe = defaultdict(list)
    for r in rows:
        by_qe[r["qe"]].append(r)
    qes = sorted(by_qe.keys())
    active = []  # list of dict(last_x,last_y,bid)
    next_bid = 1
    for qe in qes:
        pts = by_qe[qe]
        used = set()
        for r in pts:
            best_idx, bestd = None, thr
            for idx, br in enumerate(active):
                if idx in used:
                    continue
                d = ((br["last_x"] - r["x"]) ** 2 + (br["last_y"] - r["y"]) ** 2) ** 0.5
                if d < bestd:
                    best_idx, bestd = idx, d
            if best_idx is None:
                r["branch_id"] = next_bid
                active.append(dict(last_x=r["x"], last_y=r["y"], bid=next_bid))
                next_bid += 1
            else:
                r["branch_id"] = active[best_idx]["bid"]
                active[best_idx]["last_x"] = r["x"]
                active[best_idx]["last_y"] = r["y"]
                used.add(best_idx)
    return rows


def write_csv(rows, l, pol):
    path = os.path.join(DATA_DIR, f"fig6_loci_{pol}_l{l}.csv")
    rows_sorted = sorted(rows, key=lambda r: (r["branch_id"], r["qe"]))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("q_e,branch_id,eps_re,eps_im,residual\n")
        for r in rows_sorted:
            fh.write(f"{r['qe']:.17g},{r['branch_id']},{r['x']:.17g},"
                     f"{r['y']:.17g},{r['residual']:.3e}\n")
    return path


# ---------------------------------------------------------------- 主流程
def main(panels=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    panels = panels or PANELS
    all_stats = []
    for l, pol in panels:
        rows = compute_panel(l, pol)
        stitch_branches(rows)
        path = write_csv(rows, l, pol)
        n_branch = len(set(r["branch_id"] for r in rows))
        n_neg = len(set(r["branch_id"] for r in rows if r["x"] < 0))
        print(f"  -> {path} ({len(rows)}行, {n_branch}支, Re<0支数={n_neg})")
        all_stats.append(dict(l=l, pol=pol, n_rows=len(rows), n_branch=n_branch,
                              n_neg_branch=n_neg))
    return all_stats


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        # 单面板冒烟测试 (小规模, 验证代码通路与耗时量级)
        rows = compute_panel(1, "TM", n_qe=8)
        stitch_branches(rows)
        print(f"smoke: {len(rows)} 行, {len(set(r['branch_id'] for r in rows))} 支")
        for r in sorted(rows, key=lambda r: (r['branch_id'], r['qe']))[:15]:
            print(f"  qe={r['qe']:.3f} bid={r['branch_id']} "
                  f"z={r['x']:.4f}+{r['y']:.4f}j resid={r['residual']:.2e}")
    elif len(sys.argv) > 1 and sys.argv[1].startswith("panel="):
        # 单面板全量: panel=TM1 / panel=TE3 等
        tag = sys.argv[1].split("=", 1)[1]
        pol = "TM" if tag.startswith("TM") else "TE"
        l = int(tag[2:])
        main(panels=[(l, pol)])
    else:
        main()
