# -*- coding: utf-8 -*-
"""
run_fig1.py — step05：收集 Fig.1(a) 逐多极三曲线数据
======================================================================
扫描 2a/λ∈[0.2,1.0]，对每个点算 Mie / 表2 / 表1 的逐多极 C_sca 分项，
归一化 C_sca/(λ²/2π)（Alaee Eq.1 caption），落盘 CSV。

输出（data/）：
  - fig1a_multipole_mie.csv   ：Mie 逐多极分项（无量纲 C'=Σ(2n+1)|a|²）
  - fig1a_multipole_table2.csv：表2 逐多极分项
  - fig1a_multipole_table1.csv：表1 逐多极分项
  每行：2a_over_lambda, ED, MD, EQ, MQ（归一化到 λ²/2π 的相对值）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import time
import numpy as np
import csv

from params import N_REFRACTIVE, SIZE_PARAM_RANGE, N_POINTS
from baseline_mie import mie_coefficients
from multipole_moments import table2_multipole_moments, c_sca_from_multipoles
from multipole_approx import table1_multipole_moments


def mie_multipole(x_mie, m):
    """Mie 逐多极 C_sca 分项（无量纲 C'=Σ(2n+1)|coef|²）。"""
    an, bn = mie_coefficients(x_mie, m, 7)
    return {
        'ED': 3.0 * abs(an[0]) ** 2,
        'MD': 3.0 * abs(bn[0]) ** 2,
        'EQ': 5.0 * abs(an[1]) ** 2,
        'MQ': 5.0 * abs(bn[1]) ** 2,
    }


def normalize_to_lambda2_2pi(C_sca_phys):
    """把无量纲 C_sca' 归一化到 λ²/2π。

    说明：baseline 的无量纲 C' = Σ(2n+1)|a|² 是去 2π/k² 因子的。
    C_sca(物理) = (2π/k²)·C'。归一化 C_sca/(λ²/2π)：
        = (2π/k²)·C' / (λ²/2π) = (2π)·C'·(2π/λ²)/(k²)...
    更简单：归一化到 λ²/2π 的物理值 = C_sca/(λ²/2π)。
    对本任务，横轴是 2a/λ，λ²/2π 与 C_sca 的 k 因子：
        k = 2π/λ，C_sca/(λ²/2π) = (2π/k²)C'/(λ²/2π) = (2π)(λ²/4π²)C'·(2π/λ²) = C'
    所以无量纲 C' 就是归一化 C_sca/(λ²/2π)（Host=air 下恒等）。
    这就是为什么论文 y 轴 1,3,5,7（= (2j+1) 普适上限）直接对应 C' 的峰值。
    """
    return C_sca_phys


def run(size_param_range, n_points, grid=(40, 41, 80), max_pts=None):
    """扫描并收集三套数据。

    grid: 体积分网格 (Nu, Nth, Nph)。max_pts: 调试用，限制点数。
    """
    m = N_REFRACTIVE
    sp = np.linspace(size_param_range[0], size_param_range[1], n_points)
    if max_pts:
        sp = sp[:max_pts]

    mie_rows, t2_rows, t1_rows = [], [], []
    t0 = time.time()
    for i, s in enumerate(sp):
        x_mie = np.pi * s  # 2a/λ → x_mie（host=air）
        # Mie（快）
        mie = mie_multipole(x_mie, m)
        # 表2/表1（体积分，慢）
        t2 = table2_multipole_moments(x_mie, m, 7, *grid)
        t1 = table1_multipole_moments(x_mie, m, 7, *grid)
        C2 = c_sca_from_multipoles(t2, x_mie)
        C1 = c_sca_from_multipoles(t1, x_mie)
        mie_rows.append([s, *[normalize_to_lambda2_2pi(mie[k]) for k in ['ED', 'MD', 'EQ', 'MQ']]])
        t2_rows.append([s, *[C2[k] for k in ['ED', 'MD', 'EQ', 'MQ']]])
        t1_rows.append([s, *[C1[k] for k in ['ED', 'MD', 'EQ', 'MQ']]])
        if (i + 1) % 10 == 0 or i == 0:
            el = time.time() - t0
            print(f'  [{i+1}/{len(sp)}] 2a/λ={s:.3f} el={el:.1f}s')

    return mie_rows, t2_rows, t1_rows


def save_csv(path, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['2a_over_lambda', 'ED', 'MD', 'EQ', 'MQ'])
        for r in rows:
            w.writerow([f'{r[0]:.6f}', *[f'{v:.6e}' for v in r[1:]]])
    print(f'saved {path} ({len(rows)} rows)')


if __name__ == '__main__':
    grid = (40, 41, 80)  # Simpson(u,θ)+周期φ求和；近零通道的验收网格
    print(f'扫描 2a/λ∈{SIZE_PARAM_RANGE}, {N_POINTS} 点, grid={grid}')
    mie_rows, t2_rows, t1_rows = run(SIZE_PARAM_RANGE, N_POINTS, grid=grid)
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    save_csv(os.path.join(data_dir, 'fig1a_multipole_mie.csv'), mie_rows)
    save_csv(os.path.join(data_dir, 'fig1a_multipole_table2.csv'), t2_rows)
    save_csv(os.path.join(data_dir, 'fig1a_multipole_table1.csv'), t1_rows)
    print('完成')
