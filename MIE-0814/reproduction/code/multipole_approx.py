# -*- coding: utf-8 -*-
"""
multipole_approx.py — Alaee 表1 近似多极矩（常数核，长波长近似）
======================================================================
本文件是 mie-f 复现 step04 第三阶段：表1 长波长近似多极矩（ED/MD/EQ/MQ）。
表1 是表2 的 kr→0 极限——把球 Bessel 核 j_l/(kr)^l 换成其极限常数
（j_0→1, j_1/(kr)→1/3, j_2/(kr)²→1/15, j_3/(kr)³→1/105），积分核退化为
纯多项式（讲义 §10 完整推导 + §11 noteworthy）。

定位（repro-plan-v2.md §2.2 step04 阶段3）：
  - 复用 mie_theory.internal_E_field + multipole_moments 的体积分框架；
  - 表1 用于误差分析：面板(c) 的"近似曲线"= 表1，与 Mie/表2 对比，
    复现论文声称的"2a/λ≈0.75 处 ED/MD 误差 >100%"（Layer3 验证点）；
  - Layer2 验证：小 x 时表1 ≈ 表2（<1%）。

公式（Alaee 表1，讲义 §10，量纲自洽）：
    ED:  p_α ≈ −(1/iω){∫J_α + (k²/10)∫[(r·J)r_α − 2r²J_α]}
    MD:  m_α ≈ (1/2)∫(r×J)_α
    EQ:  Q^e_αβ ≈ −(1/iω){∫[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ]
                         + (k²/14)∫[4r_αr_β(r·J)−5r²(r_αJ_β+r_βJ_α)+2r²(r·J)δ_αβ]}
    MQ:  Q^m_αβ ≈ ∫{r_α(r×J)_β + r_β(r×J)_α}

无量纲化与 multipole_moments.py 完全一致（u=r/a, ρ=x_mie·u, J=(ε_r−1)E）：
  - j_0 → 1；j_1/(kr) → 1/3；j_2/(kr)² → 1/15；j_3/(kr)³ → 1/105（常数核）
  - 其余与表2 结构相同，仅核替换
"""
from __future__ import annotations

import numpy as np

from mie_theory import internal_E_field
from multipole_moments import _cartesian_position, _integrate_3d, _moments_grid


def table1_multipole_moments(x_mie: float, m: complex, n_max: int,
                             Nu: int = 40, Nth: int = 41, Nph: int = 80) -> dict:
    """表1 近似多极矩（常数核），无量纲（同 multipole_moments 约定）。

    返回与 table2_multipole_moments 同结构 dict（'p','m','Qe','Qm','grid','x_mie'）。
    核替换：j_0→1, j_1/(kr)→1/3, j_2/(kr)²→1/15, j_3/(kr)³→1/105。
    """
    Jx, Jy, Jz, U, Th, Ph, u, th, ph = _moments_grid(x_mie, m, n_max, Nu, Nth, Nph)
    rx, ry, rz = _cartesian_position(U, Th, Ph)
    rdotJ = rx * Jx + ry * Jy + rz * Jz
    Jcomp = [Jx, Jy, Jz]
    rcomps = [rx, ry, rz]

    # ---- ED（表1，常数核）----
    # p_α ∝ ∫[J_α + (k²/10)((r·J)r_α − 2r²J_α)]
    # 无量纲: (k²/10)(r·J)r_α → (x_mie²/10)(rdotJ)u_α；r²J_α → u²J_α·x_mie²/10
    p = np.zeros(3, dtype=complex)
    for idx, (rA, JA) in enumerate(zip(rcomps, Jcomp)):
        integrand = JA + (x_mie ** 2 / 10.0) * (rdotJ * rA - 2.0 * (U ** 2) * JA)
        p[idx] = _integrate_3d(integrand, u, th, ph)

    # ---- MD（表1，常数核 1/3）----
    # m_α ∝ (1/2)∫(r×J)_α  → 无量纲 (1/2)∫(u×J)_α
    cross_x = ry * Jz - rz * Jy
    cross_y = rz * Jx - rx * Jz
    cross_z = rx * Jy - ry * Jx
    m = np.zeros(3, dtype=complex)
    for idx, cr in enumerate([cross_x, cross_y, cross_z]):
        m[idx] = 0.5 * _integrate_3d(cr, u, th, ph)

    # ---- EQ（表1，常数核 1/3 + 1/105）----
    # Q^e_αβ ∝ ∫[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ] + (k²/14)∫[4r_αr_β(r·J)−5r²(r_αJ_β+r_βJ_α)+2r²(r·J)δ_αβ]
    Qe = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(3):
            rA, rB = rcomps[a], rcomps[b]
            JA, JB = Jcomp[a], Jcomp[b]
            delta = 1.0 if a == b else 0.0
            term1 = 3.0 * (rB * JA + rA * JB) - 2.0 * rdotJ * delta
            term2 = (
                4.0 * rA * rB * rdotJ
                - 5.0 * (U ** 2) * (rA * JB + rB * JA)
                + 2.0 * (U ** 2) * rdotJ * delta
            ) * (x_mie ** 2 / 14.0)
            Qe[a, b] = _integrate_3d(term1 + term2, u, th, ph)

    # ---- MQ（表1，常数核 1）----
    # Q^m_αβ ∝ ∫{r_α(r×J)_β + r_β(r×J)_α}
    crosses = [cross_x, cross_y, cross_z]
    Qm = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(3):
            Qm[a, b] = _integrate_3d(
                rcomps[a] * crosses[b] + rcomps[b] * crosses[a], u, th, ph)

    return {
        'p': p, 'm': m, 'Qe': Qe, 'Qm': Qm,
        'grid': (Nu, Nth, Nph),
        'x_mie': x_mie,
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    for x in [0.1, 0.5]:
        mom = table1_multipole_moments(x, 2.5, 7, 40, 40, 80)
        print(f'x={x}: p={mom["p"]}, |p|²={np.sum(np.abs(mom["p"])**2):.4f}')
