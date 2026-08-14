# -*- coding: utf-8 -*-
"""
baseline_mie.py — 独立最小 Lorenz-Mie 基准（Layer1 物理约束锚点）
====================================================================
本文件是 mie-f 复现 step04 第一阶段的 **独立 Mie 基准**：
直接用 scipy.special 直算 a_n / b_n 系数与散射截面，**不依赖本仓库任何其他模块**
（唯一例外是可选 import 本仓库 params.py 取常数/换算，见模块尾部注释）。

用途（repro-plan-v2.md §2 / WORK_LOG 2026-08-03 设计修正）：
  - 作为 Layer1 物理约束的锚点，证明后续 verifier 脚本（表1/表2 多极矩近似）
    自身正确 —— 防"自己验证自己"。
  - 复现对象：Alaee 2018 Fig.1(a)，介电球（ε_r=6.25, n=2.5）散射截面 vs 尺寸参数
    2a/λ∈[0.2,1.0]。host=air。

公式（Bohren & Huffman Ch.4，Mie 系数 4.56/4.57）：
    x  = ka                                  （B&H 尺寸参数）
    m  = √ε_r / √ε_d                          （相对折射率；host=air 时 m = n = 2.5）
    ψ_n(ρ) = ρ j_n(ρ),   ξ_n(ρ) = ρ h_n^(1)(ρ) = ρ (j_n + i y_n)   （Ricatti-Bessel）
    ψ'_n(ρ) = j_n(ρ) + ρ j'_n(ρ)             （解析导数，避免数值差分）
    ξ'_n(ρ) = (j_n + i y_n) + ρ (j'_n + i y'_n)

    a_n（电多极/TM，B&H 4.56）：
        [m ψ_n(mx) ψ'_n(x) − ψ_n(x) ψ'_n(mx)] / [m ψ_n(mx) ξ'_n(x) − ξ_n(x) ψ'_n(mx)]
    b_n（磁多极/TE，B&H 4.57）：
        [ψ_n(mx) ψ'_n(x) − m ψ_n(x) ψ'_n(mx)] / [ψ_n(mx) ξ'_n(x) − m ξ_n(x) ψ'_n(mx)]

截面（B&H 4.61-4.62 略去入射幅度因子）：
    C_sca = (2π/k²) Σ_n (2n+1)(|a_n|²+|b_n|²)
    C_ext = (2π/k²) Σ_n (2n+1) Re(a_n+b_n)
    C_abs = C_ext − C_sca

⚠️ 常数因子选择（重要，见 cross_sections 注释）：
    本实现返回**无量纲** C_sca/C_ext（去掉 2π/k² 常数因子）。理由：
      1. Layer1 物理约束（能量守恒 C_ext=C_sca+C_abs、无吸收 C_abs=0、
         瑞利 Q_sca∝x⁴、大 x Q_ext→2、光学定理无吸收等价式）**均与 k 无关**
         —— 因为 C_ext 与 C_sca 共享同一 2π/k² 因子，相减即消去；
      2. 最终论文曲线一律除以 λ²/2π 归一化（Alaee Eq.1 caption），a、λ 均在
         归一化中消去；
      3. 效率因子 Q = C/(πa²) 会用显式 k 表达（Q_sca = C_sca·k²/(π)），
         见 Q_sca。
    若未来 Layer3 需要绝对截面（物理量纲 C），乘回 (2π/k²) 即可。

实现纪律：
  - 特殊函数一律用 scipy.special.spherical_jn / spherical_yn（含 derivative=True），
    不自写 j_n/y_n；
  - ψ/ξ 导数用解析组合（见上），不数值差分；
  - m·x 是复宗量，numpy/scipy 全向量化支持。
"""
from __future__ import annotations

import numpy as np
from scipy.special import spherical_jn, spherical_yn


