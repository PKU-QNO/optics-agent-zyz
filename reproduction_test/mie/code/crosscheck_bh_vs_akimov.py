"""T2 逐点交叉验证: BH 式 (scattering.mie_ab) vs Akimov 式 (akimov_coeffs).

case: 0703-01-akimov-mie-v1 | step04 T2
判据（formalization.yaml / repro_plan T2 / GATE1 决定3 blocker 口径）:
  max|a_BH - a_Akimov| < 1e-12 且 max|b_BH - b_Akimov| < 1e-12
  >= 1e-12 即 blocker（停机, 不进 T3）。

网格:
  确定性: l in {1,2,3} x eps_ratio in [-10,15]（避开 0 的 ±1e-6 邻域）
          x q_e in (0,10], >= 1000 点
  随机:   同域, 固定 seed（确定性可复现）, >= 300 点

极点处理: 若某点 BH 或 Akimov 分母模长 < DEN_EPS（0/0 或极点, 如恰命中 loci）,
  按分母模长设阈跳过并计数, 不算失配（日志说明跳过多少、为什么）。
"""
from __future__ import annotations

import sys
import numpy as np

CODE_DIR = "reproduction_test/mie/code"
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from scattering import mie_ab            # noqa: E402  BH 主源
from akimov_coeffs import akimov_ab       # noqa: E402  Akimov 独立实现

TOL = 1e-12
DEN_EPS = 1e-9          # 分母模长阈: 低于此判为极点/退化, 跳过
EPS_ZERO_GUARD = 1e-6   # eps_ratio=0 附近 ±邻域回避（m=0 退化点）
LS = (1, 2, 3)


def _m_from_eps(eps_ratio: float) -> complex:
    """m = sqrt(eps_ratio), 主值 Im m >= 0（eps_ratio<0 时纯虚正）。"""
    return np.sqrt(complex(eps_ratio))


def _denoms(l: int, m: complex, x: float):
    """返回 BH 与 Akimov 两式 a,b 的分母模长, 用于极点判定。

    直接复算两式分母（与各自模块内部同式）, 只用于跳过判据, 不参与差值。
    """
    from scipy.special import spherical_jn, spherical_yn

    def psi(ll, z):
        jl = spherical_jn(ll, z)
        return z * jl, jl + z * spherical_jn(ll, z, derivative=True)

    def xi(ll, z):
        jl = spherical_jn(ll, z)
        yl = spherical_yn(ll, z)
        h1 = jl + 1j * yl
        h1p = spherical_jn(ll, z, derivative=True) + 1j * spherical_yn(ll, z, derivative=True)
        return z * h1, h1 + z * h1p

    x_ = x
    mx = m * x
    psi_mx, psip_mx = psi(l, mx)
    psi_x, psip_x = psi(l, x_)
    xi_x, xip_x = xi(l, x_)
    # BH 分母
    a_den_bh = m * psi_mx * xip_x - xi_x * psip_mx
    b_den_bh = psi_mx * xip_x - m * xi_x * psip_mx
    # Akimov 分母
    q_e, q_i = x_, mx
    a_den_ak = q_i * psi_mx * xip_x - q_e * xi_x * psip_mx
    b_den_ak = q_e * psi_mx * xip_x - q_i * xi_x * psip_mx
    return abs(a_den_bh), abs(b_den_bh), abs(a_den_ak), abs(b_den_ak)


def _grid_points():
    """确定性网格: >=1000 点。eps 含负值, 避开 0 邻域。"""
    eps_vals = np.linspace(-10.0, 15.0, 26)          # 步长 1.0
    eps_vals = eps_vals[np.abs(eps_vals) > EPS_ZERO_GUARD]
    qe_vals = np.linspace(0.05, 10.0, 40)            # (0,10]
    pts = []
    for l in LS:
        for eps in eps_vals:
            for qe in qe_vals:
                pts.append((l, float(eps), float(qe)))
    return pts


def _random_points(n=300, seed=20260704):
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        l = int(rng.integers(1, 4))
        eps = float(rng.uniform(-10.0, 15.0))
        if abs(eps) <= EPS_ZERO_GUARD:
            continue
        qe = float(rng.uniform(0.001, 10.0))
        pts.append((l, eps, qe))
    return pts


def _run(points, label):
    max_da = 0.0
    max_db = 0.0
    worst = None
    skipped = 0
    used = 0
    for (l, eps, qe) in points:
        m = _m_from_eps(eps)
        adb, bdb, ada, bda = _denoms(l, m, qe)
        if min(adb, bdb, ada, bda) < DEN_EPS:
            skipped += 1
            continue
        a_bh, b_bh = mie_ab(l, m, qe)
        a_ak, b_ak = akimov_ab(l, m, qe)
        da = abs(a_bh - a_ak)
        db = abs(b_bh - b_ak)
        used += 1
        if da > max_da:
            max_da = da
        if db > max_db:
            max_db = db
        if max(da, db) >= max(max_da, max_db) and max(da, db) == max(da, db):
            if worst is None or max(da, db) > worst[3]:
                worst = (l, eps, qe, max(da, db))
    print(f"[{label}] points={len(points)} used={used} skipped(pole)={skipped}")
    print(f"[{label}] max|da|={max_da:.3e}  max|db|={max_db:.3e}")
    if worst:
        print(f"[{label}] worst @ l={worst[0]} eps={worst[1]:.4f} qe={worst[2]:.4f} diff={worst[3]:.3e}")
    return max_da, max_db, skipped


def main() -> int:
    det = _grid_points()
    rnd = _random_points()
    print(f"确定性网格点数={len(det)} (要求>=1000), 随机点数={len(rnd)} (要求>=300)")
    da1, db1, sk1 = _run(det, "deterministic")
    da2, db2, sk2 = _run(rnd, "random")
    max_da = max(da1, da2)
    max_db = max(db1, db2)
    print("-" * 60)
    print(f"TOTAL max|da|={max_da:.3e}  max|db|={max_db:.3e}  tol={TOL:.0e}")
    print(f"TOTAL skipped(pole, |den|<{DEN_EPS:.0e})={sk1 + sk2}")
    if max_da < TOL and max_db < TOL:
        print("PASS crosscheck_bh_vs_akimov: 两式数值等价")
        return 0
    print("FAIL crosscheck_bh_vs_akimov: 超差, T2 blocker（停机, 不进 T3）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
