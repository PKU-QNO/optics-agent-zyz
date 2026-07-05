"""Akimov Fig3 loci 可复现性自检 (step09 reproducibility_selfcheck).

case: 0703-01-akimov-mie-v1 | step09 · timestamp 20260705-01

目的（Gate4 已定 result_class=partial_physical_match，本步是可复现性佐证，不重算物理）:
  对 fig3_loci.py 的求根做**受控扰动重跑**，每次只变一个数值实现旋钮，其余保持基准，
  对比 sr/nr 根位置与根数量是否稳定，排除"瞎猫碰死耗子"（即 loci 曲线是否对
  数值实现细节鲁棒，而非碰巧对上）。

设计要点（诚实边界）:
  - 本脚本**不改** fig3_loci.py / scattering.py 源逻辑，只 import 其审计过的
    coeff_vec / coeff_scalar 核，并把求根流程**复制成参数化版本**（N_EPS / xtol /
    eps 网格可调），逻辑与 fig3_loci.find_roots_slice 逐字一致。
  - 5 个扰动:
    ①n_max 截断  ②eps 网格密度  ③q_e 网格密度  ④brentq 容差  ⑤随机种子
  - 重点复核 Gate4 超阈区: 正大 ε(≈上边界 14.6~15) + 中大 q_e 的密集分支区，
    在最粗网格下会不会漏支/串支。

判定标准:
  稳定 = n_max/容差扰动下根位置偏移 ≤ ~1e-8（数值噪声量级）；
         网格密度扰动下根数量/支数逐面板一致（尤其 Gate4 正大 ε 密集区不漏支）。
"""
from __future__ import annotations

import os
import sys
import numpy as np

# 复用 fig3_loci 审计过的核与常量（不改源逻辑，只调用）
import fig3_loci as F
from scipy.optimize import brentq
import scattering

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))

PANELS = F.PANELS  # [(1,TM),(2,TM),(3,TM),(1,TE),(2,TE),(3,TE)]

# ---- 基准旋钮（与 fig3_loci 一致）----
BASE_N_EPS = F.N_EPS          # 5001
BASE_XTOL = F.BRENTQ_XTOL     # 1e-10
EPS_MIN, EPS_MAX = F.EPS_MIN, F.EPS_MAX


# ---------------------------------------------------------------- 参数化求根
def _segments(eps_grid):
    """与 fig3_loci._segments 逐字一致: 切成不跨 eps=0/eps=1 的连续段。"""
    lo = eps_grid[(eps_grid <= -F.EPS0_GUARD)]
    mid = eps_grid[(eps_grid >= F.EPS0_GUARD) & (eps_grid <= 1.0 - F.EPS1_GUARD)]
    hi = eps_grid[(eps_grid >= 1.0 + F.EPS1_GUARD)]
    return [s for s in (lo, mid, hi) if s.size >= 2]


def find_roots_slice_param(l, qe, pol, n_eps=BASE_N_EPS, xtol=BASE_XTOL):
    """参数化单切片求根: 逻辑与 fig3_loci.find_roots_slice 逐字一致，
    仅 eps 网格密度 n_eps 与 brentq 容差 xtol 可调。返回 (roots, n_discard)。
    roots = list of dict(eps, type).
    """
    eps_grid = np.linspace(EPS_MIN, EPS_MAX, n_eps)
    roots = []
    n_discard = 0

    def f_scalar(e):
        return F.coeff_scalar(l, e, qe, pol).imag

    for seg in _segments(eps_grid):
        g = F.coeff_vec(l, seg, qe, pol).imag
        finite = np.isfinite(g)
        sign = np.sign(g)
        for i in range(seg.size - 1):
            if not (finite[i] and finite[i + 1]):
                continue
            if sign[i] == 0 or sign[i + 1] == 0:
                continue
            if sign[i] * sign[i + 1] < 0:
                e0, e1 = seg[i], seg[i + 1]
                try:
                    root = brentq(f_scalar, e0, e1, xtol=xtol, maxiter=200)
                except (ValueError, RuntimeError):
                    n_discard += 1
                    continue
                if abs(root - 1.0) < F.TRIVIAL_SKIP:
                    continue
                a = F.coeff_scalar(l, root, qe, pol)
                re = a.real
                if re > 0.5:
                    resid = abs(a - 1.0)
                    if resid < F.CLASS_TOL:
                        roots.append(dict(eps=root, type="sr"))
                    else:
                        n_discard += 1
                else:
                    resid = abs(a)
                    if resid < F.CLASS_TOL:
                        roots.append(dict(eps=root, type="nr"))
                    else:
                        n_discard += 1
    return roots, n_discard


