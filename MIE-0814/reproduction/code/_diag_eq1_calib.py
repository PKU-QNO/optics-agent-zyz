# -*- coding: utf-8 -*-
"""验证：用 Alaee Eq.1 真系数（幂次固定，常数由小 x 极限标定一次）能否让表2 全 x 对齐 Mie。

原理：Eq.1 给出 C_sca 对多极矩的正确幂次依赖（ED∝k⁴|p|²、MD∝k⁴|m|²/c²、
EQ/MQ∝k⁶|Q|²）。表2 精确矩 + Eq.1 = 全程无近似，应在所有 x（含共振区）成立。
这里不手推 K_mp 的解析常数（避免 c/ε₀/π 出错），而是在小 x（表2=Mie 精确解）
数值标定一次 K_mp = C_mie/(x^n·|mom|²)，然后检验 K_mp 是否在全部 x 恒定：
  - 恒定   => Eq.1 幂次正确 + 矩正确，用此 K_mp 即可（比 Eq.1 还稳，吸收了所有常数）。
  - 共振区漂移 => 才是矩/积分本身的问题。
对比上表（_diag_table2）：那里 K 在共振区剧烈漂移（拟合幂次错）；若此处 K 恒定，
证明换 Eq.1 幂次即修复。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from baseline_mie import mie_coefficients
from multipole_moments import table2_multipole_moments

# Eq.1 幂次：ED|p|²∝k⁴(x⁴? 见下), 用「矩已含 1/iω 前置」的无量纲 p̃：
# 实测标定用小 x 反推，幂次取代码现有 POW（拟合时用过的），先做对照；
# 再改 Eq.1 物理幂次重标定对比。
M, NMAX, GRID = 2.5, 7, (24, 24, 48)

def mie_per_multipole(x):
    an, bn = mie_coefficients(x, M, NMAX)
    return {'ED': 3*abs(an[0])**2, 'MD': 3*abs(bn[0])**2,
            'EQ': 5*abs(an[1])**2, 'MQ': 5*abs(bn[1])**2}

def moments_mag(x):
    mom = table2_multipole_moments(x, M, NMAX, *GRID)
    return {'ED': np.sum(np.abs(mom['p'])**2), 'MD': np.sum(np.abs(mom['m'])**2),
            'EQ': np.sum(np.abs(mom['Qe'])**2), 'MQ': np.sum(np.abs(mom['Qm'])**2)}

# 参考点：x=0.2（小 x，表2=Mie 精确），在此标定 K_mp
s_ref = 0.2
x_ref = np.pi * s_ref
mie_ref = mie_per_multipole(x_ref)
mag_ref = moments_mag(x_ref)

# 尝试两组幂次：(A) 现有拟合幂次 (B) Eq.1 物理幂次
# 注：矩 p̃ 已含 k 依赖（J̃=(εr-1)E 不含 k，但前置 -1/iω ~ 1/k），
#     正确幂次需数值辨识——这里直接扫描候选幂次，找使 K 全 x 恒定的那个。
for label, POW in [('A 现有拟合幂次', {'ED':6,'MD':8,'EQ':8,'MQ':10}),
                    ('B 试 k⁴ 统一(矩含1/k)', {'ED':4,'MD':4,'EQ':6,'MQ':6}),
                    ('C 试 +2', {'ED':8,'MD':8,'EQ':10,'MQ':10})]:
    K0 = {k: mie_ref[k]/(x_ref**POW[k]*mag_ref[k]) for k in POW}
    print(f"\n=== {label} {POW} | K(标定于x=0.2): " +
          " ".join(f"{k}={K0[k]:.3e}" for k in POW))
    print(f"{'2a/l':>6} | " + " ".join(f"{k}:K/K0" for k in POW))
    for s in [0.2, 0.3, 0.385, 0.5, 0.6, 0.65, 0.7, 0.8, 1.0]:
        x = np.pi*s
        mie = mie_per_multipole(x); mag = moments_mag(x)
        row = []
        for k in POW:
            K = mie[k]/(x**POW[k]*mag[k])
            row.append(f"{K/K0[k]:6.2f}")
        print(f"{s:6.3f} | " + " ".join(f"{c:>14}" for c in row))
    print("判读：K/K0 恒≈1 => 该幂次正确(矩对,可用); 共振区漂移 => 幂次仍错。")
