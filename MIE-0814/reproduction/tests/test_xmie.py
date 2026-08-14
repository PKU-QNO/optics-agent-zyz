# -*- coding: utf-8 -*-
"""
test_xmie.py — 内部场/电流密度测试（step04 阶段2，TDD）
====================================================================
测试对象：code/mie_theory.py（内部场系数 c_n/d_n + 球内 E(r) + 电流 J）。
依赖：code/baseline_mie.py（复用已验证的 a_n/b_n）、code/params.py（换算）。

覆盖内容（formalization/alaee2018-fig1.yaml §solver.strategy 步骤2 + step04 阶段2）：
  1. test_xmie_conversion — size_param_to_x_mie 换算（2a/λ → x_mie = π·(2a/λ)）
  2. test_xmie_peak_anchors — Mie 共振峰位锚点（step04 实测 2026-08-05）
     ED a_1 峰 2a/λ≈0.500（x_mie≈π/2）；MD b_1 峰 2a/λ≈0.385（x_mie≈1.209）；
     EQ a_2 峰 2a/λ≈0.647（x_mie≈2.033）；MQ b_2 峰 2a/λ≈0.543（x_mie≈1.705）
  3. test_internal_coefficients_denominator_consistency — B&H 约束：
     c_n 分母 = b_n 分母；d_n 分母 = a_n 分母（gate③ 硬性要求）
  4. test_internal_field_finite — 内部场在球内有限（无 NaN/inf），幅值合理
  5. test_internal_field_m1_limit — m→1 极限：内部场 = 入射场 x̂ e^{ikz}（机器精度）
  6. test_internal_field_matches_miepython — 与独立第三方库 miepython 交叉验证
     （c_n/d_n 逐系数 + 球内电场逐点，误差 < 1e-8）

物理注意（实现/测试都受此约束）：
  - c_n/d_n 分子**两项都带 m**（与 c_n 分子相同，B&H 4.52 一般 μ 形式化简）。
    notes/alaee2018-mie-coeff.md §4 自检注释「c_n/d_n 分子相同，两项都带 m」，
    且经 miepython + 球面切向边界条件双重验证（若 d 分子第二项不带 m 则违背切向连续）。
  - 内部场 E_in 归一化 u = r/a ∈ [0,1]：球内电场只依赖 ρ = m·x_mie·u（见 mie_theory 文档）。
"""
from __future__ import annotations