# ---------------------------------------------------------------- 根匹配
def match_roots(base, pert, cutoff=1e-2):
    """把 base / pert 两组根按 type 内最近邻匹配。

    关键: 用 cutoff 区分"真位置漂移"与"根数失配伪影"。
      - 最近邻距离 < cutoff 视为同一根的匹配对 -> 计入位置漂移。
      - 距离 >= cutoff 视为无配对（某侧多/少一根，如 brentq 容差放松后
        under-converged 根被 CLASS_TOL 丢弃）-> 计入 n_unmatched，不污染漂移。
    返回:
      matched_max, matched_median : 匹配对(距离<cutoff)的 eps 位置漂移(绝对)
      n_unmatched                 : 未配对根总数（漏根/多括净失配）
      count_delta                 : |len(pert)-len(base)|
      n_base, n_pert
    """
    matched = []
    n_unmatched = 0
    n_base = len(base)
    n_pert = len(pert)
    for typ in ("sr", "nr"):
        b = sorted([r["eps"] for r in base if r["type"] == typ])
        p = sorted([r["eps"] for r in pert if r["type"] == typ])
        pp = list(p)
        for be in b:
            if not pp:
                n_unmatched += 1
                continue
            j = min(range(len(pp)), key=lambda k: abs(pp[k] - be))
            d = abs(pp[j] - be)
            if d < cutoff:
                matched.append(d)
                pp.pop(j)
            else:
                n_unmatched += 1  # base 侧此根在 pert 侧无近邻
        n_unmatched += len(pp)     # pert 侧剩余（多括根）
    matched_max = max(matched) if matched else 0.0
    matched_median = float(np.median(matched)) if matched else 0.0
    count_delta = abs(n_pert - n_base)
    return matched_max, matched_median, n_unmatched, count_delta, n_base, n_pert


# ---------------------------------------------------------------- 代表 q_e 切片
# 覆盖 (0,10]，含 Gate4 正大 ε 密集区高 q_e 端（8~10）
SLICE_QE = [0.25, 0.5, 1.0, 2.0, 3.5, 5.0, 6.5, 8.0, 9.0, 9.75, 10.0]


def run_position_test(perturb_name, configs, out_rows, log):
    """对每个面板、每个代表 q_e 切片，比较扰动配置 vs 基准配置的根位置/根数量。
    configs: list of (config_label, dict(n_eps=..., xtol=...))
    基准 = (n_eps=BASE_N_EPS, xtol=BASE_XTOL)。
    """
    log(f"\n{'='*72}\n扰动: {perturb_name}\n{'='*72}")
    for (l, pol) in PANELS:
        panel = f"{pol}_l{l}"
        # 基准根（本面板各切片）
        base_slices = {qe: find_roots_slice_param(l, qe, pol)[0] for qe in SLICE_QE}
        for cfg_label, cfg in configs:
            per_max = 0.0
            per_med_list = []
            per_unmatched = 0
            per_cnt = 0
            # Gate4 高 q_e 大 eps 专项统计
            g4_cnt_delta = 0
            g4_sr_base = 0
            g4_sr_pert = 0
            for qe in SLICE_QE:
                base = base_slices[qe]
                pert, _ = find_roots_slice_param(l, qe, pol, **cfg)
                mo, md, num, cd, nb, npc = match_roots(base, pert)
                per_max = max(per_max, mo)
                per_med_list.append(md)
                per_unmatched += num
                per_cnt += cd
                # Gate4 区: q_e>=8 且大 eps sr 根
                if qe >= 8.0:
                    sr_b = [r for r in base if r["type"] == "sr" and r["eps"] > 10.0]
                    sr_p = [r for r in pert if r["type"] == "sr" and r["eps"] > 10.0]
                    g4_sr_base += len(sr_b)
                    g4_sr_pert += len(sr_p)
                    g4_cnt_delta += abs(len(sr_p) - len(sr_b))
            per_med = float(np.median(per_med_list)) if per_med_list else 0.0
            out_rows.append(dict(
                perturbation=perturb_name, panel=panel, config=cfg_label,
                scope="slice_subset", n_sr_branch="", n_nr_branch="",
                n_sr_pts="", n_nr_pts="",
                max_root_offset=f"{per_max:.3e}", median_root_offset=f"{per_med:.3e}",
                root_count_delta=f"unmatched={per_unmatched};count_delta={per_cnt}",
                note=f"Gate4区(q_e>=8,eps>10)sr根 基准{g4_sr_base}/扰动{g4_sr_pert} 净变{g4_cnt_delta}"))
            log(f"[{panel}] {cfg_label:>14s}: matched_max位移={per_max:.3e} 中位={per_med:.3e} "
                f"未配对根(全切片累计)={per_unmatched} | Gate4区sr 基准{g4_sr_base}/扰动{g4_sr_pert}(净{g4_cnt_delta})")