def mie_coefficients(x_mie: float, m: complex, n_max: int):
    """Lorenz-Mie 散射系数 a_n, b_n（B&H 4.56/4.57）。

    参数
    ----
    x_mie : float
        B&H 尺寸参数 x = ka（host 波数 × 半径；注意不是 Alaee 横轴 2a/λ，
        换算见 params.size_param_to_x_mie）。
    m : complex
        相对折射率 m = n/n_d = √ε_r/√ε_d。可带虚部（吸收介质）。
    n_max : int
        最大多极阶 n（从 1 到 n_max）。

    返回
    ----
    (a_n, b_n) : (np.ndarray, np.ndarray)
        长度 n_max 的复数数组，下标 0 对应 n=1。a_n=电多极/TM，b_n=磁多极/TE
        （B&H 约定，与 formalization spec observables.per_multipole 一致）。
    """
    n = np.arange(1, n_max + 1)  # 多极阶 1..n_max

    # 宗量：x 为实数（host 无吸收），m*x 为（可能）复宗量（球内）
    z = m * x_mie

    # -- 外/入射侧：实宗量 x ----------------------------------------------
    j_x = spherical_jn(n, x_mie)
    j_x_d = spherical_jn(n, x_mie, derivative=True)
    y_x = spherical_yn(n, x_mie)
    y_x_d = spherical_yn(n, x_mie, derivative=True)

    # -- 球内侧：复宗量 z ------------------------------------------------
    j_z = spherical_jn(n, z)
    j_z_d = spherical_jn(n, z, derivative=True)
    y_z = spherical_yn(n, z)
    y_z_d = spherical_yn(n, z, derivative=True)

    # -- Ricatti-Bessel 函数及其解析导数 ----------------------------------
    # ψ(ρ) = ρ j(ρ)；ψ'(ρ) = j(ρ) + ρ j'(ρ)
    psi_x = x_mie * j_x
    psi_x_d = j_x + x_mie * j_x_d
    psi_z = z * j_z
    psi_z_d = j_z + z * j_z_d

    # ξ(ρ) = ρ (j + i y)；ξ'(ρ) = (j + i y) + ρ (j' + i y')
    xi_x = x_mie * (j_x + 1j * y_x)
    xi_x_d = (j_x + 1j * y_x) + x_mie * (j_x_d + 1j * y_x_d)

    # -- Mie 系数（B&H 4.56/4.57）-----------------------------------------
    # 电多极 / TM
    a_num = m * psi_z * psi_x_d - psi_x * psi_z_d
    a_den = m * psi_z * xi_x_d - xi_x * psi_z_d
    # 磁多极 / TE
    b_num = psi_z * psi_x_d - m * psi_x * psi_z_d
    b_den = psi_z * xi_x_d - m * xi_x * psi_z_d

    a_n = a_num / a_den
    b_n = b_num / b_den
    return a_n, b_n


def _multipole_weights(n_max: int) -> np.ndarray:
    """退化权重 w_n = 2n+1（n=1..n_max），用于截面求和。"""
    return 2.0 * np.arange(1, n_max + 1) + 1.0


def cross_sections(x_mie: float, m: complex, n_max: int | None = None):
    """散射/消光/吸收截面（**无量纲**，去掉 2π/k² 常数因子）。

    参数
    ----
    x_mie : float
        B&H 尺寸参数 ka。
    m : complex
        相对折射率。
    n_max : int | None
        截断阶。None 时用 Wiscombe 截断 n_max = ceil(x + 4x^(1/3) + 2)
        （formalization spec 截断标准）。

    返回
    ----
    (C_sca, C_ext, C_abs) : (float, float, float)
        无量纲截面。其中
            C_sca = Σ_n (2n+1)(|a_n|²+|b_n|²)
            C_ext = Σ_n (2n+1) Re(a_n+b_n)
            C_abs = C_ext − C_sca
        ⚠️ 未乘 (2π/k²) 常数因子 —— 对 Layer1 约束无影响（C_ext 与 C_sca 共享
        同因子，C_abs=C_ext−C_sca 自动消去；效率因子用显式 k，见 Q_sca）。
        需要物理量纲截面时乘回 (2π/k²) 即可。
    """
    if n_max is None:
        n_max = wiscombe_nmax(x_mie)
    a_n, b_n = mie_coefficients(x_mie, m, n_max)
    w = _multipole_weights(n_max)

    c_sca = float(np.sum(w * (np.abs(a_n) ** 2 + np.abs(b_n) ** 2)))
    c_ext = float(np.sum(w * np.real(a_n + b_n)))
    c_abs = c_ext - c_sca
    return c_sca, c_ext, c_abs


