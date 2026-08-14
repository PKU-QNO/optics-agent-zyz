# -*- coding: utf-8 -*-
"""诊断：表2 大 x 失效的真凶是积分还是 c_sca_from_multipoles 的拟合标定。

方法：对每个 x，算表2 多极矩 -> 用 Mie 基准反推每个多极的标定常数
    K_mp(x) = C_mie_mp / (x_mie^n_mp * |moment_mp|^2)
若 K_mp(x) 随 x（尤其共振区）漂移 => 标定错（拟合 A·x^n 不普适），
   改成 Eq.1 真系数即可修复。
若 K_mp(x) 恒定但仍 != A_mp => 是积分/公式错。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from baseline_mie import mie_coefficients
from multipole_moments import table2_multipole_moments

# 各多极当前拟合用的幂次（来自 c_sca_from_multipoles）
POW = {'ED': 6, 'MD': 8, 'EQ': 8, 'MQ': 10}
# 当前拟合系数 A_mp
A_FIT = {'ED': 0.00865, 'MD': 0.00558, 'EQ': 0.000042, 'MQ': 0.000008}

M = 2.5
NMAX = 7
GRID = (24, 24, 48)  # 稍粗以求快，趋势判断足够

def mie_per_multipole(x):
    an, bn = mie_coefficients(x, M, NMAX)
    return {'ED': 3*abs(an[0])**2, 'MD': 3*abs(bn[0])**2,
            'EQ': 5*abs(an[1])**2, 'MQ': 5*abs(bn[1])**2}

print(f"{'2a/l':>6} {'x_mie':>6} | " + " ".join(f"{k:>22}" for k in POW))
print("     (每格: K(x)=C_mie/(x^n|mom|^2), 括号=K/A_fit, A_fit是当前拟合值)")
for s in [0.2, 0.3, 0.385, 0.5, 0.6, 0.65, 0.7, 0.8, 1.0]:
    x = np.pi * s
    mom = table2_multipole_moments(x, M, NMAX, *GRID)
    mie = mie_per_multipole(x)
    mag = {'ED': np.sum(np.abs(mom['p'])**2), 'MD': np.sum(np.abs(mom['m'])**2),
           'EQ': np.sum(np.abs(mom['Qe'])**2), 'MQ': np.sum(np.abs(mom['Qm'])**2)}
    cells = []
    for k in POW:
        K = mie[k] / (x**POW[k] * mag[k])
        cells.append(f"{K:9.3e}({K/A_FIT[k]:6.2f})")
    print(f"{s:6.3f} {x:6.3f} | " + " ".join(f"{c:>22}" for c in cells))
print("\n判读：括号=K/A_fit。若远离1（尤其0.5/0.65共振区）且随x变 => 拟合标定错（诊断成立）。")
print("若括号≈常数但!=1 => 积分缺整体常数。若括号恒≈1 => 标定竟对，需查别处。")
