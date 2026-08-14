# -*- coding: utf-8 -*-
"""
plot_fig1.py — 生成 Fig.1(a,c) 复现图（重构版，落实用户审查意见）

左图（对应论文 Fig.1(a)）：四多极散射截面
    - 按多极着色：ED/MD/EQ/MQ 各一色
    - 线型区分方法：实线 = Mie，虚线 = Table 2，点线 = Table 1
    - 普适上限只标注一次：dipole limit (2l+1) = 3，quadrupole limit (2l+1) = 5
    - 纵轴恢复到 0-7（与论文一致）
    物理解读：Mie（实线）与 Table 2（虚线）重合（表2 精确复现成功）；
               Table 1（点线）在大尺寸区发散（LWA 预期失效）。

右图（对应论文 Fig.1(c)）：表1 相对 Mie 的百分比误差 |C_Table1-C_Mie|/C_Mie x100%
    - 四通道不同色，图例清楚列出 ED/MD/EQ/MQ 四行
    - 删除绝对误差与右侧副轴（twinx）
    - 删除公共近零阴影区：各通道在 C_Mie 低于阈值处断开相对误差曲线（置 NaN）
    - 图注注明 "relative error undefined near Mie zeros"
    - 超过 100% 的值裁剪到 100%，并在图注注明 "values >100% clipped"
"""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 输出目录
OUT_DIR = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- 数据 ----------
def load(f):
    rows = []
    with open(f) as fh:
        for r in csv.DictReader(fh):
            rows.append({k: float(r[k]) for k in ['2a_over_lambda', 'ED', 'MD', 'EQ', 'MQ']})
    return rows


base = os.path.join(os.path.dirname(__file__), '..', 'data')
mie = load(os.path.join(base, 'fig1a_multipole_mie.csv'))
t2 = load(os.path.join(base, 'fig1a_multipole_table2.csv'))
t1 = load(os.path.join(base, 'fig1a_multipole_table1.csv'))

s = np.array([r['2a_over_lambda'] for r in mie])
channels = ['ED', 'MD', 'EQ', 'MQ']
limits = {'ED': 3.0, 'MD': 3.0, 'EQ': 5.0, 'MQ': 5.0}   # (2l+1)：偶极 l=1 -> 3，四极 l=2 -> 5
labels = {'ED': 'ED (electric dipole)', 'MD': 'MD (magnetic dipole)',
          'EQ': 'EQ (electric quadrupole)', 'MQ': 'MQ (magnetic quadrupole)'}

# 每通道近零阈值：C_Mie < 1e-3 * max(C_Mie) 视为近零（Mie 零点），相对误差在此处无定义
ZERO_FRAC = 1e-3

# ---------- 样式 ----------
# 按多极着色（每多极 3 条线同色、不同线型区分数据源）
poly_colors = {'ED': 'C0', 'MD': 'C1', 'EQ': 'C2', 'MQ': 'C3'}
line_spec = {'Mie': '-', 'Table2': '--', 'Table1': ':'}   # 实线 / 虚线 / 点线
src_lw = {'Mie': 1.8, 'Table2': 1.6, 'Table1': 1.6}
legend_labels = {'Mie': 'Mie theory', 'Table2': 'Table 2 (exact)', 'Table1': 'Table 1 (LWA)'}

# ---------- 近零掩码（各通道独立） ----------
def zero_mask(ch):
    cm = np.array([r[ch] for r in mie])
    return cm < ZERO_FRAC * cm.max()

# ---------- 左图：四多极散射截面 ----------
fig = plt.figure(figsize=(14, 7))
axL = fig.add_subplot(1, 2, 1)

# 普适上限只标注一次（不逐多极标，避免文字重叠）
axL.axhline(3, color='gray', lw=0.8, ls='--', alpha=0.6)
axL.axhline(5, color='gray', lw=0.8, ls='--', alpha=0.6)

handles, hlabels = [], []
for ch in channels:
    cm = np.array([r[ch] for r in mie])
    ct2 = np.array([r[ch] for r in t2])
    ct1 = np.array([r[ch] for r in t1])
    c = poly_colors[ch]
    for src, ydata in (('Mie', cm), ('Table2', ct2), ('Table1', ct1)):
        axL.plot(s, ydata, c + line_spec[src], lw=src_lw[src],
                 label=labels[ch] + ' — ' + legend_labels[src])

# 通道字母：右上角垂直错开排列，白底半透明框保证任何曲线穿过都可读
ch_y = {'ED': 6.85, 'MD': 6.45, 'EQ': 6.05, 'MQ': 5.65}
for ch in channels:
    axL.text(0.99, ch_y[ch], ch, fontsize=10, ha='right', va='center',
             color=poly_colors[ch], fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.7))