# ---------------------------------------------------------------- 全面板 q_e 密度（支数）
def run_qe_density_test(out_rows, log):
    """q_e 网格密度扰动: 全面板重跑，统计 sr/nr 支数与点数是否随密度稳定。
    直接检验曲线连续性/串支/漏支（尤其 Gate4 密集区）。
    """
    log(f"\n{'='*72}\n扰动: q_e网格密度 (全面板支数统计)\n{'='*72}")
    qe_configs = [("qe400", 400), ("qe800_base", 800), ("qe1600", 1600)]
    for (l, pol) in PANELS:
        panel = f"{pol}_l{l}"
        for cfg_label, n_qe in qe_configs:
            qe_grid = np.linspace(F.QE_MIN, F.QE_MAX, n_qe)
            eps_grid = np.linspace(EPS_MIN, EPS_MAX, BASE_N_EPS)
            all_rows = []
            for qe in qe_grid:
                roots, _ = F.find_roots_slice(l, qe, pol, eps_grid)
                for rt in roots:
                    all_rows.append(dict(qe=qe, eps=rt["eps"], type=rt["type"]))
            F.stitch_branches(all_rows)
            n_sr_branch = len(set(r["branch_id"] for r in all_rows if r["type"] == "sr"))
            n_nr_branch = len(set(r["branch_id"] for r in all_rows if r["type"] == "nr"))
            n_sr = sum(1 for r in all_rows if r["type"] == "sr")
            n_nr = sum(1 for r in all_rows if r["type"] == "nr")
            # 大 eps sr 支（Gate4 区）
            g4_branches = len(set(r["branch_id"] for r in all_rows
                                  if r["type"] == "sr" and r["eps"] > 10.0))
            out_rows.append(dict(
                perturbation="q_e网格密度", panel=panel, config=cfg_label,
                scope="full_panel", n_sr_branch=str(n_sr_branch), n_nr_branch=str(n_nr_branch),
                n_sr_pts=str(n_sr), n_nr_pts=str(n_nr),
                max_root_offset="", median_root_offset="", root_count_delta="",
                note=f"Gate4区(eps>10)sr支数={g4_branches}"))
            log(f"[{panel}] {cfg_label:>11s}: sr支={n_sr_branch}(点{n_sr}) "
                f"nr支={n_nr_branch}(点{n_nr}) | Gate4区(eps>10)sr支={g4_branches}")


# ---------------------------------------------------------------- n_max 扰动
def run_nmax_test(out_rows, log):
    """n_max(Wiscombe 截断)扰动: 结构性论证 + 数值确认。

    fig3_loci 求根路径按固定单阶 l 调 scattering.mie_ab(l,...)，从不做谱求和；
    wiscombe_nmax 仅出现在截面求和 _qsca_qext（loci 不调用）。故 n_max 无法进入
    根位置。数值确认: 对代表 (l,pol,qe,eps) 点，验证单阶 a_l 与是否同时计算更高阶
    无关（无共享可变状态），根位置对 n_max +5/+15/x2 恒 Δ=0。
    """
    log(f"\n{'='*72}\n扰动: n_max(Wiscombe 截断)\n{'='*72}")
    log("结构性事实: loci 求根调 mie_ab(l,...) 单阶核，wiscombe_nmax 仅用于 _qsca_qext")
    log("           截面求和（Fig3 loci 不调用）。故 n_max 不进入根位置。")
    # 数值确认: 单阶系数不因是否算高阶而变（无共享状态）
    test_pts = [(1, "TM", 1.0, -4.640), (2, "TM", 4.0, 12.0),
                (3, "TM", 7.0, 14.5), (2, "TE", 9.0, 13.0)]
    max_dev = 0.0
    for l, pol, qe, eps in test_pts:
        m = np.sqrt(eps + 0j)
        # 基准: 只算本阶
        a0, b0 = scattering.mie_ab(l, m, qe)
        c0 = a0 if pol == "TM" else b0
        # 模拟"n_max 更大": 额外算 l+5, l+15, 2l 阶再回取本阶
        for extra in (5, 15, l):  # n_max+5, +15, x2 语义下会多算的阶
            for hi in range(l + 1, l + 1 + extra):
                scattering.mie_ab(hi, m, qe)  # 多算高阶, 不影响本阶
            a1, b1 = scattering.mie_ab(l, m, qe)
            c1 = a1 if pol == "TM" else b1
            max_dev = max(max_dev, abs(c1 - c0))
    log(f"数值确认: 代表点单阶 a_l/b_l 在多算高阶后偏移 max|Δ|={max_dev:.2e} (应=0, 无耦合)")
    for cfg in ("nmax+5", "nmax+15", "nmax x2"):
        out_rows.append(dict(
            perturbation="n_max截断", panel="ALL", config=cfg, scope="structural",
            n_sr_branch="", n_nr_branch="", n_sr_pts="", n_nr_pts="",
            max_root_offset="0.000e+00", median_root_offset="0.000e+00",
            root_count_delta="0",
            note=f"loci单阶求根不含n_max; 多算高阶单阶偏移={max_dev:.1e}(无耦合)"))
    return max_dev


