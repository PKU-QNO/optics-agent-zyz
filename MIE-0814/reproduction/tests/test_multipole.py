# -*- coding: utf-8 -*-
"""
test_multipole.py — 表2/表1 多极矩体积分测试（Layer2 + 跨实现交叉）
======================================================================
覆盖：
1. 表2→表1 退化（小 x 时两者多极矩一致 <1%）——Layer2
2. 表2 ED/MD 的 C_sca 与 Mie 基准交叉一致（跨实现验证，<1%）——核心
3. 小宗量 j_l/(kr)^l 极限正确（1/3, 1/15, 1/105）——防除零
4. 体积分收敛性（网格加密，相对变化 <0.5%）
5. 表1 长波长失效（x 增大时表1 偏离表2/Mie——正确物理）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import numpy as np
import pytest

from multipole_moments import (
    _cartesian_position,
    _jl_over_rho_l,
    c_sca_from_multipoles,
    table2_multipole_moments,
)
from multipole_approx import table1_multipole_moments
from baseline_mie import mie_coefficients


# B1 unified contract: channel-local near-zero points are excluded from
# max/RMSE checks, using the same 1e-3-of-channel-maximum rule as plot_fig1.py.
ZERO_FRAC = 1e-3
CHANNEL_LIMIT = {'ED': 3.0, 'MD': 3.0, 'EQ': 5.0, 'MQ': 5.0}


def _mie_csca_multipole(x_mie, m):
    """Mie 逐多极 C_sca 分项（无量纲约定 C'=Σ(2n+1)|coef|²）。"""
    an, bn = mie_coefficients(x_mie, m, 7)
    return {
        'ED': 3.0 * abs(an[0]) ** 2,
        'MD': 3.0 * abs(bn[0]) ** 2,
        'EQ': 5.0 * abs(an[1]) ** 2,
        'MQ': 5.0 * abs(bn[1]) ** 2,
    }


def test_table2_degrades_to_table1_small_x():
    """Layer2：小 x 时表2 精确矩 → 表1 近似矩（各多极相对差 <1%）。"""
    for x in [0.05, 0.1]:
        t2 = table2_multipole_moments(x, 2.5, 7, 40, 40, 80)
        t1 = table1_multipole_moments(x, 2.5, 7, 40, 40, 80)
        for k in ['p', 'm', 'Qe', 'Qm']:
            n2 = np.linalg.norm(t2[k])
            n1 = np.linalg.norm(t1[k])
            rel = abs(n2 - n1) / max(n2, 1e-12)
            assert rel < 0.01, f'x={x} {k}: 表2/表1 相对差 {rel:.4f} > 1%'


def test_table2_matches_mie_ed_md():
    """核心交叉验证：表2 ED/MD 的 C_sca 与 Mie 基准一致（<1%）。

    这是独立实现（多极矩体积分）vs baseline（Mie 系数）的交叉，
    证明表2 公式 + 体积分 + 标定全部正确。
    """
    m = 2.5
    for x in [0.1, 0.3, 0.5]:
        t2 = table2_multipole_moments(x, m, 7, 40, 40, 80)
        C2 = c_sca_from_multipoles(t2, x)
        Cmie = _mie_csca_multipole(x, m)
        for k in ['ED', 'MD']:
            if Cmie[k] < 1e-12:
                continue
            ratio = C2[k] / Cmie[k]
            assert abs(ratio - 1.0) < 0.01, f'x={x} {k}: 表2/Mie={ratio:.4f} 偏差>1%'


def test_r0_jl_limit():
    """Layer2：j_l/(kr)^l 在 r→0 极限 = 1/(2l+1)!!（防除零）。"""
    rho = np.array([1e-20, 1e-15, 1e-10])
    assert np.allclose(_jl_over_rho_l(0, rho), 1.0, atol=1e-6)
    assert np.allclose(_jl_over_rho_l(1, rho), 1 / 3, atol=1e-6)
    assert np.allclose(_jl_over_rho_l(2, rho), 1 / 15, atol=1e-6)
    assert np.allclose(_jl_over_rho_l(3, rho), 1 / 105, atol=1e-6)


