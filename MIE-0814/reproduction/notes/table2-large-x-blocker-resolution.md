# Alaee 2018 表2“大 $x$ 失效”根因与解阻报告

## 结论

表2 大 $x$ 失效的最终根因是坐标分量误写。旧实现把

$$
u_x=\sin\theta\cos\phi,\quad
u_y=\sin\theta\sin\phi,\quad
u_z=\cos\theta
$$

当成了 $r_\alpha/a$；正确关系是

$$
\frac{r_x}{a}=U\sin\theta\cos\phi,\quad
\frac{r_y}{a}=U\sin\theta\sin\phi,\quad
\frac{r_z}{a}=U\cos\theta.
$$

因此旧 ED 的 $\mathbf r\cdot\mathbf J$ 和 $\mathbf r_\alpha$ 各少一个径向因子，旧 MD 的 $\mathbf r\times\mathbf J$ 少一个，EQ/MQ 的张量组合少一个或两个。小 $x$ 的经验常数把这一错误遮住了；在共振和大 $x$ 区，错误的径向相消被破坏，导致表2/Mie 比值崩溃。

## 波数与核

自由空间 Green 函数的辐射展开决定表2球 Bessel 核使用 host 波数：

$$
\rho=k_{\rm host}r=x_{\rm mie}U.
$$

内部波数 $k_{\rm in}=m k_{\rm host}$ 只通过内部场 $E_{\rm in}(r)$ 进入电流空间结构。代码保留 `kernel_k="internal"` 作为反例诊断，但默认值为 `"host"`。在 $2a/\lambda=0.65$ 的粗验收网格，错误 `k_in` 分支的 ED/Mie 比值约为 $390.85$，而 host-k 为 $0.9931$。

## ED 中间形式与界面项

讲义 §11 的 `p_partial` 与对称无迹 ED 形式只有在对紧支撑电流作完整分部积分（包括球面界面分布/表面项）时才可互换。把有限球内部的普通体函数逐点代入 `p_partial`，在修正坐标后仍不能作为表2对称式的逐点替代；因此本实现继续采用论文表2的对称无迹体积分，并把 `multipole_ppartial.py` 限定为诊断路径。这个结果排除了“只需给表2补一个经验边界常数”的解释。

## Eq.1 解析归一化

当前矩定义为 $\widetilde{\mathbf J}=(\epsilon_r-1)\mathbf E_{\rm in}$，并取 $a=1$。将 $J=-i\omega\epsilon_0\widetilde J$ 代回 Alaee Eq.1、再按 $\lambda^2/(2\pi)$ 归一化后，代码使用：

$$
C_{\rm ED}=\frac{x^6}{12\pi^2}\sum_\alpha|p_\alpha|^2,\quad
C_{\rm MD}=\frac{x^8}{12\pi^2}\sum_\alpha|m_\alpha|^2,
$$

$$
C_{\rm EQ}=\frac{x^8}{1440\pi^2}\sum_{\alpha\beta}|Q^e_{\alpha\beta}|^2,\quad
C_{\rm MQ}=\frac{x^{10}}{1440\pi^2}\sum_{\alpha\beta}|Q^m_{\alpha\beta}|^2.
$$

旧的 `.00865/.00558/.000042/.000008` 已删除。

## 数值验收

高精度网格为 `(Nu,Nθ,Nφ)=(40,41,80)`：$\phi$ 使用不含重复端点的周期求和，$U$ 与 $\theta$ 使用 Simpson。九个指定点的四通道最大偏差为 $0.174\%$（$s=2a/\lambda=0.8$ 的 EQ）；准静态点 $s=0.2,0.3$ 的最大偏差为 $0.0033\%$。

200 点均匀扫描 $s\in[0.2,1.0]$（同一网格）得到：

| 通道 | 最大相对误差 | 位置 $s$ |
|---|---:|---:|
| ED | 0.9624% | 0.66231 |
| MD | 0.03834% | 1.00000 |
| EQ | 0.6157% | 0.79497 |
| MQ | 0.6585% | 0.91558 |

三个加密锚点 $x_{\rm mie}\approx2.042,2.513,3.142$ 的四通道误差均小于 2%。原有测试 `20 passed`；扩展后的快速回归为 `33 passed`，200 点扫描作为显式慢测运行。

## 外部来源审计（备选路线）

- 论文：[Alaee et al., arXiv:1701.00755](https://arxiv.org/abs/1701.00755)。
- 作者仓库：[RasoulAlaee/exact_multipoles](https://github.com/RasoulAlaee/exact_multipoles)：仅有 Mathematica 多极积分 notebook，没有独立球体 Mie 验收脚本。
- 独立实现：[MENP](https://github.com/Hinamoooon/MENP)，`MENP/exactME.m` 核对到 host $k=\omega/c$、表2四式、电流定义和 Eq.1；`demo_sphere/demo_exact.csv` 提供球体示例。
- [MDS: Multipole Decomposition for Scattering](https://github.com/HUST-CPO/Multipole-Decomposition-for-Scattering) 作为交叉检索来源，未被直接拷贝。

上述来源用于公式和波数交叉核验，本地 Mie 基准仍来自 `baseline_mie.py`，没有把外部数据当作验收基准。

## 修改文件与人工事项

修改：`code/multipole_moments.py`（坐标、积分器、host-k 诊断分支、Eq.1 常数）、`code/multipole_approx.py`（表1同一坐标修正）、`code/multipole_ppartial.py`（诊断路径坐标/核参数）、`code/run_fig1.py`（默认验收网格）、`tests/test_multipole.py`（九点、核、常数、共振和慢测）。`baseline_mie.py` 与 `mie_theory.py` 未修改。

修复后已用 `(40,41,80)` 网格重新生成 `data/fig1a_multipole_mie.csv`、`data/fig1a_multipole_table2.csv` 和 `data/fig1a_multipole_table1.csv`，每份均为 200 个数据行；从落盘 CSV 重新计算的最大误差与上表一致。

仍需人工判断：若要把 `p_partial` 写成包含界面分布的严格分布论实现，需要对讲义 §11/FC2015 补充材料逐项复核；本次解阻不依赖该替代路径。外部仓库的版本锁定和 Mathematica notebook 的运行环境也未纳入本地依赖。