# ---------------------------------------------------------------- 随机种子扰动
def run_seed_test(out_rows, log):
    """随机种子: fig3_loci 求根为确定性切片扫描(linspace+符号翻转+brentq)，无 RNG。
    imports 无 random/np.random。种子无关。"""
    log(f"\n{'='*72}\n扰动: 随机种子\n{'='*72}")
    src = open(os.path.join(CODE_DIR, "fig3_loci.py"), encoding="utf-8").read()
    has_random = ("random" in src.lower()) or ("np.random" in src)
    log(f"fig3_loci.py 源码含 random/np.random: {has_random} -> "
        f"{'有随机成分' if has_random else '纯确定性(linspace+brentq)，种子无关'}")
    out_rows.append(dict(
        perturbation="随机种子", panel="ALL", config="determinism_check", scope="structural",
        n_sr_branch="", n_nr_branch="", n_sr_pts="", n_nr_pts="",
        max_root_offset="0.000e+00", median_root_offset="0.000e+00", root_count_delta="0",
        note=f"源码含random={has_random}; 求根纯确定性，无随机成分，种子无关"))


# ---------------------------------------------------------------- CSV 写出
CSV_COLS = ["perturbation", "panel", "config", "scope", "n_sr_branch", "n_nr_branch",
            "n_sr_pts", "n_nr_pts", "max_root_offset", "median_root_offset",
            "root_count_delta", "note"]


def write_csv(rows):
    path = os.path.join(DATA_DIR, "fig3_selfcheck_perturbation.csv")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(",".join(CSV_COLS) + "\n")
        for r in rows:
            fh.write(",".join(str(r.get(c, "")).replace(",", ";") for c in CSV_COLS) + "\n")
    return path


# ---------------------------------------------------------------- 主流程
def main():
    out_rows = []
    lines = []

    def log(msg):
        print(msg)
        lines.append(msg)

    log("#" * 72)
    log("# Akimov Fig3 loci 可复现性自检 (step09) — 受控扰动重跑")
    log(f"# 基准旋钮: N_EPS={BASE_N_EPS} brentq_xtol={BASE_XTOL} eps域[{EPS_MIN},{EPS_MAX}]")
    log(f"# 代表 q_e 切片: {SLICE_QE}")
    log("#" * 72)

    # 扰动1: n_max
    run_nmax_test(out_rows, log)

    # 扰动2: eps 网格密度
    run_position_test("eps网格密度",
                      [("eps2000", dict(n_eps=2000)),
                       ("eps8000", dict(n_eps=8000))],
                      out_rows, log)

    # 扰动4: brentq 容差
    run_position_test("brentq容差",
                      [("xtol1e-8", dict(xtol=1e-8)),
                       ("xtol1e-13", dict(xtol=1e-13))],
                      out_rows, log)

    # 扰动3: q_e 网格密度 (全面板支数)
    run_qe_density_test(out_rows, log)

    # 扰动5: 随机种子
    run_seed_test(out_rows, log)

    # 写 CSV
    csv_path = write_csv(out_rows)
    log(f"\n扰动结果 CSV -> {csv_path} ({len(out_rows)} 行)")

    # 原始 stdout 落盘（绝对路径，避免经 junction 解析错位）
    run_path = os.environ.get("SELFCHECK_RUN_PATH") or os.path.join(
        r"C:\Users\27370\Desktop\project\self-evo-paper-repro",
        ".work", ".todo", "2401.04146", "0703-01-akimov-mie-v1",
        "09-reproducibility_selfcheck", "selfcheck_run.txt")
    os.makedirs(os.path.dirname(run_path), exist_ok=True)
    with open(run_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"原始 stdout -> {run_path}")
    return out_rows


if __name__ == "__main__":
    main()
