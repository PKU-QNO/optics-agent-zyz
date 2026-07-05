"""Akimov Fig3 超辐射/非辐射 loci 求根 (step06 T3).

case: 0703-01-akimov-mie-v1 | step06 run_and_monitor · T3

方法（严格照 formalization.yaml solver.recommended_strategy）:
  1. 固定 q_e 切片扫描 (>=800 点覆盖 (0,10]).
  2. 每个 q_e 上对 eps_ratio in [-10,15] 密网格 (>=4000 点) 算
     g(eps) = Im a_l (TM) 或 Im b_l (TE).
  3. 检测 g 符号翻转区间, scipy.optimize.brentq 精化到 xtol<=1e-10.
  4. 酉性实数化分类 (step05 已证严格): 无耗时 |a_l|^2 = Re a_l ⟹
     Im a_l = 0 ⟺ a_l in {0,1}. 根处 Re>0.5 -> 超辐射 sr (断言 |a-1|<1e-8),
     Re<0.5 -> 非辐射 nr (断言 |a|<1e-8). 断言失败的根丢弃并记日志 (数值伪根/极点).
  5. 按根连续性串支 (branch_id), 输出六 CSV.
  6. 从 eps 比算 m: m = np.sqrt(eps+0j) (主值 Im>=0; step05 偶函数结论保证分支无关).

特殊处理:
  - eps=1: a_l=b_l=0 对所有 l,q_e 恒成立 (阻抗匹配平凡非辐射线) —— 解析已知,
    直接作为 branch_id=0 的 nr 线标注, 不靠求根 (并在扫描中排除其邻域避免退化括根).
  - eps=0: m=0 退化点, 网格避开 (±1e-6 邻域), 且分段扫描不跨该点括根.

求值策略:
  - 网格扫描用本文件内 *向量化* BH 评估器 coeff_vec (公式与 scattering.mie_ab
    逐字一致, step06 已核 6 点 max|Δ|=0.00e+00), 为效率.
  - brentq 精化与所有 Layer2 断言用 *审计过* 的 scattering.mie_ab 标量核, 保证
    根位置与自洽判据都跑在 Gate3 通过的核上.
"""
from __future__ import annotations

import os
import numpy as np
from scipy.special import spherical_jn, spherical_yn
from scipy.optimize import brentq

import scattering  # 审计过的 BH 核; brentq 精化与 Layer2 断言均调它

# ---------------------------------------------------------------- 路径
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))

# ---------------------------------------------------------------- 域与网格
EPS_MIN, EPS_MAX = -10.0, 15.0
QE_MIN, QE_MAX = 0.0125, 10.0
N_QE = 800            # >=800 切片
N_EPS = 5001          # 覆盖 [-10,15], 间距 0.005 (>=4000)
EPS0_GUARD = 1e-6     # eps=0 邻域避开半径
EPS1_GUARD = 1e-3     # eps=1 平凡线邻域避开半径
BRENTQ_XTOL = 1e-10
CLASS_TOL = 1e-8      # sr: |a-1|<tol ; nr: |a|<tol
TRIVIAL_SKIP = 1e-2   # brentq 命中 eps 距 1 小于此 -> 归为平凡线跳过


# ---------------------------------------------------------------- 向量化 BH 评估器
def _psi_vec(l, z):
    jl = spherical_jn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    return z * jl, jl + z * jlp


def _xi_vec(l, z):
    jl = spherical_jn(l, z)
    yl = spherical_yn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    ylp = spherical_yn(l, z, derivative=True)
    h = jl + 1j * yl
    hp = jlp + 1j * ylp
    return z * h, h + z * hp


def coeff_vec(l, eps, qe, pol):
    """向量化 (eps 为数组) 返回该通道复系数.

    pol='TM' -> a_l ; pol='TE' -> b_l. 公式与 scattering.mie_ab 逐字一致.
    """
    eps = np.asarray(eps, dtype=complex)
    m = np.sqrt(eps)          # 主值 Im>=0
    x = qe
    mx = m * x
    psi_mx, psip_mx = _psi_vec(l, mx)
    psi_x, psip_x = _psi_vec(l, x)
    xi_x, xip_x = _xi_vec(l, x)
    if pol == "TM":
        num = m * psi_mx * psip_x - psi_x * psip_mx
        den = m * psi_mx * xip_x - xi_x * psip_mx
    else:  # TE
        num = psi_mx * psip_x - m * psi_x * psip_mx
        den = psi_mx * xip_x - m * xi_x * psip_mx
    return num / den


def coeff_scalar(l, eps, qe, pol):
    """标量: 调审计过的 scattering.mie_ab (a,b) 取对应通道."""
    a, b = scattering.mie_ab(l, np.sqrt(eps + 0j), qe)
    return a if pol == "TM" else b


