# -*- coding: utf-8 -*-
"""
test_mie.py — Layer1 物理约束测试（TDD 纪律：物理约束先硬编码）
====================================================================
测试对象：code/baseline_mie.py（独立最小 Mie 基准）+ code/params.py（换算）。

覆盖的 Layer1 硬约束（formalization/alaee2018-fig1.yaml §verification.layer1）：
  1. test_energy_conservation — C_ext = C_sca + C_abs（相对误差 < 1e-10，扫多 x）
  2. test_zero_abs_lossless   — ε_r 纯实 ⇒ C_abs = 0（介电球 ε_r=6.25）
  3. test_rayleigh_limit      — 小 x：Q_sca ∝ x⁴（log-log 斜率 4 ± 0.05）
  4. test_large_size_limit    — 大 x：Q_ext → 2
  5. test_optical_theorem     — 无吸收球：Σ(2n+1)Re(a_n+b_n) = Σ(2n+1)(|a|²+|b|²)
                                （= 能量守恒的无吸收形式，与 k 无关）
  6. test_xmie_conversion     — size_param_to_x_mie(0.5) = π·0.5

物理注意（实现/测试都受此约束）：
  - 对无吸收实介电球，Q_ext(x) → 2 是**慢衰减带 ripple 的振荡收敛**（Mie 理论
    固有行为，非实现 bug）。实测 x=50 时 Q_ext≈2.076 超出 ±0.05 容差，x=120
    才进 |Q−2|<0.02。因此 test_large_size_limit 用 x=120 + 容差 0.05（在
    spec「Q_ext→2」语义内），并保留对 x=50 的说明性弱断言（仅记录行为，不设门禁）。
  - 能量守恒、瑞利斜率、光学定理无吸收等价式均**与 k（及 2π/k² 因子）无关**，
    故可直接测试无量纲截面。
"""
from __future__ import annotations

import numpy as np
import pytest

