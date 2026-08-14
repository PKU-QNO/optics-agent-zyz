# Alaee 2018 Fig.2 formalization 对抗审查（gate②）

> 审查日期：2026-08-08  
> 对象：`formalization/alaee2018-fig2.yaml`、`notes/fig2-parameters.md`、`data/gold_epsilon.csv`、`data/_gold_sources/*.yml`  
> 真相源：Alaee 2018 原论文页 2--4、`sections/11_exact_multipoles.tex`、`sections/12_unified.tex`、Bohren--Huffman Ch.4  
> 裁决：**必改项已落盘，spec 现可提交用户 gate② 核准；在用户放行前不视为 gate② 已通过。**

## 发现的问题（按严重度）

### 🔴 严重（必改，已修复）

1. **三源均值不能作为 Fig.2 金球的权威材料输入。**
   - 原 `mean_n/mean_k` 在 1700 nm 为 JC/Olmon/McPeak 三源均值，1705 nm 突然变为 Olmon 单源。
   - 实测断点：$\epsilon_1=-143.22\to-136.16$，$\epsilon_2=10.80\to8.85$。此时 JC 仍覆盖到约 1937 nm，因此“JC/McPeak 均越界”不成立。
   - 机制：这种人工跳变会改变共振和电流分布，可被误判为公式或网格问题。
   - 修复：JC 仅用于 500--1935 nm 论文形状对比；Olmon-EV 用于 500--2500 nm 全区间方法验收；三源在 500--1700 nm 分别计算包络。

2. **复色散电流辅助函数曾将 $\epsilon=m^2$ 误写为 $m m^*=|m|^2$。**
   - 机制：对 $m=n+i\kappa$，$|m|^2$ 是实数，会完全丢失 $\operatorname{Im}\epsilon$ 和错置极化电流幅值。
   - 修复：`internal_current_density` 已改为 $\tilde{J}=(m^2-1)E$，并新增 550 nm 复数回归测试。`multipole_moments._moments_grid` 原本已用正确的 $m^2-1$。

3. **参数笔记对金球横轴与扫描范围自相矛盾。**
   - 原文一处写横轴 $\lambda$、另一处写 400--1000 nm，与论文 Fig.2 及后文的 $2a/\lambda\in[0.2,1.0]$ 冲突。
   - 修复：统一为在 $2a/\lambda$ 上等距取 200 点，再用 $\lambda_{\rm nm}=500/(2a/\lambda)$ 反算非均匀波长。

### 🟡 中等（缺字段/歧义，已补）

1. **550 nm 的“互差 <7.4%/<13%”缺少定义且数值不成立。**
   - 明确用 `max pairwise range / |arithmetic mean|` 后，按 CSV 未舍入数据得 $\epsilon_1$ 11.35%、$\epsilon_2$ 25.75%。
   - 三源是独立文献和样品，但不是同一不变真值的重复测量；应解释为样品/工艺敏感性。

2. **“同一 $\epsilon$ 下不影响核心验收”过于绝对。**
   - Table2/Mie 的解析等价确实与材料源无关；但材料源会改变共振、近零点与数值条件，因而会影响固定网格误差和论文形状对比。

3. **色散金球扫描不能直接使用 $Q_{\rm sca}\propto x^4$ 硬约束。**
   - Fig.2(b) 保持 $a=250$ nm 并通过改变波长扫描，所以 $\epsilon(\lambda)$ 同时变化。
   - 修复：Rayleigh 标度只用于固定复 $\epsilon$ 的独立单元测试；$\operatorname{Re}\epsilon\simeq-2$ 也只作准静态小球测试，不作 250 nm 金球的峰位硬锚点。

4. **验收指标不完整。**
   - 修复后的机器可读口径：$C_{\rm Mie}^{\rm norm}\ge10^{-4}$ 时 max relative <1%、p95 relative <0.1%；全点 max absolute <0.002；近零点只计绝对误差；网格加密变化 <0.1%。

5. **真相源路径和 B&H 公式编号有漂移。**
   - 讲义实际文件为 `11_exact_multipoles.tex`，不是不存在的 `11_table2.tex`。
   - $c_n/d_n$ 来自 B&H Eq.(4.52) 一般内部系数的非磁化简；Eq.(4.53) 后文字说明其分母分别与 $b_n/a_n$ 配对。

### 🟢 轻微

1. Fig.2 上下排列应写为 `2×1 vertical`，而不是“1×2 纵向”。已修正。
2. 论文 exact 曲线主要使用标记点覆盖 Mie 实线；绘图时可使用 marker，不必强制虚线。
3. `C_abs=C_ext-C_sca` 若由同一函数定义则是代数恒等式，不能单独作为独立能量守恒证据；已在 spec 降级为内部一致性检查。

## ✅ 已核实

- Fig.2 仅 (a)(b) 两面板，无误差子图；布局为上介电球、下金球。
- 双面板横轴均为 $2a/\lambda\in[0.2,1.0]$；$a=250$ nm 时对应 $\lambda\in[500,2500]$ nm。
- 介电球 $\epsilon_r=2.5^2=6.25$；PDF 文字层的“2.52”是上标丢失。
- 归一化为 $C_{\rm sca}/(\lambda^2/2\pi)$；ED/MD 通道上限为 3，EQ/MQ 为 5。
- $x_{\rm Mie}=ka=\pi(2a/\lambda)$，金球也使用 host 尺寸参数。
- Table 2 辐射核中 $k=k_{\rm host}$；$k_{\rm in}=mk_{\rm host}$ 只决定 $E_{\rm in}/J$ 的空间结构。
- Table 2 四式、Eq.(1) 的 ED/MD/EQ/MQ 解析常数以及 $r_\alpha/a=U\times$方向余弦均未发现新转录错误。
- Mie $a_n/b_n/c_n/d_n$ 代数形式对复 $m$ 不变；金数据直接用 $m=n+i\kappa$、$\kappa>0$。

## 结论

1. **spec 能否直接用于实现？**  
   修改前不能；本次必改项落盘后，已具备提交用户 gate② 核准的条件。

2. **哪些必须改才能进 gate②？**  
   数据源用途分离、禁止静默切源/外推、修正复电流前因子、统一轴与扫描范围、明确近零点和网格验收指标。这些均已落盘。

3. **金数据 3 源方案是否可靠？**  
   作为材料敏感性包络可靠；作为单一权威均值不可靠。带间区偏差不改变 Table2/Mie 的解析等价，但会影响数值条件和论文图形。

4. **$>1700$ nm 用 Olmon 单源是否引入断裂？**  
   是。现有 legacy mean 在 1700/1705 nm 有明显跳变，故已禁止将它作为主输入。Olmon 全区间单源本身是连续方案，但必须明确标识为方法验收而非论文 JC 保真。

5. **复折射率 Mie 还有何实现要点？**  
   直接使用 $m=n+i\kappa$、$\kappa>0$；复宗量 Bessel 保持原公式；极化电流用 $m^2-1$；在 550/1000/1700/1935/2500 nm 对 $a_n/b_n/c_n/d_n$、$C_{\rm abs}\ge0$ 和 miepython 进行交叉。

## 本次落盘

- 修订 `formalization/alaee2018-fig2.yaml`、`notes/fig2-parameters.md`、`opus-prompts/06-fig2-formalization-review.md`。
- 新增 `data/_gold_sources/manifest.yaml`和本审查报告。
- 修正 `code/mie_theory.py::internal_current_density`，新增复数电流与 Fig.2 金数据/Mie 回归测试。
