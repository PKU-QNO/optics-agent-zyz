# -*- coding: utf-8 -*-
"""
mie_theory.py — Lorenz-Mie 内部场（c_n/d_n 系数 + 球内 E(r) + 电流 J）
======================================================================
本文件是 mie-f 复现 step04 **第二阶段**：在 baseline_mie.py（独立 Mie 基准，
a_n/b_n 散射系数）基础上**只新增内部场部分**，不重复实现 a_n/b_n。

定位（repro-plan-v2.md §2.2 step04 阶段2）：
  - **复用 baseline_mie**：散射系数 a_n/b_n、截面、换算已由第一阶段验证，
    直接 `import`，不重写。
  - **新增内容**：内部场系数 c_n/d_n（B&H 4.53-4.54）→ 球内电场 E_in(r)
    （矢量球谐展开，正则 j_n）→ 电流密度 J = −iωε₀(ε_r−1)E。
    这是后续 multipole_moments.py（表2 精确多极矩体积分）的**前提**：
    表1/表2 全部从 J(r) 出发积分，J 必须由内部场 E 算对。

公式来源（formalization/alaee2018-fig1.yaml + notes/alaee2018-mie-coeff.md，gate③ 已对 B&H 原书核）：
  - c_n（B&H 4.53）：
        c_n = [m ψ_n(x) ξ'_n(x) − m ξ_n(x) ψ'_n(x)]
              / [ψ_n(mx) ξ'_n(x) − m ξ_n(x) ψ'_n(mx)]
    ⚠️ 分母 = b_n 分母（B&H 原文约束：c_n 分母与 b_n 相同）。
  - d_n（B&H 4.54）：
        d_n = [m ψ_n(x) ξ'_n(x) − m ξ_n(x) ψ'_n(x)]
              / [m ψ_n(mx) ξ'_n(x) − ξ_n(x) ψ'_n(mx)]
    ⚠️ 分母 = a_n 分母（B&H 原文约束：d_n 分母与 a_n 相同）。
    ⚠️ **分子两项都带 m**（与 c_n 分子相同，B&H 4.52 一般 μ 形式化简；
    见 notes/alaee2018-mie-coeff.md §4 自检注释「c_n/d_n 分子相同，两项都带 m」）。
    已用独立库 miepython（cn_dn）+ 球面切向边界条件双重验证：若分子第二项不带 m，
    d_n 与边界条件不符（见 step04 阶段2 调试记录）。
  - 内部场（B&H 4.53-4.54 展开 + 讲义 §2 L123-126，x 偏振 z 传播平面波 E0=1）：
        E_in(r) = Σ_n i^n (2n+1)/(n(n+1)) [ c_n M_o1n^(1)(k_in r) − i d_n N_e1n^(1)(k_in r) ]
    其中 k_in = k_0·m（球内波数），M/N 用正则 j_n。
  - 电流（spec J_omega，e^{−iωt} 约定）：
        J = −iω ε₀ (ε_r − 1) E_in
    对本任务 J 的绝对尺度不影响归一化 C_sca（会消去），相对相位/空间分布是关键，
    故本模块返回去掉公共常数因子 (−iωε₀) 的复振幅 j̃ = (ε_r−1)·E_in，
    物理 J = (−iωε₀)·j̃（见 internal_current_density 文档）。

实现纪律：
  - 复用 baseline_mie.mie_coefficients 返回的 a_n/b_n（以及分母中间量），
    c_n/d_n 的分母约束在 test 中数值验证；
  - 特殊函数一律 scipy.special（spherical_jn / spherical_yn / lpmv），不自写；
  - π/τ 角函数用标准 Mie 递推（B&H 4.47），已在验证中对照平面波展开到机器精度；
  - 时谐约定 e^{−iωt} 与 spec 一致。
"""
from __future__ import annotations

import numpy as np
from scipy.special import lpmv, spherical_jn, spherical_yn

from baseline_mie import mie_coefficients  # 复用第一阶段验证过的散射系数

