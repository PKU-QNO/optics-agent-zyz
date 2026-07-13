"""Fig6 Layer1/2 物理验证 (step07).

case: 0707-02-akimov-mie-v1 | step07 physical_verification

Layer1 (硬约束, 断言型):
  H1. |coeff(l,z,q_e,pol) - 0.5| < 1e-8 对 CSV 全部行成立 (独立于 fig6_loci.py
      重新调 scattering.mie_ab 复算，不信任 CSV 里已存的 residual 列)。
  H2. Im(eps_ratio) >= -1e-6 对全部行成立 (spec 域约束: 材料耗散 Im ε_i>=0)。

Layer2 (论文内自洽交叉验证):
  L1. 等分关系 sigma_sca,l^sa = sigma_abs,l^sa = (1/4) sigma_sca,l^sr
      在超吸收根处代入截面公式独立重算 (formulas.md 第六节)。
  L2. 完备性自查 (formulas.md/tex:L361 逐字): Re>0 区域 TM/TE 均应有"多个"
      (>1) 分支；Re<0 区域应恰好 1 个 TM 分支、0 个 TE 分支。

不做的事: 不做 Layer3 (与论文图数字化定量对比)，那是 step08+Gate4 之后的范围。
"""
from __future__ import annotations

import os
import sys
import csv
import numpy as np

import scattering

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))

PANELS = [(1, "TM"), (2, "TM"), (3, "TM"), (1, "TE"), (2, "TE"), (3, "TE")]

H1_TOL = 1e-8
H2_TOL = 1e-6
L1_RELTOL = 1e-8


def read_csv(l, pol):
    path = os.path.join(DATA_DIR, f"fig6_loci_{pol}_l{l}.csv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            rows.append(dict(qe=float(row["q_e"]), bid=int(row["branch_id"]),
                             x=float(row["eps_re"]), y=float(row["eps_im"]),
                             residual=float(row["residual"])))
    return rows


def coeff(l, z, qe, pol):
    m = np.sqrt(complex(z))
    a, b = scattering.mie_ab(l, m, qe)
    return a if pol == "TM" else b


def verify_panel(l, pol, log):
    rows = read_csv(l, pol)
    n = len(rows)
    h1_max = 0.0
    h1_fail = 0
    h2_fail = 0
    l1_max = 0.0
    l1_fail = 0
    for r in rows:
        z = complex(r["x"], r["y"])
        c = coeff(l, z, qe=r["qe"], pol=pol)
        resid = abs(c - 0.5)
        h1_max = max(h1_max, resid)
        if resid >= H1_TOL:
            h1_fail += 1
        if r["y"] < -H2_TOL:
            h2_fail += 1
        # L1 等分关系: 单通道截面 (归一 sigma/(pi R^2), 与 fig3_loci.selfcheck 同套归一)
        # sigma_sca,l = (2/qe^2)(2l+1)|c|^2 ; sigma_abs,l = (2/qe^2)(2l+1)[Re(c)-|c|^2]
        qe = r["qe"]
        sig_sca = (2.0 / qe ** 2) * (2 * l + 1) * abs(c) ** 2
        sig_abs = (2.0 / qe ** 2) * (2 * l + 1) * (c.real - abs(c) ** 2)
        sig_target = (2.0 / qe ** 2) * (2 * l + 1) * 0.25  # 理论 (2l+1)/(2qe^2) 型 (此归一下多因子2)
        rel = max(abs(sig_sca - sig_target), abs(sig_abs - sig_target)) / sig_target
        l1_max = max(l1_max, rel)
        if rel >= L1_RELTOL and resid < H1_TOL:
            # 只有在断言通过(a_l确实=0.5)的前提下才算L1失败(避免H1本身失败的根污染L1统计)
            l1_fail += 1

    # 完备性自查 (L2)
    branches = {}
    for r in rows:
        branches.setdefault(r["bid"], []).append(r)
    n_pos = sum(1 for b in branches.values() if all(p["x"] >= 0 for p in b))
    n_neg = sum(1 for b in branches.values() if any(p["x"] < 0 for p in b))
    n_total_branch = len(branches)

    log.append(f"[{pol} l={l}] 行数={n} 分支数={n_total_branch} "
               f"(Re全>=0支={n_pos}, 含Re<0支={n_neg})")
    log.append(f"  H1 |coeff-0.5|: max={h1_max:.3e} fail(>={H1_TOL:.0e})={h1_fail}/{n}")
    log.append(f"  H2 Im(eps)>=-{H2_TOL:.0e}: fail={h2_fail}/{n}")
    log.append(f"  L1 等分关系相对误差: max={l1_max:.3e} fail(>={L1_RELTOL:.0e})={l1_fail}/{n}")

    return dict(l=l, pol=pol, n=n, n_branch=n_total_branch, n_pos=n_pos, n_neg=n_neg,
               h1_max=h1_max, h1_fail=h1_fail, h2_fail=h2_fail,
               l1_max=l1_max, l1_fail=l1_fail)


