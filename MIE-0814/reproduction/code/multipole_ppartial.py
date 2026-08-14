# -*- coding: utf-8 -*-
"""表2 ED 的中间形式（eq:p_partial, 讲义 §11）诊断实现。

动机（opus 2026-08-06）：表2 对称无迹形式 p_α=−(1/iω){∫J_α j_0+(k²/2)∫[3(r·J)r_α−r²J_α]j_2/(kr)²}
与中间形式 eq:p_partial 是**积分意义下的规范等价**（差分部积分边界项），逐点**不**等价。
修正坐标实现后，它用于检查与表2对称式的积分等价，而不再把二者差异预判为
缺失界面项。有限球内电流的分部积分必须连同紧支撑/界面分布项一起处理。

中间形式（讲义 §11 L96-99，逐点成立）：
    p_α = −(1/iω) ∫ [ J_α ( j_0(ρ) + j_2(ρ) ) − 3 (r·J) r_α j_2(ρ)/r² ] d³r
其中 ρ = k r（host 波数，自由空间多极展开的辐射波数；与表2 同一 k）。
本文件去公共因子 −(1/iω)，返回无量纲矩 ∝ ∫[...] dV。

r→0 极限：j_2(ρ)/r² = j_2(k r)/r² = k²·[j_2(ρ)/ρ²] → k²/15（用 j_2/ρ²→1/15）。
无量纲化 u=r/a、ρ=x_mie·u：j_2(ρ)/r² = (x_mie/a)²·j_2(ρ)/ρ²，去 a 幂次后
用 j_2(ρ)/ρ²（_LIMIT[2]=1/15 兜底 r=0），与表2 实现共享 _jl_over_rho_l。
"""
from __future__ import annotations
import numpy as np
from multipole_moments import (
    _cartesian_position,
    _integrate_3d,
    _jl_over_rho_l,
    _moments_grid,
    _radiation_rho,
    a_dot_b,
)


def table2_ED_ppartial(x_mie: float, m: complex, n_max: int,
                       Nu: int = 40, Nth: int = 41, Nph: int = 80,
                       kernel_k: str = 'host') -> np.ndarray:
    """表2 ED 中间形式逐点积分，返回无量纲 p 向量 (px,py,pz)（去 −1/iω 与 a 幂次）。

    p_α ∝ ∫ [ J_α (j_0(ρ)+j_2(ρ)) − 3 (u·J) u_α · j_2(ρ)/u_无量纲² · ... ]
    无量纲：r_α = a·u_α，(r·J)r_α j_2/r² = a²(u·J)u_α · j_2/(a²u²)·...
    注意 j_2(ρ)/r² 的 r² 是物理 r²=(a u)²，故 j_2(ρ)/r² = j_2(ρ)/(a u)²。
    去 a 幂次后与表2 ED 第二项共享同一 j_2/ρ² 核（ρ=x_mie·u）。
    """
    Jx, Jy, Jz, U, Th, Ph, u, th, ph = _moments_grid(
        x_mie, m, n_max, Nu, Nth, Nph)

    rho = _radiation_rho(x_mie, U, m, kernel_k)
    j0 = _jl_over_rho_l(0, rho)          # j_0(ρ)（l=0 → j_0 本身，极限1）
    j2 = __import__('scipy.special', fromlist=['spherical_jn']).spherical_jn(2, rho)
    j2o2 = _jl_over_rho_l(2, rho)        # j_2(ρ)/ρ²（极限 1/15）

    rx, ry, rz = _cartesian_position(U, Th, Ph)
    rdotJ = a_dot_b(rx, ry, rz, Jx, Jy, Jz)

    # 中间形式被积函数：J_α(j_0+j_2) − 3(u·J)u_α · [j_2(ρ)/u²]
    # j_2(ρ)/u² = x_mie²·j_2(ρ)/ρ²  = x_mie²·j2o2（因 ρ=x_mie·u ⇒ ρ²=x_mie²u²）
    j2_over_u2 = (x_mie ** 2) * j2o2
    p = np.zeros(3, dtype=complex)
    for idx, (rA, JA) in enumerate(zip([rx, ry, rz], [Jx, Jy, Jz])):
        integrand = JA * (j0 + j2) - 3.0 * rdotJ * rA * j2_over_u2
        p[idx] = _integrate_3d(integrand, u, th, ph)
    return p


if __name__ == '__main__':
    from baseline_mie import mie_coefficients
    M, NMAX = 2.5, 7
    # 标定 K：在 x=0.2（准静态，中间形式=Mie）定 ED 常数，再测全 x 是否恒定
    def mie_ED(x):
        an, _ = mie_coefficients(x, M, NMAX)
        return 3.0 * abs(an[0]) ** 2
    # ED 矩幂次：C_ED ∝ x^6·|p|²（代码现有 POW）。先标定再扫。
    x_ref = np.pi * 0.2
    p_ref = table2_ED_ppartial(x_ref, M, NMAX)
    K0 = mie_ED(x_ref) / (x_ref ** 6 * np.sum(np.abs(p_ref) ** 2))
    print(f"K0(x=0.2) = {K0:.4e}")
    print(f"{'2a/l':>6} {'x_mie':>6} {'Mie_ED':>10} {'ppart_ED':>10} {'ratio':>8}")
    for s in [0.2, 0.3, 0.385, 0.5, 0.6, 0.65, 0.7, 0.8, 1.0]:
        x = np.pi * s
        p = table2_ED_ppartial(x, M, NMAX)
        C = K0 * x ** 6 * np.sum(np.abs(p) ** 2)
        r = C / mie_ED(x)
        print(f"{s:6.3f} {x:6.3f} {mie_ED(x):10.4f} {C:10.4f} {r:8.3f}")
    print("注意：ratio 不恒≈1（大 x 处严重偏离）=> 逐点 eq:p_partial 中间形式与表2 对称无迹形式"
          "并不逐点等价（有限球内体函数缺界面/表面项）。该文件是诊断路径，不用于生产；"
          "生产实现用表2 对称无迹体积分（multipole_moments.py）。")
