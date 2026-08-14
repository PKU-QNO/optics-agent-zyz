# -*- coding: utf-8 -*-
"""分离诊断：内部场在共振区(x_mie~1.57)是否仍与 miepython 一致。

盲区：test_xmie 的 miepython 逐点验证只在 x_mie=0.7 做过；表2 失效在 x_mie≥1.6。
若内部场在共振区偏 => 根因是内部场，不是表2 积分。
若内部场在共振区仍准 => 才是表2 积分/公式问题。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import miepython
from mie_theory import internal_E_field

M = 2.5
a = 1.0
# 覆盖准静态(0.7)、ED共振(π/2≈1.571)、失效区(2.04, 2.51)
for x_mie in [0.7, np.pi*0.5, np.pi*0.65, np.pi*0.8]:
    lam = 2*np.pi*a/x_mie
    errs = []
    for (u,th,ph) in [(0.3,0.5,0.8),(0.5,0.785,0.927),(0.7,1.2,2.0),
                       (0.9,0.3,4.0),(0.95,1.0,1.0),(0.6,1.5,5.0)]:
        rr=np.array([[[u]]]);tt=np.array([[[th]]]);pp=np.array([[[ph]]])
        Ex,Ey,Ez = internal_E_field(x_mie,M,10,rr,tt,pp)
        xc=u*np.sin(th)*np.cos(ph);yc=u*np.sin(th)*np.sin(ph);zc=u*np.cos(th)
        E_mp = miepython.e_near_cartesian(lam,2*a,M,1.0,xc,yc,zc,include_incident=False)
        E_mine=np.array([Ex[0,0,0],Ey[0,0,0],Ez[0,0,0]])
        errs.append(float(np.max(np.abs(E_mine-E_mp))))
    print(f"x_mie={x_mie:.3f} (2a/λ={x_mie/np.pi:.3f}): max|E_mine−E_miepython| = {max(errs):.3e}")
