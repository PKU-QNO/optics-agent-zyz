# Jackson Classical Electrodynamics 3rd Ed. — Chapters 4, 9, 10 结构化摘要

> 来源 OCR 文件：`Jackson_1999_Ch4_9_10.ocr/Jackson_1999_Ch4_9_10.md`（2933 行，C 级 OCR 质量）
> 用途：mie-f 理论复现（Grahn 2012 / Alaee 2018）的 Jackson 公式参考
> 摘要涵盖：Ch4 静电多极子、Ch9 电磁辐射多极展开、Ch10 散射与衍射

---

## 1. 内容索引

### 第 4 章 — 静电多极子（Electrostatic Multipoles）

| 节号 | 标题 | 内容概要 |
|------|------|---------|
| 4.1 | Multipole Expansion of Potential | 电势 $\Phi(\mathbf{x})$ 的球谐展开：$\Phi(\mathbf{x}) = \frac{1}{4\pi\epsilon_0}\sum_{l,m}\frac{4\pi}{2l+1}q_{lm}\frac{Y_{lm}(\theta,\phi)}{r^{l+1}}$ |
| 4.2 | Multipole Moments | 球多极矩 $q_{lm} = \int r^l Y_{lm}^*(\theta',\phi')\rho(\mathbf{x}')d^3x'$；$q_{00}=Q$（总电荷），$q_{1m}$ 与 Cartesian 偶极矩 $\mathbf{p}$ 的关系，$q_{2m}$ 与四极矩 $Q_{ij}$ 的关系 |
| 4.3 | Energy and Force in External Fields | 多极子在外部场中的能量：$W = qV(0) - \mathbf{p}\cdot\mathbf{E}(0) - \frac{1}{6}\sum_{ij}Q_{ij}\frac{\partial E_j}{\partial x_i}(0) + ...$ |
| 4.4 | Dielectric Sphere in Uniform Field | 均匀场中介电球的极化；Clausius-Mossotti 关系；永久极化球 |
| 4.5–4.6 | Boundary Value Problems | 球/圆柱边值问题的多极展开解法 |
| 4.7 | Energy in Multipole Expansion | 系统自能和相互作用能的多极展开 |
| 4.8–4.9 | Additional Topics | 镜像法、球谐函数加法 |

### 第 9 章 — 电磁辐射多极展开（Multipole Expansion of EM Fields）

| 节号 | 标题 | 内容概要 |
|------|------|---------|
| 9.1 | Radiation Fields from Sources | 推迟势解；辐射区 $1/r$ 场；矢量球谐函数 $\mathbf{X}_{lm}$ 引入 |
| 9.2 | Electric Dipole Radiation | Hertz 偶极子辐射场 (9.18–9.20)，总功率 (9.23)，中心馈电短天线 |
| 9.3 | Magnetic Dipole and Electric Quadrupole | 磁偶极辐射场 (9.30–9.36)，电四极辐射场 (9.37–9.41)，多极之间干涉 |
| 9.4 | General Multipole Expansion | 矢量球谐函数 $\mathbf{X}_{lm} = \mathbf{L}Y_{lm}/\sqrt{l(l+1)}$，$\mathbf{L} = -i\mathbf{r}\times\nabla$；电场多极 (TM) 与磁场多极 (TE) 的通解形式 (9.122) |
| 9.5 | Multipole Coefficients | 源积分形式：$a_E(l,m)$ 和 $a_M(l,m)$ 由源电流 $\mathbf{J}$ 和磁化 $\mathbf{M}$ 的积分给出 (9.165)；长波极限下化为多极矩 (9.169–9.176) |
| 9.6 | Angular Distribution of Radiation | $\frac{dP}{d\Omega} = \frac{Z_0}{2k^2}\big|\sum_{l,m}(-i)^{l+1}[a_E(l,m)\mathbf{X}_{lm} + a_M(l,m)\mathbf{n}\times\mathbf{X}_{lm}]\big|^2$；总功率 $P = \frac{Z_0}{2k^2}\sum_{l,m}(|a_E|^2 + |a_M|^2)$ |
| 9.7 | Angular Momentum of Radiation | 辐射携带角动量：$\frac{dM_z}{dt} = \frac{m}{\omega}\frac{dU}{dt}$ 对纯 $(l,m)$ 模 |
| 9.8 | Parity of Multipole Fields | 电多极 (TM)：$\mathbf{H}$ 宇称 $(-1)^l$，$\mathbf{E}$ 宇称 $(-1)^{l+1}$；磁多极 (TE) 相反 |
| 9.9 | Aperture Coupling | 小孔衍射的有效偶极矩 $\mathbf{p}_{\text{eff}}, \mathbf{m}_{\text{eff}}$；极化率 |
| 9.10 | Problems | 天线、波导激励、谐振腔、球形腔 $Q$ 值 |

### 第 10 章 — 散射与衍射（Scattering and Diffraction）

| 节号 | 标题 | 内容概要 |
|------|------|---------|
| 10.1 | Scattering at Long Wavelengths | 小散射体的偶极近似；散射截面、Rayleigh 定律 ($\omega^4$) |
| 10.1B | Small Dielectric Sphere | 电偶极散射，微分散射截面 (10.6–10.10)，总散射截面 (10.11)，极化 (10.9) |
| 10.1C | Small Conducting Sphere | 电偶极 + 磁偶极干涉；微分截面 (10.13–10.16)，向后增强 |
| 10.1D | Collection of Scatterers | 结构因子 $\mathcal{F}(\mathbf{q})$，相干/非相干叠加 |
| 10.2 | Perturbation Theory of Scattering | Born 近似；$\delta\epsilon$, $\delta\mu$ 微扰；散射振幅 (10.27–10.31) |
| 10.2C | Blue Sky | Rayleigh 散射解释蓝天；衰减系数 (10.35)；大气散射 |
| 10.2D | Density Fluctuations | Einstein-Smoluchowski 公式 (10.40)；临界乳光 |
| 10.2E | Optical Fibers | 光纤中 Rayleigh 散射极限；衰减约 $0.85/[\lambda(\mu\text{m})]^4$ dB/km |
| 10.3 | Spherical Wave Expansion of Plane Wave | 平面波的球面波展开 (10.44–10.55)；$m=\pm1$ 对应圆极化 |
| 10.4 | Scattering by a Sphere | Mie 散射的球谐展开；散射系数 $\alpha_\pm(l), \beta_\pm(l)$；散射/吸收截面 (10.62–10.63)；完美导体球的 $ka\ll1$ 极限 |
| 10.11 | Optical Theorem | 光学定理 $\sigma_t = \frac{4\pi}{k}\text{Im}[\epsilon_0^*\cdot\mathbf{f}(\mathbf{k}=\mathbf{k}_0)]$；前向散射振幅与介电常数的关系 (10.146) |

---

## 2. 关键公式/概念索引

### 2.1 球谐函数与矢量球谐函数

| 公式 | 说明 | 位置 |
|------|------|------|
| $\mathbf{L} = -i\mathbf{r}\times\nabla$ | 角动量算符 | (9.99) |
| $\mathbf{X}_{lm} = \mathbf{L}Y_{lm}/\sqrt{l(l+1)}$ | 矢量球谐函数定义 | (9.119) |
| $\int \mathbf{X}_{l'm'}^*\cdot\mathbf{X}_{lm}d\Omega = \delta_{ll'}\delta_{mm'}$ | 正交归一性 | (9.120) |
| $\mathbf{n}\cdot\mathbf{X}_{lm}=0$ | 横向性 | — |

### 2.2 球 Bessel 函数

| 公式 | 说明 | 位置 |
|------|------|------|
| $j_l(\rho), n_l(\rho), h_l^{(1,2)}(\rho) = j_l \pm i n_l$ | 定义 | (9.84) |
| $j_0=\sin\rho/\rho, j_1=\sin\rho/\rho^2 - \cos\rho/\rho$, ... | 低阶显式 | (9.87) |
| 小参数：$j_l(\rho)\to\rho^l/(2l+1)!!$, $n_l(\rho)\to-(2l-1)!!/\rho^{l+1}$ | 小参数渐近 | (9.88) |
| 大参数：$h_l^{(1)}(\rho)\to(-i)^{l+1}e^{i\rho}/\rho$ | 大参数渐近 | (9.89) |
| $j_{l-1}+j_{l+1} = (2l+1)j_l/\rho$ | 递推关系 | (9.90) |

### 2.3 静态多极展开

| 公式 | 说明 | 位置 |
|------|------|------|
| $\Phi(\mathbf{x}) = \frac{1}{4\pi\epsilon_0}\sum_{l,m}\frac{4\pi}{2l+1}q_{lm}\frac{Y_{lm}}{r^{l+1}}$ | 电势多极展开 | (4.1–4.2) |
| $q_{lm} = \int r'^l Y_{lm}^*(\theta',\phi')\rho(\mathbf{x}')d^3x'$ | 球多极矩定义 | (4.3) |
| $q_{00} = \frac{1}{\sqrt{4\pi}}Q$ | 单极子（总电荷） | — |
| $\mathbf{p}$ 与 $q_{1m}$ 关系 | $q_{11}=-\sqrt{\frac{3}{8\pi}}(p_x-ip_y), q_{10}=\sqrt{\frac{3}{4\pi}}p_z$ | (4.6–4.7) |
| $Q_{ij}$ 与 $q_{2m}$ 关系 | $q_{20}=\frac{1}{2}\sqrt{\frac{5}{4\pi}}Q_{33}$, etc. | (4.9) |
| $W = qV(0) - \mathbf{p}\cdot\mathbf{E}(0) - \frac{1}{6}\sum_{ij}Q_{ij}\frac{\partial E_j}{\partial x_i}(0)+...$ | 多极子在外部场中的能量 | (4.24) |
| $U = \frac{1}{4\pi\epsilon_0}\left[\frac{\mathbf{p}_1\cdot\mathbf{p}_2}{r^3} - 3\frac{(\mathbf{p}_1\cdot\mathbf{r})(\mathbf{p}_2\cdot\mathbf{r})}{r^5}\right]$ | 两个偶极子相互作用能 | (4.27) |

