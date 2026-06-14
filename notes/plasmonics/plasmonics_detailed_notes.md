# Plasmonics 课程详细笔记

[toc]

资料来源：

- `20260413-第一章-plasmonics-1.pdf`：第一章，表面等离激元基础，68 页
- `20260518-第二章-Plasmonics-2.pdf`：第二章，表面等离激元的发展、前沿及应用，115 页
- `20260525-第三章-理论方法.pdf`：第三章，介观光学理论方法，59 页

## 0. 总览：这门课到底在讲什么

Plasmonics 的核心是：在金属-介质微纳结构中，利用自由电子集体振荡与电磁场的耦合，把光场压缩、传输、增强、聚焦、分束、存储或与量子体系耦合。

最重要的学习线索是“光学模式”：

- SPP：沿金属-介质界面传播、垂直界面倏逝衰减的表面等离激元极化激元。
- SPR / LSPR：局域金属纳米结构中的表面等离激元共振，常表现为吸收、散射或消光峰。
- 波导模式：平面、槽形、柱形、球链、弯曲、混合型等 SPP 波导模式。
- 周期结构模式：局域 SPR 与周期衍射、扩展 SPP 耦合形成带隙、异常透射、beaming、几何共振等。

学习时可以抓住三句话：

1. 材料给出介电函数，结构给出边界条件，二者共同决定模式。
2. SPP 强局域但有损耗，传播长度和局域尺度之间总有折中。
3. 真实纳米结构通常边界复杂，解析模型给物理图像，数值方法给具体结果。

## 1. 第一章：表面等离激元基础

### 1.1 微纳光学与超材料光学的出发点

微纳光学研究的是在微纳米或亚波长尺度上操控光。可操控的对象包括传播、局域增强、聚焦、分束、存储以及量子光场与物质体系的相互作用。

超材料光学强调通过材料参数与结构设计改变光学响应。常见参数是介电常数 $\epsilon$ 与磁导率 $\mu$，其中零、负值等异常参数区域会带来非常规光学行为。

课程的基础判断：

- 微纳光学的理论基础是 Maxwell 方程。
- Plasmonics 的材料基础通常是金属在可见光或近红外频段的负介电常数。
- 结构尺度达到亚波长后，近场、倏逝波和边界条件成为关键。

### 1.2 Drude 模型：金属为什么会有负介电常数

Drude 模型把金属中的自由电子看成在外电场驱动下运动的电子气。若外电场为随频率 $\omega$ 振荡的电磁场，电子位移响应产生极化，从而得到金属介电函数。

无损耗的基本结果：

$$
\begin{aligned}
\epsilon_m(\omega) &= 1 - \frac{\omega_p^2}{\omega^2} \\
\omega_p^2 &= \frac{4 \pi n e^2}{m}
\end{aligned}
$$

其中 $\omega_p$ 是等离子体频率，主要由自由电子密度 $n$ 决定。

更一般的写法考虑高频背景响应与损耗：

$$
\epsilon_m(\omega) = \epsilon_m(\infty) \left[1 - \frac{\omega_p^2}{\omega^2 + i \omega \gamma}\right]
$$

物理含义：

- 当 $\omega > \omega_p$ 时，$\epsilon_m > 0$，电磁波可以在金属中传播。
- 当 $\omega < \omega_p$ 时，$\epsilon_m < 0$，波矢变成复数，光场在金属中指数衰减，表现为趋肤效应。
- 趋肤深度定义为场强衰减到 $e^{-1}$ 的距离：

$$
\delta = \frac{1}{|k_z|}
$$

这部分是理解 SPP 的前置条件：SPP 通常发生在金属介电常数实部为负的频段。

### 1.3 金属-介质界面的 SPP

SPP 是 P 偏振电磁场与金属表面自由电子集体振荡耦合后形成的界面模式。它沿界面传播，在垂直界面的金属侧和介质侧均呈指数衰减。

设金属介电常数为 $\epsilon_1$，介质介电常数为 $\epsilon_2$，界面传播方向为 $x$。由 Maxwell 方程和边界条件可得 SPP 色散关系：

$$
k_x = \frac{\omega}{c} \sqrt{\frac{\epsilon_1 \epsilon_2}{\epsilon_1 + \epsilon_2}}
$$

SPP 出现的关键条件：

$$
\operatorname{Re}(\epsilon_1) < 0
$$

$$
|\operatorname{Re}(\epsilon_1)| > \epsilon_2
$$

从 Fresnel 反射系数的角度看，IM 界面（介质-金属界面）的 P 偏振反射系数可写成：

$$
r_p =
\frac{\epsilon_2 k_{z1} - \epsilon_1 k_{z2}}
{\epsilon_2 k_{z1} + \epsilon_1 k_{z2}}
$$

普通布鲁斯特角对应的是 $r_p=0$，也就是分子为零；界面 SPP 更常用的判据则是反射系数的极点，即分母为零：

$$
\epsilon_2 k_{z1} + \epsilon_1 k_{z2}=0
$$

这可以看成布鲁斯特角现象在复波矢/倏逝波条件下的解析延拓：入射波不再是普通传播波，而是在垂直界面方向指数衰减的束缚模式。因此，用反射系数语言理解 SPP 时，关键不是“反射消失”，而是界面本身支持一个无需外部传播光直接匹配的本征表面模式。

几个重要结论：

- 只有 P 偏振/TM 波可以激发 SPP，S 偏振/TE 波没有非平凡解。
- SPP 的波矢大于同频率下介质中的光波波矢，因此自由空间光不能直接相位匹配激发 SPP，通常需要棱镜、光栅、纳米结构或近场耦合。
- 垂直界面方向为倏逝波，所以 SPP 是表面束缚模式。

### 1.4 SPP 的穿透深度与传播长度

金属侧和介质侧的场强衰减长度反映了 SPP 的局域性。课件给出的典型数值：

- $\lambda = 600\,\mathrm{nm}$：
  - 银：金属侧约 $23\,\mathrm{nm}$，介质侧约 $371\,\mathrm{nm}$
  - 金：金属侧约 $29\,\mathrm{nm}$，介质侧约 $281\,\mathrm{nm}$
- $\lambda = 1000\,\mathrm{nm}$：
  - 银：金属侧约 $22\,\mathrm{nm}$，介质侧约 $1122\,\mathrm{nm}$
  - 金：金属侧约 $24\,\mathrm{nm}$，介质侧约 $1020\,\mathrm{nm}$

传播长度定义为沿界面传播时强度衰减到 $e^{-1}$ 的距离：

$$
L_i = \frac{1}{2k_x''}
$$

典型数值：

- $\lambda = 600\,\mathrm{nm}$：银约 $50.7\,\mu\mathrm{m}$，金约 $4.9\,\mu\mathrm{m}$
- $\lambda = 1000\,\mathrm{nm}$：银约 $698.1\,\mu\mathrm{m}$，金约 $91.7\,\mu\mathrm{m}$

理解重点：金属损耗越小，传播越远；场越局域，通常损耗越明显。局域性与传播长度是 SPP 器件设计中的基本矛盾。

### 1.5 平面 SPP 波导

平面 SPP 波导通过多层金属/介质结构耦合多个界面 SPP 模式。常见结构包括金属薄膜、介质-金属-介质、金属-介质-金属等。

学习重点：

- 每个金属-介质界面本身支持 SPP。
- 当两个界面足够近时，两个表面模式会耦合，形成对称/反对称模式。
- 模式的有效折射率、传播长度、穿透深度随金属厚度、介质折射率和间隙尺寸改变。
- MIM 结构常用于强局域，IMI 或薄金属膜结构常用于长程传播。

设计时要关注：

- 色散关系
- 模式分布
- 传播长度
- 金属侧/介质侧穿透深度
- 可能应用，如传感、波导、分束、增强发光

PPT1 第 33-39 页给出了几类典型平面系统中的 SPP 模式，可以按“耦合方式”和“局域-损耗折中”来理解：

#### 1.5.1 IMI 波导：长程与短程 SPP

IMI（insulator-metal-insulator）结构是介质-金属薄膜-介质。单个 IM 界面各自支持 SPP；当金属膜足够薄时，两个界面的 SPP 会通过金属膜耦合，分裂为偶模和奇模，也常称为 short-range SP 与 long-range SP。

以对称 air/Ag/air、$\lambda=600\,\mathrm{nm}$ 为例，PPT 中给出：

- $d=30\,\mathrm{nm}$：$L_S=11.1\,\mu\mathrm{m}$，$L_L=476.3\,\mu\mathrm{m}$。
- $d=50\,\mathrm{nm}$：$L_S=22.6\,\mu\mathrm{m}$，$L_L=143.3\,\mu\mathrm{m}$。

这里 $L_S$ 表示短程模式传播长度，$L_L$ 表示长程模式传播长度。直观图像是：两个界面模式耦合后，一个模式更强地压进金属、损耗更大、传播更短；另一个模式在金属中场分布较弱、损耗更小、传播更长。

#### 1.5.2 非对称 IMI：bound mode 与 leaky mode

非对称 IMI 中，上下介质折射率不同，模式性质会出现 cutoff，并可分为 bound mode 和 leaky mode：

- bound mode：场包络仍在界面附近指数衰减，是束缚表面模式。
- leaky mode：场能量会远离界面泄漏，已经不是理想束缚 SPP。

PPT 的例子为 $\lambda=632\,\mathrm{nm}$ 的银膜系统，参数约为 $n_1=2.0$、$n_3=1.9$、$\epsilon_m=-19+0.53i$。非对称性可显著改变长程 SPP 的传播长度，也能用于 refractometric sensors 一类折射率传感。

#### 1.5.3 MIM 波导：纳米间隙中的强局域

MIM（metal-insulator-metal）结构是金属-介质-金属。它可以看成两个金属/介质界面的 SPP 通过中间介质层耦合，模式横向尺寸主要由 gap 厚度决定。

核心特点：

- 模式强烈局域在介质间隙中。
- 可以突破普通介质波导的衍射尺度限制。
- 损耗通常比长程 IMI 模式更大，因为场更贴近金属。

所以 MIM 更适合强调 nano-scale light confinement，而 IMI/薄金属膜结构更适合强调 long-range propagation。

#### 1.5.4 平面异质结构：用多层设计降低损耗

PPT 给出一类 planar heterostructure：在非对称环境中支持 long-range SP。例子包括 water / SiN / Cu / glass 的多层结构。其设计思想是利用多层结构调节模式分布，让场尽量避开高损耗金属区域，从而得到更低损耗的 LRSP。

这类结构的要点不是单个界面，而是“整体边界条件”决定模式。换句话说，多层系统中的 SPP 已经不是某一个 IM 界面模式的简单复制，而是多个界面模式耦合后的本征模式。

#### 1.5.5 Conductor-gap-dielectric：亚波长 gap 模式