# 测试与被测文件同仓：code/ 与 tests/ 为同级目录
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]  # reproduction/
_CODE_DIR = _REPO_ROOT / "code"
for _p in (_CODE_DIR, _REPO_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from baseline_mie import (  # noqa: E402
    Q_ext,
    Q_sca,
    c_sca_per_multipole,
    cross_sections,
    mie_coefficients,
    wiscombe_nmax,
)
from params import N_REFRACTIVE, size_param_to_x_mie, wiscombe_nmax as _p_wiscombe  # noqa: E402

# 被测物理量：介电球相对折射率 n = 2.5（host=air，m = n）
_M = N_REFRACTIVE
# 纯实 ε_r=6.25 ⇒ 相对误差容差（机器精度量级）
_TOL_ENERGY = 1e-10


def test_energy_conservation():
    """C_ext = C_sca + C_abs（相对误差 < 1e-10），扫多个 x_mie。"""
    for x in (0.1, 0.5, 1.0, 2.0, 3.0):
        c_sca, c_ext, c_abs = cross_sections(x, _M)
        # C_abs = C_ext − C_sca 恒等式是定义，但这里独立检查守恒成立：
        # |C_ext − (C_sca + C_abs)| / C_ext < 1e-10
        rel_err = abs(c_ext - (c_sca + c_abs)) / c_ext
        assert rel_err < _TOL_ENERGY, f"x={x}: 能量守恒被破坏 rel_err={rel_err:.3e}"


def test_zero_abs_lossless():
    """纯实 ε_r=6.25（无吸收）⇒ C_abs = 0（< 1e-10）。"""
    for x in (0.1, 0.5, 1.0, 2.0, 3.0):
        c_sca, c_ext, c_abs = cross_sections(x, _M)
        # 无量纲 C_sca ~ O(1)，C_abs 应 < 1e-10（同量级绝对阈值）
        assert abs(c_abs) < 1e-10, f"x={x}: 无吸收球 C_abs={c_abs:.3e} 应≈0"


def test_rayleigh_limit():
    """小 x：Q_sca ∝ x⁴，log-log 斜率 4 ± 0.05。"""
    xs = np.array([0.01, 0.02, 0.05])
    qs = np.array([Q_sca(float(x), _M) for x in xs])
    # log-log 线性拟合斜率
    slope = np.polyfit(np.log(xs), np.log(qs), 1)[0]
    assert abs(slope - 4.0) < 0.05, f"瑞利斜率 {slope:.4f} 应≈4"


def test_large_size_limit():
    """大 x：Q_ext → 2（消光极限）。

    物理说明：无吸收实介电球 Q_ext→2 是带 ripple 的慢振荡收敛。
    x=50 处 Q_ext≈2.076（超出 ±0.05 容差），x=120 处 |Q_ext−2|≈0.0186 进带。
    故本测试用 x=120 + 容差 0.05（spec「Q_ext→2」语义），并额外记录 x=50 行为。
    """
    # 门禁：x=120 进带（|Q−2| < 0.05）
    x_gate = 120.0
    q_ext = Q_ext(x_gate, _M)
    assert abs(q_ext - 2.0) < 0.05, f"x={x_gate}: Q_ext={q_ext:.5f} 应→2（±0.05）"

    # 记录性（非门禁）：x=50 时 Q_ext 应在 2±0.1 附近（ripple 幅度内）
    x_note = 50.0
    q_ext_50 = Q_ext(x_note, _M)
    assert abs(q_ext_50 - 2.0) < 0.1, (
        f"x={x_note}: Q_ext={q_ext_50:.5f}（ripple 振荡，2±0.1 内即可）"
    )


def test_optical_theorem():
    """无吸收球光学定理（与 k 无关形式）：
    Σ(2n+1)Re(a_n+b_n) = Σ(2n+1)(|a_n|²+|b_n|²)。

    说明：对无吸收球，C_ext=C_sca（C_abs=0），且 C_ext=Σ(2n+1)Re(a_n+b_n)、
    C_sca=Σ(2n+1)(|a|²+|b|²)（同无量纲因子），两者相等即光学定理 C_ext=(4π/k)Im S(0)
    在无吸收下的等价式（不依赖 k）。Layer1 保留此独立断言，防「能量守恒+零吸收」
    共享同一代码路径导致自洽但错误。
    """
    for x in (0.5, 1.0, 2.0):
        a_n, b_n = mie_coefficients(x, _M, wiscombe_nmax(x))
        w = 2.0 * np.arange(1, len(a_n) + 1) + 1.0
        lhs = float(np.sum(w * np.real(a_n + b_n)))      # ∝ C_ext
        rhs = float(np.sum(w * (np.abs(a_n) ** 2 + np.abs(b_n) ** 2)))  # ∝ C_sca
        rel = abs(lhs - rhs) / rhs
        assert rel < 1e-10, f"x={x}: 光学定理无吸收等价式 rel={rel:.3e}"


def test_xmie_conversion():
    """size_param_to_x_mie：2a/λ=0.5 ⇒ x_mie = π·0.5 = 1.570796…"""
    assert size_param_to_x_mie(0.5) == pytest.approx(np.pi * 0.5)


def test_wiscombe_nmax_consistency():
    """baseline_mie 自含截断与 params.py 截断一致（防两份漂移）。"""
    for x in (0.5, 1.0, 2.0, 10.0, 50.0):
        assert wiscombe_nmax(x) == _p_wiscombe(x), f"x={x}: 两份 Wiscombe 截断不一致"


def test_c_sca_per_multipole_sums_to_total():
    """逐多极 C_sca 数组之和 = 总 C_sca（同截断）。"""
    for x in (0.5, 1.0, 2.0):
        per_n = c_sca_per_multipole(x, _M)
        c_sca, _, _ = cross_sections(x, _M)
        assert abs(float(np.sum(per_n)) - c_sca) < 1e-12 * max(1.0, c_sca)


def test_first_resonance_xmie_anchor():
    """物理锚点（gate③ 硬性要求：π 换算校验）。

    介电球 n=2.5（ε_r=6.25）的 Mie 共振峰位由 x_mie = π·(2a/λ) 换算后应落在
    物理正确的 x_mie 位置。实测（本实现，多层独立验证已确认正确）：
        a_1（ED 电偶极）峰  x_mie≈1.571 = π/2（2a/λ=0.5）
        b_1（MD 磁偶极）峰  x_mie≈1.210（2a/λ=0.385）
        b_2（MQ 磁四极）峰  x_mie≈1.706（2a/λ=0.543）
        a_2（EQ 电四极）峰  x_mie≈2.033（2a/λ=0.647）
    若 π 换算错误（直接拿 2a/λ 当 x_mie），所有峰位偏移 π 倍，此测试即失败。

    ⚠️ 与 spec 锚点备注的关系：formalization spec 记「磁偶极峰 2a/λ≈0.5–0.7」，
    实测该区间实际是 ED/EQ/MQ 三峰混合区（MD 峰在 0.385，不在区间内）——
    spec 的峰归属措辞有误，但「第一个共振在 2a/λ≈0.5」与实测 a_1 峰吻合。
    本测试以**实测峰位的 x_mie 绝对值**为锚（不依赖 spec 的 MD 归属），
    既校验 π 换算又记录真实物理。若未来确认 spec 更正，同步更新即可。
    """
    grid = np.linspace(0.2, 1.0, 2001)
    xs = np.pi * grid  # x_mie = π·(2a/λ)

    def peak_x(a_b_idx):
        # a_b_idx: (0,0)=a1, (0,1)=b1, (1,0)=a2, (1,1)=b2
        n_idx, pol = a_b_idx
        mags = np.array([
            float(np.abs(mie_coefficients(xi, _M, 3)[pol][n_idx])) for xi in xs
        ])
        return xs[int(np.argmax(mags))]  # 峰对应的 x_mie

    # 各峰 x_mie 实测值（容差取扫描步长量级 ~π*0.8/2000≈1.3e-3，用 2e-2 留裕量）
    x_a1 = peak_x((0, 0))
    assert abs(x_a1 - np.pi / 2) < 2e-2, f"a_1(ED) 峰 x_mie={x_a1:.4f} 应≈π/2={np.pi/2:.4f}"
    x_b1 = peak_x((0, 1))
    assert abs(x_b1 - 1.210) < 2e-2, f"b_1(MD) 峰 x_mie={x_b1:.4f} 应≈1.210"
    x_b2 = peak_x((1, 1))
    assert abs(x_b2 - 1.706) < 2e-2, f"b_2(MQ) 峰 x_mie={x_b2:.4f} 应≈1.706"
    x_a2 = peak_x((1, 0))
    assert abs(x_a2 - 2.033) < 2e-2, f"a_2(EQ) 峰 x_mie={x_a2:.4f} 应≈2.033"

    # 换算直接校验：2a/λ=0.5 处第一个共振（a_1 峰）就在 x_mie≈π/2
    assert abs(x_a1 - np.pi * 0.5) < 2e-2, "a_1 峰 2a/λ=0.5 即 x_mie=π·0.5（π 换算锚点）"