# ---------------------------------------------------------------------------
# 材料常数（直接 import params，不重复定义；此处仅取内部场需要的）
# ---------------------------------------------------------------------------
from params import EPS_R, N_REFRACTIVE  # noqa: F401  # ε_r=6.25, n=2.5（文档性导入，见 __main__）


# ---------------------------------------------------------------------------
# Ricatti-Bessel 辅助（与 baseline_mie 相同的定义，此处为 c_n/d_n 分子所需）
# ---------------------------------------------------------------------------
def _riccati_psi(rho: np.ndarray) -> np.ndarray:
    """ψ_n(ρ) = ρ j_n(ρ)，n 取 1..len(rho)。"""
    return rho * spherical_jn(np.arange(1, len(rho) + 1), rho)


def _riccati_xi(rho: np.ndarray) -> np.ndarray:
    """ξ_n(ρ) = ρ h_n^(1)(ρ) = ρ (j_n + i y_n)。"""
    n = np.arange(1, len(rho) + 1)
    return rho * (spherical_jn(n, rho) + 1j * spherical_yn(n, rho))


def _dpsi(rho: np.ndarray) -> np.ndarray:
    """ψ'_n(ρ) = j_n(ρ) + ρ j'_n(ρ)（解析导数）。"""
    n = np.arange(1, len(rho) + 1)
    return spherical_jn(n, rho) + rho * spherical_jn(n, rho, derivative=True)


def _dxi(rho: np.ndarray) -> np.ndarray:
    """ξ'_n(ρ) = (j + i y) + ρ (j' + i y')（解析导数）。"""
    n = np.arange(1, len(rho) + 1)
    return (
        (spherical_jn(n, rho) + 1j * spherical_yn(n, rho))
        + rho * (spherical_jn(n, rho, derivative=True) + 1j * spherical_yn(n, rho, derivative=True))
    )


def internal_field_coefficients(x_mie: float, m: complex, n_max: int):
    """内部场系数 c_n, d_n（B&H 4.53/4.54）。

    参数
    ----
    x_mie : float
        B&H 尺寸参数 x = ka（host 波数 × 半径；换算见 params.size_param_to_x_mie）。
    m : complex
        相对折射率 m = n/n_d = √ε_r/√ε_d。
    n_max : int
        最大多极阶 n（从 1 到 n_max）。

    返回
    ----
    (c_n, d_n, denom_c, denom_d) : (np.ndarray, np.ndarray, np.ndarray, np.ndarray)
        c_n / d_n：长度 n_max 的复数数组（下标 0 对应 n=1）。
        denom_c / denom_d：对应分母，供 test 验证「c_n 分母 = b_n 分母、
        d_n 分母 = a_n 分母」的 B&H 约束（gate③ 硬性要求）。
    """
    n = np.arange(1, n_max + 1)
    z = m * x_mie  # 球内宗量（可能复）

    # -- 外/入射侧：实宗量 x（ξ 是 h^(1)，配合 e^{−iωt}） ----------------
    psi_x = _riccati_psi(np.full(n_max, x_mie))
    dpsi_x = _dpsi(np.full(n_max, x_mie))
    xi_x = _riccati_xi(np.full(n_max, x_mie))
    dxi_x = _dxi(np.full(n_max, x_mie))

    # -- 球内侧：复宗量 z ------------------------------------------------
    psi_z = _riccati_psi(np.full(n_max, z))
    dpsi_z = _dpsi(np.full(n_max, z))

    # -- c_n / d_n 分子与分母（B&H 4.53/4.54，gate③ 已核） -----------------
    # ⚠️ c_n 与 d_n 分子相同（两项都带 m）——已用 miepython + 边界条件双重验证
    #（notes §4 自检注释「c_n/d_n 分子相同，两项都带 m」；若 d 分子第二项不带 m 则违背切向连续）
    c_num = m * psi_x * dxi_x - m * xi_x * dpsi_x
    c_den = psi_z * dxi_x - m * xi_x * dpsi_z          # = b_n 分母（B&H 约束）
    d_num = m * psi_x * dxi_x - m * xi_x * dpsi_x      # 与 c_num 相同
    d_den = m * psi_z * dxi_x - xi_x * dpsi_z          # = a_n 分母（B&H 约束）

    c_n = c_num / c_den
    d_n = d_num / d_den
    return c_n, d_n, c_den, d_den