PPT 第 38 页的 conductor-gap-dielectric 系统由金属、纳米低折射率 gap 和高折射率介质组成。例如 Au / SiO2 gap / Ge 波导。结论是：即使在低于普通介质波导 cutoff 的厚度下，也可以存在 ultrasmall-loss guided mode。

它的物理解释是：导体-介质界面的 SPP 被超薄低折射率 gap 改造，形成 gap 本征模式。这个模式兼具亚波长局域和相对较低损耗，是后面杂化 SPP 波导的基本思想之一。

#### 1.5.6 Ultra-long-range SP：低折射率层贴近金属

PPT 第 39 页介绍 ultra-long-range SP mode：把低折射率介质层放在金属薄膜旁边，再由高折射率包层调节整体模式。例子中金属为 $20\,\mathrm{nm}$ Au，低折射率内层为 $n_1$，高折射率包层为 $n_2$。

设计思想是让模式能量更多分布在低损耗介质侧，同时保留表面等离激元的界面束缚性质。其关键词包括 cutoff、attenuation 和 ultra-long range。它代表了 SPP 波导设计中的另一端：牺牲一部分局域性，换取极长传播距离。

### 1.6 局域表面等离激元与 Mie 理论

Mie 理论是求解球形或球对称散射体吸收、散射、消光的解析理论。它通过把电磁场按球谐函数展开，并使用边界条件求出各阶多极模式系数。

核心物理图像：

- 金属纳米球中的自由电子在外光场驱动下集体振荡。
- 共振时出现强消光峰，并伴随近场局域与增强。
- 小颗粒主要是偶极共振；颗粒变大后，四极、多极模式逐渐出现。

准静态近似下，当半径 $R \ll \lambda$ 时只保留偶极项。金属小球在介质 $\epsilon_m$ 中的偶极 SPR 条件近似为：

$$
\operatorname{Re}(\epsilon_{\mathrm{metal}}) = -2\epsilon_{\mathrm{medium}}
$$

重要趋势：

- 金、银、铜小球尺寸增大时，共振峰红移。
- 介电函数虚部越大，共振峰越宽，损耗越强。
- 外界介电常数增大时，SPR 红移且强度变化明显，因此可用于折射率传感。
- 小颗粒消光主要来自吸收，大颗粒消光中散射比例增加。

### 1.7 金属纳米球壳的 Mie 共振

金属纳米球壳比实心球有更强的可调谐性。内外表面等离激元模式发生杂化，形成多个共振峰。

主要结论：

- 球壳由厚变薄时，共振峰红移。
- 外界介电常数增大时，偶极共振红移并变宽。
- 多层球壳可通过多极模式耦合和杂化产生多重共振。
- 球壳的宽谱可调性使其适合太阳能收集、生物医学光热、传感等应用。

## 2. 第二章：SPP 的发展、前沿及应用

课堂文稿里反复出现的主线是：第二章不是按公式推导讲，而是按“模式能做什么”讲。可以把它读成三条线：

- **传播型 SPP**：作为波导，核心问题是能不能在亚波长尺度上传得足够远。
- **局域型 SPR/LSPR**：作为共振，核心问题是能不能把光场压到小体积、产生强近场和可调谱线。
- **周期结构中的 SPP**：作为集体模式，核心问题是周期、倒格矢、衍射级如何帮助光与 SPP 互相转换。

老师在文稿中也提醒：SPP 文献非常多，课堂不可能逐篇深入。听第二章时最重要的不是记住每篇文章，而是学会判断每个工作处在什么模式问题上：它是在解决耦合、传输、局域增强、方向性发射、量子接口，还是材料/制备带来的新自由度。

### 2.1 历史线索与里程碑

这一节不是简单列论文，而是用一串里程碑说明 Plasmonics 如何从“光栅异常”和“金属小球散射”发展成纳米光子器件、量子光学、石墨烯等离激元和热载流子方向。下面每条都保留 PPT 中的英文题名或关键词，便于和原课件、后续论文检索对应。

#### 课上先复习的基础判断

英文对照：**optical modes**；**SPP mode**；**localized SPP mode**；**Drude model**；**Johnson and Christy optical constants**

老师先把第二章放回“模式”这个框架里：光子晶体最重要的是能带和带隙，回音壁结构最重要的是 whispering-gallery mode，plasmonics 里最重要的就是传播型 SPP mode 和局域型 LSPR/SPR mode。也就是说，不要只看结构长什么样，要问它支持什么模式、模式场在哪里、模式如何和外界光耦合。

传播型 SPP 的基本回答应包括：

- 它是金属-介质界面上的 TM 表面波。
- 沿界面传播，垂直界面方向指数衰减。
- 传播常数 $k_{\mathrm{SPP}}>k_0$，所以等效波长比自由空间波长短。
- 它之所以特殊，根源是金属自由电子集体振荡使介电常数实部为负。

局域型 SPP/LSPR 则更像“被困在纳米颗粒附近的共振场”。小金属球最简单时是偶极共振；尺寸继续增大，会出现四极、八极等高阶模式；再到更大尺度时，和介质微球中的回音壁模式在数学图像上会有相通之处。

材料上，课上特别强调金、银、铜等贵金属，实际最常用的是金和银。可见光附近金、银的 $\epsilon$ 实部通常为负；在约 $600\,\mathrm{nm}$ 附近，金的实部可粗略记为约 $-10$，银约 $-20$。银在 $400-600\,\mathrm{nm}$ 的损耗较低，所以实验上常喜欢银；但银容易氧化、不如金稳定。Drude 模型能给出趋势，但真正计算常直接用实验测得的光学常数，例如 Johnson and Christy 数据。

#### 1902：Wood 异常，最早的表面波线索

英文对照：**Wood's anomalies**；**On a Remarkable Case of Uneven Distribution of Light in a Diffraction Grating Spectrum**

Wood 在观察光栅衍射谱时发现某些波长附近的光强分布会突然异常变化，不能用简单的几何光学或普通光栅衍射直觉解释。后来人们认识到，这类异常与金属表面波、光栅动量匹配以及表面等离激元激发密切相关。它不是现代 SPP 理论的完整形式，但提供了“周期金属结构会强烈改变光传播”的早期实验事实。

#### 1908：Mie 理论，局域 SPR 的解析起点

英文对照：**Mie theory**；**Exact solution of sphere, spherical symmetry structure**

Mie 理论给出了球形颗粒对电磁波散射、吸收和消光的精确解。对 Plasmonics 来说，它的重要性在于：金属纳米球的消光峰可以解释为不同多极阶数的局域表面等离激元共振。小球半径远小于波长时主要是偶极共振；尺寸增大后，四极、六极等高阶模式会逐渐出现。因此，Mie 理论是从解析角度理解 LSPR 的基准模型。

#### 1907-1909：Zenneck 与 Sommerfeld，表面电磁波的理论雏形

英文对照：**Zenneck (1907) & Sommerfeld (1909)**；**theoretically radiation frequency surface EM waves**

PPT 中把 Zenneck 和 Sommerfeld 放在 Mie 之后，是因为他们从理论上讨论了两个介质边界处的射频表面电磁波。典型条件是一个介质具有损耗，例如金属或有损电介质，另一个介质损耗较小。这个阶段还不是现代光频 SPP 的完整理论，但已经出现了“表面波被界面束缚、沿界面传播”的基本数学结构。PPT 还强调，介电函数的虚部，即损耗部分，在束缚表面电磁波中起到重要作用。

#### 1939：Fano，把 Wood 异常解释为表面波耦合

英文对照：**Fano (1939)**；**surface EM waves were responsible for the striking anomalies in the continuous source diffraction spectra of metallic gratings**

Fano 对 Wood anomalies 给出更清楚的物理解释：金属光栅异常与金属-空气界面的表面电磁波有关。光栅提供额外波矢，把入射光耦合到表面波。PPT 中还总结了 Fano 的三个层次：射频下有损介质/空气界面表面波、光频下金属/空气界面表面波、以及无损介质/空气界面的 Brewster anomaly。它们可看作不同材料参数下由同一类数学方程描述的奇异情形。

#### 1957-1958：Ritchie 与 Stern，把表面等离激元和电磁辐射联系起来

英文对照：**Ritchie (1957)**；**Surface plasma excitations**；**Stern (1958)**；**EM radiation coupled to surface plasmons**

Ritchie 从理论上证明金属表面存在 surface plasma excitations，也就是表面等离子体激发。Stern 进一步说明，金属表面的表面电磁波可以涉及电磁辐射与表面等离激元的耦合，并首次推导了表面电磁波的色散关系。这个阶段很重要：它把早期“表面波”语言推进到“电子集体振荡 + 电磁场”的 plasmon 语言。

#### 1960：Powell 与 Swan，电子束实验观测表面等离激元

英文对照：**Powell & Swan (1960)**；**Observed the excitation of surface plasmons at metal interfaces using electrons**

Powell 和 Swan 用电子作为激发源，在金属界面观测到表面等离激元激发。电子束可以提供较大的动量，因此比远场光更容易直接激发表面等离激元。这一事件说明 surface plasmon 不只是理论本征模，也可以通过实验激发和探测。

#### 1968：光栅衍射中的 SPR 效应被明确提出

英文对照：**SURFACE-PLASMON RESONANCE EFFECT IN GRATING DIFFRACTION**

Ritchie、Arakawa、Cowan 等人的工作把表面等离激元共振与光栅衍射联系起来。核心思想是：自由空间光的面内动量通常不够大，不能直接激发 SPP；但光栅可以提供额外倒格矢，使入射光与 SPP 满足相位匹配。这是后来光栅耦合、异常透射、beaming 等结构的重要物理基础。

#### 1968-1971：Otto 与 Kretschmann，棱镜耦合激发 SPP

英文对照：**Otto (1968)**；**ATR (prism coupling) method**；**Kretschmann (1971)**；**widely used device geometry**

Otto 提出了用 ATR（attenuated total reflection，衰减全反射）棱镜耦合的方法，把普通体电磁波耦合到表面电磁波。Kretschmann 随后改进 Otto 几何，形成今天最常见的 Kretschmann configuration。它的关键是用高折射率棱镜提高入射光的面内波矢，在金属薄膜另一侧激发表面等离激元。现代 SPR 传感器大量使用的就是这个基本几何。

#### 1989：Knoll，表面等离激元显微术

英文对照：**Knoll (1989)**；**Surface Plasmon Microscopy**

Knoll 引入 Surface Plasmon Microscopy 技术，把 SPR 从单点反射谱测量推进到空间成像。由于 SPR 对界面折射率、薄膜厚度、吸附层和局域环境非常敏感，它可以用来观察表面过程的空间分布。这个方向后来发展到生物传感、电化学成像和界面反应成像。

#### 1998：亚波长孔阵列的异常光透射，现代 Plasmonics 的引爆点

英文对照：**Extraordinary optical transmission through subwavelength holes**