# ---------------------------------------------------------------- 单切片求根
def _segments(eps_grid):
    """把 eps 网格切成不跨 eps=0 / eps=1 退化点的连续段, 避免跨点伪括根."""
    lo = eps_grid[(eps_grid <= -EPS0_GUARD)]
    mid = eps_grid[(eps_grid >= EPS0_GUARD) & (eps_grid <= 1.0 - EPS1_GUARD)]
    hi = eps_grid[(eps_grid >= 1.0 + EPS1_GUARD)]
    return [s for s in (lo, mid, hi) if s.size >= 2]


def find_roots_slice(l, qe, pol, eps_grid):
    """在固定 q_e 切片上求 Im(coeff)=0 的根, 分类 sr/nr.

    返回 (roots, n_discard):
      roots = list of dict(eps, type, residual, a)
      n_discard = 断言失败被丢弃的伪根数
    """
    roots = []
    n_discard = 0

    def f_scalar(e):
        return coeff_scalar(l, e, qe, pol).imag

    for seg in _segments(eps_grid):
        g = coeff_vec(l, seg, qe, pol).imag
        # 有限性保护
        finite = np.isfinite(g)
        sign = np.sign(g)
        # 相邻符号翻转 (跳过含 0 或非有限的相邻对)
        for i in range(seg.size - 1):
            if not (finite[i] and finite[i + 1]):
                continue
            if sign[i] == 0 or sign[i + 1] == 0:
                continue
            if sign[i] * sign[i + 1] < 0:
                e0, e1 = seg[i], seg[i + 1]
                try:
                    root = brentq(f_scalar, e0, e1, xtol=BRENTQ_XTOL, maxiter=200)
                except (ValueError, RuntimeError):
                    n_discard += 1
                    continue
                # 平凡线邻域跳过 (由解析 branch0 覆盖)
                if abs(root - 1.0) < TRIVIAL_SKIP:
                    continue
                a = coeff_scalar(l, root, qe, pol)
                re = a.real
                if re > 0.5:
                    resid = abs(a - 1.0)
                    if resid < CLASS_TOL:
                        roots.append(dict(eps=root, type="sr", residual=resid, a=a))
                    else:
                        n_discard += 1
                else:
                    resid = abs(a)
                    if resid < CLASS_TOL:
                        roots.append(dict(eps=root, type="nr", residual=resid, a=a))
                    else:
                        n_discard += 1
    return roots, n_discard


# ---------------------------------------------------------------- 串支
def stitch_branches(rows, thr=2.0):
    """rows: list of dict(qe,eps,type). 按 q_e 递增, 同 type 内最近邻串支.

    返回同结构 + branch_id (int). branch_id=0 保留给平凡线 (调用方另加).
    """
    for typ in ("sr", "nr"):
        pts = sorted([r for r in rows if r["type"] == typ], key=lambda r: (r["qe"], r["eps"]))
        # 按 qe 分组
        active = []          # list of dict(last_qe, last_eps, bid)
        next_bid = 1
        for r in pts:
            best, bestd = None, thr
            for br in active:
                d = abs(br["last_eps"] - r["eps"])
                if d < bestd:
                    best, bestd = br, d
            if best is None:
                r["branch_id"] = next_bid
                active.append(dict(last_qe=r["qe"], last_eps=r["eps"], bid=next_bid))
                next_bid += 1
            else:
                r["branch_id"] = best["bid"]
                best["last_qe"] = r["qe"]
                best["last_eps"] = r["eps"]
    return rows


# ---------------------------------------------------------------- 面板计算
PANELS = [
    (1, "TM"), (2, "TM"), (3, "TM"),
    (1, "TE"), (2, "TE"), (3, "TE"),
]