def _pi_tau(n_max: int, costh: np.ndarray):
    """π_n(cosθ)、τ_n(cosθ)（B&H 4.47 标准递推）。

    π_0=0, π_1=1；τ_n = n cosθ π_n − (n+1) π_{n−1}。
    返回形状 (n_max, Nθ) 的数组，行 0..n_max−1 对应 n=1..n_max。
    """
    costh = np.asarray(costh, dtype=float)
    pi = np.zeros((n_max + 1,) + costh.shape)
    tau = np.zeros((n_max + 1,) + costh.shape)
    pi[1] = 1.0
    for n in range(2, n_max + 1):
        pi[n] = (2 * n - 1) / (n - 1) * costh * pi[n - 1] - n / (n - 1) * pi[n - 2]
    for n in range(1, n_max + 1):
        tau[n] = n * costh * pi[n] - (n + 1) * pi[n - 1]
    return pi[1:], tau[1:]  # 下标 0..n_max-1 = n=1..n_max


def internal_E_field(x_mie: float, m: complex, n_max: int,
                     r_grid: np.ndarray, theta_grid: np.ndarray, phi_grid: np.ndarray):
    """球内电场 E_in(r) 的笛卡尔分量（x 偏振、z 传播平面波，E0=1，e^{−iωt}）。

    展开（B&H 4.53-4.54 系数 + 讲义 §2，已验证到机器精度）：
        E_in(r) = Σ_n i^n (2n+1)/(n(n+1)) [ c_n M_o1n^(1)(k_in r) − i d_n N_e1n^(1)(k_in r) ]
    其中 k_in = k_0·m（球内波数），M/N 用正则 j_n（矢量球谐定义见函数内注释，
    已对照平面波展开 x̂e^{ikz} = Σ i^n(2n+1)/(n(n+1))[M_o1n − i N_e1n] 数值验证）。

    参数
    ----
    x_mie : float
        B&H 尺寸参数 ka（实）。
    m : complex
        相对折射率（球内 ε_r 实 ⇒ m 实，但保持复数接口）。
    n_max : int
        最大多极阶。
    r_grid, theta_grid, phi_grid : np.ndarray
        **同形状**球坐标网格数组（r/θ/φ 同维度，逐点对应）。
        **r_grid 是归一化半径 u = r/a ∈ [0,1]**（无量纲）：球内电场只依赖
        球内宗量 ρ = k_in·r = m·k0·r = m·x_mie·(r/a)，与绝对 a 无关
        （spec geometry：半径是符号量，只出现无量纲 2a/λ）。调用方传
        u = r/a 即可（sphere_grid 已归一化）。

    返回
    ----
    (Ex, Ey, Ez) : (np.ndarray, np.ndarray, np.ndarray)
        球内电场笛卡尔分量复振幅（E0=1 归一化）。形状与输入网格相同。
    """
    r_grid = np.asarray(r_grid, dtype=float)
    theta_grid = np.asarray(theta_grid, dtype=float)
    phi_grid = np.asarray(phi_grid, dtype=float)
    shape = r_grid.shape
    u_flat = r_grid.ravel()  # 归一化半径 u = r/a ∈ [0,1]
    th_flat = theta_grid.ravel()
    ph_flat = phi_grid.ravel()
    n_pt = u_flat.size

    # 球内宗量 ρ = k_in·r = m·x_mie·u（k_in = m·k0，x_mie = k0·a ⇒ k_in·r = m·x_mie·u）
    rho = m * x_mie * u_flat

    # 安全宗量（r=0 处 ρ→0，矢量球谐除 ρ 项 0/0；用小量 eps 兜底保持连续）
    eps_r = 1e-12
    rho_safe = np.where(np.abs(rho) < eps_r, eps_r, rho)

    costh = np.clip(np.cos(th_flat), -1.0, 1.0)   # cosθ（θ 是极角，先取 cos 再裁剪）
    sinth = np.sqrt(np.maximum(0.0, 1.0 - costh ** 2))
    # φ 单位向量定义在 sinθ=0 处退化；取 x 偏振投影安全值
    cosph = np.where(sinth > 1e-12, np.cos(ph_flat), 1.0)
    sinph = np.where(sinth > 1e-12, np.sin(ph_flat), 0.0)

    pi_arr, tau_arr = _pi_tau(n_max, costh)  # 形状 (n_max, n_pt)

    Ex = np.zeros(n_pt, dtype=complex)
    Ey = np.zeros(n_pt, dtype=complex)
    Ez = np.zeros(n_pt, dtype=complex)

    c_n, d_n, _, _ = internal_field_coefficients(x_mie, m, n_max)

    # 预取各 n 的球 Bessel（按点循环避免 3D 索引开销；n_max 小，点量级 1e4 可接受）
    # 注意 spherical_jn 对复宗量数组按 (n, x) 广播：传 [:,None] 阶 × [None,:] 点
    n_idx = np.arange(1, n_max + 1)
    jn_rho = spherical_jn(n_idx[:, None], rho_safe[None, :])        # (n_max, n_pt)
    jn_drho = spherical_jn(n_idx[:, None], rho_safe[None, :], derivative=True)  # (n_max, n_pt)
    dpsi_rho = jn_rho + rho_safe[None, :] * jn_drho                 # ψ'(ρ) = j + ρ j'

    # 角因子（每点、每 n）：sinθ·π_n = P_n^1(cosθ)（径向需用此组合，θ→0 有限）
    sinth_pi = sinth[None, :] * pi_arr                  # (n_max, n_pt)
    cosph_ = cosph[None, :]                             # (1, n_pt)
    sinph_ = sinph[None, :]

    # 逐 n 累加（显式循环，n_max ≤ ~8，点 1e4 → 8 次向量化广播）
    for i in range(n_max):
        n = i + 1
        coef = (1j ** n) * (2 * n + 1) / (n * (n + 1))
        # 球坐标分量的复振幅（B&H 矢量球谐，m=1 实角结构 cosφ/sinφ）
        # M_o1n = [0, cosφ π j_n, −sinφ τ j_n]
        Mn_th = cosph_ * pi_arr[i] * jn_rho[i]
        Mn_ph = -sinph_ * tau_arr[i] * jn_rho[i]
        # N_e1n = [n(n+1) cosφ P_n^1 j_n/ρ, cosφ τ ψ'/ρ, −sinφ π ψ'/ρ]，P_n^1 = sinθ π_n
        # ⚠️ ρ 是逐点数组（形状 (1, n_pt)），不是标量：必须广播除 ρ，不能索引
        rho_b = rho_safe[None, :]
        Nn_r = n * (n + 1) * cosph_ * sinth_pi[i] * jn_rho[i] / rho_b
        Nn_th = cosph_ * tau_arr[i] * dpsi_rho[i] / rho_b
        Nn_ph = -sinph_ * pi_arr[i] * dpsi_rho[i] / rho_b

        # E_sph = coef·(c_n M − i d_n N)（球坐标分量，形状 (1, n_pt)）
        Er = coef * (0.0 - 1j * d_n[i] * Nn_r)
        Eth = coef * (c_n[i] * Mn_th - 1j * d_n[i] * Nn_th)
        Eph = coef * (c_n[i] * Mn_ph - 1j * d_n[i] * Nn_ph)

        # 球→笛卡尔（θ/φ 单位向量投影；sinth/costh 形状 (n_pt,) 扩到 (1, n_pt) 后全部一致）
        s_ = sinth[None, :]
        c_ = costh[None, :]
        Ex += (s_ * cosph_ * Er + c_ * cosph_ * Eth - sinph_ * Eph)[0]
        Ey += (s_ * sinph_ * Er + c_ * sinph_ * Eth + cosph_ * Eph)[0]
        Ez += (c_ * Er - s_ * Eth)[0]

    return Ex.reshape(shape), Ey.reshape(shape), Ez.reshape(shape)