Ebbesen 小组发现，金属薄膜上的亚波长孔阵列可以出现远超单个小孔预期的透射增强。传统直觉认为孔径远小于波长时透射应很弱，但周期孔阵列可以通过光与表面等离激元耦合，把能量有效隧穿到另一侧再辐射出去。PPT 把它称为 SPP 的重要起点，因为它让表面等离激元从“表面波现象”变成可设计的纳米光学器件机制。

#### 2002：Bull's eye 结构实现小孔出射光定向发射

英文对照：**Beaming light from a bull's eyes structure**；**Beaming light from a subwavelength hole**

小孔出射光通常会向各个方向衍射发散。Ebbesen 小组在亚波长孔周围加入同心环形沟槽，即 bull's eye 结构，利用表面沟槽和 SPP 的耦合来重整出射相位，使光束沿特定方向发射。这个结果说明金属表面微纳结构不仅能增强透射，还能控制远场方向性，是纳米天线、方向性发射和集成光输出的重要思想来源。

#### 2002：纠缠光子经过金属孔阵列，SPP 可携带量子特征

英文对照：**Plasmon-assisted transmission of entangled photons**

Altewischer 等研究了纠缠光子通过纳米结构金属孔阵列的过程。PPT 的物理图像是：光子先转换成表面等离激元，穿过孔阵列后再辐射成光子；实验表明量子纠缠特征可以在这个光子-SPP-光子转换过程中保留。这件事很关键，因为它把 Plasmonics 从经典增强和传输问题推向量子光学：SPP 不只是经典表面波，也可以参与量子信息过程。

#### 2002：金/银纳米立方体合成，形状控制成为调谐 SPR 的手段

英文对照：**Synthesis of Ag and Au nanocubes**；**Shape-Controlled Synthesis of Gold and Silver Nanoparticles**

Younan Xia 等人的工作展示了金、银纳米颗粒尺寸、形状和结构的可控合成。对 Plasmonics 来说，材料制备不是附属问题，因为 SPR 波长、线宽和近场热点强烈依赖颗粒形状。纳米球、纳米棒、纳米三角、纳米笼、纳米星等结构之所以能对应不同颜色和不同近场增强，本质上来自几何边界条件对自由电子集体振荡模式的调控。

#### 2003：复杂纳米结构的等离激元杂化模型

英文对照：**A hybridization model for plasmon response**；**A hybridization model for the plasmon response of complex nanostructures**

Halas、Nordlander 等提出 plasmon hybridization 图像，用类似分子轨道杂化的方式理解复杂金属纳米结构中的多个共振峰。例如金属纳米壳可看成实心球模式与空腔模式耦合，内外表面等离激元杂化后产生 bonding/antibonding 型共振。这个模型给了一个非常好用的直觉：复杂结构的 SPR 不是凭空出现，而是简单模式之间耦合、分裂和重组的结果。

#### 2003：表面等离激元亚波长光学综述，确立应用版图

英文对照：**Surface plasmon subwavelength optics**

Barnes、Dereux 和 Ebbesen 的综述把表面等离激元定位为连接纳米尺度光子学与电子学的桥梁。PPT 中强调它在光子回路、光谱学、生物光子学、太阳能和非线性光学中的应用。这类综述的意义在于把零散现象整理成研究纲领：利用 SPP 的亚波长束缚和近场增强，发展比普通介质光学更小、更强耦合的器件。

#### 2004：金属膜介导的 Forster 能量转移

英文对照：**Forster Energy Transfer Across a Metal Film**；**Energy Transfer Across a Metal Film Mediated by Surface Plasmon Polaritons**

Barnes 等研究了供体和受体分子隔着银膜时的能量转移。普通 Forster 能量转移通常是近距离偶极-偶极相互作用，但金属膜中的 SPP 可以作为中介，把分子间能量传递扩展到更特殊的结构中。它体现了 molecular plasmonics 的思想：把分子、聚合物薄膜、金属薄膜结合起来，做主动等离激元器件。

#### 2005：银超透镜突破衍射极限

英文对照：**Optical Imaging below the Diffraction Limit**；**Sub-Diffraction-Limited Optical Imaging with a Silver Superlens**

Xiang Zhang 相关工作利用银薄膜表面等离激元收集并放大倏逝波，实现约 $60\,\mathrm{nm}$、约 $\lambda/6$ 的成像分辨率。普通远场成像失去亚波长信息，是因为倏逝波不能传播到远处；超透镜利用金属负介电响应和 SPP 共振，使这些近场高空间频率信息得到部分恢复。这说明 Plasmonics 可以突破传统光学分辨率限制。

#### 2005：光学纳米天线把光压缩到 gap 中

英文对照：**Resonant Optical Antennas**

Hecht、Martin 等研究了金属纳米天线。PPT 例子中入射光约 $830\,\mathrm{nm}$，天线长度远小于半波长，gap 约 $30\,\mathrm{nm}$，共振时电场强烈局域在间隙中。它的意义是把射频天线的思想搬到光频段：金属纳米结构可以接收、局域和重新辐射光，并在 gap 中产生极强近场，是 SERS、单分子探测和增强发光的重要基础。

#### 2006：Channel SPP 波导器件

英文对照：**Channel SPP waveguide components including interferometers and ring resonators**

Ebbesen 小组在银槽结构中实现 channel plasmon subwavelength waveguide components，包括干涉仪和环形谐振器。它面对的问题是：通信波段光路要小型化、高密度集成，但普通介质波导受衍射限制。Channel SPP 结构把光束缚在金属槽中，同时保持相对较低损耗，使 SPP 不只是单个界面现象，而可以构造成器件网络。

#### 2007：量子点耦合金属纳米线，生成单个 SPP 量子

英文对照：**Generation of single optical plasmons in metallic nanowires coupled to quantum dots**

Lukin 等相关工作把量子点与金属纳米线耦合，实现单个表面等离激元量子的产生。这里的目标不再是增强经典光场，而是让单个量子发射体把能量高效耦合进一维 SPP 通道。它为单光子开关、单光子晶体管、长程量子比特传输等概念提供了物理平台。

#### 2007：基于纳米 SPP 的单光子晶体管设想

英文对照：**Quantum light switch: A single-photon transistor using nanoscale surface plasmons**；**A single-photon transistor using nanoscale surface plasmons**

光子适合高速传输，但光子-光子相互作用很弱，难以实现强非线性量子操控。PPT 中这类工作利用量子发射体与纳米 SPP 的强耦合，让一个光子能够显著影响另一个光子的传播，从而走向单光子探测、纠缠、可控相位门和量子非线性器件。它代表 Plasmonics 与量子信息交叉的早期重要方向。

#### 2009：Spaser 与深亚波长 plasmon laser

英文对照：**Core-shell nanostructure spaser**；**Demonstration of a spaser-based nanolaser**；**Plasmon lasers at deep subwavelength scale**

Spaser 可以理解为 surface plasmon amplification by stimulated emission of radiation，即表面等离激元的受激辐射放大。Noginov 等实现 core-shell nanostructure spaser；Xiang Zhang 等展示 deep subwavelength scale plasmon laser。它们面对的是传统激光腔尺寸受衍射限制的问题，利用金属纳米结构的局域等离激元模式，把相干光源压缩到远小于波长的尺度。

#### 2010：介观量子发射体改变 plasmon-matter interaction

英文对照：**modified plasmon-matter interaction with mesoscopic quantum emitters**；**Strongly modified plasmon-matter interaction with mesoscopic quantum emitters**

Mads Lykke Andersen 等研究量子点等介观量子发射体的有限尺寸如何影响其与 SPP 的耦合。传统偶极近似常把量子发射体看成点偶极，但当发射体尺寸、近场梯度和纳米结构尺度相当时，不同衰减通道会被显著改变。PPT 强调的意义是：量子点尺寸本身会影响 SPP 与 quantum emitter 的耦合，因此量子 Plasmonics 中不能总把发射体当成无尺寸点源。

#### 2010：局域电化学电流的 SPR 成像

英文对照：**Imaging Local Electrochemical Current via Surface Plasmon Resonance**

NJ Tao 等利用 SPR 对界面折射率、电荷和局域反应变化的敏感性，发展电化学显微成像。PPT 中强调它可以把局域电化学电流变化转换成光学信号，用于研究非均匀表面反应和痕量化学分析。这说明 SPR 不只是在物理光学中有用，也能成为化学和界面科学的成像工具。

#### 2010：Plasmonics 的综合论证

英文对照：**APPLIED PHYSICS: The Case for Plasmonics**；**The Case for Plasmonics**

Brongersma 和 Shalaev 的文章强调，通过把光压缩到纳米体积，plasmonic elements 可以研究和利用强光-物质相互作用。它类似一篇“为什么这个领域值得做”的宣言：Plasmonics 的价值不只是某个器件，而是提供一种把光学长度尺度降到电子器件尺度附近的通用路线。

#### 2011：混合纳米光子架构

英文对照：**hybrid photonic architectures**

Oliver Benson 的相关综述强调，把单分子、纳米晶体、半导体量子点、纳米线和金属纳米颗粒等不同光子单元组装起来，可以得到单个组分没有的功能。Plasmonics 在其中常扮演“强局域场”和“强耦合接口”的角色，把量子发射体和光子线路连接起来。

#### 2011：Plasmonics 进入量子图景

英文对照：**Plasmonics Goes Quantum**

Jacob 和 Shalaev 强调，纳米尺度模式体积可以带来强耦合、反聚束等量子光学效应。这个事件的意义是重新审视 SPP：它不只是有损耗的经典电磁模式，也可以作为量子态、单光子非线性和量子信息接口的一部分。当然，金属损耗仍是量子 Plasmonics 的核心挑战。

#### 2012：DNA 自组装手性等离激元结构

英文对照：**DNA-based self-assembly of chiral plasmonic nanostructures with tailored optical response**

Kuzyk、Schreiber 等利用 DNA origami 高精度组装金属纳米颗粒，形成纳米尺度螺旋等手性 plasmonic structures。PPT 强调定位精度优于 $2\,\mathrm{nm}$，并且光学响应可以在 handedness、colour 和 intensity 上被理性设计和调节。它说明 Plasmonics 不只依赖电子束刻蚀等 top-down 工艺，也可以通过 bottom-up 自组装实现复杂三维光学响应。

#### 2012-2014：石墨烯等离激元，可电调的红外纳米光学

英文对照：**Gate-tuning of graphene plasmons revealed by infrared nano-imaging**；**Controlling graphene plasmons with resonant metal antennas and spatial conductivity patterns**

石墨烯支持中红外到太赫兹波段的高度局域等离激元，并且可通过栅压调节载流子密度，从而调节 plasmon 波长。PPT 中的 graphene/SiO2/Si back-gated structures 说明传播型 graphene plasmons 可以被红外纳米成像直接观察。相比金银等传统金属，石墨烯的优势是主动可调，适合红外调制、传感和可重构 plasmonic circuits。

