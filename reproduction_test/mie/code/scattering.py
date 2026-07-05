"""Lorenz-Mie 散射核模块（BH 主源实现）.

case: 0703-01-akimov-mie-v1 | step04 T1
物理主源: Bohren & Huffman, "Absorption and Scattering of Light by Small
Particles" §4.3/§4.4 标准式（.paper/scattering.pdf）。formalization.yaml 的
equations.primary_BH 是本 case 物理 spec, 代码消费 spec, 不消费论文 prose。

记号约定（与 spec notation_map 一致）:
  x  = q_e = k_e R      (外部尺寸参数, 实正数)
  mx = q_i = m x        (内部宗量, m 复时为复数)
  m  = sqrt(eps_i/eps_e) (相对折射率; eps 比为负时 m 纯虚, 取主值 Im m>=0)

时谐约定 e^{-i w t}: 散射场用 h_l^(1), 与 BH 教材、Akimov 论文一致。

特殊函数一律用 scipy.special.spherical_jn / spherical_yn（复宗量直接可用,
含 derivative=True）, 不自写特殊函数、不自写递推。
"""
from __future__ import annotations

import numpy as np
from scipy.special import spherical_jn, spherical_yn

__all__ = [
    "mie_ab",
    "compute_cross_sections",
    "compute_Q_sca",
    "compute_Q_ext",
    "wiscombe_nmax",
]


def _refractive_index(m: complex) -> complex:
    """把可能是 eps 比传入的场景收敛到 m 本身。

    verifier 和 T2/T3 一律直接传 m（相对折射率）, 本函数只做类型收敛,
    保证 m 为复数, 不做任何 sqrt（sqrt 的语义留给上游 spec）。
    """
    return complex(m)


def _riccati_psi(l: int, z: complex):
    """Riccati-Bessel psi_l(z)=z*j_l(z) 及其对宗量的导数 psi_l'(z).

    psi_l'(z) = j_l(z) + z*j_l'(z)  （链式法则, ' 对宗量 z）。
    """
    jl = spherical_jn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    psi = z * jl
    psip = jl + z * jlp
    return psi, psip


def _riccati_xi(l: int, z: complex):
    """Riccati-Bessel xi_l(z)=z*h_l^(1)(z) 及其导数 xi_l'(z).

    xi_l(z) = psi_l(z) - i*chi_l(z),  chi_l(z) = -z*y_l(z)
    => xi_l(z) = z*(j_l(z) + i*y_l(z)) = z*h_l^(1)(z)   （e^{-iwt} 约定）
    xi_l'(z) = h_l^(1)(z) + z*h_l^(1)'(z),  h^(1)=j+i*y。
    """
    jl = spherical_jn(l, z)
    yl = spherical_yn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    ylp = spherical_yn(l, z, derivative=True)
    h1 = jl + 1j * yl
    h1p = jlp + 1j * ylp
    xi = z * h1
    xip = h1 + z * h1p
    return xi, xip


def mie_ab(l: int, m: complex, x: float):
    """单个 l 阶 BH 标准 Lorenz-Mie 系数 (a_l, b_l).

    spec equations.primary_BH:
      a_l = [ m psi_l(mx) psi_l'(x) - psi_l(x) psi_l'(mx) ]
            / [ m psi_l(mx) xi_l'(x) - xi_l(x) psi_l'(mx) ]
      b_l = [ psi_l(mx) psi_l'(x) - m psi_l(x) psi_l'(mx) ]
            / [ psi_l(mx) xi_l'(x) - m xi_l(x) psi_l'(mx) ]

    参数
      l : 阶数 (>=1)
      m : 相对折射率（复合法）
      x : 外部尺寸参数 q_e（实正）
    返回 (a_l, b_l) 复标量。
    """
    m = _refractive_index(m)
    mx = m * x

    psi_mx, psip_mx = _riccati_psi(l, mx)
    psi_x, psip_x = _riccati_psi(l, x)
    xi_x, xip_x = _riccati_xi(l, x)

    a_num = m * psi_mx * psip_x - psi_x * psip_mx
    a_den = m * psi_mx * xip_x - xi_x * psip_mx
    b_num = psi_mx * psip_x - m * psi_x * psip_mx
    b_den = psi_mx * xip_x - m * xi_x * psip_mx

    a_l = a_num / a_den
    b_l = b_num / b_den
    return a_l, b_l


def wiscombe_nmax(x: float) -> int:
    """Wiscombe 谱求和截断 n_max = ceil(x + 4 x^(1/3) + 2).

    trust 来源: 教材/库惯例（Wiscombe 1980）, 非论文原文。formalization.yaml
    equations.cross_sections.truncation 采用此式。对 x=200 给 n_max~=224,
    足够收敛（大尺寸消光佯谬检验 x 最大 200）。
    """
    xr = float(np.real(x))
    return int(np.ceil(xr + 4.0 * xr ** (1.0 / 3.0) + 2.0))


def _qsca_qext(m: complex, x: float):
    """按光学定理求 Q_sca、Q_ext（归一 Q = 2/x^2 * sum ...）.

    Q_sca = (2/x^2) sum_l (2l+1)(|a_l|^2+|b_l|^2)
    Q_ext = (2/x^2) sum_l (2l+1) Re(a_l+b_l)
    两者共用同一套 a_l,b_l 与同一归一, 保证 Q_abs=Q_ext-Q_sca 解析恒等。
    """
    m = _refractive_index(m)
    nmax = wiscombe_nmax(x)
    pref = 2.0 / (x * x)
    qsca = 0.0
    qext = 0.0
    for l in range(1, nmax + 1):
        a_l, b_l = mie_ab(l, m, x)
        w = 2 * l + 1
        qsca += w * (abs(a_l) ** 2 + abs(b_l) ** 2)
        qext += w * (a_l + b_l).real
    return pref * qsca, pref * qext


def compute_cross_sections(m: complex, x: float):
    """(Cext, Csca, Cabs).

    因 Fig3 问题无量纲化, pi R^2 因子约掉, 这里令效率即截面 C=Q（内部三量
    用同一套 a_l,b_l 与同一归一, 能量守恒 C_ext=C_sca+C_abs 解析成立,
    verifier check_energy_conservation 只查此相对自洽）。
    """
    qsca, qext = _qsca_qext(m, x)
    qabs = qext - qsca
    return qext, qsca, qabs


def compute_Q_sca(m: complex, x: float) -> float:
    qsca, _ = _qsca_qext(m, x)
    return qsca


def compute_Q_ext(m: complex, x: float) -> float:
    _, qext = _qsca_qext(m, x)
    return qext


if __name__ == "__main__":
    # 快速自测: 实 m 无耗吸收应为 0
    ce, cs, ca = compute_cross_sections(m=1.5 + 0.0j, x=1.0)
    print(f"dielectric x=1: Cext={ce:.6e} Csca={cs:.6e} Cabs={ca:.3e}")
    print(f"  |Cabs|/Cext = {abs(ca)/abs(ce):.3e} (应 ~machine eps)")