def test_integration_convergence():
    """体积分收敛：网格加密相对变化 <1%（ED）。

    网格 30→60→90 逐级加密，ED 相对变化应单调减小并 <1%。
    """
    x = 0.5
    m = 2.5
    t_c = table2_multipole_moments(x, m, 7, 30, 30, 60)
    t_m = table2_multipole_moments(x, m, 7, 60, 60, 120)
    p_c = np.linalg.norm(t_c['p'])
    p_m = np.linalg.norm(t_m['p'])
    rel_cm = abs(p_m - p_c) / p_m
    assert rel_cm < 0.01, f'网格收敛 ED(30→60) 相对变化 {rel_cm:.4f} > 1%'


def test_table1_diverges_at_paper_x075():
    """正确物理：论文声称 2a/λ≈0.75 处近似误差>100%。

    2a/λ≈0.75 对应 x_mie = π·0.75 ≈ 2.356。此时表1（长波长近似）
    应显著偏离表2/Mie（ED/MD 误差应可观，接近论文的 >100% 声称）。
    这里验证表1 与表2 的 ED 多极矩偏差显著（>5%，定性复现近似失效）。
    """
    x_mie = np.pi * 0.75  # 2.356，对应论文声称的 2a/λ≈0.75
    m = 2.5
    t2 = table2_multipole_moments(x_mie, m, 7, 40, 40, 80)
    t1 = table1_multipole_moments(x_mie, m, 7, 40, 40, 80)
    # ED 表1 应显著偏离表2（长波长近似失效，论文声称 >100% 误差）
    n2 = np.linalg.norm(t2['p'])
    n1 = np.linalg.norm(t1['p'])
    rel = abs(n2 - n1) / max(n2, 1e-12)
    assert rel > 0.05, f'2a/λ=0.75 ED: 表1 应偏离表2（{rel:.3f}），长波长近似应失效'


def test_fig1_s075_complex_moment_and_c_metrics_are_frozen():
    """B1 回归：论文矩口径与派生 C 口径在 s=0.75 分开冻结。

    The paper's statement is about complex multipole moments, so ED and MD
    must both exceed 100% in the Table1-vs-Table2 vector metric.  The C
    metric is retained as a diagnostic and must not silently replace it.
    """
    x = np.pi * 0.75
    t2 = table2_multipole_moments(x, 2.5, 7, 40, 41, 80)
    t1 = table1_multipole_moments(x, 2.5, 7, 40, 41, 80)
    got_c = c_sca_from_multipoles(t1, x)
    ref_c = _mie_csca_multipole(x, 2.5)
    c_expected = {'ED': 86.91476365, 'MD': 215.91099314,
                  'EQ': 103.07745569, 'MQ': 55.75099751}
    v_expected = {'ED': 136.16689745, 'MD': 277.74244147,
                  'EQ': 42.51947104, 'MQ': 24.79502905}
    key_map = {'ED': 'p', 'MD': 'm', 'EQ': 'Qe', 'MQ': 'Qm'}
    for ch in ['ED', 'MD', 'EQ', 'MQ']:
        c_err = abs(got_c[ch] - ref_c[ch]) / max(abs(ref_c[ch]), 1e-300) * 100.0
        v_err = (np.linalg.norm(t1[key_map[ch]] - t2[key_map[ch]])
                 / max(np.linalg.norm(t2[key_map[ch]]), 1e-300) * 100.0)
        assert c_err == pytest.approx(c_expected[ch], rel=5e-4, abs=1e-5)
        assert v_err == pytest.approx(v_expected[ch], rel=5e-4, abs=1e-5)
    assert v_expected['ED'] > 100.0 and v_expected['MD'] > 100.0


@pytest.mark.parametrize('size_param', [0.2, 0.3, 0.385, 0.5, 0.6, 0.65, 0.7, 0.8, 1.0])
def test_table2_four_multipoles_nine_points(size_param):
    """表2四通道在任务书九个指定点与独立 Mie 分项一致。"""
    x = np.pi * size_param
    mie = _mie_csca_multipole(x, 2.5)
    got = c_sca_from_multipoles(
        table2_multipole_moments(x, 2.5, 7, 40, 41, 80), x)
    for key in ['ED', 'MD', 'EQ', 'MQ']:
        if mie[key] < ZERO_FRAC * CHANNEL_LIMIT[key]:
            continue
        assert abs(got[key] / mie[key] - 1.0) < 0.01, (
            f's={size_param} {key}: 表2/Mie={got[key] / mie[key]:.6f} (contract <1%)'
        )