#### 2013：单向手性传播 SPP

英文对照：**Unidirectional Chiral Propagating SPP**；**Near-Field Interference for the Unidirectional Excitation of Electromagnetic Guided Modes**

Zayats 等研究了圆偏振偶极近场干涉如何单向激发波导模式。直观说，手性源的近场具有自旋角动量，和 SPP 的传播方向-偏振锁定相结合，可以让能量主要向一个方向耦合。这与 spin-orbit interaction of light、quantum spin Hall effect of light 等方向相连，可用于片上单向量子光路和偏振纠缠信息处理。

#### 2014：量子隧穿控制等离激元共振

英文对照：**Quantum Tunnelling between Plasmon nanostructures**；**Quantum Plasmon Resonances Controlled by Molecular Tunnel Junctions**

当两个金属纳米结构之间的间隙缩小到亚纳米尺度时，经典电磁理论会预测极强 gap field；但实际电子可以发生隧穿，改变电荷积累和共振模式。Nijhuis 等通过分子隧穿结控制 plasmon resonance，说明量子输运会重塑纳米间隙等离激元。这是从经典 Plasmonics 走向 quantum-corrected Plasmonics 的关键例子。

#### 综述文章：PPT 用来建立全局视野的三条线

英文对照：**Surface plasmon resonance sensors: review**；**Surface plasmon subwavelength optics**；**Photonic structures in biology**；**Plasmonics: Merging Photonics and Electronics at Nanoscale Dimensions**；**Nano-optics from sensing to waveguiding**

PPT 第 36-37 页单独列出综述文章，是为了把领域分成几条主线。Homola 等的 SPR sensors review 对应传感主线；Ebbesen 等的 Surface plasmon subwavelength optics 对应亚波长光学与器件主线；Sambles 等的 Photonic structures in biology 对应自然界微纳光学结构；Ozbay 的 Merging Photonics and Electronics 强调 plasmonics 作为光子学和电子学之间的尺度桥梁；Halas 的 Nano-optics from sensing to waveguiding 则把传感、局域场和导波放在同一纳米光学框架中。

#### Progresses 1：设计型表面等离激元、负磁导率和纳米颗粒波导

英文对照：**Local detection of electromagnetic energy transport below the diffraction limit in metal nanoparticle plasmon waveguides**；**Experimental Verification of Designer Surface Plasmons**；**Nanofabricated media with negative permeability at visible frequencies**

Maier 等展示金属纳米颗粒链中低于衍射极限的能量传输，说明离散金属颗粒也能像波导一样通过近场耦合传递电磁能量。Hibbins、Evans、Sambles 的 designer surface plasmons 验证了人工结构可以在非自然频段模拟和设计表面等离激元。Grigorenko、Geim 等的负磁导率可见光纳米结构则连接到 metamaterials，说明微纳金属结构可产生自然材料没有的有效电磁参数。

#### Progresses 2：超透镜、非周期孔阵列、超平滑金属和单 SPP 波粒二象性

英文对照：**Magnifying Superlens in the Visible Frequency Range**；**Transmission resonances through aperiodic arrays of subwavelength apertures**；**Ultrasmooth Patterned Metals for Plasmonics and Metamaterials**；**Wave-particle duality of single surface plasmon polaritons**

Smolyaninov 等的 visible superlens 延续超分辨成像主线；Matsui 的 aperiodic arrays 说明异常透射不只存在于简单周期结构，非周期孔阵列也能产生透射共振；Nagpal 等强调金属表面粗糙度会显著影响损耗和器件性能，因此 ultrasmooth patterned metals 是实用 plasmonics 的工艺基础；Kolesov 等展示 single surface plasmon polaritons 的波粒二象性，把 SPP 明确推向单量子层面的实验研究。

#### Applications 1-2：生长控制、负折射、慢光、SERS、微腔和催化探针

英文对照：**Controlling anisotropic nanoparticle growth through plasmon excitation**；**Negative Refraction at Visible Frequencies**；**Slow guided surface plasmons at telecom frequencies**；**Measurement of the Distribution of Site Enhancements in Surface-Enhanced Raman Scattering**；**High-Q surface-plasmon-polariton whispering-gallery microcavity**；**Nanoplasmonic Probes of Catalytic Reactions**

这些应用页说明 Plasmonics 的功能不只限于导波。Jin 等利用 plasmon excitation 控制纳米颗粒各向异性生长，体现光场反过来调控材料形貌；Lezec、Dionne、Atwater 的 visible negative refraction 连接到负折射超材料；Sandtke 和 Kuipers 的 telecom slow guided surface plasmons 面向通信波段慢光；Fang 等测量 SERS site enhancements 的空间分布，回答热点到底在哪里；High-Q SPP whispering-gallery microcavity 把 SPP 与微腔高品质因子结合；Larsson 等用纳米等离激元探针研究催化反应，把 SPR 敏感性用于化学过程监测。

#### Applications 3-4：石墨烯传感、窄线宽纳米棒、单分子反应、手性纳米颗粒、电光调制和 OLED 增强

英文对照：**Mid-infrared plasmonic biosensing with graphene**；**Femtosecond laser reshaping yields gold nanorods with ultranarrow surface plasmon resonances**；**Real-space and real-time observation of a plasmon-induced chemical reaction of a single molecule**；**Amino-acid- and peptide-directed synthesis of chiral plasmonic gold nanoparticles**；**Low-loss plasmon-assisted electro-optic modulator**；**Stable, high-performance sodium-based plasmonic devices in the near infrared**；**Plasmonic enhancement of stability and brightness in organic light-emitting devices**

PPT 第 43-44 页列出更近年的应用方向：石墨烯中红外生物传感利用可调 graphene plasmons；飞秒激光 reshaping 让金纳米棒具有超窄 SPR 线宽；单分子 plasmon-induced chemical reaction 的实时实空间观测把 plasmonics 带入表面化学动力学；氨基酸/多肽指导合成手性金纳米颗粒则连接到 chiral plasmonics；低损耗 plasmon-assisted electro-optic modulator 说明 plasmonics 可以进入高速调制器；钠基 near-infrared plasmonic devices 和 OLED 稳定性/亮度增强则显示材料体系和光电器件应用仍在扩展。

#### 2015-2020：热载流子、石墨烯极限与单分子输运

英文对照：**Efficient hot-electron transfer by a plasmon-induced interfacial charge-transfer transition**；**Fundamental limits to graphene plasmonics**；**Determining plasmonic hot-carrier energy distributions via single-molecule transport measurements**

后期 PPT 还列出一组 Nature/Science 前沿：plasmon-induced hot electron transfer、graphene plasmonics 的基本极限、以及用单分子输运测量 hot-carrier energy distributions。这些工作把 Plasmonics 推向能量转换、光化学、光催化和纳米电子输运问题。重点不再只是场增强，而是“光激发表面等离激元后，能量如何变成电子、热、化学反应或电信号”。

这条历史线说明：Plasmonics 从经典表面波和散射问题出发，经历了亚波长透射、方向性发射、纳米天线、超分辨、波导集成、量子发射体耦合、spaser、石墨烯等离激元、量子隧穿和热载流子等阶段。它的核心始终是同一个问题：如何利用金属或低维导体中的自由载流子集体振荡，在亚波长尺度上重塑光场和光-物质相互作用。

### 2.2 SPP 波导

SPP 波导的基本目的：在亚波长尺度传输光，实现器件小型化与高密度集成。

课堂补充的读法：看到任何一个 SPP 波导，先问两个问题。

- **束缚光场能力**：场到底压在金属表面、槽底、gap 中，还是大部分漏到外面？束缚越强，器件可做得越小，串扰越低。
- **传播长度**：传播常数有虚部，金属有欧姆损耗，所以模式一定会衰减。束缚越强往往越靠近金属，损耗也可能越大。

因此 SPP 波导设计几乎一直在做一个折中：既想要 sub-wavelength confinement，又想要 long-range propagation。很多“新波导”的真正卖点，不是形状新，而是它在这两个指标之间找到了更好的平衡。

常见类型：

- 平面波导
- 槽形波导
- 柱形波导/金属纳米线
- 金属纳米管
- 金属纳米球链波导
- 弯形波导和 T 型分束器
- 金属-介质混合型波导
- 杂化 SPP 波导
- C 型、弯曲混合波导等复杂结构

共性特点：

- 尺度在亚波长范围内。
- 电场束缚在金属表面或间隙区域。
- 传播长度有限，因为金属存在欧姆损耗。
- 主要用于分束器、干涉仪、环形谐振器、集成纳米光子器件。

几个结构的物理图像：

#### 2.2.1 纳米金属条形 SPP 波导

英文对照：**Plasmon-polariton waves guided by thin lossy metal films of finite width: Bound modes of asymmetric structures**

金属条形波导相当于有限宽度、有限厚度的金属薄膜。PPT 中的色散图显示：由于横向 $x$ 和 $y$ 方向都存在对称/反对称组合，条形波导可出现四支 SP 模式。传播常数实部决定模式相速度和有效折射率，虚部决定衰减和传播长度。

图像上的关键结论：

- 厚度较薄时，倏逝波特征明显，场向周围介质延伸更多。
- 不同对称性的模式损耗不同，传播长度不同。
- 条形结构比无限平面更接近真实芯片波导，但也引入边缘散射和模式分裂。

#### 2.2.2 槽形 SPP 波导与 channel plasmon

英文对照：**Channel Plasmon-Polariton Guiding by Subwavelength Metal Grooves**；**Single-mode subwavelength waveguide with channel plasmon-polaritons in triangular grooves on a metal surface**

槽形波导是在金属表面刻出 V 型或三角形沟槽。PPT 中的场分布显示，电磁能量集中在槽内，尤其靠近槽底区域，因此适合把光限制在亚波长尺度。

理解角度：

- 可把它和 MIM 波导类比：都是通过金属边界把模式压到狭窄介质区域。
- 槽形波导通常希望同时获得较好局域性和较长传播长度。
- Ebbesen 小组进一步把 channel SPP 做成干涉仪和环形谐振器，说明这种结构可以从“单根波导”扩展为集成纳米光子器件。

#### 2.2.3 柱形 SPP 波导：金属纳米线与金属纳米管

英文对照：**L. Novotny et al, Phys. Rev. E 50, 4094 (1994)**

柱形波导具有圆柱对称性，因此比任意三维结构更容易解析。PPT 区分了金属纳米线和金属纳米管：

- 金属纳米线：对每个角向阶数 $n$，可出现表面模式，如 $TM_0$、$HE_n$ 等。
- 金属纳米管：存在 $HE_1$ 表面模式以及多个管内波导模式 $HE_{1n}$；当管内径减小时，部分管内模式会截止。
- 表面模式和波导模式之间可发生模式转换。

这类结构常用于理解一维 SPP 传播，也常作为量子点、分子等纳米发射体的耦合通道。