def compute_panel(l, pol, qe_grid, eps_grid, verbose=True):
    """算一个面板的全部根. 返回 (rows, stats)."""
    all_rows = []
    total_discard = 0
    for qe in qe_grid:
        roots, nd = find_roots_slice(l, qe, pol, eps_grid)
        total_discard += nd
        for rt in roots:
            all_rows.append(dict(qe=qe, eps=rt["eps"], type=rt["type"], residual=rt["residual"]))
    stitch_branches(all_rows)
    # 平凡非辐射线 eps=1 (解析, branch_id=0): 每个 q_e 一点
    triv_res = abs(coeff_scalar(l, 1.0, qe_grid[len(qe_grid) // 2], pol))
    for qe in qe_grid:
        all_rows.append(dict(qe=qe, eps=1.0, type="nr", branch_id=0, residual=triv_res))
    # 统计
    n_sr_branch = len(set(r["branch_id"] for r in all_rows if r["type"] == "sr"))
    n_nr_branch = len(set(r["branch_id"] for r in all_rows if r["type"] == "nr"))
    n_sr = sum(1 for r in all_rows if r["type"] == "sr")
    n_nr = sum(1 for r in all_rows if r["type"] == "nr" and r["branch_id"] != 0)
    stats = dict(l=l, pol=pol, n_sr_branch=n_sr_branch, n_nr_branch=n_nr_branch,
                 n_sr=n_sr, n_nr=n_nr, n_discard=total_discard, triv_res=triv_res)
    if verbose:
        print(f"[panel {pol} l={l}] sr支={n_sr_branch}(点{n_sr}) "
              f"nr支={n_nr_branch}(点{n_nr}, 含平凡线0) 丢弃伪根={total_discard} "
              f"平凡线残差={triv_res:.2e}")
    return all_rows, stats


def write_csv(rows, l, pol):
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    rows_sorted = sorted(rows, key=lambda r: (r["type"], r["branch_id"], r["qe"]))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("q_e,eps_ratio,branch_id,type,residual\n")
        for r in rows_sorted:
            # eps/q_e 用 %.17g 全 float64 精度存盘: 保证 Layer2 独立 re-eval 复现
            # 存盘时的根残差 (%.10g 截断会在陡坡/密集区把 |a-1| 放大到 ~1e-4, 造成
            # 伪 FAIL; 根本身在 brentq 全精度处已强制 <1e-8).
            fh.write(f"{r['qe']:.17g},{r['eps']:.17g},{r['branch_id']},{r['type']},{r['residual']:.3e}\n")
    return path


# ---------------------------------------------------------------- 主流程
def build_grids():
    qe_grid = np.linspace(QE_MIN, QE_MAX, N_QE)
    eps_grid = np.linspace(EPS_MIN, EPS_MAX, N_EPS)
    return qe_grid, eps_grid


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    qe_grid, eps_grid = build_grids()
    print(f"网格: q_e {N_QE}点 [{QE_MIN},{QE_MAX}] | eps {N_EPS}点 [{EPS_MIN},{EPS_MAX}]")
    all_stats = []
    for l, pol in PANELS:
        rows, stats = compute_panel(l, pol, qe_grid, eps_grid)
        path = write_csv(rows, l, pol)
        print(f"  -> {path}  ({len(rows)} 行)")
        all_stats.append(stats)
    return all_stats


# ---------------------------------------------------------------- Layer2 自洽验证
def _read_csv(l, pol):
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for ln in fh:
            qe, eps, bid, typ, resid = ln.strip().split(",")
            rows.append(dict(qe=float(qe), eps=float(eps), branch_id=int(bid),
                             type=typ, residual=float(resid)))
    return rows


def selfcheck():
    """Layer2 论文内自洽验证. 所有断言与截面均调审计过的 scattering.mie_ab.

    单通道截面 (归一 sigma/(pi R^2)):
      TM 通道: (2/qe^2)(2l+1)|a_l|^2 ; TE 通道: (2/qe^2)(2l+1)|b_l|^2
    sr (该通道系数=1): 应 = 2(2l+1)/qe^2 ; nr (该通道系数=0): 应 ~0.
    """
    print("=" * 70)
    print("Layer2 论文内自洽验证 (step06 T3) — 全部断言调 scattering.mie_ab 核")
    print("=" * 70)
    overall = dict(sr=0, nr=0, sr_fail=0, nr_fail=0,
                   sr_a_resid_max=0.0, sr_sigma_relerr_max=0.0, sr_sigabs_max=0.0,
                   nr_a_max=0.0, nr_sigma_max=0.0)
    for l, pol in PANELS:
        rows = _read_csv(l, pol)
        sr = [r for r in rows if r["type"] == "sr"]
        nr = [r for r in rows if r["type"] == "nr" and r["branch_id"] != 0]
        # 每面板抽查 (全量太多; 均匀抽 <=400 点保证覆盖各支)
        def sample(lst, n=400):
            if len(lst) <= n:
                return lst
            step = len(lst) // n
            return lst[::step]
        p_sr_amax = p_sr_relmax = p_sr_absmax = 0.0
        p_nr_amax = p_nr_sigmax = 0.0
        for r in sample(sr):
            a, b = scattering.mie_ab(l, np.sqrt(r["eps"] + 0j), r["qe"])
            c = a if pol == "TM" else b
            a_resid = abs(c - 1.0)
            sig = (2.0 / r["qe"] ** 2) * (2 * l + 1) * abs(c) ** 2
            sig_target = 2.0 * (2 * l + 1) / r["qe"] ** 2
            rel = abs(sig - sig_target) / sig_target
            # sigma_abs,l = (2/qe^2)(2l+1)[Re c - |c|^2]
            sigabs = (2.0 / r["qe"] ** 2) * (2 * l + 1) * (c.real - abs(c) ** 2)
            p_sr_amax = max(p_sr_amax, a_resid)
            p_sr_relmax = max(p_sr_relmax, rel)
            p_sr_absmax = max(p_sr_absmax, abs(sigabs))
            overall["sr"] += 1
            if a_resid >= 1e-8 or rel >= 1e-8:
                overall["sr_fail"] += 1
        for r in sample(nr):
            a, b = scattering.mie_ab(l, np.sqrt(r["eps"] + 0j), r["qe"])
            c = a if pol == "TM" else b
            a_mag = abs(c)
            sig = (2.0 / r["qe"] ** 2) * (2 * l + 1) * abs(c) ** 2
            p_nr_amax = max(p_nr_amax, a_mag)
            p_nr_sigmax = max(p_nr_sigmax, sig)
            overall["nr"] += 1
            if a_mag >= 1e-8 or sig >= 1e-16:
                overall["nr_fail"] += 1
        overall["sr_a_resid_max"] = max(overall["sr_a_resid_max"], p_sr_amax)
        overall["sr_sigma_relerr_max"] = max(overall["sr_sigma_relerr_max"], p_sr_relmax)
        overall["sr_sigabs_max"] = max(overall["sr_sigabs_max"], p_sr_absmax)
        overall["nr_a_max"] = max(overall["nr_a_max"], p_nr_amax)
        overall["nr_sigma_max"] = max(overall["nr_sigma_max"], p_nr_sigmax)
        print(f"[{pol} l={l}] sr抽查{min(len(sr),400)}/{len(sr)}: "
              f"max|a-1|={p_sr_amax:.2e} sigma_rel_max={p_sr_relmax:.2e} "
              f"max|sigma_abs|={p_sr_absmax:.2e} | "
              f"nr抽查{min(len(nr),400)}/{len(nr)}: max|a|={p_nr_amax:.2e} "
              f"max_sigma={p_nr_sigmax:.2e}")

    # 平凡线 eps=1 抽查
    print("-" * 70)
    qe_samp = np.linspace(QE_MIN, QE_MAX, 20)
    triv_max = 0.0
    for l, pol in PANELS:
        for qe in qe_samp:
            a, b = scattering.mie_ab(l, np.sqrt(1.0 + 0j), qe)
            triv_max = max(triv_max, abs(a), abs(b))
    print(f"平凡线 eps=1 抽查 (6面板 x 20 q_e): max(|a_l|,|b_l|) = {triv_max:.2e} "
          f"(判据 <1e-14: {'PASS' if triv_max < 1e-14 else 'FAIL'})")

    # step03 锚点核对
    print("-" * 70)
    r1 = _read_csv(1, "TM")
    sr1 = [r for r in r1 if r["type"] == "sr"]
    # 找 qe 最接近 1.0 的 sr 根
    near = sorted(sr1, key=lambda r: abs(r["qe"] - 1.0))[:5]
    anchor = min(near, key=lambda r: abs(r["eps"] - (-4.640)))
    a, b = scattering.mie_ab(1, np.sqrt(anchor["eps"] + 0j), anchor["qe"])
    print(f"step03 锚点 (l=1 TM, q_e≈1 -> eps≈-4.640): "
          f"实测 q_e={anchor['qe']:.4f} eps={anchor['eps']:.6f} "
          f"残差|a-1|={abs(a - 1.0):.2e} "
          f"(命中±0.01: {'PASS' if abs(anchor['eps'] - (-4.640)) < 0.01 else 'FAIL'})")

    # 总判据
    print("=" * 70)
    print(f"总计: sr根抽查{overall['sr']}(fail={overall['sr_fail']}) "
          f"nr根抽查{overall['nr']}(fail={overall['nr_fail']})")
    print(f"  sr: max|a-1|={overall['sr_a_resid_max']:.2e} "
          f"sigma_rel_max={overall['sr_sigma_relerr_max']:.2e} "
          f"max|sigma_abs|={overall['sr_sigabs_max']:.2e}")
    print(f"  nr: max|a|={overall['nr_a_max']:.2e} "
          f"max_sigma={overall['nr_sigma_max']:.2e}")
    all_pass = (overall["sr_fail"] == 0 and overall["nr_fail"] == 0
                and triv_max < 1e-14
                and abs(anchor["eps"] - (-4.640)) < 0.01)
    print(f"Layer2 自洽全过: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 70)
    return all_pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selfcheck":
        selfcheck()
    elif len(sys.argv) > 1 and sys.argv[1] == "smoke":
        # 单面板单切片冒烟
        qe_grid, eps_grid = build_grids()
        r, nd = find_roots_slice(1, 1.0, "TM", eps_grid)
        print("smoke l=1 TM qe=1 根:")
        for rt in r:
            print(f"  eps={rt['eps']:.6f} type={rt['type']} resid={rt['residual']:.2e} a={rt['a']:.6g}")
        print("丢弃:", nd)
    else:
        main()