import numpy as np
import pytest

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]  # reproduction/
_CODE_DIR = _REPO_ROOT / "code"
for _p in (_CODE_DIR, _REPO_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from baseline_mie import mie_coefficients  # noqa: E402
from mie_theory import (  # noqa: E402
    internal_E_field,
    internal_current_density,
    internal_field_coefficients,
    sphere_grid,
)
from params import N_REFRACTIVE, size_param_to_x_mie  # noqa: E402

# 被测物理量：介电球相对折射率 n = 2.5（host=air，m = n）
_M = N_REFRACTIVE

# 峰位锚点容差（2a/λ 绝对 0.02，task spec 指定）
_TOL_PEAK = 0.02

# 网格规模（足够密且不慢）
_GRID = (30, 24, 32)


def test_xmie_conversion():
    """size_param_to_x_mie：2a/λ=0.5 ⇒ x_mie = π·0.5；2a/λ=1.0 ⇒ x_mie = π。"""
    assert size_param_to_x_mie(0.5) == pytest.approx(np.pi * 0.5)
    assert size_param_to_x_mie(1.0) == pytest.approx(np.pi)


def _peak_2a_over_lambda(a_b_idx, n_max=3):
    """扫描 2a/λ∈[0.2,1.0] 找 |a_n| 或 |b_n| 极大对应的 2a/λ。

    a_b_idx : (n_idx, pol) 元组，(0,0)=a1, (0,1)=b1, (1,0)=a2, (1,1)=b2。
    """
    grid = np.linspace(0.2, 1.0, 2001)
    xs = np.pi * grid  # x_mie = π·(2a/λ)
    n_idx, pol = a_b_idx
    mags = np.array([
        float(np.abs(mie_coefficients(xi, _M, n_max)[pol][n_idx])) for xi in xs
    ])
    return float(grid[int(np.argmax(mags))])


def test_xmie_peak_anchors():
    """Mie 共振峰位锚点（step04 实测 2026-08-05，gate③ π 换算校验）。

    ⚠️ 锚点已按 step04 实测修正：早期 spec 记「MD 峰 2a/λ≈0.5–0.7」是猜错
    （该区间实为 EQ/MQ 峰混合区），实测 MD 峰在 2a/λ≈0.385。测试用实测值。
    若峰位偏 π 倍 = x_mie 换算错（gate③ 翻车点）。
    """
    # ED a_1 峰 2a/λ≈0.500（x_mie≈π/2，Fröhlich 偶极共振）
    assert abs(_peak_2a_over_lambda((0, 0)) - 0.500) < _TOL_PEAK
    # MD b_1 峰 2a/λ≈0.385（x_mie≈1.209，ka·n≈π 球内驻波）
    assert abs(_peak_2a_over_lambda((0, 1)) - 0.385) < _TOL_PEAK
    # EQ a_2 峰 2a/λ≈0.647（x_mie≈2.033）
    assert abs(_peak_2a_over_lambda((1, 0)) - 0.647) < _TOL_PEAK
    # MQ b_2 峰 2a/λ≈0.543（x_mie≈1.705）
    assert abs(_peak_2a_over_lambda((1, 1)) - 0.543) < _TOL_PEAK


def _coefficient_denominators(x_mie):
    """从 baseline 的 a_n/b_n 与 internal 的 c_n/d_n 提取各分母。

    返回 (a_den, b_den, c_den, d_den)（长度 n_max=4 的复数数组）。
    """
    import numpy as _np

    n_max = 4
    n = _np.arange(1, n_max + 1)
    z = _M * x_mie
    from scipy.special import spherical_jn, spherical_yn

    j_x = spherical_jn(n, x_mie); j_x_d = spherical_jn(n, x_mie, derivative=True)
    y_x = spherical_yn(n, x_mie); y_x_d = spherical_yn(n, x_mie, derivative=True)
    j_z = spherical_jn(n, z); j_z_d = spherical_jn(n, z, derivative=True)
    y_z = spherical_yn(n, z); y_z_d = spherical_yn(n, z, derivative=True)
    psi_x = x_mie * j_x; psi_x_d = j_x + x_mie * j_x_d
    psi_z = z * j_z; psi_z_d = j_z + z * j_z_d
    xi_x = x_mie * (j_x + 1j * y_x)
    xi_x_d = (j_x + 1j * y_x) + x_mie * (j_x_d + 1j * y_x_d)

    a_den = _M * psi_z * xi_x_d - xi_x * psi_z_d
    b_den = psi_z * xi_x_d - _M * xi_x * psi_z_d
    # c_n/d_n 分母（B&H 4.53/4.54，gate③ 已核）
    c_den = psi_z * xi_x_d - _M * xi_x * psi_z_d      # 应与 b_den 相同
    d_den = _M * psi_z * xi_x_d - xi_x * psi_z_d      # 应与 a_den 相同
    return a_den, b_den, c_den, d_den


def test_internal_coefficients_denominator_consistency():
    """B&H 原文结构约束（gate③ 硬性要求，notes §4 逐字）：
    'the denominators of the internal coefficients c_n and d_n are identical
     to those of the scattering coefficients b_n and a_n, respectively.'
    即：c_n 分母 = b_n 分母；d_n 分母 = a_n 分母。

    数值验证：扫多个 x_mie，比较分母数组（相对误差 < 1e-12）。
    """
    for x_mie in (0.3, 0.7, 1.0, 1.5, 2.0, np.pi * 0.5):
        a_den, b_den, c_den, d_den = _coefficient_denominators(x_mie)
        # c 分母 = b 分母
        rel_cb = np.max(np.abs(c_den - b_den)) / np.max(np.abs(b_den))
        assert rel_cb < 1e-12, f"x={x_mie}: c_den 应=b_den, rel={rel_cb:.2e}"
        # d 分母 = a 分母
        rel_da = np.max(np.abs(d_den - a_den)) / np.max(np.abs(a_den))
        assert rel_da < 1e-12, f"x={x_mie}: d_den 应=a_den, rel={rel_da:.2e}"

        # internal_field_coefficients 返回的分母也应满足同一约束
        _, _, c_den_f, d_den_f = internal_field_coefficients(x_mie, _M, 4)
        assert np.allclose(c_den_f, b_den, rtol=1e-12), f"x={x_mie}: 实现 c_den≠b_den"
        assert np.allclose(d_den_f, a_den, rtol=1e-12), f"x={x_mie}: 实现 d_den≠a_den"


def test_internal_field_finite():
    """内部场在球内有限（无 NaN/inf），幅值合理。

    对多个共振/非共振 x_mie 扫网格，检查：
      - 无 NaN/inf；
      - 幅值 O(1~5)（E0=1 归一化，高折射率介电球共振增强合理）；
      - 电流复振幅 J = (ε_r−1)E 同样有限。
    """
    r, th, ph = sphere_grid(*_GRID, 1.0)
    for x_mie in (0.3, np.pi * 0.5, np.pi * 0.385, np.pi * 0.647):
        Ex, Ey, Ez = internal_E_field(x_mie, _M, 6, r, th, ph)
        for comp in (Ex, Ey, Ez):
            assert np.all(np.isfinite(comp)), f"x={x_mie}: E 含 NaN/inf"
        max_abs = float(np.max(np.abs(Ex)))
        assert max_abs < 50.0, f"x={x_mie}: |Ex|={max_abs:.2f} 异常偏大"

        Jx, Jy, Jz = internal_current_density(x_mie, _M, 6, r, th, ph)
        for comp in (Jx, Jy, Jz):
            assert np.all(np.isfinite(comp)), f"x={x_mie}: J 含 NaN/inf"


def test_complex_current_uses_m_squared_not_modulus_squared():
    """吸收介质的 J_tilde=(epsilon_r-1)E 必须保留复介电函数。

    host=air 时 epsilon_r=m**2；若误用 m*conj(m)=|m|**2，则会丢失
    Im(epsilon_r)，并在 Fig.2 金球路径上给出错误的电流幅值。
    """
    m = 0.424149 + 2.472051j  # Johnson & Christy, 550 nm
    x_mie = np.pi * (500.0 / 550.0)
    r, th, ph = sphere_grid(4, 4, 8, 1.0)
    E = internal_E_field(x_mie, m, 8, r, th, ph)
    J = internal_current_density(x_mie, m, 8, r, th, ph)
    expected_prefactor = m ** 2 - 1.0

    for e_comp, j_comp in zip(E, J):
        assert np.allclose(j_comp, expected_prefactor * e_comp, rtol=1e-12, atol=1e-12)
    assert not np.isclose(expected_prefactor, abs(m) ** 2 - 1.0)


def test_internal_field_m1_limit():
    """m→1 极限：内部场 = 入射场 x̂ e^{ikz}（球消失，a_n/b_n→0）。

    这是内部场展开正确性的独立验证：c_n→1, d_n→1 时
        E_in = Σ i^n(2n+1)/(n(n+1))[M_o1n − i N_e1n] 应 = x̂ e^{ikz}。
    数值：机器精度量级（< 1e-6）。
    """
    r, th, ph = sphere_grid(*_GRID, 1.0)
    x_mie = np.pi * 0.5
    Ex, Ey, Ez = internal_E_field(x_mie, 1.0, 10, r, th, ph)
    want = np.exp(1j * x_mie * r * np.cos(th))  # x̂ e^{i·x·u·cosθ}，x_mie=k0·a
    err = float(np.max(np.abs(Ex - want)))
    assert err < 1e-6, f"m→1 极限应=入射场, max|Ex−e^ikz|={err:.2e}"
    # Ey/Ez 应≈0（x 偏振）
    assert float(np.max(np.abs(Ey))) < 1e-6
    assert float(np.max(np.abs(Ez))) < 1e-6


def test_internal_field_matches_miepython():
    """与独立第三方库 miepython 交叉验证（防自我一致）。

    - c_n/d_n 逐系数一致（< 1e-8）；
    - 球内电场逐点一致（< 1e-8）。
    miepython 已独立验证球面切向边界条件（其 e_near 内部场满足连续）。
    """
    miepython = pytest.importorskip("miepython")

    # -- c_n/d_n 系数对比 ----------------------------------------------
    for x_mie in (0.3, 0.7, 1.0, np.pi * 0.5):
        c_mp, d_mp = miepython.cn_dn(_M, x_mie, 6)
        c_mine, d_mine, _, _ = internal_field_coefficients(x_mie, _M, 6)
        assert np.allclose(c_mine, c_mp, rtol=1e-8, atol=1e-10), \
            f"x={x_mie}: c_n 与 miepython 不一致"
        assert np.allclose(d_mine, d_mp, rtol=1e-8, atol=1e-10), \
            f"x={x_mie}: d_n 与 miepython 不一致"

    # -- 球内电场逐点对比 ----------------------------------------------
    a = 1.0
    x_mie = 0.7
    lam = 2 * np.pi * a / x_mie  # 使 ka = 2πa/λ = x_mie
    test_pts = [(0.3, 0.5, 0.8), (0.5, 0.785, 0.927), (0.7, 1.2, 2.0),
                (0.9, 0.3, 4.0), (0.6, 1.5, 5.0), (0.2, 2.0, 3.0)]
    for (u, th, ph) in test_pts:
        rr = np.array([[[u]]]); tt = np.array([[[th]]]); pp = np.array([[[ph]]])
        Ex, Ey, Ez = internal_E_field(x_mie, _M, 10, rr, tt, pp)
        xc = u * np.sin(th) * np.cos(ph)
        yc = u * np.sin(th) * np.sin(ph)
        zc = u * np.cos(th)
        E_mp = miepython.e_near_cartesian(
            lam, 2 * a, _M, 1.0, xc, yc, zc, include_incident=False
        )
        E_mine = np.array([Ex[0, 0, 0], Ey[0, 0, 0], Ez[0, 0, 0]])
        err = float(np.max(np.abs(E_mine - E_mp)))
        assert err < 1e-8, \
            f"u={u} th={th:.3f} ph={ph:.3f}: 内部场与 miepython 差 {err:.2e}"