#### 2.2.4 球链 SPP 波导

英文对照：**Plasmonics: Localization and guiding of electromagnetic energy in metal/dielectric**

球链波导由一串金属纳米颗粒组成。能量不是在连续金属表面传播，而是通过相邻颗粒之间的近场耦合逐个传递。

PPT 的主要图像结论：

- 小球上的电场偏振不同，会形成横向 $T$ 模式和纵向 $L$ 模式。
- 小球间距改变会移动消光峰位置。
- 颗粒链可实现低于衍射极限的能量传输，但损耗和制造误差会影响传播距离。

直观上，球链像“等离激元版耦合谐振器阵列”：每个颗粒是一个局域 SPR 谐振器，相邻谐振器靠近场耦合形成传播带。

#### 2.2.5 聚焦后用 SPP 波导传输

英文对照：**Plasmonics: Merging Photonics and Electronics at Nanoscale Dimensions**

PPT 展示了半圆排列纳米小孔把入射光聚焦，聚焦后的能量再耦合进 SPP 波导传输的示意。这个例子说明 SPP 器件不只是“传输线”，还可以把自由空间光的聚焦、耦合和片上传输整合起来。

设计要点：

- 纳米孔阵列提供相位调控和动量匹配。
- 焦点处近场增强更容易耦合到金属波导模式。
- 这类结构体现了“自由空间光学元件 + SPP 波导”的混合器件思路。

#### 2.2.6 弯形波导与 T 型分束器

英文对照：**Bends and splitters in metal-dielectric-metal subwavelength plasmonic waveguides**

PPT 显示 SPP 通过弯形波导和 T 型分束器后仍可保持较高透射率。其意义是：如果 SPP 只能直线传播，就无法构成复杂回路；弯曲和分束能力是构建片上 plasmonic circuit 的基本单元。

弯曲结构需要平衡：

- 弯曲半径越小，器件越紧凑，但散射和辐射损耗更强。
- MIM 型波导局域强，适合急弯，但欧姆损耗更明显。
- 介质混合型波导损耗较低，但弯曲半径通常不能过小。

#### 2.2.7 金属-介质混合型波导与杂化 SPP 波导

英文对照：**Hybrid plasmonic waveguide**；**Sub-wavelength confinement and long-range propagation**

混合型波导的目标是同时获得强局域和长传播。PPT 给出两类图像：

- 金属界面附近放置介质条，通过近场耦合把传播的 SP 能量局域在介质条上。
- 高折射率介质纳米线、低折射率 gap 和金属半空间组成 hybrid waveguide，介质柱基模与金属界面 SPP 杂化。

核心结论：

- 电磁场可被局域在 gap 中或高介电常数材料中。
- gap 区域越薄，局域越强，但对金属损耗更敏感。
- 杂化模式是“介质波导模式 + SPP 模式”的折中，常用于低损耗、亚波长光互连。

文稿中老师用“模式耦合”解释 hybrid waveguide：上方介质纳米线本身有一个介质波导模式，下方金属界面本身有一个 SPP 模式；如果两者传播常数接近、近场重叠足够大，就会发生杂化。耦合强度可直观理解为两个模式近场的 overlap，离得越远 overlap 越小，耦合趋近于零；离得越近，gap 中电场越强。这个图像也提醒我们：杂化不是凭空多出一个“神奇模式”，而是已有模式在空间靠近后重新组合。

#### 2.2.8 其它 SPP 波导结构

PPT 还给出 C 型波导、弯型混合波导以及若干示意性结构。它们共同说明：SPP 波导的设计空间很大，几何边界就是模式工程的工具。改变截面形状、金属厚度、介质折射率、gap 宽度和弯曲路径，都可以改变局域性、损耗、模式数和耦合效率。

### 2.3 SPR 及其应用

SPR 是局域金属颗粒或纳米结构中的表面等离激元共振。通过调节材料、尺寸、形状、周围介质和颗粒间距离，可以把共振调到可见光、近红外、中红外甚至更长波段。

课堂补充的读法：SPR 应用的共同出发点不是“金属颗粒很漂亮”，而是局域模式带来的三件事。

- 光场被压在纳米结构附近，尤其是尖角、gap、粗糙热点。
- 共振频率对形状、尺寸、材料和环境折射率非常敏感。
- 共振模式可以和分子、量子点、半导体、石墨烯、化学反应等其它自由度耦合。

所以这一节看到各种 nanocube、nanoshell、nanorod、nanostar、nanocrescent 时，不要逐个死记形状；要问它改了哪个边界条件、产生了什么热点、共振峰怎样移动、能服务哪类测量或器件。

#### 2.3.1 SERS / TERS

表面增强拉曼散射依赖 SPR 造成的局域电场增强。典型机制：

- 纳米颗粒、纳米岛、尖角和间隙处产生热点。
- 局域场增强使拉曼信号强度大幅提升。
- 聚集、尖端、星形、月牙形等结构常能产生更强热点。

课件例子：

- 13 nm 金小球孤立时共振约在 520 nm，聚集后红移到约 700 nm，并在 647 nm 激发下增强 SERS。
- 银纳米岛尺寸增大时，共振红移，场增益系数增加。
- 金 nanostar、nanocrescent、nanoring 等具有多重共振和尖端局域场，适合超灵敏检测。

Raman/SERS 的能级图可以这样理解：入射光把分子激发到虚能级，随后散射回不同振动态。Rayleigh scattering 不改变振动态；Stokes Raman scattering 输出光频率降低；anti-Stokes Raman scattering 输出光频率升高。SERS/TERS 的作用不是改变 Raman 选择定则本身，而是通过金属纳米结构的局域场热点增强入射场和散射场，使原本很弱的 Raman 信号变得可测。

TERS（Tip Enhanced Raman Scattering）把增强结构做成金属探针尖端。尖端半径小、曲率大，局域电场强，可同时获得高空间分辨和 Raman 光谱信息。

#### 2.3.2 形状调控

不同形状带来不同 SPR：

- PPT 总览图显示，纳米结构形状可以把 SPR 调到可见光、近红外、中红外甚至更长波段。银纳米球偏短波，金纳米棒、纳米壳、nanostrip 等可覆盖更长波长。
- 纳米三角形：尺寸增大导致红移，可出现偶极与四极共振。
- nanobar / nanorice：百纳米尺度内可用散射谱表征，DDA 常用于理论计算。
- 金纳米棒：共振从可见到近红外，适合 SERS 与生物成像。
- 金纳米笼：光学性质可调，可用于靶向光热治疗。
- C 型/nanoring：多重 SPR 模式。

基本规律：

- 尺寸增大，通常红移。
- 尖角、缝隙、狭窄间隔增强局域场。
- 形状越复杂，多极与多重共振越丰富。

几个典型图像结论：

- 银纳米三角形尺寸增大时，共振红移；近场图和电荷图显示偶极、四极等模式具有不同热点分布。
- SNOM 可直接探测共振时的近场分布，并与 AFM 形貌和理论计算相互印证。
- nanobar 和 nanorice 的散射谱随长宽比明显改变，说明各向异性几何是调谐 SPR 的强手段。
- nanocrescent、nanostar 的尖角会集中电场，因此特别适合超灵敏 SERS。
- nanoring 或 C 形结构可产生多个环流/电偶极/多极模式，表现为多重 SPR 峰。

文稿中还强调了一个尺度连续性：小金属球从十几纳米到几十纳米时，主要看偶极和少量多极 SPR；颗粒继续变大，高阶多极越来越多；再到微米级介质球时，就会接近回音壁模式的语言。也就是说，SPR、Mie 多极和 WGM 不是完全割裂的名字，而是在不同尺度、材料和边界条件下描述模式的不同习惯。

#### 2.3.3 颗粒间耦合

两个或多个金属颗粒靠近时，SPR 会发生耦合，类似能级杂化。

典型结论：

- 两个银球中，光场偏振平行于中心连线时共振红移；垂直于中心连线时共振蓝移。
- 金纳米棒也有类似规律：平行排列红移，垂直排列蓝移，相互垂直时可出现模式分裂。
- 距离越近，耦合越强，红移或蓝移越明显。
- 颗粒数增加会增强集体耦合效应。

这部分是“plasmon ruler”的基础：可以用 SPR 峰位变化反推出纳米间距。

PPT 中的 dimer 图像可以用“等离激元能级分裂”理解：两个颗粒靠近时，各自的偶极模式会耦合成较低能和较高能的组合。平行于颗粒中心连线的偏振会让相邻端面出现相反电荷，增强吸引型耦合，常导致红移；垂直偏振下耦合方式不同，常表现为蓝移。距离越近，耦合越强，峰位移动越明显。

Plasmon ruler equation 的经验意义是：峰移随颗粒间距增加快速衰减，因此可用吸收/散射谱中的 SPR 峰位估计纳米尺度距离变化。它适合监测分子构象变化、颗粒聚集和纳米组装过程。

#### 2.3.4 太阳能、非线性、生物传感和存储

SPR 应用的共同逻辑是利用强吸收、强散射或强近场。

应用例子：

- 太阳能收集：调节金/银纳米球壳的核壳比例，让吸收谱覆盖太阳光谱。
- 二次谐波/三次谐波：SPR 增强局域场，提高非线性响应。
- 多波混频：耦合纳米金颗粒可增强频率转换。
- 生物传感：环境折射率变化导致 SPR 峰位移动。
- 五维光存储：利用波长、偏振和空间维度进行复用。
- gap plasmon：间隙模式可增强自发辐射、单光子收集、强耦合与真空倏逝场效应。

更具体地说：

- 太阳能收集中，金属纳米球壳的核壳比例改变会移动吸收峰；把不同尺寸球壳混合，可让吸收覆盖约 $200-1500\,\mathrm{nm}$ 的太阳光谱区域。
- 非线性光学中，银岛膜在 $1060\,\mathrm{nm}$ 激发下可产生 $530\,\mathrm{nm}$ 二次谐波；三次谐波例子中还可见 $355\,\mathrm{nm}$ 输出，且膜厚存在最优值。
- 多波混频依赖耦合金纳米颗粒的局域场增强，把频率转换集中到纳米热点附近。
- 生物传感利用环境折射率变化导致的 SPR 峰位移动；不同表面修饰可让传感具有分子选择性。
- 五维光存储把 wavelength、polarization、spatial dimensions 复用，利用金纳米棒的各向异性 SPR 写入更多信息维度。
- gap surface plasmon 是后续量子微纳光学的重要入口：它能增强 spontaneous emission、提高 single photon collection、产生 strong coupling，甚至用于讨论 evanescent vacuum。

### 2.4 周期性结构中的 SPP

周期金属纳米结构可看成 polaritonic crystals。它与光子晶体类似，但对象是金属-介质界面上的 SPP 或局域 SPR。