def internal_current_density(x_mie: float, m: complex, n_max: int,
                             r_grid: np.ndarray, theta_grid: np.ndarray, phi_grid: np.ndarray):
    """球内电流密度 J = −iωε₀(ε_r−1)E_in 的笛卡尔复振幅。

    物理约定（spec J_omega，e^{−iωt}）：
        J = −iωε₀(ε_r−1) E_in
    其中 ω = k₀c = (x_mie/a)·c，ε₀ 真空介电常数。对 Fig.1(a) 复现，
    J 的**绝对尺度**在 C_sca 归一化（除 λ²/2π 与 |E_inc|²）中消去，只有
    **相对空间分布与相位**进入多极矩积分。因此本函数返回**去掉公共常数
    因子 (−iωε₀) 的复振幅** j̃ = (ε_r−1)·E_in：
        J = (−iωε₀)·j̃,    j̃ = (ε_r − 1)·E_in
    需要绝对电流时乘回 (−iωε₀) 即可（调用方按需）。

    参数/返回
    --------
    同 internal_E_field；返回 (Jx, Jy, Jz)（形状同网格）。
    """
    Ex, Ey, Ez = internal_E_field(x_mie, m, n_max, r_grid, theta_grid, phi_grid)
    # host=air 时 m=√ε_r ⇒ ε_r=m²。对吸收介质 m=n+iκ，
    # m·conj(m)=|m|² 仅是实数，会丢失 Im(ε_r) 并给出错误的极化电流。
    eps_r = complex(m) ** 2
    prefac = eps_r - 1.0
    return prefac * Ex, prefac * Ey, prefac * Ez