### 2.4 辐射多极展开

| 公式 | 说明 | 位置 |
|------|------|------|
| $\mathbf{E} = \sum_{lm}[a_E(l,m)f_l(kr)\mathbf{X}_{lm} + \frac{i}{k}a_M(l,m)\nabla\times g_l(kr)\mathbf{X}_{lm}]$ | 电场通解 | (9.122) |
| $\mathbf{H} = \frac{1}{Z_0}\sum_{lm}[a_M(l,m)g_l(kr)\mathbf{X}_{lm} - \frac{i}{k}a_E(l,m)\nabla\times f_l(kr)\mathbf{X}_{lm}]$ | 磁场通解 | (9.122) |
| $a_E(l,m) = \frac{k^2}{i\sqrt{l(l+1)}}\int Y_{lm}^* j_l(kr)[\cdots]d^3x$ | 电多极系数（源积分） | (9.165) **关键** |
| $a_M(l,m) = -\frac{k^2}{\sqrt{l(l+1)}}\int Y_{lm}^* j_l(kr)[\cdots]d^3x$ | 磁多极系数（源积分） | (9.165) **关键** |
| 长波：$a_E(l,m) \propto k^{l+2}(Q_{lm}+Q'_{lm})$ | 长波极限下化为多极矩 | (9.169–9.176) |
| $\frac{dP}{d\Omega} = \frac{Z_0}{2k^2}|\sum_{l,m}(-i)^{l+1}[a_E\mathbf{X}_{lm} + a_M\mathbf{n}\times\mathbf{X}_{lm}]|^2$ | 辐射角分布 | (9.151) |
| $P = \frac{Z_0}{2k^2}\sum_{l,m}(|a_E|^2 + |a_M|^2)$ | 总辐射功率 | (9.152) |
| $\frac{dM_z}{dt} = \frac{m}{\omega}\frac{dU}{dt}$ | 每光子角动量 $m\hbar$ | — |

### 2.5 散射理论

| 公式 | 说明 | 位置 |
|------|------|------|
| $\frac{d\sigma}{d\Omega} = k^4 a^6 \left|\frac{\epsilon_r-1}{\epsilon_r+2}\right|^2 \frac{1}{2}(1+\cos^2\theta)$ | 小介电球 Rayleigh 散射 | (10.10) |
| $\sigma = \frac{8\pi}{3}k^4 a^6\left|\frac{\epsilon_r-1}{\epsilon_r+2}\right|^2$ | 总散射截面 | (10.11) |
| $\frac{d\sigma}{d\Omega} = k^4a^6[\frac{5}{8}(1+\cos^2\theta)-\cos\theta]$ | 小导体球散射（电偶极+磁偶极干涉） | (10.16) / (10.72) |
| $\sigma_{\text{sc}} = \frac{\pi}{2k^2}\sum_l(2l+1)[|\alpha(l)|^2+|\beta(l)|^2]$ | 球散射部分波截面 | (10.62) |
| $\sigma_t = -\frac{\pi}{k^2}\sum_l(2l+1)\text{Re}[\alpha(l)+\beta(l)]$ | 总消光截面 | (10.63) |
| $\sigma_t = \frac{4\pi}{k}\text{Im}[\epsilon_0^*\cdot\mathbf{f}(\mathbf{k}=\mathbf{k}_0)]$ | 光学定理 | (10.139) |
| $\epsilon(\omega)/\epsilon_0 = 1 + \frac{4\pi N}{k^2}\epsilon_0^*\cdot\mathbf{f}(k,0)$ | 前向散射振幅与介电常数 | (10.146) |
| $e^{i\mathbf{k}\cdot\mathbf{x}} = 4\pi\sum_{lm}i^l j_l(kr)Y_{lm}^*(\theta_k,\phi_k)Y_{lm}(\theta,\phi)$ | 平面波球谐展开 | (10.43–10.44) |

### 2.6 Rayleigh 散射与衰减

| 公式 | 说明 | 位置 |
|------|------|------|
| $\alpha = N\sigma \simeq \frac{2k^4}{3\pi N}|n-1|^2$ | 气体 Rayleigh 衰减系数 | (10.35) |
| $\alpha = \frac{1}{6\pi N}\left(\frac{\omega}{c}\right)^4\left|\frac{(\epsilon_r-1)(\epsilon_r+2)}{3}\right|^2 NkT\beta_T$ | Einstein-Smoluchowski 公式（含密度涨落） | (10.40) |
| $\alpha (\text{dB/km}) \approx 0.85/[\lambda (\mu\text{m})]^4$ | 光纤 Rayleigh 散射极限 | §10.2E |

### 2.7 偶极辐射场

| 公式 | 说明 | 位置 |
|------|------|------|
| $\mathbf{E}_{\text{sc}} = \frac{1}{4\pi\epsilon_0}k^2\frac{e^{ikr}}{r}[(\mathbf{n}\times\mathbf{p})\times\mathbf{n} - \mathbf{n}\times\mathbf{m}/c]$ | 偶极散射场（远场） | (10.2) |
| $\frac{d\sigma}{d\Omega}(\mathbf{n},\epsilon;\mathbf{n}_0,\epsilon_0) = \frac{k^4}{(4\pi\epsilon_0 E_0)^2}|\epsilon^*\cdot\mathbf{p} + (\mathbf{n}\times\epsilon^*)\cdot\mathbf{m}/c|^2$ | 偶极近似散射截面 | (10.4) |

---

## 3. 可供 mie-f 理论复现参考的内容

### 3.1 核心公式：Jackson Eq. (9.165)

这是 **Alaee 2018** 引用的关键公式，给出从源分布直接计算多极系数的积分形式：

$$
\begin{aligned}
a_E(l,m) &= \frac{ik^3}{\sqrt{l(l+1)}} \int j_l(kr) Y_{lm}^* \mathbf{L}\cdot\left(\mathbf{M} + \frac{1}{k^2}\nabla\times\mathbf{J}\right) d^3x \\
a_M(l,m) &= -\frac{k^2}{\sqrt{l(l+1)}} \int j_l(kr) Y_{lm}^* \mathbf{L}\cdot\left(\mathbf{J} + \nabla\times\mathbf{M}\right) d^3x
\end{aligned}
$$

其中 $\mathbf{L} = -i\mathbf{r}\times\nabla$ 是角动量算符，$\mathbf{J}$ 是电流密度，$\mathbf{M}$ 是磁化强度。对于非磁性材料 $\mathbf{M}=0$，简化为：

$$
\begin{aligned}
a_E(l,m) &= \frac{ik}{\sqrt{l(l+1)}} \int j_l(kr) Y_{lm}^* \mathbf{L}\cdot(\nabla\times\mathbf{J}) d^3x \\
a_M(l,m) &= -\frac{k^2}{\sqrt{l(l+1)}} \int j_l(kr) Y_{lm}^* \mathbf{L}\cdot\mathbf{J} d^3x
\end{aligned}
$$

**在 mie-f 中的角色**：该公式将光学纳米结构的散射/辐射特性转化为多极矩的积分计算，是 Grahn 2012 和 Alaee 2018 将米氏散射理论推广到任意形状基底结构的基础。

### 3.2 长波极限下的多极矩

当 $ka \ll 1$（结构尺寸远小于波长），(9.165) 简化为多极矩的简单幂次关系：

- 电多极：$a_E(l,m) \propto k^{l+2} Q_{lm}$ — 电偶极 $l=1$ 主导
- 磁多极：$a_M(l,m) \propto k^{l+2} M_{lm}$ — 磁偶极 $l=1$ 主导
- 电四极 $a_E(2,m) \propto k^4$，比偶极 $k^3$ 高一阶

这就是 Rayleigh 散射 $\sigma \propto k^4 \propto \lambda^{-4}$ 的根源。

### 3.3 球谐展开平面波（10.44–10.55）

$$
e^{i\mathbf{k}\cdot\mathbf{x}} = 4\pi\sum_{l=0}^\infty i^l j_l(kr) \sum_{m=-l}^l Y_{lm}^*(\theta_k,\phi_k) Y_{lm}(\theta,\phi)
$$

这是 Mie 散射理论中入射平面波展开为球面波的基础。其中 $j_l(kr)$ 为球 Bessel 函数，$Y_{lm}$ 为球谐函数。

### 3.4 矢量多极展开通解（9.122）

电场和磁场展开为矢量球谐函数 $\mathbf{X}_{lm}$ 的叠加：

$$
\begin{aligned}
\mathbf{E}(\mathbf{x}) &= \sum_{l,m} \left[a_E(l,m) j_l(kr) \mathbf{X}_{lm} + \frac{i}{k} a_M(l,m) \nabla\times j_l(kr)\mathbf{X}_{lm}\right] \\
c\mathbf{B}(\mathbf{x}) &= \sum_{l,m} \left[\frac{-i}{k} a_E(l,m) \nabla\times j_l(kr)\mathbf{X}_{lm} + a_M(l,m) j_l(kr)\mathbf{X}_{lm}\right]
\end{aligned}
$$

该通解是 **mie-f 理论复现的核心结构**，每一个场的多极分量由 $a_E(l,m)$ 和 $a_M(l,m)$ 唯一确定。

### 3.5 散射截面部分波展开（10.62–10.63）

对球对称散射体，总散射截面和消光截面统一为散射系数 $\alpha(l), \beta(l)$ 的求和：

$$
\sigma_{\text{sc}} = \frac{\pi}{2k^2}\sum_{l=1}^\infty (2l+1)[|\alpha(l)|^2 + |\beta(l)|^2]
$$

$$
\sigma_t = -\frac{\pi}{k^2}\sum_{l=1}^\infty (2l+1)\text{Re}[\alpha(l) + \beta(l)]
$$

### 3.6 完美导体球的 Mie 散射极限

当 $ka \ll 1$（长波极限），导体球的散射系数为：

$$
\alpha_\pm(1) = -\frac{1}{2}\beta_\pm(1) = -\frac{2i}{3}(ka)^3
$$

对应的微分截面 (10.72) 与纯偶极近似 (10.16) 一致，验证了电偶极 + 磁偶极干涉产生向后增强的结论。

### 3.7 Grahn 2012 相关公式汇总

Grahn 2012 构建任意基底结构的光学响应时使用的核心方法：

1. **多极系数 (9.165)** — 从电流分布 $J(\mathbf{x})$ 和磁化 $M(\mathbf{x})$ 积分计算 $a_E, a_M$
2. **矢量球谐函数 $\mathbf{X}_{lm}$** — 场的基函数，定义见 (9.119)
3. **球 Bessel 函数 $j_l(kr)$** — 径向依赖，小参数渐近式 (9.88)
4. **球谐函数 $Y_{lm}$** — 角度依赖，用于正交投影
5. **辐射角分布 (9.151)** — 从 $a_E, a_M$ 到远场辐射模式的映射
6. **总辐射功率 (9.152)** — 正交性使不同 $l,m$ 贡献直接相加
7. **前向散射振幅与光学定理 (10.139, 10.146)** — 散射与消光的关系

### 3.8 Alaee 2018 直接引用

Alaee 2018 将 Jackson Eq. (9.165) 作为计算纳米结构多极响应的核心手段，结合长波极限近似来简化偶极和四极贡献的计算。其关键步骤：

1. 给定纳米结构的几何形状 → 计算诱导电流分布 $\mathbf{J}(\mathbf{x})$
2. 通过 (9.165) 积分得到多极系数 $a_E(l,m), a_M(l,m)$
3. 多极系数代入 (9.151) 获得远场散射模式
4. 对基底上的结构，改变积分区域和相位因子

---

## 4. 可信度注意事项

### OCR 总体质量评估

**等级：C 级**（适合阅读提取公式框架，但局部有误差）

### 已知问题

| 类型 | 示例 | 影响 |
|------|------|------|
| **公式符号误识别** | $Y_{lm}$ 被识别为 $Y_{I0}$ 或 $Y_{ln}$（如行 1032, 1688） | 公式名可识别，个别下标错位 |
| **变量名错位** | $j_l(kr)$ 有时变为 $j_l(kr)$ 显示不全或缺失括号 | 不影响理解，但直接引用需核对 \\
| **角标混淆** | $m$ 与 $n$, $l$ 与 $1$ 混淆（OCR 典型问题） | 阅读时可推断，复制需警惕 |
| **下标格式不稳** | 部分公式中下标 $l$ 显示为斜体或断裂 | 易读 |
| **图片仅占位** | 全部以 `![](images/...)` 形式存在，无图片实际内容 | 图片内容（图表、示意图）不可见 |
| **缺失空行** | 部分章节标题与正文间缺少空行 | 不影响公式 |
| **行内乱码** | 行 1688 附近有 `Y_{I0}` 应为 `Y_{l0}$ | 单个符号不影响整体 |
| **部分章节缺失** | 第 10 章仅有 §10.1–10.4 和 §10.11 完整，§10.5–§10.10 中间有间断 | 总结不完整 |

### 推荐使用方式

- **框架理解**：此摘要可直接用于理解 Jackson 多极展开的整体理论框架
- **公式复制**：任何从本文档提取的公式在用于正式写作前，应与原始 Jackson 第三版纸质版或 PDF 核对
- **数值引用**：本文档包含的系数值（如 $Q= a/\delta$ 公式、衰减系数数值）在引用前需验证
- **交叉验证**：Alaee 2018 和 Grahn 2012 中直接引用的 Jackson 公式编号（如 Eq. 9.165）应对比原文

---

## 5. 章节页码对照

> OCR 源文件是一份连续的 Markdown，无原始页码信息。以下为 OCR 内部章节头位置索引。

| OCR 行号 | 内容 | 对应 Jackson 章节 |
|----------|------|-------------------|
| 1–2 | **CHAPTER 4** — Multipoles, Electrostatics | Ch. 4 |
| ~5–130 | §4.1 Multipole Expansion of Potential | §4.1 |
| ~131–250 | §4.2 Multipole Moments | §4.2 |
| ~251–350 | §4.3 Energy and Force | §4.3 |
| ~351–500 | §4.4 Dielectric Sphere | §4.4 |
| ~501–600 | §4.5–4.6 Boundary Value Problems | §4.5–4.6 |
| ~601–700 | §4.7 Energy in Multipole Expansion | §4.7 |
| ~701–850 | §4.8–4.9 Additional Topics | §4.8–4.9 |
| ~851–900 | End of Chapter 4 Problems | Ch.4 Problems |
| 901 | **CHAPTER 9** — Radiation, Multipole Fields | Ch. 9 |
| ~903–1000 | §9.1 Radiation Fields | §9.1 |
| ~1001–1100 | §9.2 Electric Dipole Radiation | §9.2 |
| ~1101–1200 | §9.3 Magnetic Dipole & Electric Quadrupole | §9.3 |
| ~1201–1350 | §9.4 General Multipole Expansion | §9.4 |
| ~1351–1550 | §9.5 Multipole Coefficients (含 Eq. 9.165) | §9.5 |
| ~1551–1620 | §9.6 Angular Distribution of Radiation | §9.6 |
| ~1621–1680 | §9.7 Angular Momentum | §9.7 |
| ~1681–1720 | §9.8 Parity of Multipole Fields | §9.8 |
| ~1721–1820 | §9.9 Aperture Coupling | §9.9 |
| ~1821–1959 | §9.10 Problems (9.15–9.24) | §9.10 |
| 2040 | **CHAPTER 10** — Scattering and Diffraction | Ch. 10 |
| 2048–2079 | §10.1 Scattering at Long Wavelengths | §10.1 |
| 2080–2132 | §10.1B Small Dielectric Sphere | §10.1B |
| 2134–2180 | §10.1C Small Conducting Sphere | §10.1C |
| 2182–2212 | §10.1D Collection of Scatterers | §10.1D |
| 2214–2325 | §10.2 Perturbation Theory / Born Approx. | §10.2 |
| 2326–2378 | §10.2C Blue Sky | §10.2C |
| 2380–2444 | §10.2D Critical Opalescence | §10.2D |
| 2446–2452 | §10.2E Optical Fibers | §10.2E |
| 2454–2550 | §10.3 Spherical Wave Expansion of Plane Wave | §10.3 |
| 2552–2710 | §10.4 Scattering by a Sphere (Mie) | §10.4 |
| 2712–2904 | §10.11 Optical Theorem | §10.11 |
| 2906–2933 | References and Suggested Reading | References |

**注意**：
- OCR 文件中 §10.5–§10.10 未包含，直接从 §10.4 跳至 §10.11
- **第 10 章 OCR 覆盖不全** — 缺少 Huygens-Kirchhoff 衍射理论 (§10.5–§10.7)、Babinet 原理 (§10.8)、圆形孔径衍射 (§10.9)、短波极限衍射 (§10.10) 等内容
- Ch.1–Ch.3 未包含在此 OCR 文件中

---

*摘要生成日期：2026-07-26 | 参考源：Jackson J.D., Classical Electrodynamics, 3rd ed., Wiley (1999)*