课堂文稿里这一节的真实重点是把“光子晶体的能带/带隙直觉”搬到 SPP。带就是有模式、能传播的频率区间；带隙就是没有对应模式、不能传播的频率区间。周期性金属表面同样可以通过周期、孔径、孔深、沟槽和材料参数来改写 SPP 的色散关系。

对比：

- 光子晶体：周期性介质结构，周期约为光波长，产生光子带隙。
- 等离激元晶体：金属表面周期性缺陷或孔阵列，周期约为 SPP 波长，产生 SPP 带隙、散射、异常透射和方向性发射。

重要现象：

- 异常光透射：亚波长孔阵列透过率远超单孔预期，源于光与表面等离激元耦合。
- 厚度影响：薄膜中两侧 SPP 模式可耦合产生共振透射；膜变厚后耦合减弱，透射下降。
- Beaming：孔周围表面起伏或光栅把出射光重定向，实现高方向性发射。
- 局域到扩展的转变：孤立颗粒以 LSPR 为主；颗粒接近形成小 gap；连续金属薄膜孔阵列中扩展 SPP 占主导。
- 几何共振：周期结构中衍射极与 SPR 相互激励，形成窄线宽、高强度共振。

补充课堂直觉：

- Extraordinary optical transmission 不是“凭空穿过去很多光”，而是相对于小孔占空比和 Bethe 小孔直觉来说透射异常增强。课上用例子说，占空比约 $10\%$ 时，透射可到 $11\%-13\%$，这个“略超占空比”的事实在亚波长孔阵列中已经很反常。
- 超透通常发生在允许传播的导带附近，而不是带隙中。带隙里没有对应模式，自然不利于透射增强。
- 薄膜厚度很关键：薄膜较薄时，上下表面的 SPP 可相互耦合，光可经历 light $\rightarrow$ SPP $\rightarrow$ light 的转换；膜变厚后，两侧耦合衰减，异常透射变弱。
- 牛眼结构和带沟槽的小孔不是只增强总透射，还能重整出射相位，使光变得更准直，这就是 beaming。
- 周期结构中的透射最大常和反射最小、吸收最大联系在一起；这说明入射光确实被耦合进了表面模式，而不是普通几何穿孔透射。

PPT 中把 photonic crystals 和 polaritonic crystals 做了并列比较：

- Photonic crystals 是周期性介质结构，周期约为光波长，通过 Bragg 散射形成 photonic band gaps，用来选择性透射或反射某些频率。
- Polaritonic crystals 是金属-介质界面上的周期缺陷或孔阵列，周期约为 SPP 波长，可形成 SPP band gaps，并实现 SPP 到 SPP、SPP 到光的散射。
- 光子晶体主要通过介质折射率和周期调节性质；等离激元晶体则还可以通过金属表面形貌、孔深、孔径、沟槽周期等调节。

异常透射的理论图像：

- 表面阻抗边界条件可较好解释实验。
- 增强透射来自 surface plasmons 辅助的隧穿。
- 薄膜较薄时，光在孔内多次往返，形成类似电子 resonant tunneling 的相干增强。
- 膜变厚时，两个表面的 SP 模式耦合减弱，透射随厚度指数下降；再厚时，更像入射光先被困在一个表面的 SP，再隧穿到另一侧 SP，最后耦合出射。

Beaming 的物理图像：

- 单个亚波长孔本来会强烈发散。
- 孔周围的周期 corrugations 提供相位调控和动量匹配。
- 出射光由表面结构重新组织成方向性较强的光束。

Sambles 小组的工作强调：金属表面周期点阵可以在可见光区域形成 surface modes 的 full photonic band gap。PPT 例子中周期约 $300\,\mathrm{nm}$，点半径约 $100\,\mathrm{nm}$，银膜厚度约 $40\,\mathrm{nm}$。这说明 SPP 也可以像光子晶体中的光一样，通过周期结构形成带隙和色散调控。

文稿中还补了一个科研史层面的判断：Sambles 小组较早做了周期结构和 band gap 相关工作，但其中一部分在微波波段，且没有以“超透”这个极有冲击力的光学现象来组织故事，因此影响力被 Ebbesen 小组的 1998-2003 年工作盖住。这里可学到一个经验：同样的物理机制，在哪个波段实现、以什么现象呈现、怎样讲清楚它的意义，会显著影响领域反应。

局域到扩展的转变可以这样记：孤立金属纳米颗粒以 localized SPP/LSPR 为主；颗粒靠近时出现小间隙和强近场耦合；当颗粒并合成连续金属薄膜孔阵列时，extended SPP 成为主导。

课堂还举了两个和周期性有关的细节：

- 矩形孔、长方形孔也可以发生异常透射；孔的纵横比越大，透射增强可能越强，因为孔形状会改变局域模式和耦合效率。
- 金属纳米颗粒阵列中，近场耦合与衍射级相互作用可形成超窄线宽。宽线宽通常来自单颗粒 SPR，窄线宽来自周期衍射/集体模，两者耦合时容易出现 Fano 型谱线。

纳米金椭球链中的超窄几何共振来自近场衍射效应。PPT 给出的例子中，金颗粒约 $60 \times 40 \times 15\,\mathrm{nm}^3$，折射率 $n=1.46$，周期 $h=519\,\mathrm{nm}$。其极化率满足类似：

$$
\sigma_{\mathrm{ext}} \propto k\,\operatorname{Im}(\alpha^*)
$$

其中 $1/\alpha$ 与阵列和函数实部的交点会导致消光极大。几何共振通常线宽很窄，适合折射率传感和窄带滤波。

## 3. 第三章：介观光学理论方法

### 3.1 为什么需要理论和数值方法

介观光学结构的尺寸可与波长相当，甚至远小于波长。此时：

- 边界形状复杂。
- 近场分布强烈依赖几何细节。
- 可解析求解的模型有限。
- 实际器件常需要数值计算。

课堂文稿把这一节讲得更像“为什么要学方法论”。核心观点是：理论方法不只是计算工具，而是看问题的角度。AI、商用软件、开源代码可以帮你把 Maxwell 方程算出来，但它们不能替你判断结果是否可信、物理图像是否合理、参数变化是否抓住了主要矛盾。

为什么解析解很少：

- 平面单界面、多层平面膜、球、圆柱等高对称结构可以解析或半解析处理。
- 薄膜上放一个球、椭球、三角形、粗糙边界、复杂纳米天线等真实结构，通常就不能靠手推解析解。
- 实验制备出来的结构往往“奇形怪状”，理论必须发展 FDTD、FEM、CDA、DDA、TMM、GFM/GMM 等方法来处理。

判断一个数值结果是否可信时，至少要问：

- 是否满足已知极限：例如小球结果能否回到 Mie 理论或准静态近似。
- 是否有网格/时间步/边界条件收敛检查。
- 是否和实验趋势、文献结果或另一种方法交叉验证。
- 是否符合基本物理直觉：尺寸变大是否红移，gap 变小是否增强近场，损耗变大是否降低传播长度。

课件中的方法分类：

- 纯数值：FDTD、FEM
- 偶极近似：CDA、DDA
- 周期结构：MMS、PWE
- 不规则纳米结构：GFM、TMM

### 3.2 FDTD：有限时域差分

FDTD 是电磁领域最常用的纯数值方法之一。它直接离散 Maxwell 方程，在时域推进电场和磁场。

基本思想：

$$
\begin{aligned}
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{H} &= \frac{\partial \mathbf{D}}{\partial t} + \mathbf{J} \\
\mathbf{D} &= \epsilon \mathbf{E} \\
\mathbf{B} &= \mu \mathbf{H}
\end{aligned}
$$

将空间导数和时间导数用有限差分近似：

$$
\frac{\partial f}{\partial t} \approx \frac{f(x,t_2)-f(x,t_1)}{\Delta t}
$$

$$
\frac{\partial f}{\partial x} \approx \frac{f(x_2,t)-f(x_1,t)}{\Delta x}
$$

FDTD 的特点：

- 适用性强：可处理任意电磁波段、任意结构、任意介电常数。
- 原理直接：本质是数值求解带边界条件的 Maxwell 方程。
- 代价较高：需要大量计算资源和时间。
- 输出需要物理判断：结果中可能有数值伪影、边界反射、网格误差，需要用物理图像提炼。

课堂中特别提醒：网格不是越小越好。$\Delta x$ 太大当然不能分辨结构；但盲目把网格取得极小，会导致计算量暴涨、数值条件变差，有时反而更容易出错。合理网格要同时看波长、最小几何尺寸、材料色散、金属 skin depth 和计算资源。例如结构特征只有 $10\,\mathrm{nm}$ 时，$1\,\mathrm{nm}$ 量级网格可能有意义；如果结构尺度是 $200\,\mathrm{nm}$，全域都用 $1\,\mathrm{nm}$ 网格可能只是浪费。

课件提到的软件：

- XFDTD
- Rsoft
- Lumerical/Solutions
- COMSOL（FEM）
- EastFDTD
- Meep：MIT 开源 FDTD 软件，常用于光子晶体和电磁仿真。

PPT 中还强调了 total field/scattered field 的分解：

$$
\mathbf{E}^{\mathrm{total}}
= \mathbf{E}^{\mathrm{incident}}+\mathbf{E}^{\mathrm{scattered}}
$$

$$
\mathbf{H}^{\mathrm{total}}
= \mathbf{H}^{\mathrm{incident}}+\mathbf{H}^{\mathrm{scattered}}
$$

这样做的意义是：入射场通常已知，真正需要数值求解的是被结构散射出来的场。将 Maxwell 方程写成散射场形式后，再把时间和空间导数离散，就能逐步推进 $\mathbf{E}$ 和 $\mathbf{H}$。

数值稳定性和网格要求也很关键。PPT 给出的直观要求是：

$$
\Delta x \ll \lambda
$$

$$
\Delta t \ll \frac{\Delta x}{\sqrt{3}c}
$$

第一条保证空间网格足够细，能分辨波长和结构细节；第二条是时间步长不能太大，否则电磁场在网格中传播会出现数值不稳定。实际仿真中，FDTD 的结果不能只看彩图，需要结合能量守恒、网格收敛、边界反射和物理图像一起判断。

文稿中还提到 Meep 这类开源 FDTD 软件和 XFDTD、Rsoft、Lumerical、EastFDTD、COMSOL 等商用/工程软件。真正写论文或报告时，不应只写“用了 FDTD”，还要说明软件、版本、网格、边界条件、材料参数来源和收敛检查；否则别人无法判断计算是否可复现。

### 3.3 CDA：耦合偶极子近似

CDA 把每个组成颗粒看成一个偶极子，只考虑偶极之间的耦合。

适用范围：

- 纳米颗粒尺寸远小于波长。
- 高阶多极共振影响较小。
- 颗粒间距较大，一般大于半个波长时偶极近似较可靠。
- 组成单元常为球、椭球，也可推广到其他形状。