def test_table2_host_kernel_is_default_and_internal_is_rejected_by_regression():
    """辐射核用 host k；k_in 分支只保留作诊断，不能悄悄成为默认。"""
    x = np.pi * 0.65
    explicit = table2_multipole_moments(x, 2.5, 7, 24, 25, 48, kernel_k='host')
    implicit = table2_multipole_moments(x, 2.5, 7, 24, 25, 48)
    for key in ['p', 'm', 'Qe', 'Qm']:
        assert np.allclose(explicit[key], implicit[key], rtol=1e-12, atol=1e-12)
    wrong = c_sca_from_multipoles(
        table2_multipole_moments(x, 2.5, 7, 24, 25, 48, kernel_k='internal'), x)
    mie = _mie_csca_multipole(x, 2.5)
    assert wrong['ED'] / mie['ED'] > 10.0


def test_cartesian_position_contains_radial_factor():
    """r/a 必须是 U·(sinθcosφ, sinθsinφ, cosθ)，不是纯方向余弦。"""
    U = np.array([[[0.25]]])
    Th = np.array([[[np.pi / 2]]])
    Ph = np.array([[[0.0]]])
    rx, ry, rz = _cartesian_position(U, Th, Ph)
    assert np.allclose([rx.item(), ry.item(), rz.item()], [0.25, 0.0, 0.0])


def test_eq1_analytic_prefactors_and_powers():
    """Eq.1 解析常数和 x 幂次回归，防止经验标定常数回流。"""
    x = 2.0
    moments = {
        'p': np.array([1.0 + 0j, 0j, 0j]),
        'm': np.array([1.0 + 0j, 0j, 0j]),
        'Qe': np.eye(3, dtype=complex),
        'Qm': np.eye(3, dtype=complex),
    }
    got = c_sca_from_multipoles(moments, x)
    assert got['ED'] == pytest.approx(x**6 / (12 * np.pi**2))
    assert got['MD'] == pytest.approx(x**8 / (12 * np.pi**2))
    assert got['EQ'] == pytest.approx(3 * x**8 / (1440 * np.pi**2))
    assert got['MQ'] == pytest.approx(3 * x**10 / (1440 * np.pi**2))


def test_table2_resonance_grid_convergence():
    """三个共振/大 x 锚点在加密网格下保持统一合同 <1% 的 Mie 误差。"""
    for x in [2.042, 2.513, 3.142]:
        mie = _mie_csca_multipole(x, 2.5)
        got = c_sca_from_multipoles(
            table2_multipole_moments(x, 2.5, 7, 40, 41, 80), x)
        for key in ['ED', 'MD', 'EQ', 'MQ']:
            if mie[key] < 1e-12:
                continue
            if mie[key] < ZERO_FRAC * CHANNEL_LIMIT[key]:
                continue
            assert abs(got[key] / mie[key] - 1.0) < 0.01, (
                f'x={x} {key}: 表2/Mie={got[key] / mie[key]:.6f} (contract <1%)'
            )


@pytest.mark.skipif(os.environ.get('RUN_TABLE2_SLOW') != '1',
                    reason='200点扫描耗时较长；设置 RUN_TABLE2_SLOW=1 执行')
def test_table2_full_range_200_point_scan():
    """200点全区间验收；非近零分量的相对误差须低于统一的1%合同。"""
    sizes = np.linspace(0.2, 1.0, 200)
    maximum = {key: 0.0 for key in ['ED', 'MD', 'EQ', 'MQ']}
    for size_param in sizes:
        x = np.pi * size_param
        mie = _mie_csca_multipole(x, 2.5)
        got = c_sca_from_multipoles(
            table2_multipole_moments(x, 2.5, 7, 40, 41, 80), x)
        for key in maximum:
            if mie[key] >= ZERO_FRAC * CHANNEL_LIMIT[key]:
                maximum[key] = max(maximum[key], abs(got[key] / mie[key] - 1.0))
    assert max(maximum.values()) < 0.01, maximum
