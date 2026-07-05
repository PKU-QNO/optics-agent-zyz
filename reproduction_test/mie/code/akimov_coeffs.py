"""Akimov 论文式 Lorenz-Mie 系数（独立实现, 交叉验证用）.

case: 0703-01-akimov-mie-v1 | step04 T2
源: formalization.yaml equations.cross_check_akimov（Akimov arXiv 2401.04146
式 (S:a_l)/(S:b_l)）, 分子分母带显式 q_i, q_e 因子。

设计约束（关键）: 本模块必须是 **独立实现**——自己的 Riccati-Bessel 求值路径,
不 import scattering.py 的 mie_ab。否则 BH vs Akimov 交叉验证失去意义。
故此处重新用 scipy.special 从头算 psi/xi（与 scattering.py 是两份平行代码,
只共用 scipy 底层特殊函数, 这是刻意的: 交叉验证检验的是"两条公式形式"
是否等价, 底层特殊函数用同一个 scipy 是合理的共同信赖基）。

记号: q_e = x（外部尺寸参数）, q_i = m x（内部宗量）, m = sqrt(eps_i/eps_e)。

Akimov 式（显式 q_i, q_e 因子）:
  a_l = [ q_i psi_l(q_i) psi_l'(q_e) - q_e psi_l(q_e) psi_l'(q_i) ]
        / [ q_i psi_l(q_i) xi_l'(q_e) - q_e xi_l(q_e) psi_l'(q_i) ]
  b_l = [ q_e psi_l(q_i) psi_l'(q_e) - q_i psi_l(q_e) psi_l'(q_i) ]
        / [ q_e psi_l(q_i) xi_l'(q_e) - q_i xi_l(q_e) psi_l'(q_i) ]
"""
from __future__ import annotations

from scipy.special import spherical_jn, spherical_yn

__all__ = ["akimov_ab"]


def _psi(l: int, z: complex):
    """独立 Riccati-Bessel psi_l(z)=z j_l(z) 及导数（对宗量）。"""
    jl = spherical_jn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    return z * jl, jl + z * jlp


def _xi(l: int, z: complex):
    """独立 Riccati-Bessel xi_l(z)=z h_l^(1)(z)=z(j_l+i y_l) 及导数。"""
    jl = spherical_jn(l, z)
    yl = spherical_yn(l, z)
    jlp = spherical_jn(l, z, derivative=True)
    ylp = spherical_yn(l, z, derivative=True)
    h1 = jl + 1j * yl
    h1p = jlp + 1j * ylp
    return z * h1, h1 + z * h1p


def akimov_ab(l: int, m: complex, x: float):
    """Akimov 显式 q_i,q_e 形式的 (a_l, b_l).

    参数
      l : 阶数
      m : 相对折射率
      x : q_e（外部尺寸参数）
    返回 (a_l, b_l)。
    """
    q_e = x
    q_i = complex(m) * x

    psi_qi, psip_qi = _psi(l, q_i)
    psi_qe, psip_qe = _psi(l, q_e)
    xi_qe, xip_qe = _xi(l, q_e)

    a_num = q_i * psi_qi * psip_qe - q_e * psi_qe * psip_qi
    a_den = q_i * psi_qi * xip_qe - q_e * xi_qe * psip_qi
    b_num = q_e * psi_qi * psip_qe - q_i * psi_qe * psip_qi
    b_den = q_e * psi_qi * xip_qe - q_i * xi_qe * psip_qi

    return a_num / a_den, b_num / b_den