课堂补充：CDA 中的“偶极子”是真实纳米颗粒的等效响应。它能成立，是因为小颗粒的主要辐射通道通常是偶极；四极、八极等高阶暗模式传播不远。如果颗粒太大、颗粒间距太小，或者 gap 中多极/电荷转移很强，CDA 就会失效。

核心方程：

$$
P_i = \alpha_i E_{\mathrm{loc},i}
$$

$$
E_{\mathrm{loc},i} = E_{\mathrm{inc},i} + E_{\mathrm{dipole},i}
$$

对 $N$ 个颗粒建立 $N$ 个自洽线性方程，求出每个偶极矩 $P_i$，再计算消光、吸收、散射。

更完整地说，局域场由入射场和其它偶极子的散射场共同决定：

$$
E_{\mathrm{loc},i}
= E_{0}\exp(i\mathbf{k}\cdot\mathbf{r}_i)
- \sum_{j=1,j\ne i}^{N} A_{ij}P_j
$$

因此 CDA 的核心是一个自洽线性方程组。求出所有 $P_i$ 后，可计算消光截面和吸收截面。PPT 中给出的形式强调：消光与入射场和诱导偶极矩的相干响应有关，吸收还要扣除偶极子辐射散射损失。

小球的偶极极化率可由 Mie 理论中的偶极展开系数 $a_1$ 给出：

$$
\alpha_{\mathrm{dipole}}=\frac{3a_1}{2k^3}
$$

这条公式很有用：它把 Mie 理论和 CDA 连接起来。对球形颗粒，单颗粒响应可以从精确解中提取；对非球形颗粒，则需要近似模型或其它数值方法先求极化率。

对非球形颗粒，文稿给出的实用思路是：先用可靠方法或文献结果求单颗粒的偶极响应 $\alpha$，再把它放进 CDA 计算整个阵列。也可以先从全是球的体系开始，与已知文献或 Mie/CDA 结果对上，再逐步把一两个颗粒换成方形、三角形或其它形状。这样做不是形式主义，而是在给复杂模型建立可信的基准。

优点：

- 物理图像清楚。
- 计算比全波方法轻。
- 特别适合颗粒阵列、几何共振、窄线宽共振分析。

缺点：

- 只保留偶极模式。
- 颗粒太大、间距太小或高阶多极强时不准确。

CDA 在周期阵列中常用于解释几何共振（geometric resonance）。几何共振的物理图像是：周期结构中的衍射级与单颗粒 SPR 相互激励、相互增强，形成线宽很窄的共振峰。PPT 中一维银纳米小球链和二维金椭球阵列都展示了这种现象。

应用上，几何共振可用于波分复用和液晶调谐：

- 多重几何共振：各个衍射级若落在 SPR 光谱范围内，都可能激发较强几何共振；峰强可大于单颗粒 SPR，线宽通常只有几个纳米。
- 液晶调谐：把纳米颗粒阵列浸入向列型液晶中，通过改变液晶光轴方向改变阵列轴向有效折射率，从而移动几何共振波长。
- PPT 给出的调谐规律是 $\Delta \lambda=\Delta n\cdot d$，调节范围与阵列周期成正比；当周期约 $460-560\,\mathrm{nm}$ 时，调节范围约 $92.7-111.7\,\mathrm{nm}$。

### 3.4 DDA：离散偶极子近似

DDA 把一个连续、不规则散射体划分为许多小体元，每个小体元作为一个偶极子。它可以看成 CDA 的网格化推广。

与 CDA 的区别：

- CDA 的偶极单元是实际纳米颗粒。
- DDA 的偶极单元是人为划分的网格单元。
- DDA 的单元极化率需要近似模型，如 Clausius-Mossotti 极化率。

适用特点：

- 可处理各种几何形状。
- 原则上不严格限制整体尺度。
- 精度取决于网格大小与极化率模型。
- 网格越细，通常越接近真实结果，但计算量越大。

典型用途：

- 金属纳米棒、nanorice、复杂颗粒的 SPR 光谱。
- 与 Mie 理论对比验证球形颗粒计算。
- 处理不易解析的形状。

DDA 与 CDA 的主要区别是“偶极子是不是实际颗粒”。CDA 中每个偶极单元就是一个真实纳米颗粒；DDA 中一个连续散射体被人为切分成很多小立方体，每个小立方体被赋予一个偶极极化率。

课堂中解释 DDA 为什么能成立：每个小体元足够小，通常只有几纳米甚至更小，远小于光波长，因此可以用准静态偶极响应描述。也就是说，DDA 不是假设整个大结构只有偶极，而是假设每个网格小体元只需要偶极；复杂多极响应由许多小偶极的集体耦合拼出来。

PPT 中给出的 Clausius-Mossotti 极化率近似为：

$$
\alpha_j^{\mathrm{CM}}
= \frac{3d^3}{4\pi}\frac{\epsilon_j-1}{\epsilon_j+2}
$$

其中 $d$ 是正方体网格边长，$\epsilon_j$ 是该网格处介电常数。这个公式在网格无限小时才严格准确，实际计算常需要修正模型。

DDA 的误差和网格大小直接相关：

- 同样半径下，划分单元越多，误差越小。
- PPT 中用复折射率 $1.33+0.01i$ 的小球与 Mie 理论比较，说明 DDA 在网格足够细时可相当准确。
- 但若网格太粗，形状边界会被阶梯化，nanobar 等结构的模拟谱与实验谱会出现差异。

文稿中还提醒：实验和理论谱线相差几十纳米在微纳实验中并不少见，关键要看趋势、模式归属和误差来源是否说得通。不要把“曲线不完全重合”简单理解为理论错，也不要因为趋势像就完全放弃收敛和参数检查。

### 3.5 TMM：转移矩阵方法

TMM 将入射光和散射光都展开为矢量球谐函数，用一个 T-matrix 联系入射场展开系数和散射场展开系数。

紧凑表达：

$$
\begin{bmatrix} p \\ q \end{bmatrix}
= T
\begin{bmatrix} a \\ b \end{bmatrix}
$$

其中 $\begin{bmatrix} a & b \end{bmatrix}^T$ 是入射场展开系数，$\begin{bmatrix} p & q \end{bmatrix}^T$ 是散射场展开系数。

求解关键：

- 通过边界条件求 T 矩阵。
- 电场、磁场切向分量在边界上连续。
- 最一般方法可用 EBCM，即扩展边界条件方法。

特点：

- 原则上适用于任意形状、任意尺度系统。
- 对有对称性的结构可大幅简化。
- 计算量通常较大，复杂形状或大尺度结构会变得困难。
- 当小球链中颗粒间距很小、偶极耦合不再足够时，TMM 比 CDA 更合适。

TMM 的计算流程可以概括为三步：

1. 把入射场、散射场和散射体内部场都用矢量球谐函数展开。
2. 用边界条件建立展开系数之间的线性关系。
3. 求出转移矩阵 $T$，再由散射场系数计算消光、散射等光学量。

最一般的求解方法是 EBCM（Extended Boundary Condition Method）。PPT 中给出的边界条件是电场和磁场切向分量连续：

$$
\hat{\mathbf{n}}\times\mathbf{E}_{+}(\mathbf{r})
=
\hat{\mathbf{n}}\times\mathbf{E}_{-}(\mathbf{r})
$$

$$
\hat{\mathbf{n}}\times\mathbf{H}_{+}(\mathbf{r})
=
\hat{\mathbf{n}}\times\mathbf{H}_{-}(\mathbf{r})
$$

求出矩阵 $Q$ 和 $\mathrm{Rg}Q$ 后，可写成：

$$
T(P)=-(\mathrm{Rg}Q)Q^{-1}
$$

TMM 特别适合处理近距离耦合的小球链。PPT 例子中，一维银小球链含 $150$ 个直径约 $15\,\mathrm{nm}$ 的银小球；随着小球间距减小，近场耦合增强，共振红移。此时如果继续用 CDA，会因为只考虑偶极耦合而不够准确，TMM 保留多极贡献，因此更合适。

### 3.6 GFM/GTM：格林函数/格林张量方法

格林函数方法通过引入参考系统的 Green tensor，把复杂边界散射问题转化为体积分方程。

课堂中的直观解释：GFM 是另一种看 Maxwell 方程的方式。FDTD/FEM 是把整个空间网格化后直接推进或求解；GFM 则先知道一个背景系统的响应 $G^0$，再把散射体看成一组极化源，这些源通过 Green tensor 把场传播到空间任意位置。边界条件并没有消失，而是被包含在所选背景 Green tensor 和积分方程里。

主线是 Lippmann-Schwinger 方程：散射体内外任意点的电场可由入射场、格林张量和散射体内部电场积分得到。

物理意义：

- 先自洽求出散射体内部电场。
- 再由积分公式得到空间任意点的近场或远场。
- 知道电场后可计算吸收、散射、消光，也可分析 SPR。

优点：

- 解析程度高。
- 包含电多极成分，比单纯偶极近似更精确。
- 适合不规则亚波长结构、纳米天线、近场问题、层状结构、有限光子带隙、SPP 表面颗粒散射等。

主要难点：

- Green tensor 在 $r = r'$ 处存在奇点，需要特殊处理。
- 课件强调这是方法中的主要近似来源。
- 网格大小需要谨慎，光波段常用约 `5-15 nm`。