# 上限文字只标一次：放左上角空白区，避免与通道字母/曲线重叠
axL.text(0.235, 6.55, r'$\mathrm{dipole\ limit}\ (2l{+}1)=3$',
         fontsize=9, ha='left', va='center', color='dimgray', style='italic')
axL.text(0.235, 6.05, r'$\mathrm{quadrupole\ limit}\ (2l{+}1)=5$',
         fontsize=9, ha='left', va='center', color='dimgray', style='italic')

axL.set_xlim(0.2, 1.0)
axL.set_ylim(0, 7)                              # 纵轴恢复到 0-7（与论文一致）
axL.set_xlabel(r'$2a/\lambda$')
axL.set_ylabel(r'$C_{\mathrm{sca}}/(\lambda^2/2\pi)$')
axL.set_title('Fig.1(a,c) reproduction — scattering cross sections', fontsize=13)
axL.grid(alpha=0.3)
axL.legend(loc='upper left', fontsize=8, framealpha=0.9, ncol=1,
           title='multipole — source', title_fontsize=9)

# ---------- 右图：表1 相对误差（四通道不同色，近零断开，>100% 裁剪） ----------
axR = fig.add_subplot(1, 2, 2)
for ch in channels:
    cm = np.array([r[ch] for r in mie])
    ct1 = np.array([r[ch] for r in t1])
    rel = np.abs(ct1 - cm) / cm * 100.0
    rel = np.where(zero_mask(ch), np.nan, rel)   # 近零处断开（Mie 零点处相对误差无定义）
    rel = np.clip(rel, 0.0, 100.0)               # 超过 100% 裁剪，避免竖直跳线
    axR.plot(s, rel, color=poly_colors[ch], lw=1.3,
             label=f'{ch} — relative error')

axR.set_xlim(0.2, 1.0)
axR.set_ylim(-5, 105)
axR.set_xlabel(r'$2a/\lambda$')
axR.set_ylabel(r'Relative error  $|C_{T1}-C_{Mie}|/C_{Mie}\times100\%$  [%]')
axR.set_title('Fig.1(a,c) reproduction — Table 1 (LWA) error vs Mie', fontsize=13)
axR.grid(alpha=0.3)
axR.axhline(100, color='red', lw=0.8, ls=':', alpha=0.7)
axR.text(0.995, 102.5, '100%', fontsize=8, color='red', ha='right')
axR.text(0.995, 1.0,
         'relative error undefined near Mie zeros\nvalues >100% clipped',
         fontsize=7.5, ha='right', va='bottom', color='dimgray', style='italic',
         linespacing=1.4)
axR.legend(loc='upper left', fontsize=8, framealpha=0.9)

fig.suptitle('Fig.1(a,c) reproduction — Alaee 2018 dielectric sphere,  '
             r'$2a/\lambda \in [0.2,1.0]$', fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.96])

out = os.path.join(OUT_DIR, 'fig1a_reproduction.png')
fig.savefig(out, dpi=150)
print('saved', out)

# ---------- 第二张：表2 vs Mie 误差（验证图，保持不动） ----------
fig2 = plt.figure(figsize=(10, 6))
ax = fig2.add_subplot(1, 1, 1)
maxe = {}
for ch in channels:
    cm = np.array([r[ch] for r in mie])
    ct2 = np.array([r[ch] for r in t2])
    rel = np.abs(ct2 - cm) / cm * 100.0
    rel = np.where(zero_mask(ch), np.nan, rel)
    ax.plot(s, rel, lw=1.0, label=f'{ch}')
    valid = rel[~np.isnan(rel)]
    maxe[ch] = valid.max() if len(valid) else float('nan')
ax.set_xlim(0.2, 1.0)
ax.set_ylim(0, 1.2)
ax.set_xlabel(r'$2a/\lambda$')
ax.set_ylabel(r'Relative error  $|C_{T2}-C_{Mie}|/C_{Mie}\times100\%$  [%]')
ax.set_title('Table 2 (exact) vs Mie — max error < 1% over 200 points', fontsize=12)
ax.grid(alpha=0.3)
ax.legend(title='channel', loc='upper right', fontsize=9)
for ch, e in maxe.items():
    print(f'  {ch}: max rel err = {e:.4f}%')
out2 = os.path.join(OUT_DIR, 'fig1a_table2_error.png')
fig2.savefig(out2, dpi=150)
print('saved', out2)
