# Grahn 2012 映射笔记（第 3 轮 step03）

本笔记只解释 `formalization/grahn.yaml` 已冻结的实现，不替代 spec。公式同时给出原文
编号（source equation）和本地实现标签（local equation）；若两者发生冲突，以原文编号和
spec 为准。

## 1. 约定和尺度

采用 $e^{-i\omega t}$、$\mathbf E_i=\hat{\mathbf x}E_0e^{ikz}$。host 的绝对介电常数为
$\epsilon_d=\epsilon_0\epsilon_{rd}$，因此

$$
\mathbf J_S=-i\omega(\epsilon-\epsilon_d)\mathbf E,
\qquad
k=\omega\sqrt{\mu_0\epsilon_d},\quad \eta=\sqrt{\mu_0/\epsilon_d}.
$$

代码以 $a=1,E_0=1$ 和 $\widetilde{\mathbf J}=(\epsilon_r-\epsilon_{rd})\mathbf E$ 做积分。
公共因子 $-i\omega\epsilon_d$ 与 $k^2\eta$ 合并为 $-ik^3$，所以结果仍是无量纲的
Mie $a_n/b_n$。归一化截面为

$$
\frac{C_{\rm sca}}{\lambda_d^2/(2\pi)}
 =\frac12\sum_{lm}(2l+1)(|a_E(l,m)|^2+|a_M(l,m)|^2).
$$

## 2. $M^{(2)}$ 四对象

Grahn 原文 Eq.(27)（local `eq:Ml`）给出

$$
M^{(l)}=\frac{i}{(l-1)!\,\omega}\int \mathbf J\,\mathbf r\cdots\mathbf r\,d^3r.
$$

因此 $M^{(2)}_{\alpha\beta}=i\int J_\alpha r_\beta/\omega$ 是一般的 3×3
**原始、不对称**张量。实现 `M2_four_objects` 显式返回

$$
\begin{aligned}
M_{\rm STF}&=\tfrac12(M+M^T)-\tfrac13I\,\mathrm{tr}M,\\
M_{\rm A}&=\tfrac12(M-M^T),\qquad M_{\rm tr}=\tfrac13I\,\mathrm{tr}M,
\end{aligned}
$$

并逐元素验证 $M=M_{\rm STF}+M_{\rm A}+M_{\rm tr}$。长波限定的电四极桥为
$Q^e=6M_{\rm STF}$；有限 $kr$ 时禁止把 Alaee Table 2 的核矩直接喂进此映射。
反对称部分的对偶

$$m_\gamma=\tfrac12\int(\mathbf r\times\mathbf J)_\gamma d^3r
 =\tfrac{i\omega}{2}\epsilon_{\gamma\alpha\beta}M^{(2)}_{\alpha\beta}
$$

是磁偶极的来源；迹部分为球对称暗模。

## 3. 路径 A：无核张量映射

由无核 $p=M^{(1)}$、$Q^e=6M_{\rm STF}$ 和
$O_{\alpha\beta\gamma}=i\int J_\alpha r_\beta r_\gamma/(2\omega)$，实现原文映射：

**D1 归一化合同：**Alaee 的 $Q^e=6M_{\rm STF}$ 与 Grahn (39)--(41) 的
$Q$ 不是同一输入；Grahn 的 $Q$ 是 Eq.(27) 的 $M^{(2)}_{\rm raw}$。由于这些线性组合
自动消去迹和反对称部分，代码允许 `q_for_mapping="raw"` 或 `"stf"`（逐 $m$ 等价），
而直接传入未除以 6 的 `"qe"` 会 fail-closed。该分歧与处理记录在
`codex-prompts/out/A2-discrepancies.md`，不修改 spec。

| source equation | local label | 代码对象 |
|---|---|---|
| (39) | `eq:mapping_E2_2` | `a_E(2,±2)` |
| (40) | `eq:mapping_E2_1` | `a_E(2,±1)` |
| (41) | `eq:mapping_E2_0` | `a_E(2,0)` |
| (42) | `eq:mapping_E1` | `a_E(1,±1)`，含 $7C_3O$ |
| (43) | `eq:mapping_E1_0` | `a_E(1,0)`，含 $7\sqrt2C_3O$ |
| (44) | `eq:mapping_M2_2` | `a_M(2,±2)`（磁四极） |
| (45) | `eq:mapping_M2_1` | `a_M(2,±1)`（磁四极） |
| (46) | `eq:mapping_M2_0` | `a_M(2,0)`（磁四极） |
| (47) | `eq:mapping_M1_1` | `a_M(1,±1)`，用 raw M2 反对称部分 |
| (48) | `eq:mapping_M1_0` | `a_M(1,0)`，用 raw M2 反对称部分 |

其中

$$
C_1=-\frac{ik^3}{6\pi\epsilon_dE_0},\quad
C_2=-\frac{k^4}{60\pi\epsilon_dE_0},\quad
C_3=-\frac{ik^5}{210\pi\epsilon_dE_0}.
$$

`p_only_switch=False` 是默认值；打开它只删去 $a_E(1,m)$ 中的八极修正，不改变
其他通道。四极的 $m=0,\pm1,\pm2$ 全部保留；只有球体的简化报告才使用 $m=\pm1$。

## 4. 路径 B：有限核积分

主实现是原文 Eq.(15)(16)（local `eq:aE_clean`/`eq:aM_clean`）。令
$\Psi_l(\rho)=\rho j_l(\rho)$，使用

$$
j_l''(\rho)=\left[\frac{l(l+1)}{\rho^2}-1\right]j_l(\rho)-\frac{2}{\rho}j_l'(\rho),\quad
\Psi_l'=j_l+\rho j_l',\quad \Psi_l''=2j_l'+\rho j_l''.
$$

$\rho\to0$ 时使用 $j_l(\rho)\sim\rho^l/(2l+1)!!$ 的级数极限，禁止数值二阶差分。
角函数为 source Eq.(17)--(19)（local `O_lm`, `tau_lm`, `pi_lm`）：

$$
O_{lm}=\frac1{\sqrt{l(l+1)}}\sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}},\quad
\tau_{lm}=\frac{dP_l^m(\cos\theta)}{d\theta},\quad
\pi_{lm}=\frac{m}{\sin\theta}P_l^m(\cos\theta).
$$

Gauss--Legendre 内点不包含极点，因此 $\pi_{lm}$ 的可去奇性不会被直接除零。
`grahn_kernel_coefficients` 返回全 $m$ 复系数，`c_sca_from_coefficients` 实现 source
Eq.(20)。Eq.(13)(14) 直接导数路线仅为解析 bump 电流保留接口，真实 Mie 球不使用有限
差分导数（球面边界会产生分布项）。

## 5. 独立检查与错误注入

`far_field_projection` 单独构造 `sph_harm_y` 角基和
`spherical_jn + 1j*spherical_yn` 的 $h_l^{(1)}$；`miepython_gate` 缺包时返回
`BLOCKED`，不会以 pytest skip 冒充通过。`analytic_bump_closed_forms` 固定 spec 的
$I_0=64\pi R^3/315$、$I_2=64\pi R^5/3465$、$I_4=64\pi R^7/15015$、
$I_{22}=64\pi R^7/45045$，并由数值积分做网格收敛验证。

测试中的注入项逐一覆盖：a/b 互换、丢弃 $m=0,\pm1,\pm2$、坐标平移、时间相位、
$r\leftrightarrow\hat r$、$\Psi$ 导数、$\tau/\pi$ 互换以及 $a_E/a_M$ 相位互换。