文稿中说得更直接：$G^0(\mathbf{r},\mathbf{r}')$ 里的 $\mathbf{r}$ 可以在散射体外，$\mathbf{r}'$ 在散射体内；但求散射体内部自洽场时，$\mathbf{r}$ 和 $\mathbf{r}'$ 可能落在同一个小体元，这就出现 singular point。这个奇点处理不好，结果会完全错；所以 GFM 的“解析味道”很强，但实际数值实现仍然需要谨慎。

GFM 的主方程可写成 Lippmann-Schwinger 形式：

$$
\mathbf{E}(\mathbf{r})
= \mathbf{E}^{0}(\mathbf{r})
- k^2 \int d\mathbf{r}'\,
G^{0}(\mathbf{r},\mathbf{r}',\omega)
\epsilon_s(\mathbf{r}',\omega)
\mathbf{E}(\mathbf{r}')
$$

它的含义是：空间任意点的电场等于入射场加上散射体内部所有极化源通过 Green tensor 传播到该点的贡献。实际计算通常先自洽求散射体内部电场，再求外部近场或远场。

PPT 中还给出 $G$ 与 $G^0$ 的关系：

$$
G = G^0 - G^0 \epsilon_s G
$$

这个关系说明完整系统的 Green tensor 可以由参考背景 Green tensor 加上散射修正得到。对自发辐射、LDOS、近场增强等问题，Green tensor 本身就是很核心的物理量。

具体应用例子：

- 不规则纳米散射体的近场：如 3D letter F，网格一般取 $\lambda/100$ 到 $\lambda/50$，光波段约 $5-15\,\mathrm{nm}$。
- 光学纳米天线：PPT 指出 nanoantenna 理论计算可用 GTM，能解释 gap 中强场增强。
- 不规则金属 SPR：2D silver ellipse、triangle 的共振峰会随入射方向移动，近场分布也随模式改变。
- 层状结构：需要使用适合分层背景的 Green tensor。
- 有限光子带隙：GFM 可处理有限尺度结构中的带隙问题。
- SPP 表面纳米颗粒散射：当纳米颗粒离表面约 $50\,\mathrm{nm}$ 内时，颗粒越大吸收/散射越强；同等大小颗粒越靠近表面，散射所占比例越大。

校验思路也很重要。文稿中老师多次提到，当年做 GFM/GTM 时会拿 FDTD、文献结果、实验结果互相比对。例如先复现 3D letter F 的近场分布、纳米天线 gap 增强、椭圆/三角形颗粒的 SPR，再推广到自己的问题。对于层状结构或尖角结构，背景 Green tensor 和角点处理都可能成为误差来源，不能只相信一套程序。

### 3.7 GMM：格林矩阵方法与共振容量

GMM（Green's matrix method）是在 GFM 基础上发展出的表面等离激元共振分析方法。它把 Lippmann-Schwinger 方程离散成矩阵本征值问题，通过求 Green matrix 的本征值和本征矢直接获得纳米结构的共振信息和近场信息。

课堂里的核心理解是：GMM 不是先扫波长看哪儿有峰，而是先问“这个几何结构在什么介电常数下最容易形成共振”。把 Green tensor 离散成矩阵后，每个本征值/本征矢对应一种可能的场分布；再看哪个本征模式能给出最大的内部或近场响应，从而判断它是真正重要的 SPR 模式。

物理上，GMM 的关键是把“某个结构在什么介电常数下会发生 SPR”转化为材料参数和本征值的对应关系。PPT 中定义：

$$
s=\frac{1}{\epsilon(\mathbf{r},\omega)-\epsilon_0(\omega)}
$$

本征值可以直接和材料参数对应，本征矢则可表示结构内部和外部电场，包括近场与远场。

因此 GMM 的读谱方式和普通实验谱稍有不同：

- 先在“介电常数空间”里找到结构的共振条件。
- 再用真实材料的 $\epsilon(\omega)$ 把它映射回波长。
- 对金、银等几十纳米结构，若结构远小于波长，不同入射波长下求得的几何共振条件常相近。
- 不同偏振会选中不同本征场分布，因此对应不同共振。

PPT 中还引入 resonance capacity（RC，共振容量）：

$$
C_n =
\frac{\int_V d\mathbf{r}'\,|\epsilon_n|\,|\operatorname{res}[\mathbf{E}(\mathbf{r}')]_n|^2}
{\int_V d\mathbf{r}'\,|\epsilon(\omega)|\,|\mathbf{E}^{0}(\mathbf{r}')|^2}
$$

RC 的物理意义：

- 定量表达金属自由电子从环境中汇聚电磁能量的能力。
- RC 越大，通常近场增强越强。
- 通过 RC 分布可以筛选强近场 SPR 模式。
- 远场消光峰往往对应 RC 较高的 SPR。

GMM 的例子：

- 与纳米天线实验对比：$830\,\mathrm{nm}$ 下，单个纳米条可能没有明显 SPR，但加入 gap 后可出现强 SPR。
- 矩形纳米条：固定横截面后增加长度，SPR 可从可见调到红外；在 $900\,\mathrm{nm}$ 后，共振波长与长度近似线性，长度每增加 $1\,\mathrm{nm}$，共振约红移 $2.6\,\mathrm{nm}$。
- GMM 与 DDA 对比：在金/银纳米条设计中结果吻合较好。
- 二元纳米金属结构：随着两块金属介电常数变化，可出现介电影响区、共振混乱区、联合共振区、共振高原区和新共振枝出现区。通常两种金属介电常数相近时容易调节共振波长；差异较大时可能得到更强近场增益。

GMM 的局限也很清楚：由于格林矩阵对称，计算中常得到实介电常数值，而真实金属介电常数有虚部，会带来误差。PPT 的观点是：如果虚部和实部的比值较小，忽略虚部通常不严重改变 SPR 的主要性质。

文稿里还补了一点方法判断：GMM、GFM、TMM 现在未必是日常仿真最常用的工具，但它们训练的是“用本征模、偶极子、Green tensor 看问题”的能力。即使最后用 COMSOL 或 FDTD 出图，能否看懂图里的模式、判断哪个峰是偶极、哪个峰是多极、哪个峰来自阵列衍射，仍然依赖这些半解析图像。

### 3.8 方法选择速查表

| 方法 | 主要思想 | 适合问题 | 优点 | 局限 |
| --- | --- | --- | --- | --- |
| FDTD | 时域离散 Maxwell 方程 | 任意结构、任意材料、宽频响应 | 通用、直观 | 计算量大，结果需仔细分析 |
| FEM | 有限元求解频域/时域方程 | 复杂边界、多物理场 | 边界适应性好 | 网格与边界设置影响大 |
| CDA | 实际颗粒视作偶极子 | 小颗粒、稀疏阵列、几何共振 | 快、物理图像清楚 | 忽略高阶多极 |
| DDA | 连续散射体离散成偶极网格 | 不规则纳米颗粒 | 可处理复杂形状 | 精度依赖网格和极化率 |
| TMM | 矢量球谐展开系数由 T 矩阵联系 | 球形/近球形/多颗粒散射 | 多极完整、适合紧耦合 | 求 T 矩阵复杂 |
| GFM/GTM | Green tensor 积分方程 | 不规则近场、纳米天线、SPR | 解析性强、含多极 | 奇点处理困难 |
| GMM | Green matrix 本征值问题 | SPR 模式筛选、共振设计 | 可直接给出共振信息和 RC | 常忽略介电常数虚部 |

### 3.9 课堂补充：怎么读前沿文献

第三讲后半段还讲了“前沿报告”该怎么读文献，这和第二章的文献式讲法直接相关。核心不是堆很多文章，而是选一个小方向，把它的发展脉络、关键节点和自己的理解说清楚。

读文献时可以按这个顺序：

1. 先选一个足够小的方向，例如 SPP 量子接口、graphene plasmons、gap plasmon 增强发光、周期阵列几何共振等。
2. 先看综述建立地图，但真正形成观点要回到原始论文，因为综述是二手材料。
3. 读单篇论文时，先读题目和摘要。摘要通常包含背景、转折、本文做了什么、意义是什么。
4. 特别注意摘要和 introduction 里的 **however / despite / although** 一类转折句，因为它们通常指出前人没有解决的问题，也就是本文创新点的入口。
5. 正文里优先抓 model setup 或 experimental setup 的物理假设，再抓支持核心观点的关键图。不是每个参数扫描都同等重要。
6. 结论部分重点看作者声称的未来影响，但要带着判断读：多篇文章都指向同一趋势时，才更可能是真正的发展方向。

关于 AI，老师的态度可以概括为：先自己查、自己形成初步判断，再用 AI 补充和整理。若一开始就完全交给 AI，容易被它的框架牵着走，最后没有自己的问题意识。比较好的用法是：自己先定小方向、选几篇核心论文、读出主线，再让 AI 帮忙检查遗漏、补背景、整理表格。

## 4. 贯穿三章的核心概念关系

### SPP 与 SPR 的区别

SPP：

- 传播型表面模式。
- 常在平面金属-介质界面或波导中讨论。
- 关注色散、传播长度、穿透深度、相位匹配。

SPR/LSPR：

- 局域共振模式。
- 常在纳米球、纳米棒、纳米壳、尖端、颗粒阵列中讨论。
- 关注消光峰、近场增强、共振红移/蓝移、传感和 SERS。

二者并不割裂：周期孔阵列、球链、纳米波导、gap plasmon 等结构中，局域模式与传播模式会耦合和转化。

### 红移与蓝移的常见来源

红移常见原因：

- 颗粒尺寸增大。
- 外界介电常数增大。
- 球壳变薄。
- 颗粒间距变小且偏振平行于连接轴。
- 纳米棒长径比增加。

蓝移常见原因：

- 偏振垂直于颗粒连接轴且耦合增强。
- 某些反键合/高能模式增强。
- 周期或几何条件改变使衍射极移向短波。

### 局域增强的来源

局域增强一般来自：

- 共振：频率匹配 SPR/SPP。
- 几何尖端：尖角、星形、月牙形结构。
- 间隙热点：两个金属结构之间的纳米 gap。
- 阵列耦合：衍射极与 SPR 形成几何共振或 Fano 线型。

## 5. 复习时最应掌握的公式

Drude 介电函数：

$$
\begin{aligned}
\epsilon_m(\omega) &= 1 - \frac{\omega_p^2}{\omega^2} \\
\omega_p^2 &= \frac{4 \pi n e^2}{m}
\end{aligned}
$$

含损耗形式：

$$
\epsilon_m(\omega) = \epsilon_m(\infty) \left[1 - \frac{\omega_p^2}{\omega^2 + i \omega \gamma}\right]
$$

SPP 色散：

$$
k_x = \frac{\omega}{c} \sqrt{\frac{\epsilon_1 \epsilon_2}{\epsilon_1 + \epsilon_2}}
$$

SPP 存在条件：

$$
\operatorname{Re}(\epsilon_1) < 0
$$

$$
|\operatorname{Re}(\epsilon_1)| > \epsilon_2
$$

SPP 传播长度：

$$
L_i = \frac{1}{2k_x''}
$$

金属小球准静态偶极 SPR：

$$
\operatorname{Re}(\epsilon_{\mathrm{metal}}) = -2\epsilon_{\mathrm{medium}}
$$

CDA 偶极关系：

$$
P_i = \alpha_i E_{\mathrm{loc},i}
$$

$$
E_{\mathrm{loc},i} = E_{\mathrm{inc},i} + \sum_{j \ne i} E_{\mathrm{dipole},j}
$$

FDTD 差分思想：

$$
\frac{\partial f}{\partial t} \approx \frac{\Delta f}{\Delta t}
$$

$$
\frac{\partial f}{\partial x} \approx \frac{\Delta f}{\Delta x}
$$

## 6. 一句话版总结

第一章建立 SPP/SPR 的基本模型：金属负介电常数来自 Drude 自由电子响应，界面 SPP 来自 TM 波与自由电子集体振荡耦合，局域 SPR 可由 Mie 理论解释。

第二章展示 Plasmonics 的发展和应用：从异常透射、beaming、超透镜到波导、SERS、生物传感、太阳能、非线性和量子器件，核心都是利用 SPP/SPR 的亚波长局域与场增强。

第三章给出处理真实结构的方法：FDTD/FEM 直接数值解 Maxwell 方程，CDA/DDA 用偶极近似降低复杂度，TMM 和 GFM 保留更多多极与解析结构，用于复杂散射和近场问题。