def c_sca_per_multipole(x_mie: float, m: complex, n_max: int | None = None) -> np.ndarray:
    """逐多极阶的 C_sca 贡献数组（每个 n 一项）。

    定义（无量纲，同 cross_sections 约定）：
        C_sca_n = (2n+1)(|a_n|²+|b_n|²)，n=1..n_max
    注意：未乘 2π/k² 常数因子（理由同 cross_sections）。

    对 per-multipole 论文曲线（Alaee Fig.1(a) ED/MD/EQ/MQ），只需取 l=1,2：
        ED = C_sca_n[0]   （a_n, n=1, 电多极/TM）
        MD = C_sca_n[1]   （b_n, n=1, 磁多极/TE）
        EQ = C_sca_n[2]   （a_n, n=2）
        MQ = C_sca_n[3]   （b_n, n=2）
    （formalization spec observables.per_multipole；gate② 修正勿再写反。）
    注意 ED/MD 是 C_sca_n 的「同阶两项之和」，逐极分解到单偏振需取 a 或 b 单项；
    论文 Fig.1(a) 逐多极曲线按 a_n/b_n 单项拆，这里返回同阶两项和，供总截面
    逐阶剖分使用；单偏振曲线由调用方按 a_n/b_n 拆分。

    参数/返回
    --------
    同 mie_coefficients；返回长度 n_max 的浮点数组。
    """
    if n_max is None:
        n_max = wiscombe_nmax(x_mie)
    a_n, b_n = mie_coefficients(x_mie, m, n_max)
    w = _multipole_weights(n_max)
    return w * (np.abs(a_n) ** 2 + np.abs(b_n) ** 2)


def Q_sca(x_mie: float, m: complex, n_max: int | None = None) -> float:
    """散射效率因子 Q_sca = C_sca/(πa²)（无量纲，物理标准定义）。

    推导：C_sca(物理量纲) = (2π/k²) Σ(2n+1)(|a|²+|b|²)。
    本模块无量纲 C_sca' = Σ(2n+1)(|a|²+|b|²)，故
        Q_sca = C_sca/(πa²) = (2π/k²)·C_sca'/(πa²) = (2/k²a²)·C_sca'
              = (2/x_mie²)·C_sca'
    等价于 Q_sca = C_sca' · k²/(2π)·...   —— 直接写 2/x² 即可（k·a = x_mie）。

    用途：瑞利极限验证（小 x 时 Q_sca ∝ x⁴，log-log 斜率=4）；大 x 消光上限
    Q_ext→2（需另算 Q_ext = 2/x²·C_ext'）。

    参数/返回
    --------
    同 cross_sections；返回 float。
    """
    if n_max is None:
        n_max = wiscombe_nmax(x_mie)
    a_n, b_n = mie_coefficients(x_mie, m, n_max)
    w = _multipole_weights(n_max)
    c_sca_dimless = float(np.sum(w * (np.abs(a_n) ** 2 + np.abs(b_n) ** 2)))
    return 2.0 / x_mie ** 2 * c_sca_dimless


def Q_ext(x_mie: float, m: complex, n_max: int | None = None) -> float:
    """消光效率因子 Q_ext = C_ext/(πa²) = 2/x² · C_ext'（无量纲 C_ext'）。"""
    if n_max is None:
        n_max = wiscombe_nmax(x_mie)
    a_n, b_n = mie_coefficients(x_mie, m, n_max)
    w = _multipole_weights(n_max)
    c_ext_dimless = float(np.sum(w * np.real(a_n + b_n)))
    return 2.0 / x_mie ** 2 * c_ext_dimless


# 与仓库其余部分解耦：本文件自包含 Wiscombe 截断（不强制 import params.py）。
# 若上层想用 params.py 的换算/截断，可自行 import；本文件保持独立可跑。
def wiscombe_nmax(x_mie: float) -> int:
    """Wiscombe 截断：n_max = ceil(x + 4x^(1/3) + 2)。"""
    return int(np.ceil(x_mie + 4.0 * x_mie ** (1.0 / 3.0) + 2.0))


if __name__ == "__main__":
    # 快速自检：n=2.5 无吸收介电球，能量守恒 + 瑞利斜率
    for x in (0.5, 1.0, 2.0):
        csca, cext, cabs = cross_sections(x, 2.5)
        print(f"x={x}: C_sca={csca:.6e} C_ext={cext:.6e} C_abs={cabs:.3e}")