def main():
    log = []
    log.append("=" * 70)
    log.append("Fig6 超吸收态 Layer1/2 物理验证 (step07)")
    log.append("=" * 70)
    stats = []
    for l, pol in PANELS:
        stats.append(verify_panel(l, pol, log))
        log.append("-" * 70)

    h1_total_fail = sum(s["h1_fail"] for s in stats)
    h2_total_fail = sum(s["h2_fail"] for s in stats)
    l1_total_fail = sum(s["l1_fail"] for s in stats)
    h1_pass = h1_total_fail == 0
    h2_pass = h2_total_fail == 0
    l1_pass = l1_total_fail == 0

    # L2 完备性判据 (formulas.md/tex:L361 逐字):
    #  TM (l=1,2,3): 每个面板 Re>0 分支数 > 1 (multiple), 且恰好 1 支含 Re<0
    #  TE (l=1,2,3): 每个面板 Re>0 分支数 > 1 (multiple), 且 0 支含 Re<0
    complet_lines = []
    completeness_pass = True
    for s in stats:
        if s["pol"] == "TM":
            ok = (s["n_pos"] > 1) and (s["n_neg"] == 1)
            expect = "Re>0多支 & 恰1支含Re<0"
        else:
            ok = (s["n_pos"] > 1) and (s["n_neg"] == 0)
            expect = "Re>0多支 & 0支含Re<0"
        completeness_pass = completeness_pass and ok
        complet_lines.append(f"  [{s['pol']} l={s['l']}] 期望={expect} "
                             f"实际(Re全>=0支={s['n_pos']}, 含Re<0支={s['n_neg']}) "
                             f"{'PASS' if ok else 'FAIL'}")

    log.append("=" * 70)
    log.append(f"H1 (|coeff-0.5|<{H1_TOL:.0e}) 全局: {'PASS' if h1_pass else 'FAIL'} "
               f"(fail={h1_total_fail})")
    log.append(f"H2 (Im(eps)>=-{H2_TOL:.0e}) 全局: {'PASS' if h2_pass else 'FAIL'} "
               f"(fail={h2_total_fail})")
    log.append(f"L1 (等分关系) 全局: {'PASS' if l1_pass else 'FAIL'} (fail={l1_total_fail})")
    log.append("L2 完备性自查 (tex:L361 逐字判据):")
    log.extend(complet_lines)
    log.append(f"L2 完备性全局: {'PASS' if completeness_pass else 'FAIL'}")
    log.append("=" * 70)
    all_pass = h1_pass and h2_pass and l1_pass
    log.append(f"Layer1(硬约束) 全过: {'PASS' if all_pass else 'FAIL'}")
    log.append(f"Layer2(自洽+完备性) 全过: {'PASS' if (l1_pass and completeness_pass) else 'FAIL'}")
    log.append("=" * 70)

    out = "\n".join(log)
    print(out)
    # 注意: reproduction_test/ 是到 optics_agent/reproduction_test 的 filesystem junction,
    # __file__ 的 abspath 解析会落在 optics_agent 侧, 相对路径拼接 ../../../ 无法回到
    # self-evo-paper-repro 侧真实 case 目录 —— 这里改用写死绝对路径规避该 junction 陷阱。
    CASE_ROOT = r"C:\Users\27370\Desktop\project\self-evo-paper-repro\.work\.todo\2401.04146\0707-02-akimov-mie-v1"
    log_path = os.path.join(CASE_ROOT, "06-run_and_monitor", "fig6_layer1_verify.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write(out + "\n")
    print(f"\n[verify] 日志写入 {log_path}")
    # 同时在 reproduction_test/mie/data/ 下也存一份 (main-agent spawn prompt 要求的路径)
    data_path = os.path.join(DATA_DIR, "fig6_layer1_verify.txt")
    with open(data_path, "w", encoding="utf-8") as fh:
        fh.write(out + "\n")
    print(f"[verify] 日志同时写入 {data_path}")
    return all_pass, completeness_pass


if __name__ == "__main__":
    main()