# ---------------------------------------------------------------------------
# 便捷接口：球内网格生成（供测试/后续 multipole_moments.py 使用）
# ---------------------------------------------------------------------------
def sphere_grid(n_r: int, n_theta: int, n_phi: int, a: float = 1.0):
    """球内均匀网格（r 方向含 r=0，θ/φ 用 Gauss-Legendre 避免端点）。

    返回 (r, theta, phi) 三个形状为 (n_r, n_theta, n_phi) 的网格数组，
    供 internal_E_field / internal_current_density 逐点使用。
    """
    from numpy.polynomial.legendre import leggauss
    # r: 均匀含 0（r=0 有矢量球谐极限处理）
    r = np.linspace(0.0, a, n_r)
    # θ: Gauss-Legendre 节点（0,π）避开奇异端点
    x_gl, _ = leggauss(n_theta)
    theta = np.arccos(x_gl)  # θ∈(0,π)
    # φ: 均匀含 0（周期方向）
    phi = np.linspace(0.0, 2.0 * np.pi, n_phi, endpoint=False)
    r3 = r[:, None, None] * np.ones((1, n_theta, n_phi))
    th3 = theta[None, :, None] * np.ones((n_r, 1, n_phi))
    ph3 = phi[None, None, :] * np.ones((n_r, n_theta, 1))
    return r3, th3, ph3


if __name__ == "__main__":
    # 快速自检：内部场在球内有限 + 电流复振幅有限
    a = 1.0
    r, th, ph = sphere_grid(40, 30, 60, a)
    for x_ in (np.pi * 0.5, np.pi * 0.385, np.pi * 0.647, np.pi * 0.543):
        Ex, Ey, Ez = internal_E_field(x_, 2.5, 6, r, th, ph)
        Jx, Jy, Jz = internal_current_density(x_, 2.5, 6, r, th, ph)
        print(f"x={x_:.4f}: E max|Ex|={np.max(np.abs(Ex)):.4f}  J max|Jx|={np.max(np.abs(Jx)):.4f}")
