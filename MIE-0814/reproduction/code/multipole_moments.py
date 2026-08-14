# -*- coding: utf-8 -*-
"""
multipole_moments.py — Alaee 表2 精确多极矩（球 Bessel 核体积分）
======================================================================
本文件是 mie-f 复现 step04 第三阶段：从内部场 J(r) = (ε_r−1)·E_in(r)
（去掉公共常数因子 −iωε₀）做球坐标体积分，计算表2 精确多极矩
ED/MD/EQ/MQ（讲义 §11 + formalization spec，gate② 已核）。

定位（repro-plan-v2.md §2.2 step04 阶段3）：
  - 复用 mie_theory.internal_E_field（已验证到机器精度：m→1 极限 1.7e-08、
    miepython 交叉 6e-10、中心场准静态 0.367≈0.364）。
  - 本文件只做「内部场 → 多极矩 → 逐多极 C_sca」的体积分，不重复实现场。
  - 表2 是精确多极矩（球 Bessel 核 j_l/(kr)^l），表1（multipole_approx.py）
    是其 kr→0 极限（常数核）。Layer2 验证：小 x 时两者一致 <1%。

公式（Alaee 表2，讲义 §11，量纲自洽）：
    J(r) = −iωε₀(ε_r−1) E_in(r)     →  本文件用 j̃ = (ε_r−1)E_in（去 −iωε₀ 因子）
    ED:  p_α = −(1/iω){∫J_α j_0(kr) + (k²/2)∫[3(r·J)r_α − r²J_α] j_2/(kr)²}
    MD:  m_α = (3/2)∫(r×J)_α j_1/(kr)
    EQ:  Q^e_αβ = −(3/iω){∫[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ] j_1/(kr)
                           + 2k²∫[5r_αr_β(r·J)−(r_αJ_β+r_βJ_α)r²−r²(r·J)δ_αβ] j_3/(kr)³}
    MQ:  Q^m_αβ = 15∫{r_α(r×J)_β + r_β(r×J)_α} j_2/(kr)²

无量纲化（关键，避免 a 具体值）：
    归一化半径 u = r/a ∈ [0,1]。球内宗量 ρ = k·r = (k·a)·u = x_mie·u
    （k 是 host 波数，k·a = x_mie）。j_l(kr) = j_l(x_mie·u)。
    多极矩中的 r 分量：r_α = a·u_α。k² 因子：k² = (x_mie/a)²。
    注意多极矩的绝对尺度含 a 幂次，但 C_sca 归一化到 λ²/2π 后 a 消去。
    本实现返回「无量纲多极矩」（去掉 a 幂次与 1/iω 等公共因子），
    C_sca 用相对形式算（见 c_sca_from_multipoles），只依赖无量纲组合。

实现纪律：
  - 特殊函数 scipy.special.spherical_jn，不自写；
  - r→0 处 j_l/(kr)^l 用极限值 1/(2l+1)!!（l=0:1, l=1:1/3, l=2:1/15, l=3:1/105）；
  - 球坐标体积分：dV = u² sinθ du dθ dφ，u∈[0,1], θ∈[0,π], φ∈[0,2π]；
  - φ 方向利用 x 偏振入射的 m=±1 对称性（可全数值先跑通，性能后续优化）；
  - 积分器：scipy.integrate.simpson 或逐维 trapezoid（高维网格直接求和 + 权重）。
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import simpson
from scipy.special import spherical_jn

from mie_theory import internal_E_field, sphere_grid


# ---------------------------------------------------------------------------
# r→0 极限值 j_l(ρ)/ρ^l → 1/(2l+1)!!  (防除零，G1)
# ---------------------------------------------------------------------------
_LIMIT = {0: 1.0, 1: 1.0 / 3.0, 2: 1.0 / 15.0, 3: 1.0 / 105.0}


def _jl_over_rho_l(l: int, rho: np.ndarray) -> np.ndarray:
    """j_l(ρ)/ρ^l，r→0 用极限值 1/(2l+1)!!。

    参数
    ----
    l : int
        球 Bessel 阶（0..3）。
    rho : np.ndarray
        宗量 ρ = x_mie·u（可含 0）。
    """
    rho = np.asarray(rho)
    out = np.empty(rho.shape, dtype=np.result_type(rho.dtype, np.float64))
    small = np.abs(rho) < 1e-12
    if np.any(small):
        out[small] = _LIMIT[l]
    big = ~small
    if np.any(big):
        r = rho[big]
        out[big] = spherical_jn(l, r) / r ** l
    return out


def _integrate_3d(f: np.ndarray, u: np.ndarray, th: np.ndarray, ph: np.ndarray) -> complex:
    """球坐标三重积分 ∫ f(u,θ,φ) u² sinθ du dθ dφ。

    多极矩是复数（J 复），积分结果保持复数（不 cast 成 float）。

    参数
    ----
    f : np.ndarray, 形状 (Nu, Nth, Nph)
    u, th, ph : 一维网格节点（等距）
    """
    Nu, Nth, Nph = f.shape
    # 权重 w = u² sinθ
    w = u[:, None, None] ** 2 * np.sin(th)[None, :, None]
    integrand = np.asarray(f, dtype=complex) * w
    # φ 是不含重复端点的均匀周期网格；周期求和对本问题的有限 Fourier
    # 模式是高精度求积。u、θ 使用 Simpson，避免共振附近相消后的小残差
    # 被低阶梯形误差放大。
    if Nph > 1:
        dph = ph[1] - ph[0]
        period = (ph[-1] - ph[0]) + dph
        if np.isclose(period, 2.0 * np.pi, rtol=1e-10, atol=1e-12):
            integrand = integrand.sum(axis=-1) * dph
        else:
            integrand = simpson(integrand, x=ph, axis=-1)
    else:
        integrand = integrand[..., 0] * (2 * np.pi)
    if Nth > 1:
        integrand = simpson(integrand, x=th, axis=-1)
    else:
        integrand = integrand[:, 0] * np.pi
    if Nu > 1:
        integrand = simpson(integrand, x=u, axis=0)
    else:
        integrand = integrand[0] * 1.0
    return complex(integrand)


def _cartesian_position(U: np.ndarray, Th: np.ndarray, Ph: np.ndarray):
    """返回无量纲位置 r/a 的笛卡尔分量，而不是纯方向余弦。"""
    sinth = np.sin(Th)
    return (
        U * sinth * np.cos(Ph),
        U * sinth * np.sin(Ph),
        U * np.cos(Th),
    )


def _radiation_rho(x_mie: float, U: np.ndarray, m: complex,
                   kernel_k: str = 'host') -> np.ndarray:
    """返回球 Bessel 辐射核宗量。

    ``host`` 是表2的物理路径：rho = k_host r = x_mie U。``internal``
    只用于回归诊断错误假设 rho = k_in r = m x_mie U；内部波数本来已经
    通过 ``internal_E_field`` 决定 J(r) 的空间结构。
    """
    if kernel_k == 'host':
        return x_mie * U
    if kernel_k == 'internal':
        return (m * x_mie) * U
    raise ValueError("kernel_k must be 'host' or 'internal'")


def _moments_grid(x_mie: float, m: complex, n_max: int,
                  Nu: int = 60, Nth: int = 60, Nph: int = 120):
    """构造网格并返回 (J_x, J_y, J_z, u_mesh, th_mesh, ph_mesh, u, th, ph)。

    J = (ε_r−1)·E_in（去掉 −iωε₀ 公共因子）。ε_r = m²（host=air）。
    """
    eps_r = m * m  # ε_r = m² (host=air, ε_d=1)
    u = np.linspace(1e-6, 1.0, Nu)
    th = np.linspace(1e-6, np.pi - 1e-6, Nth)
    ph = np.linspace(0.0, 2 * np.pi, Nph, endpoint=False)
    # meshgrid (ij)：R[u,th,ph]
    U, Th, Ph = np.meshgrid(u, th, ph, indexing='ij')
    Ex, Ey, Ez = internal_E_field(x_mie, m, n_max, U, Th, Ph)
    factor = (eps_r - 1.0)
    Jx = factor * Ex
    Jy = factor * Ey
    Jz = factor * Ez
    return Jx, Jy, Jz, U, Th, Ph, u, th, ph


def table2_multipole_moments(x_mie: float, m: complex, n_max: int,
                             Nu: int = 40, Nth: int = 41, Nph: int = 80,
                             kernel_k: str = 'host') -> dict:
    """表2 精确多极矩（ED/MD/EQ/MQ），无量纲（去 a 幂次与 1/iω 公共因子）。

    返回
    ----
    dict:
        'p': ED 电偶极复数向量 (px, py, pz)
        'm': MD 磁偶极复数向量 (mx, my, mz)
        'Qe': EQ 电四极复数张量 (3×3 对称无迹)
        'Qm': MQ 磁四极复数张量 (3×3)
        'grid': 网格参数 (Nu, Nth, Nph) 供收敛测试
    """
    Jx, Jy, Jz, U, Th, Ph, u, th, ph = _moments_grid(x_mie, m, n_max, Nu, Nth, Nph)
    rho = _radiation_rho(x_mie, U, m, kernel_k)

    # 无量纲位置的笛卡尔分量 r_α/a = U·方向余弦。旧实现漏乘 U，
    # 将位置误写成单位方向向量，破坏了大 x 时各径向项之间的相消。
    rx, ry, rz = _cartesian_position(U, Th, Ph)

    # 电流点积 r·J 与 r²J 的无量纲形式（r→a·u）
    rdotJ = a_dot_b(rx, ry, rz, Jx, Jy, Jz)

    # ---- ED 电偶极（表2）----
    # p_α ∝ ∫[J_α j_0 + (k²/2)(3(r·J)r_α − r²J_α) j_2/(kr)²]
    # 无量纲化：k²r² = x_mie²u², k²r_α = x_mie² u_α/a
    # p_α(无量纲) = ∫[J_α j_0(ρ) + (x_mie²/2)(3(rdotJ)u_α − u²J_α) j_2(ρ)/ρ²] dV
    j0 = _jl_over_rho_l(0, rho)
    j2o2 = _jl_over_rho_l(2, rho)
    p = np.zeros(3, dtype=complex)
    Jcomp = [Jx, Jy, Jz]
    for idx, (rA, JA) in enumerate(zip([rx, ry, rz], Jcomp)):
        integrand = JA * j0 + (x_mie ** 2 / 2.0) * (
            3.0 * rdotJ * rA - (U ** 2) * JA
        ) * j2o2
        p[idx] = _integrate_3d(integrand, u, th, ph)
    # 注：表2 ED 前置 −(1/iω)；本实现去该因子，见 c_sca_from_multipoles 说明

    # ---- MD 磁偶极（表2）----
    # m_α = (3/2)∫(r×J)_α j_1(ρ)/ρ
    # (r×J)_α 无量纲 = a·(u×J)_α；m 无量纲 = (3/2)∫(u×J)_α j_1/ρ dV
    j1o1 = _jl_over_rho_l(1, rho)
    cross_x = ry * Jz - rz * Jy
    cross_y = rz * Jx - rx * Jz
    cross_z = rx * Jy - ry * Jx
    m = np.zeros(3, dtype=complex)
    for idx, cr in enumerate([cross_x, cross_y, cross_z]):
        m[idx] = (3.0 / 2.0) * _integrate_3d(cr * j1o1, u, th, ph)
    # 表2 MD 前置 3/2（退化：3/2·(j_1/kr→1/3) = 1/2 = 表1 MD 前置，讲义 §11）

    # ---- EQ 电四极（表2）----
    # Q^e_αβ ∝ ∫{[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ] j_1/ρ
    #            + 2k²[5r_αr_β(r·J)−(r_αJ_β+r_βJ_α)r²−r²(r·J)δ_αβ] j_3/ρ³}
    j3o3 = _jl_over_rho_l(3, rho)
    Qe = np.zeros((3, 3), dtype=complex)
    comps = [rx, ry, rz]
    for a in range(3):
        for b in range(3):
            uA, uB = comps[a], comps[b]
            JA, JB = Jcomp[a], Jcomp[b]
            term1 = 3.0 * (uB * JA + uA * JB) - 2.0 * rdotJ * (1.0 if a == b else 0.0)
            term1 *= j1o1
            term2 = (
                5.0 * uA * uB * rdotJ
                - (uA * JB + uB * JA) * (U ** 2)
                - (U ** 2) * rdotJ * (1.0 if a == b else 0.0)
            )
            term2 *= (2.0 * x_mie ** 2) * j3o3
            Qe[a, b] = 3.0 * _integrate_3d(term1 + term2, u, th, ph)
    # 表2 EQ 前置 −(3/iω)（主项系数 3；退化：3·(j_1/kr→1/3) = 1 = 表1 EQ 前置，讲义 §11）

    # ---- MQ 磁四极（表2）----
    # Q^m_αβ ∝ ∫{r_α(r×J)_β + r_β(r×J)_α} j_2/ρ²
    j2sq = _jl_over_rho_l(2, rho)  # j_2/ρ²
    crosses = [cross_x, cross_y, cross_z]
    Qm = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(3):
            integrand = (comps[a] * crosses[b] + comps[b] * crosses[a]) * j2sq
            Qm[a, b] = 15.0 * _integrate_3d(integrand, u, th, ph)
    # 表2 MQ 前置 15（退化：15·(j_2/kr²→1/15) = 1 = 表1 MQ 前置，讲义 §11）

    return {
        'p': p, 'm': m, 'Qe': Qe, 'Qm': Qm,
        'grid': (Nu, Nth, Nph),
        'x_mie': x_mie,
        'kernel_k': kernel_k,
    }


def a_dot_b(ax, ay, az, bx, by, bz):
    """向量点积（逐网格）。"""
    return ax * bx + ay * by + az * bz


def c_sca_from_multipoles(moments: dict, x_mie: float) -> dict:
    """按 Alaee Eq.1 解析常数计算逐多极无量纲散射截面。

    当前矩使用 ``J_tilde=(eps_r-1)E``、``a=1``，并已吸收表2/表1各自
    的矩定义前置系数。把 ``J=-i omega eps0 J_tilde`` 代回 Eq.1，再除以
    ``lambda^2/(2 pi)``，得到下列不含经验标定的解析式：

    ED = x^6/(12 pi^2) |p|^2;  MD = x^8/(12 pi^2) |m|^2;
    EQ = x^8/(1440 pi^2) |Qe|^2; MQ = x^10/(1440 pi^2) |Qm|^2.

    返回 dict: {'ED','MD','EQ','MQ'} 各自的无量纲 C_sca 分项。
    """
    p = moments['p']
    mm = moments['m']
    Qe = moments['Qe']
    Qm = moments['Qm']
    x = x_mie
    dipole_prefactor = 1.0 / (12.0 * np.pi ** 2)
    quadrupole_prefactor = 1.0 / (1440.0 * np.pi ** 2)
    C_ed = dipole_prefactor * x ** 6 * float(np.sum(np.abs(p) ** 2))
    C_md = dipole_prefactor * x ** 8 * float(np.sum(np.abs(mm) ** 2))
    C_eq = quadrupole_prefactor * x ** 8 * float(np.sum(np.abs(Qe) ** 2))
    C_mq = quadrupole_prefactor * x ** 10 * float(np.sum(np.abs(Qm) ** 2))
    return {'ED': C_ed, 'MD': C_md, 'EQ': C_eq, 'MQ': C_mq}


if __name__ == '__main__':
    # 快速自检：小 x 准静态 ED 应主导
    import sys
    sys.path.insert(0, '.')
    for x in [0.5, 1.0]:
        mom = table2_multipole_moments(x, 2.5, 7, 40, 40, 80)
        C = c_sca_from_multipoles(mom, x)
        print(f'x={x}: C_sca per multipole = {C}')
