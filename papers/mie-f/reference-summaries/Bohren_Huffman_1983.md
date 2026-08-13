# Bohren & Huffman (1983) — Absorption and Scattering of Light by Small Particles

> **专著信息**: Craig F. Bohren, Donald R. Huffman. *Absorption and Scattering of Light by Small Particles*. Wiley-Interscience, 1983. Wiley Professional Paperback Edition 1998. ISBN 0-471-05772-X / 0-471-29340-7.
>
> **OCR 可信度**: B 级（详见第 4 节）。大部分可用，但若干公式密集页为 UNCERTAIN，关键公式使用前应核验原书扫描页。
>
> **核心地位**: 本领域最权威的教科书之一，介于高级专著与教材之间，既涵盖 Mie 散射的数学推导，又强调与体材料光学常数的结合。

---

## 1. 内容索引 (Content Index)

全书分为三部分共 14 章 + 3 个附录。页号指印刷版页码（源 PDF 页码）。

### Part 1 — Basic Theory (Ch. 1–8, pp. 3–222)

**Chapter 1. Introduction (pp. 3–11)**
- 1.1 散射与吸收的物理基础：入射波使电荷振荡 → 二次辐射（散射）+ 能量转化（吸收）
- 1.2 涨落散射 vs 粒子散射：本书限于粒子散射（弹性散射），排除分子涨落散射和 Raman/Brillouin 非弹性散射
- 1.3 单个粒子散射的物理图像：将粒子细分小区域 → 感应偶极矩 → 相干叠加 → 随尺寸/方向变化
- 1.4 粒子集合：单次散射 + 非相干叠加的条件
- 1.5 正问题（已知粒子求场）vs 反问题（由散射场推断粒子）

**Chapter 2. Electromagnetic Theory (pp. 12–56)**
- 2.1 麦克斯韦方程组与宏观本构关系（SI 制）：$\nabla\cdot\mathbf{D}=\rho_f$, $\nabla\times\mathbf{E}+\partial\mathbf{B}/\partial t=0$, $\nabla\cdot\mathbf{B}=0$, $\nabla\times\mathbf{H}=\mathbf{J}_f+\partial\mathbf{D}/\partial t$；$\mathbf{D}=\varepsilon_0\mathbf{E}+\mathbf{P}$, $\mathbf{H}=\mathbf{B}/\mu_0-\mathbf{M}$。本构关系 $\mathbf{J}_F=\sigma\mathbf{E}$, $\mathbf{B}=\mu\mathbf{H}$, $\mathbf{P}=\varepsilon_0\chi\mathbf{E}$，假定线性、均匀、各向同性（但频率相关）
- 2.2 时谐场：$\exp(-i\omega t)$ 约定（与 Born & Wolf, Stratton, Jackson 一致）。复介电常数 $\varepsilon = \varepsilon_0(1+\chi)+i\sigma/\omega$；**重要**：如果 $\varepsilon\neq0$，电场无散，即横波条件；仅当 $\varepsilon=0$ 时可能出现纵波
- 2.3.1 傅里叶变换与本构关系：从时域到频域的桥梁，卷积定理将频域本构关系 $\mathcal{P}(\omega)=\epsilon_0\chi(\omega)\mathcal{E}(\omega)$ 映射到时域 $\mathbf{P}(t)=\int G(t-t')\mathbf{E}(t')dt'$，说明频率依赖是时滞响应的体现
- 2.3.2 Kramers-Kronig 关系：$\chi'(\omega)$ 与 $\chi''(\omega)$ 通过 Hilbert 变换关联，是因果性的数学结果
- 2.4 空间色散：当电子平均自由程较大时可能重要，但本书假设可忽略
- 2.5 Poynting 矢量与能流：$\mathbf{S}=\mathbf{E}\times\mathbf{H}$；复 Poynting 定理；时谐场的吸收率为 $W_a = -\frac12\mathrm{Re}\int_A(\mathbf{E}\times\mathbf{H}^*)\cdot\hat{\mathbf{n}}dA$
- 2.6 无界介质中的平面波传播：色散关系 $k^2=\omega^2\mu\varepsilon$；复折射率 $N=n+ik$，$\varepsilon=(n+ik)^2$；吸收系数 $\alpha=4\pi k/\lambda$；穿透深度 $\delta=\lambda/4\pi k$；**实部 n<1 的物理解释**（第 9 章详述，源于共振近邻区的反常色散）
  - 2.6.1 电磁能量的吸收
- 2.7 平面界面上的反射与透射：
  - 2.7.1 正入射：Fresnel 反射系数 $r=(N_1-N_2)/(N_1+N_2)$；反射率 $R=|r|^2$
  - 2.7.2 斜入射：s/p 偏振的 Fresnel 公式；Brewster 角；全反射
- 2.8 平板的反射与透射：**平板-粒子类比**：平板折射率 $N_1$ 在介质 $N$ 中的透射/反射与粒子散射有深层对应——干涉条纹的间距由 $2a(N_1-N)$ 决定，该式直接预示 Mie 散射的干涉结构周期 $1/2a(m-1)$（4.4.2 节）
- 2.9 光学常数的实验测定：Kramers-Kronig 分析反射率数据获得 $n,k$
- 2.10 平板与粒子的类比：**核心论点**——反射、折射、传输本质上都是散射现象。折射率是大量分子散射的净效果（Ewald-Oseen 消光定理）
- 2.11 偏振：Jones 矢量、椭圆偏振参数 $\psi,\Delta$；Mueller 矩阵
  - 2.11.1 Stokes 参数：$I,Q,U,V$ 定义，$I^2\geq Q^2+U^2+V^2$
  - 2.11.2 Mueller 矩阵：4×4 变换矩阵

**Chapter 3. Absorption and Scattering by an Arbitrary Particle (pp. 57–81) [通用框架，不限于球]**
- 3.1 问题的一般提法：入射场 $\mathbf{E}_i,\mathbf{H}_i$ + 粒子（占据体积 V，界面 S，本构参数 $\varepsilon,\mu$）→ 内部场 $\mathbf{E}_1,\mathbf{H}_1$ + 散射场 $\mathbf{E}_s,\mathbf{H}_s$
  - 3.1.1 边界条件：$\hat{\mathbf{n}}\times(\mathbf{E}_1-\mathbf{E}_2)=0$, $\hat{\mathbf{n}}\times(\mathbf{H}_1-\mathbf{H}_2)=\mathbf{K}_f$；远场：散射场趋于横球面波 $E_s\propto (1/r)$
- 3.2 振幅散射矩阵：$\begin{pmatrix}E_{\parallel s}\\E_{\perp s}\end{pmatrix} = \frac{e^{ik(r-z)}}{-ikr} \begin{pmatrix}S_2&S_3\\S_4&S_1\end{pmatrix} \begin{pmatrix}E_{\parallel i}\\E_{\perp i}\end{pmatrix}$。一般情况有 4 个复元素；对球对称粒子，$S_3=S_4=0$，退化为对角矩阵
- 3.3 散射矩阵（Mueller 矩阵，4×4 相矩阵）：将入射 Stokes 参数 $(I_i,Q_i,U_i,V_i)$ 变换为散射 Stokes 参数。对非偏振入射，$S_{11}$ 给出散射强度角分布
- 3.4 消光、散射与吸收：
  - **光学定理** (3.24)：$\displaystyle C_{\mathrm{ext}} = \frac{4\pi}{k^2}\mathrm{Re}\{S(0^\circ)\}$。这是最优雅的定理之一——只需测量前向散射复振幅，就能获得总消光截面
  - $C_{\mathrm{ext}} = C_{\mathrm{sca}} + C_{\mathrm{abs}}$：消光 = 散射 + 吸收的能量守恒关系
  - 3.4.1 粒子平板的消光：类比平板干涉对消光结构的影响

**Chapter 4. Absorption and Scattering by a Sphere (pp. 82–129) [Mie 理论核心]**
- 4.1 矢量波动方程的解：从标量亥姆霍兹方程 $(\nabla^2+k^2)\psi=0$ 出发，通过矢量球谐函数 ${\bf M}=\nabla\times({\bf r}\psi)$ 和 ${\bf N}=(\nabla\times{\bf M})/k$ 构造无散解
  - 标量函数 $\psi_{emn}=\cos m\phi\,P_n^m(\cos\theta)z_n(kr)$, $\psi_{omn}=\sin m\phi\,P_n^m(\cos\theta)z_n(kr)$
  - 矢量球谐函数：${\bf M}_{emn}=\nabla\times({\bf r}\psi_{emn})$, ${\bf N}_{emn}=\frac{1}{k}\nabla\times{\bf M}_{emn}$
  - 球 Bessel 函数 $j_n(kr)$（原点有限）、$y_n(kr)$（原点发散）、$h_n^{(1)}(kr)$（出射波）、$h_n^{(2)}(kr)$（入射波）
- 4.2 平面波在矢量球谐函数中的展开：$\mathbf{E}_i=E_0 e^{ikr\cos\theta}\hat{\mathbf{x}}=E_0\sum_{n=1}^\infty i^n\frac{2n+1}{n(n+1)}({\bf M}_{o1n}^{(1)}-i{\bf N}_{e1n}^{(1)})$
- 4.3 内场与散射场：内场用 $j_n(mx)$（原点有限）展开，散射场用 $h_n^{(1)}(x)$（出射波）展开。边界条件在 $r=a$ 处匹配 tangential 场分量，导出 Mie 系数
  - 4.3.1 角度相关函数 $\pi_n(\mu)=P_n^1(\mu)/\sqrt{1-\mu^2}$, $\tau_n(\mu)=dP_n^1(\mu)/d\theta$。递推关系：(4.47): $\pi_n=\frac{2n-1}{n-1}\mu\pi_{n-1}-\frac{n}{n-1}\pi_{n-2}$, $\tau_n=n\mu\pi_n-(n+1)\pi_{n-1}$
  - 4.3.2 场模式图 (Fig. 4.4)：内场 TM/TE 模式图示。电型（TM, E-mode）对应系数 $a_n$，磁型（TE, H-mode）对应系数 $b_n$
  - **4.3.3 Mie 散射系数**（核心公式，Eq. 4.53, 4.56, 4.57）：
    - $x=ka=2\pi N a/\lambda$（尺寸参数），$m=N_1/N$（相对折射率，$N_1$ 粒子折射率，$N$ 介质折射率）
    - $a_n = \frac{m\psi_n(mx)\psi_n'(x)-\psi_n(x)\psi_n'(mx)}{m\psi_n(mx)\xi_n'(x)-\xi_n(x)\psi_n'(mx)}$
    - $b_n = \frac{\psi_n(mx)\psi_n'(x)-m\psi_n(x)\psi_n'(mx)}{\psi_n(mx)\xi_n'(x)-m\xi_n(x)\psi_n'(mx)}$
    - 式中 Riccati-Bessel 函数：$\psi_n(\rho)=\rho j_n(\rho)$, $\xi_n(\rho)=\rho h_n^{(1)}(\rho)$, $\chi_n(\rho)=-\rho y_n(\rho)$
    - $a_n$ 分母为零 $\leftrightarrow$ 电型共振（表面模 Fröhlich 模），$b_n$ 分母为零 $\leftrightarrow$ 磁型共振
- 4.4 截面与矩阵元
  - 4.4.1 截面公式（Eq. 4.61-4.62）：
    - $C_{\mathrm{sca}} = \frac{2\pi}{k^2}\sum_{n=1}^\infty (2n+1)(|a_n|^2+|b_n|^2)$
    - $C_{\mathrm{ext}} = \frac{2\pi}{k^2}\sum_{n=1}^\infty (2n+1)\mathrm{Re}\{a_n+b_n\}$
    - $C_{\mathrm{abs}} = C_{\mathrm{ext}} - C_{\mathrm{sca}}$
    - $W_s = I_i C_{\mathrm{sca}}$, $W_{\mathrm{ext}} = I_i C_{\mathrm{ext}}$（入射辐照度 $I_i = \frac12\Re\{\mathbf{E}_i\times\mathbf{H}_i^*\}$）
  - 4.4.2 消光例子（**核心章节，物理洞察丰富**）：
    - 水微粒在空气中的消光效率 $Q_{\mathrm{ext}}=C_{\mathrm{ext}}/\pi a^2$ 随 $1/\lambda$ 变化的计算（Fig. 4.6）
    - **干涉结构 (Interference structure)**：等间距的宽极大/极小，振荡于 $Q_{\mathrm{ext}}\approx 2$ 附近。来源于前向散射光与入射光的干涉：$\sin[x(m-1)]$ 项，峰间距 $\Delta(1/\lambda)=1/2a(m-1)$
    - **涟漪结构 (Ripple structure)**：尖锐的精细结构，来源于散射系数分母的零点（即共振，transcendental equations 4.54-4.55 的根）
    - **红化 (Reddening)**：小粒子对蓝光消光更强 → 透射光偏红。与日落红、星际消光关联
    - **关键警告**：$x$ 和 $m$ 不是独立变量——波长变化时折射率也随之变化（Eq. 4.63-4.64 推导中假设 $m$ 近似常数，但第 9-10 章指出这不通用）
  - 4.4.3 消光悖论：$x\to\infty$ 时 $Q_{\mathrm{ext}}\to 2$，为几何截面两倍。消解：衍射贡献与几何光学贡献各占一份。需要极窄前向接收角 (<1/2x rad) 才能观测到
  - 4.4.4 散射矩阵：
    - $S_1 = \sum_n \frac{2n+1}{n(n+1)}(a_n\pi_n+b_n\tau_n)$
    - $S_2 = \sum_n \frac{2n+1}{n(n+1)}(a_n\tau_n+b_n\pi_n)$
    - 4 个非零独立散射矩阵元 $S_{11},S_{12},S_{33},S_{34}$（Eq. 4.76 给出与 $S_1,S_2$ 的转换关系）
    - 角度散射函数 $i_1=|S_1|^2$（垂直偏振散射强度），$i_2=|S_2|^2$（平行偏振散射强度）
  - 4.4.5–4.4.8 角度散射、求和规则、有限束宽、带电球
- 4.5 不对称参数与辐射压：$g=\langle\cos\theta\rangle=\frac{4\pi}{k^2C_{\mathrm{sca}}}\sum_n[\frac{n(n+2)}{n+1}\Re\{a_n a_{n+1}^*+b_n b_{n+1}^*\}+\frac{2n+1}{n(n+1)}\Re\{a_n b_n^*\}]$
- 4.6 雷达后向散射截面：$\sigma_{\mathrm{back}} = \frac{|S_1(180^\circ)|^2+|S_2(180^\circ)|^2}{k^2}$，Mie 散射系数形式 $\sigma_{\mathrm{back}} = \frac{\pi}{k^2}|\sum_n(2n+1)(-1)^n(a_n-b_n)|^2$
- 4.7 热发射：粒子发射率 = 吸收率（基尔霍夫定律），$Q_{\mathrm{abs}}(\lambda,T)=Q_{\mathrm{ext}}-Q_{\mathrm{sca}}$
- **4.8 散射系数的数值计算**（对数导数法, Lentz 1976）：
  - 对数导数 $D_n(\rho)=\frac{d}{d\rho}\ln\psi_n(\rho)$，满足 Riccati 方程 $D_n'(\rho)+D_n^2(\rho)+(1-n(n+1)/\rho^2)=0$
  - 向下递推：$D_{n-1}(\rho)=\frac{n}{\rho}-\frac{1}{D_n(\rho)+n/\rho}$，从某大 $N$ 开始设 $D_N=0$ 向下推
  - $\psi_n$ 和 $\xi_n$ 向上递推：$\psi_{n+1}(\rho)=\frac{2n+1}{\rho}\psi_n(\rho)-\psi_{n-1}(\rho)$
  - 计算形式 (Eq. 4.88)：
    - $a_n = \frac{[D_n(mx)/m+n/x]\psi_n(x)-\psi_{n-1}(x)}{[D_n(mx)/m+n/x]\xi_n(x)-\xi_{n-1}(x)}$
    - $b_n = \frac{[mD_n(mx)+n/x]\psi_n(x)-\psi_{n-1}(x)}{[mD_n(mx)+n/x]\xi_n(x)-\xi_{n-1}(x)}$
  - 收敛判据：$n_c = x + 4x^{1/3} + 2$（Wiscombe 1980 的经验公式）
- **Notes**: Logan (1965) Mie 散射历史综述；Brillouin (1949) 消光悖论；Lentz (1976) 对数导数法原始论文

**Chapter 5. Particles Small Compared with the Wavelength (pp. 130–157) [Rayleigh 散射、椭球体静电学]**
- 5.1 小球近似 ($x\ll1$, $|m|x\ll1$)：
  - 对 $a_1$ 的级数展开至 $x^6$ 项：$a_1 \approx -i\frac{2x^3}{3}\frac{m^2-1}{m^2+2} - i\frac{2x^5}{5}\frac{(m^2-2)(m^2-1)}{(m^2+2)^2} + \frac{4x^6}{9}\left(\frac{m^2-1}{m^2+2}\right)^2$。首项即为 Rayleigh 近似
  - 磁偶极项：$b_1 \approx -i\frac{x^5}{45}(m^2-1)+O(x^7)$，比 $a_1$ 低两阶
  - Rayleigh 散射效率：$Q_{\mathrm{sca}} = \frac{8}{3}x^4\left|\frac{m^2-1}{m^2+2}\right|^2$（$\propto \lambda^{-4}$）
  - Rayleigh 吸收效率：$Q_{\mathrm{abs}} \approx 4x\,\mathrm{Im}\left\{\frac{m^2-1}{m^2+2}\right\}$（$\propto \lambda^{-1}$，吸收在 $x$ 很小时占主导）
  - 散射强度：$I_s = \frac{8\pi^4 N a^6}{\lambda^4 r^2}\left|\frac{m^2-1}{m^2+2}\right|^2 (1+\cos^2\theta)I_i$
  - 偏振度 $P = (1-\cos^2\theta)/(1+\cos^2\theta)$；$\theta=90^\circ$ 时 $P=1$（100% 线偏振）
- 5.2 静电学近似：粒子尺寸 $\ll$ 波长时，外场在粒子尺度上近似均匀，问题简化为静电场中的介质球
  - 极化率 $\alpha = 4\pi a^3(\epsilon-\epsilon_m)/(\epsilon+2\epsilon_m)$
  - 与 $a_1$ 首项一致：$a_1\approx -i\frac{k^3}{6\pi}\alpha$
- 5.3 椭球体静电学近似：
  - 退极化因子 $L_j$：旋转椭球的 $L_1$ 由 $L_1 = (1-e^2)/e^2[(1/2e)\ln((1+e)/(1-e))-1]$（长椭球, $e=\sqrt{1-b^2/a^2}$）；$L_1+L_2+L_3=1$；球：$L_j=1/3$
  - 极化率沿主轴：$a_j = 3V(\epsilon-\epsilon_m)/[3\epsilon_m+3L_j(\epsilon-\epsilon_m)]$
  - 重要极限：长针 ($a\gg b=c$) $L_1\approx(b/a)^2\ln(a/b)\to 0$, $L_2=L_3\approx 1/2$；薄盘 ($a\ll b=c$) $L_1\to 1$, $L_2=L_3\to 0$
- 5.4 涂层椭球：等效极化率公式，可化简为涂层球的特殊情况
- 5.5 极化率张量：各向异性粒子的诱导偶极矩 $\mathbf{p}=\alpha_{ij}\mathbf{E}_j$，变换规律
- 5.6 各向异性球：取向平均散射截面计算方法
- 5.7 散射矩阵：Rayleigh 散射的 Mueller 矩阵元，$S_{11}\propto 1+\cos^2\theta$, $S_{12}\propto \cos^2\theta-1$, $S_{33}\propto 2\cos\theta$, $S_{34}\propto 0$（非手性）

**Chapter 6. Rayleigh-Gans Theory (pp. 158–165) [弱散射近似]**
- 假设：$|m-1|\ll 1$（折射率接近环境），且 $2x|m-1|\ll 1$（相移小）。粒子任何内部点感受到的场近似等于入射场
- 6.1 振幅散射矩阵元：$S_1 = \frac{ik^3}{2\pi}(m-1)V f(\theta,\phi)$，$S_2 = S_1\cos\theta$。形状因子 $f(\theta,\phi)=\frac{1}{V}\int_V e^{i\mathbf{q}\cdot\mathbf{r}'}dV'$，$\mathbf{q}=\mathbf{k}_s-\mathbf{k}_i$
- 6.2 均匀球：形状因子 $f(\theta)=\frac{3}{(qa)^3}[\sin(qa)-qa\cos(qa)]$，$q=2k\sin(\theta/2)$。散射强度 $I(\theta)\propto (1+\cos^2\theta)f^2(\theta)$
- 6.3 有限圆柱：形状因子的解析表达式依赖于圆柱的长径比。前向散射与圆柱取向相关

**Chapter 7. Geometrical Optics (pp. 166–180) [大粒子极限近似]**
- 7.1 吸收与散射截面的渐近值：几何光学近似下，$Q_{\mathrm{ext}}\to 2$（+衍射的贡献，见 4.4.3）。反射效率依赖消光于 $m$，当 $m\to\infty$ 时 $Q_{\mathrm{abs}}\to 1$（全吸收黑体）
- 7.2 虹角：球内一次反射（primary rainbow）和二次反射（secondary rainbow）的散射角计算。入射光线追踪法（Fig. 7.2-7.3）——Descartes 理论。虹角 $\theta_R \approx 138^\circ$（对水）
- 7.3 冰晶晕：冰晶棱镜（六角形截面）的折射、光晕（$22^\circ$ 和 $46^\circ$ 晕）。最小偏向角原理。与常观气象光学现象的联系

**Chapter 8. A Potpourri of Particles (pp. 181–222) [多种粒子形态，含涂层球与无限长圆柱]**
- 8.1 涂层球（Aden-Kerker 系数, 1951）：核半径 $a$，壳半径 $b$，折射率 $N_1,N_2,N$。Mie 系数 $a_n,b_n$ 的显式表达式 (Eq. 8.1) 通过核-壳边界和壳-介质边界匹配导出，包含 4 个 3×3 行列式的比
  - 涂层球的 $a_n$: $a_n = \frac{\psi_n(y)[\psi_n'(m_2 y)-A_n\chi_n'(m_2 y)] - m_2\psi_n'(y)[\psi_n(m_2 y)-A_n\chi_n(m_2 y)]}{\xi_n(y)[\psi_n'(m_2 y)-A_n\chi_n'(m_2 y)] - m_2\xi_n'(y)[\psi_n(m_2 y)-A_n\chi_n(m_2 y)]}$ (8.1a)
    - 式中 $A_n = \frac{m_2\psi_n(m_2 x)\psi_n'(m_1 x)-m_1\psi_n'(m_2 x)\psi_n(m_1 x)}{m_2\chi_n(m_2 x)\psi_n'(m_1 x)-m_1\chi_n'(m_2 x)\psi_n(m_1 x)}$，$x=kN_1a$, $y=kN_2b$
  - 简化特殊情况：核消失 $a\to 0$ 退化为均匀球；壳消失 $N_2=N_1$ 同样退化为均匀球
  - 涂层球的表面模条件 (Eq. 12.14)：$(\epsilon_2+2\epsilon_m)(\epsilon_1+2\epsilon_2)+f(2\epsilon_2-2\epsilon_m)(\epsilon_1-\epsilon_2)=0$，$f=(a/b)^3$
- 8.2 各向异性球：介电张量 $\epsilon_{ij}$，散射场需通过本征值分解处理
- 8.3 旋光性粒子 (Optically active particles)：
  - 8.3.1 本构关系与平面波传播：$\mathbf{D}=\epsilon\mathbf{E}+i\xi'\mathbf{B}$, $\mathbf{B}=\mu\mathbf{H}+i\eta'\mathbf{E}$，两者耦合导致固有圆双折射
  - 8.3.2 矩阵元与截面：左/右旋圆偏振入射光的消光差异 $\Delta C_{\mathrm{ext}} = C_{\mathrm{ext}}^L-C_{\mathrm{ext}}^R$（圆二色性）；偏振面旋转（旋光）
- 8.4 无限长直圆柱：长度远大于半径，端效应可忽略
  - 8.4.1 正入射：TM 模（电型）与 TE 模（磁型）分别求解 Bessel 函数展开，散射系数 $a_{0n}, b_{0n}$ 用柱 Bessel 函数 $J_n$, $H_n^{(1)}$ 表达
  - 8.4.2 斜入射：更一般情况，沿轴方向的波数分量 $k_z=k\cos\zeta$（$\zeta$ 为入射角），横截面内有效折射率 $m'=\sqrt{m^2-\cos^2\zeta}/\sin\zeta$
  - 8.4.3 截面公式：每单位长度的散射/消光截面 (Eq. 8.38)
  - 8.4.4 正入射的散射振幅与散射矩阵 (Eq. 8.40)：对角散射矩阵 $S_3=S_4=0$
- 8.5 非均匀粒子——平均介电函数：Maxwell Garnett 有效介质近似 $\epsilon_{\mathrm{eff}}=\epsilon_m\frac{1+2f(\epsilon-\epsilon_m)/(\epsilon+2\epsilon_m)}{1-f(\epsilon-\epsilon_m)/(\epsilon+2\epsilon_m)}$；Bruggeman 有效介质近似 $\sum f_i(\epsilon_i-\epsilon_{\mathrm{eff}})/(\epsilon_i+2\epsilon_{\mathrm{eff}})=0$
- 8.6 非球粒子的计算方法概述：
  - 变量分离法（椭球坐标系）
  - 点匹配法（Waterman, 1965 原始方案）
  - 微扰法（小形变）
  - Purcell-Pennypacker 偶极子法（DDA, 离散偶极近似, 1973）
  - T-Matrix 方法（Waterman, 1971, 扩展边界条件法）

### Part 2 — Optical Properties of Bulk Matter (Ch. 9–10, pp. 227–283)

**Chapter 9. Classical Theories of Optical Constants (pp. 227–267)**
- 9.1 Lorentz 谐振子模型：$\epsilon(\omega) = 1 + \frac{\omega_p^2}{\omega_0^2-\omega^2-i\gamma\omega}$。$\omega_0$ 为共振频率，$\gamma$ 为阻尼系数，$\omega_p=Ne^2/m\epsilon_0$ 为等离子体频率
  - 实部 $\epsilon'(\omega)$ 在共振附近经历反常色散变化；虚部 $\epsilon''(\omega)$ 在 $\omega_0$ 处有 Lorentzian 线型峰
  - 弱吸收区：$\epsilon'(\omega)\approx 1+\omega_p^2/(\omega_0^2-\omega^2)$；透明介质色散公式 Cauchy 方程
  - 对金属电子行为：$\omega_0=0\to$ Drude 模型
  - 对晶格振动（红外）：$\epsilon(\omega)=\epsilon_\infty+(\epsilon_s-\epsilon_\infty)\omega_{\mathrm{TO}}^2/(\omega_{\mathrm{TO}}^2-\omega^2-i\gamma\omega)$，其中 $\omega_{\mathrm{TO}}$ 为横光学声子频率，$\epsilon_s$ 是静态介电常数，$\epsilon_\infty$ 是高频介电常数。Lyddane-Sachs-Teller 关系 $\omega_{\mathrm{LO}}^2/\omega_{\mathrm{TO}}^2=\epsilon_s/\epsilon_\infty$
- 9.2 多谐振子模型：$\epsilon(\omega)=1+\sum_j f_j\omega_p^2/(\omega_j^2-\omega^2-i\gamma_j\omega)$，$f_j$ 为振子强度
- 9.3 各向异性谐振子模型：张量 $\epsilon_{ij}(\omega)$，单轴晶体 $(\epsilon_\perp,\epsilon_\parallel)$ 的寻常光/非寻常光折射率计算
- 9.4 Drude 自由电子模型：$\epsilon(\omega) = 1 - \frac{\omega_p^2}{\omega^2+i\gamma\omega}$。$\omega\ll\gamma$（直流至远红外）: $\epsilon\approx 1+i\omega_p^2/\gamma\omega$（Hagen-Rubens 关系）；$\omega\gg\gamma$（近红外至紫外）: $\epsilon\approx 1-\omega_p^2/\omega^2$。$\omega_p$ 处 $\epsilon'=0$：金属-介质转变。**对 mie-f 重要**: 可见光/近红外区的金属光学常数直接影响 $a_n,b_n$ 中共振的性质
- 9.5 Debye 弛豫模型（极性液体）：$\epsilon(\omega)=\epsilon_\infty+(\epsilon_s-\epsilon_\infty)/(1-i\omega\tau)$
- 9.6 $\epsilon'$ 与 $\epsilon''$ 的一般关系：Kramers-Kronig 关系 $\epsilon'(\omega)=1+\frac{2}{\pi}\mathcal{P}\int_0^\infty\frac{\omega'\epsilon''(\omega')}{\omega'^2-\omega^2}d\omega'$；$\epsilon''(\omega)=-\frac{2\omega}{\pi}\mathcal{P}\int_0^\infty\frac{\epsilon'(\omega')}{\omega'^2-\omega^2}d\omega'$。和和规则 $\int_0^\infty\omega\epsilon''(\omega)d\omega=\frac{\pi}{2}\omega_p^2$

**Chapter 10. Measured Optical Properties (pp. 268–283)**
- 10.1 MgO（绝缘体）的光学常数：透明可见光区到红外 Reststrahlen 带（$\epsilon'<0$），紫外吸收边
- 10.2 Al（金属）的光学常数：Drude 模型拟合，等离子体频率 $\hbar\omega_p\approx 15$ eV，可见光区高反射率，紫外区 $\epsilon'$ 过零
- 10.3 水（液体）的光学常数：**最完整的宽谱覆盖案例**——从微波（Debye 弛豫区）、红外（分子振动吸收带，如 O-H stretch 3μm）、可见光透明窗（最低吸收区）到紫外电子吸收边。Fig. 10.5 给出了贯穿 8 个量级的 $n(\lambda)$ 和 $k(\lambda)$
- 10.4 关于 $k$ 大小的评注：$k$ 可在 0（完全透明）到 >5（强吸收）之间变化，不同波段差异巨大
- 10.5 体光学常数在小粒子计算中的有效性：**关键问题**——体光学常数是否适用于小粒子（经典尺寸效应）。当粒径 $\gg$ 晶格常数且 $\gg$ 电子平均自由程时可近似适用；粒径 <10nm 时需修正电子散射平均自由程（Drude 模型的尺寸修正 $\gamma_{\mathrm{eff}}=\gamma_{\mathrm{bulk}}+v_F/R$）
- 10.6 吸收机制与温度效应：电子跃迁、声子吸收、自由载流子吸收；温度变化影响声子数分布进而改变光学常数

### Part 3 — Optical Properties of Particles (Ch. 11–14, pp. 287–475)

**Chapter 11. Extinction (pp. 287–324)**
- **11.1 基础框架**：$C_{\mathrm{ext}}=C_{\mathrm{abs}}+C_{\mathrm{sca}}$。对小球吸收主导，对中/大球散射主导。消光效率 $Q_{\mathrm{ext}}=C_{\mathrm{ext}}/\pi a^2$
- 11.2 消光概览：实际光学常数（非固定 $m$）计算的 MgO、水、Al 消光曲线对比（Fig. 11.1-11.2）。**核心启示**：用真实光学常数计算的消光与固定 $m$ 的传统方法有显著差异
- 11.3 绝缘球中的消光效应：干涉结构和涟漪结构的详细讨论。$m$ 接近 1 时干涉结构平缓，$m$ 大时共振尖锐。粒径分布对干涉结构的平滑效应——分布式极大减小振荡幅度
- 11.4 Ripple 结构的详细讨论：来源于散射系数分母的复平面零点——即电磁共振（形态共振 morphology-dependent resonances, MDR）。微波波导模拟实验验证了 RIpple 的共振本质。Fig. 11.4: 高分辨测量揭示尖锐共振峰
- 11.5 吸收对消光的影响：吸收使干涉结构和涟漪结构衰减。吸收边附近消光行为剧烈变化。Rayleigh 极限下吸收主导 $Q_{\mathrm{abs}}\propto \lambda^{-1}$
- 11.6 非球粒子的消光计算：椭球体用 Rayleigh 近似（$x\ll1$），无限长圆柱有解析解（Ch.8.4）。消光受形状影响的典型结果——椭球比球的消光峰位偏移
- 11.7 消光测量：聚苯乙烯球（$m\approx1.2$）的测量验证 Mie 理论；不规则石英粒子（$m\approx1.54$）显示非球效应；微波消光作为人造尺度模型
- 11.8 消光总结：$Q_{\mathrm{ext}}$ 的一般行为——$x\to0$ 时 $Q_{\mathrm{abs}}\propto x$、$Q_{\mathrm{sca}}\propto x^4$；中等 $x$ 时干涉+涟漪结构；$x\to\infty$ 时 $Q_{\mathrm{ext}}\to2$

**Chapter 12. Surface Modes in Small Particles (pp. 325–379) [表面模，对 mie-f 共振分析至关重要]**
- **12.1 小球表面模**：
  - **Fröhlich 模条件** (Eq. 12.6)：$\epsilon = -2\epsilon_m$（单谐振子下，$\omega_F^2=\omega_l^2(\epsilon_{0v}+2\epsilon_m)/(\epsilon_{0e}+2\epsilon_m)$）。物理起源：$a_1$ 系数分母为零，即电偶极共振
  - **高阶表面模** (Eq. 12.1-12.2)：$\epsilon/\epsilon_m = -(n+1)/n$，$n=1,2,\dots$。$n=1$ → 电偶极 (Fröhlich)；$n=2$ → 电四极；等等。注意：磁模 $b_n$ 共振条件不同
  - **有限尺寸修正** (Eq. 12.13)：$\epsilon = -(2+\frac{12}{5}x^2)\epsilon_m$。辐射阻尼使共振频率蓝移/红移取决于 $x$ 范围
  - **涂层球表面模** (Eq. 12.14)：$(\epsilon_2+2\epsilon_m)(\epsilon_1+2\epsilon_2)+f(2\epsilon_2-2\epsilon_m)(\epsilon_1-\epsilon_2)=0$，$f=(a/b)^3$
  - **小球吸收效率** (Eq. 12.10)：$Q_{\mathrm{abs}} = 12x\frac{\epsilon_m\epsilon''}{(\epsilon'+2\epsilon_m)^2+\epsilon''^2}$。在 Fröhlich 频率处 ($\epsilon'=-2\epsilon_m$) 出现共振增强；半高宽由 $\epsilon''$ 决定
  - 空腔/气泡：$\epsilon$ 与 $\epsilon_m$ 互换角色
  - $a_n$（电模，电多极）与 $b_n$（磁模，磁多极）在表面模中的角色——电型表面模由 $a_n$ 分母零点定义，磁型表面模由 $b_n$ 分母零点定义。对非磁性材料（$\mu=1$），$b_n$ 的共振退化为几何共振（形态共振, MDR）
- 12.2 非球粒子中的表面模：
  - 椭球体：退极化因子 $L_j$ 决定共振频率 $\epsilon = \epsilon_m(1-1/L_j)$。旋转椭球的极化率张量分量的不同共振峰对应不同轴方向激发
  - 金属椭球：长轴/短轴方向的共振峰分裂——形状效应导致多重表面模
  - 随机取向的盘/针/球的平均消光：Fig. 12.17 对比显示了形状对表面模的显著影响
  - 形状效应总结：即使相同的体材料，不同形状给出完全不同的消光谱
- 12.3 绝缘体中的振动模（Reststrahlen 带）：
  - 非晶 SiO₂（石英玻璃）：约 9 μm 和 21 μm 的表面振动峰（Fig. 12.19），对应 Si-O-Si 伸缩和弯曲振动
  - 晶体 SiO₂（α-石英）：各向异性导致的更多精细共振结构
  - SiC：表面声子极化激元（surface phonon polariton | 在约 12.6 μm 处，$\epsilon'=-2\epsilon_m$, Fig. 12.21）
  - MgO：立方晶体的单 Reststrahlen 带，在约 17 μm 处（Fig. 12.23）
- 12.4 金属中的电子模（表面等离激元 surface plasmon polariton）：
  - Au, Ag, Al 的电子表面模（可见光/近紫外区）
  - Au：~520 nm 表面等离激元共振（尺寸相关，Drude 模型 $\epsilon'=-2\epsilon_m$ 条件）
  - Ag：~360 nm 表面等离激元（更尖锐，因 $\epsilon''$ 更小）
  - Al：~140 nm 紫外表面等离激元
  - Ge 电子-空穴液滴：作为表面模的极端案例

**Chapter 13. Angular Dependence of Scattering (pp. 381–428)**
- 13.1 非偏振/线偏振光散射：微分散射截面 $dC_{\mathrm{sca}}/d\Omega = i_1\sin^2\phi + i_2\cos^2\phi$（对垂直入射）；相位函数 $p(\theta) = (4/x^2Q_{\mathrm{sca}})(i_1+i_2)/2$
- 13.2 测量技术与粒子制备：粒谱选择器、单分散悬浮液制备
- 13.3 单粒子测量：悬浮单粒子（光镊/电悬浮）的角度散射测量
- 13.4 理论与实验结果对比：对聚苯乙烯球、水球等的 Mie 理论验证——$S_1,S_2$ 角度分布的精细振荡结构与实验高度一致
- 13.5 粒子粒度测量：散射图样的角度周期 → 粒径反演
- 13.6 散射矩阵对称性：对球对称粒子的散射矩阵只有 4 个独立元。旋转对称性的约束条件
- 13.7 散射矩阵测量技术：实验测 $S_{ij}$ 的方法学
- 13.8 散射矩阵部分结果：实验测量的 $S_{11},S_{12},S_{33},S_{34}$ 角度分布例证
- 13.9 Mie 理论的适用范围：对非球粒子 Mie 理论仍可近似使用；偏离的程度由形状参数决定

**Chapter 14. Applications (pp. 429–475)**
- 14.1 光学常数的测定问题：从粒子消光/散射数据反演体光学常数的方法学
- 14.2 大气气溶胶：城市大气、尘埃、火山灰的光学特性；消光、能见度
- 14.3 夜光云：高层大气的冰晶散射
- 14.4 雷达降雨测量：微波散射截面与雨滴尺寸分布、Z-R 关系
- 14.5 星际尘埃：消光曲线 (3 个特征：紫外凸起 2175Å、可见光消光斜率、近红外消光)；Draine & Lee 模型；碳质/硅酸盐尘粒
- 14.6 压力依赖的光学光谱（压力光谱）：嵌入基质中的小粒子吸收边随压力的变化
- 14.7 Giaever 免疫学载片：抗原-抗体结合的散射增强检测
- 14.8 微波生物大分子吸收：水合蛋白质的微波介电响应

### Appendixes (pp. 477–497)
- **A. 均匀球计算程序** (pp. 477-482)：完整的 FORTRAN IV 子程序 `BHMIE`，接受参数 $x,m$，返回 $Q_{\mathrm{ext}},Q_{\mathrm{sca}},Q_{\mathrm{abs}},g,Q_{\mathrm{back}},S_1(180^\circ),S_2(180^\circ),\dots$。注释行详细说明使用方法、单位限制和收敛控制。虽语言过时，但算法逻辑仍为当今多数 Mie 代码的起源
- **B. 涂层球计算程序** (pp. 483-490)：类似结构的 FORTRAN 程序 `COATED`，接受核半径、壳半径、核/壳折射率参数
- **C. 正入射无限长圆柱计算程序** (pp. 491-497)：圆柱散射系数计算的 FORTRAN 程序 `CYLNDR`

---

## 2. 关键公式/概念索引

### 2.1 Mie 散射系数

| 名称 | 公式 | 位置 |
|------|------|------|
| 尺寸参数 | $x = ka = 2\pi N a/\lambda$ | (4.52) |
| 相对折射率 | $m = N_1/N$ | (4.52) |
| 电散射系数 $a_n$ | $a_n = \frac{m\psi_n(mx)\psi_n'(x)-\psi_n(x)\psi_n'(mx)}{m\psi_n(mx)\xi_n'(x)-\xi_n(x)\psi_n'(mx)}$ | (4.56) |
| 磁散射系数 $b_n$ | $b_n = \frac{\psi_n(mx)\psi_n'(x)-m\psi_n(x)\psi_n'(mx)}{\psi_n(mx)\xi_n'(x)-m\xi_n(x)\psi_n'(mx)}$ | (4.57) |
| 对数导数形式 $a_n$ | $\frac{[D_n(mx)/m+n/x]\psi_n(x)-\psi_{n-1}(x)}{[D_n(mx)/m+n/x]\xi_n(x)-\xi_{n-1}(x)}$ | (4.88) |
| 对数导数形式 $b_n$ | $\frac{[mD_n(mx)+n/x]\psi_n(x)-\psi_{n-1}(x)}{[mD_n(mx)+n/x]\xi_n(x)-\xi_{n-1}(x)}$ | (4.88) |

式中 Riccati-Bessel 函数：$\psi_n(\rho)=\rho j_n(\rho)$，$\xi_n(\rho)=\rho h_n^{(1)}(\rho)$，$\chi_n(\rho)=-\rho y_n(\rho)$，$\xi_n=\psi_n-i\chi_n$，Wronskian $\chi_n\psi_n'-\psi_n\chi_n'=1$。

### 2.2 截面与效率

| 名称 | 公式 | 位置 |
|------|------|------|
| 散射截面 | $C_{\mathrm{sca}} = \frac{2\pi}{k^2}\sum_{n=1}^\infty (2n+1)(\|a_n\|^2+\|b_n\|^2)$ | (4.61) |
| 消光截面 | $C_{\mathrm{ext}} = \frac{2\pi}{k^2}\sum_{n=1}^\infty (2n+1)\mathrm{Re}\{a_n+b_n\}$ | (4.62) |
| 吸收截面 | $C_{\mathrm{abs}} = C_{\mathrm{ext}} - C_{\mathrm{sca}}$ | (3.20) |
| 光学定理 | $C_{\mathrm{ext}} = \frac{4\pi}{k^2}\mathrm{Re}\{S(0^\circ)\}$ | (3.24) |
| 散射效率 | $Q_{\mathrm{sca}} = C_{\mathrm{sca}}/\pi a^2$ | — |
| 消光效率 | $Q_{\mathrm{ext}} = C_{\mathrm{ext}}/\pi a^2$ | — |
| 衰减系数 | $\alpha_v = 3Q_{\mathrm{ext}}/4a$（单位粒子体积） | — |
| 质量衰减系数 | $\alpha_m = C_{\mathrm{ext}}/M$（单位质量） | — |

### 2.3 散射矩阵与振幅

| 名称 | 公式 | 位置 |
|------|------|------|
| 振幅矩阵对角线元 | $S_1 = \sum_n \frac{2n+1}{n(n+1)}(a_n\pi_n+b_n\tau_n)$ | (4.73) |
| 振幅矩阵对角线元 | $S_2 = \sum_n \frac{2n+1}{n(n+1)}(a_n\tau_n+b_n\pi_n)$ | (4.73) |
| 散射矩阵元 | $S_{11}=\frac12(\|S_2\|^2+\|S_1\|^2)$, $S_{12}=\frac12(\|S_2\|^2-\|S_1\|^2)$ | (4.76) |
| 散射矩阵元 | $S_{33}=\frac12(S_2^*S_1+S_2S_1^*)$, $S_{34}=\frac i2(S_1S_2^*-S_2S_1^*)$ | (4.76) |
| 角度函数 | $\pi_n = P_n^1/\sin\theta$, $\tau_n = dP_n^1/d\theta$ | (4.47) |
| 前向值 | $\pi_n(1)=\tau_n(1)=n(n+1)/2$ | (4.72) |
| 偏振度 | $P = -S_{12}/S_{11} = (i_\perp-i_\parallel)/(i_\perp+i_\parallel)$ | (4.78) |

### 2.4 Rayleigh 散射（$x\ll1$, $\|m\|x\ll1$）

| 名称 | 公式 | 位置 |
|------|------|------|
| $a_1$ 展开 | $a_1 \approx -i\frac{2x^3}{3}\frac{m^2-1}{m^2+2} - i\frac{2x^5}{5}\frac{(m^2-2)(m^2-1)}{(m^2+2)^2} + \frac{4x^6}{9}\left(\frac{m^2-1}{m^2+2}\right)^2$ | (5.4) |
| $b_1$ 展开 | $b_1 \approx -i\frac{x^5}{45}(m^2-1)+O(x^7)$ | (5.4) |
| 散射效率 | $Q_{\mathrm{sca}} = \frac{8}{3}x^4\left\|\frac{m^2-1}{m^2+2}\right\|^2$ | (5.8) |
| 吸收效率 | $Q_{\mathrm{abs}} = 4x\,\mathrm{Im}\left\{\frac{m^2-1}{m^2+2}\right\}$ | (5.11) |
| 散射强度（非偏振入射） | $I_s = \frac{8\pi^4 N a^6}{\lambda^4 r^2}\left\|\frac{m^2-1}{m^2+2}\right\|^2(1+\cos^2\theta)I_i$ | (5.6) |
| 后向散射效率 | $Q_b = 4x^4\left\|\frac{m^2-1}{m^2+2}\right\|^2$ | (5.9) |
| 偏振度 | $P = (1-\cos^2\theta)/(1+\cos^2\theta)$ | (5.12) |

### 2.5 表面模与 Fröhlich 模（第 12 章）

表面模是 $a_n$（电模）或 $b_n$（磁模）**分母为零**的条件在复频率平面的解。对非磁性材料 $(\mu=1)$，电表面模由 $a_n^{-1}=0$ 给出，磁模由 $b_n^{-1}=0$ 给出。物理上，表面模对应电磁能量局域在粒子表面附近的共振态：

| 名称 | 公式 | 物理解释 | 位置 |
|------|------|---------|------|
| Fröhlich 模条件 | $\epsilon = -2\epsilon_m$ | $a_1$ 分母为零，电偶极共振 | (12.6) |
| 高阶表面模 | $\epsilon/\epsilon_m = -(n+1)/n$ | $n=1$ 偶极，$n=2$ 四极，$n=3$ 八极… | (12.1-12.2) |
| 有限尺寸修正 | $\epsilon = -(2+\frac{12}{5}x^2)\epsilon_m$ | Radiative damping 使共振红移 | (12.13) |
| 吸收效率（小球） | $Q_{\mathrm{abs}} = 12x\epsilon_m\epsilon''/[(\epsilon'+2\epsilon_m)^2+\epsilon''^2]$ | Fröhlich 共振处的增强吸收 | (12.10) |
| Fröhlich 频率 | $\omega_F^2 = \omega_l^2(\epsilon_{0v}+2\epsilon_m)/(\epsilon_{0e}+2\epsilon_m)$ | 单谐振子模型中 Fröhlich 模的频率 | (12.20) |
| 涂层球表面模 | $(\epsilon_2+2\epsilon_m)(\epsilon_1+2\epsilon_2)+f(2\epsilon_2-2\epsilon_m)(\epsilon_1-\epsilon_2)=0$ | 壳层介质对共振的调谐，$f=(a/b)^3$ | (12.14) |

详细说明：

- **$n=1$ Fröhlich 模**: $\epsilon=-2\epsilon_m$，为电偶极共振（$a_1$ 分母为零）。$|E|^2$ 沿入射方向极化。这是金属纳米粒子最常见、最强的共振模
- **高阶电表面模** ($n\ge2$): $\epsilon/\epsilon_m=-(n+1)/n$。对应电四极 ($n=2$)、电八极 ($n=3$) 等。随 $n$ 增大，共振频率趋近于 $\epsilon\to -\epsilon_m$（对 Drude 金属 → 趋近于 $\omega_p/\sqrt{1+\epsilon_m}$）
- **有限尺寸修正**: 当 $x$ 不可忽略（$a\gtrsim20$nm）时，$a_1$ 共振红移
- **对 Drude 金属**（$\gamma\ll\omega_p$）: $\epsilon'=\epsilon_\infty-\omega_p^2/(\omega^2+\gamma^2)$, $\epsilon''=\omega_p^2\gamma/(\omega^3+\omega\gamma^2)$。代入 Fröhlich 条件得 $\omega_F=\omega_p/\sqrt{\epsilon_\infty+2\epsilon_m}$
- **磁表面模**: 对 $\mu=1$ 的材料，$b_n$ 分母零点对应形态共振（morphology-dependent resonances）。磁响应在高折射率电介质中实现（如 Si 的 MD 共振）

### 2.6 椭球体静电学近似（第 5.3 节）

| 名称 | 公式 | 位置 |
|------|------|------|
| 椭球极化率（沿主轴 $j$） | $a_j = 3V\frac{\epsilon-\epsilon_m}{3\epsilon_m+3L_j(\epsilon-\epsilon_m)}$ | (5.27) |
| 退极化因子和 | $L_1+L_2+L_3=1$ | (5.29) |
| 球体退极化因子 | $L_1=L_2=L_3=1/3$ | — |
| 长椭球（$a>b=c$） | $L_1 = \frac{1-e^2}{e^2}\left[\frac{1}{2e}\ln\frac{1+e}{1-e}-1\right]$, $e^2=1-b^2/a^2$ | (5.30) |
| 长针极限（$a\gg b$） | $L_1\approx(b/a)^2[\ln(2a/b)-1]$, $L_2=L_3\approx 1/2$ | — |
| 薄盘极限（$a\ll b$） | $L_1\to 1$, $L_2=L_3\to 0$ | — |
| 涂层椭球极化率 | $a_{j,c} = 3V\frac{(\epsilon_2-\epsilon_m)(\epsilon_1+2\epsilon_2)+f(\epsilon_1-\epsilon_2)(\epsilon_m+2\epsilon_2)}{(\epsilon_2+2\epsilon_m)(\epsilon_1+2\epsilon_2)+f(2\epsilon_2-2\epsilon_m)(\epsilon_1-\epsilon_2)}$ | (5.34) |

### 2.7 旋光性粒子（第 8.3 节）

| 名称 | 公式 | 位置 |
|------|------|------|
| 圆二色性消光差 | $\Delta C_{\mathrm{ext}} = C_{\mathrm{ext}}^L - C_{\mathrm{ext}}^R$ | (8.26) |
| 旋光性本构关系 | $\mathbf{D}=\epsilon\mathbf{E}+i\xi'\mathbf{B}$, $\mathbf{B}=\mu\mathbf{H}+i\eta'\mathbf{E}$ | (8.15) |
| 圆偏振散射振幅差 | $\Delta S = S_L - S_R$ | — |

### 2.8 椭球表面模（第 12.2 节）

椭球体在静电近似下的表面模条件（当 $x\ll1$ 时适用）：

| 名称 | 公式 | 位置 |
|------|------|------|
| 椭球表面模共振条件 | $\epsilon = \epsilon_m(1-1/L_j)$ | (12.23) |
| 旋转椭球 $L_1$（长椭球） | $L_1 = \frac{1-e^2}{e^2}\left[\frac{1}{2e}\ln\frac{1+e}{1-e}-1\right]$, $e^2=1-(b/a)^2$ | (5.30) |
| 旋转椭球 $L_1$（扁椭球） | $L_1 = \frac{1+e^2}{e^3}(e-\tan^{-1}e)$, $e^2=(a/b)^2-1$ | (5.31) |
| 吸收截面（椭球，沿主轴 $j$） | $C_{\mathrm{abs}}^{(j)} = kV\,\mathrm{Im}\left\{\frac{\epsilon-\epsilon_m}{\epsilon_m+L_j(\epsilon-\epsilon_m)}\right\}$ | (12.24) |

**关键物理**：椭球的表面模频率由退极化因子 $L_j$ 沿各主轴的值决定。不同轴方向的激发可产生**多个不同的共振峰**——称为 shape-dependent splitting of surface modes。观察要点：
- 长椭球（prolate）: 长轴方向 $L_1$ 小 → 共振在长波长；短轴方向 $L_2=L_3$ 大 → 共振在短波长
- 扁椭球（oblate）: 反之，厚度方向 $L_1\to 1$ 共振蓝移
- 对随机取向的椭球集合，消光谱是三个主轴方向的加权平均
- 针状粒子 ($a\gg b$) 有两个共振峰：长轴峰（近红外/可见红区）和短轴峰（近紫外/可见蓝区）

### 2.9 无限长圆柱散射（第 8.4 节）

| 名称 | 公式 | 位置 |
|------|------|------|
| 柱 Bessel 函数参数 | $x_c = kR\sin\zeta$（$\zeta$ 为入射角），$m_c = \sqrt{m^2-\cos^2\zeta}/\sin\zeta$ | — |
| TM 模散射系数 | $a_{0n} = \frac{J_n'(m_c x_c)J_n(x_c)-m_c J_n(m_c x_c)J_n'(x_c)}{J_n'(m_c x_c)H_n^{(1)}(x_c)-m_c J_n(m_c x_c)H_n^{(1)'}(x_c)}$ | (8.38) |
| TE 模散射系数 | $b_{0n} = \frac{m_c J_n'(m_c x_c)J_n(x_c)-J_n(m_c x_c)J_n'(x_c)}{m_c J_n'(m_c x_c)H_n^{(1)}(x_c)-J_n(m_c x_c)H_n^{(1)'}(x_c)}$ | (8.38) |
| 散射截面/单位长度 | $C_{\mathrm{sca}}' = \frac{4}{k}\sum_{n=-\infty}^\infty(|a_{0n}|^2+|b_{0n}|^2)$ | — |
| 消光截面/单位长度 | $C_{\mathrm{ext}}' = \frac{4}{k}\sum_{n=-\infty}^\infty\mathrm{Re}\{a_{0n}+b_{0n}\}$ | — |
| 正入射散射矩阵 | 对角元 $T_1(\phi),T_2(\phi)$，无交叉偏振($S_3=S_4=0$) | (8.40) |

### 2.10 光学常数模型（第 9 章）

| 名称 | 公式 | 位置 |
|------|------|------|
| Lorentz 谐振子 | $\epsilon(\omega) = 1 + \frac{\omega_p^2}{\omega_0^2-\omega^2-i\gamma\omega}$ | (9.1) |
| 多谐振子 | $\epsilon(\omega) = 1 + \sum_j\frac{f_j\omega_p^2}{\omega_j^2-\omega^2-i\gamma_j\omega}$ | (9.9) |
| Drude 模型（金属） | $\epsilon(\omega) = 1 - \frac{\omega_p^2}{\omega^2+i\gamma\omega}$ | (9.30) |
| 晶格振动（红外） | $\epsilon(\omega) = \epsilon_\infty + \frac{(\epsilon_s-\epsilon_\infty)\omega_{\mathrm{TO}}^2}{\omega_{\mathrm{TO}}^2-\omega^2-i\gamma\omega}$ | — |
| Kramers-Kronig（$\epsilon'$） | $\epsilon'(\omega)-1 = \frac{2}{\pi}\mathcal{P}\int_0^\infty\frac{\omega'\epsilon''(\omega')}{\omega'^2-\omega^2}d\omega'$ | (9.63) |
| Kramers-Kronig（$\epsilon''$） | $\epsilon''(\omega) = -\frac{2\omega}{\pi}\mathcal{P}\int_0^\infty\frac{\epsilon'(\omega')}{\omega'^2-\omega^2}d\omega'$ | (9.64) |
| 和则 | $\int_0^\infty\omega\epsilon''(\omega)d\omega = \frac{\pi}{2}\omega_p^2$ | (9.77) |
| Debye 弛豫 | $\epsilon(\omega) = \epsilon_\infty + \frac{\epsilon_s-\epsilon_\infty}{1-i\omega\tau}$ | (9.50) |

---

## 3. 可供将 mie-f 理论复现参考的内容

Bohren & Huffman (1983) 对 **mie-f 电磁多极展开工作** 有以下直接参考价值：

### 3.1 Mie 系数 $a_n, b_n$ 与电磁多极展开的对应关系

这是最核心的关联。该书明确建立了 TM/E-mode（电型波）与 $a_n$、TE/H-mode（磁型波）与 $b_n$ 的对应关系（第 4.3.2 节，Fig. 4.4，原 Mie 1908 的场模式图）：

| $n$ | $a_n$ (电模) | $b_n$ (磁模) |
|-----|-------------|-------------|
| 1 | 电偶极 (ED) | 磁偶极 (MD) |
| 2 | 电四极 (EQ) | 磁四极 (MQ) |
| $n$ | 电 $2^n$-极 | 磁 $2^n$-极 |

该书散射系数 $a_n$/$b_n$ 定义的 Mie 散射场展开式（Eq. 4.45）直接对应于多极展开的散射场，每个 $a_n$ 和 $b_n$ 唯一对应一种多极模式的权重。具体映射如下：

- **ED（电偶极）**: $a_1$ 项。在 Rayleigh 极限 $(x\ll 1)$ 下，$a_1\approx -i(2x^3/3)(m^2-1)/(m^2+2)$，即静电近似极化率 $\alpha = 4\pi a^3(\epsilon-\epsilon_m)/(\epsilon+2\epsilon_m)$
- **MD（磁偶极）**: $b_1$ 项。$b_1\approx -i(x^5/45)(m^2-1)$，对 $|m|>3$ 的大折射率材料，磁偶极共振会变得显著（如 Si 纳米球的 MD 共振在近红外区）
- **EQ（电四极）**: $a_2$ 项。对较大球（$x$ 增加）四极贡献变得重要；EQ 共振频率高于 ED（4 极表面模 $\epsilon=-3/2\epsilon_m$ vs ED $\epsilon=-2\epsilon_m$）
- **MQ（磁四极）**: $b_2$ 项

**重要**：mie-f 的核心任务之一就是将 BH 的解析 $a_n,b_n$（仅对球形成立）推广到**任意形状**的多极展开。这种推广不是直接重复 BH，而是：
1. 以 BH 的 $a_n,b_n$ 展开作为验证基准——任何多极展开代码对球形粒子必须回归到 BH 的 $C_{\mathrm{sca}}$ 公式
2. 从 BH 的四极/八极项获得对高阶多极物理行为的理解

### 3.2 散射截面与多极贡献的分辨

Eq. (4.61) 中 $C_{\mathrm{sca}} = \frac{2\pi}{k^2}\sum_n(2n+1)(|a_n|^2+|b_n|^2)$ 天然给出了各阶多极对散射截面的独立贡献：
- $n=1$ 项 = 偶极贡献（ED + MD）
- $n=2$ 项 = 四极贡献（EQ + MQ）
- 更高次项 = 更高阶多极

这意味着对于给定的球形粒子，可以**定量分离**每阶多极的散射权重：

| 阶数 | 散射截面贡献 | 物理 |
|------|-------------|------|
| $n=1$ | $C_{\mathrm{sca}}^{(1)} = \frac{6\pi}{k^2}(|a_1|^2+|b_1|^2)$ | ED + MD |
| $n=2$ | $C_{\mathrm{sca}}^{(2)} = \frac{10\pi}{k^2}(|a_2|^2+|b_2|^2)$ | EQ + MQ |
| $n=3$ | $C_{\mathrm{sca}}^{(3)} = \frac{14\pi}{k^2}(|a_3|^2+|b_3|^2)$ | EO + MO |
| $n$ | $C_{\mathrm{sca}}^{(n)} = \frac{2\pi(2n+1)}{k^2}(|a_n|^2+|b_n|^2)$ | $2^n$-pole |

消光截面也有对应的分解：$C_{\mathrm{ext}}^{(n)} = \frac{2\pi(2n+1)}{k^2}\mathrm{Re}\{a_n+b_n\}$。这为 mie-f 分离各多极阶的散射贡献提供了直接的理论公式基础。

**散射矩阵的各阶展开**：Eq. (4.73) 中 $S_1,S_2$ 的求和也是按 $n$ 分阶的。这意味着：
- 若只需偶极近似（Rayleigh 极限），可只取 $n=1$ 项
- mie-f 的多极展开公式应对应到 BH 中直到某 $N$ 的截断求和
- 散射矩阵元 $S_{11},S_{12},S_{33},S_{34}$ 由 $S_1,S_2$ 的模和相位通过 Eq. (4.76) 得到，所有多极信息已在 $S_1,S_2$ 中包含

### 3.3 数值计算参考

第 4.8 节详述了散射系数的稳定数值计算方法：
- 对数导数 $D_n(\rho)=\frac{d}{d\rho}\ln\psi_n(\rho)$ 的向下递推（数值稳定方案，避免 Bessel 函数的指数增长）
- $\psi_n$ 的向上递推（$\psi_{n+1}(\rho)=\frac{2n+1}{\rho}\psi_n(\rho)-\psi_{n-1}(\rho)$）
- $\xi_n=\psi_n-i\chi_n$ 的向上递推（$\chi_n$ 用 $y_n(\rho)$ 定义）
- 收敛条件：$n_c = x + 4x^{1/3} + 2$（Wiscombe 1980），对 $x=10$ 约需 $n_c=20$，对 $x=100$ 约需 $n_c=130$
- Appendix A 提供了完整的 FORTRAN 计算源代码（至今仍被很多实现的起点）

**对 mie-f 的数值参考意义**：
- BH 的对数导数法是目前已知最稳定的 Mie 系数计算方法——mie-f 的球形检验应以此为参考实现
- 递推过程中的数值溢出/下溢处理策略，对 mie-f 广义多极矩的球 Bessel 函数计算同样重要
- Appendix A 的 FORTRAN 代码实现细节（Re_{n}, Im_{n}分离、$n$ 截断控制）可直接作为 mie-f 单元测试的对比

### 3.4 材料光学常数参考

第 9-10 章提供了：
- Lorentz 谐振子模型、Drude 模型的光学常数参数化方法
- SiO₂（非晶/晶体）、MgO、⍺-SiC、Al、Au、Ag、水等的实测光学常数
- **关键**: 第 12 章表面模理论（特别是 Eq. 12.10: $Q_{\mathrm{abs}}=12x\epsilon_m\epsilon''/[(\epsilon'+2\epsilon_m)^2+\epsilon''^2]$）直接可用于分析共振增强的多极响应

### 3.5 涂层球

第 8.1 节（Eq. 8.1）给出了涂层球的 Mie 系数 $a_n, b_n$。这是多层结构多极展开的基础：
- 可用于验证 mie-f 对核-壳结构的多极分解
- 涂层球共振条件 Eq. (12.14) $(\epsilon_2+2\epsilon_m)(\epsilon_1+2\epsilon_2)+f(2\epsilon_2-2\epsilon_m)(\epsilon_1-\epsilon_2)=0$ 展示了介质环境对共振调谐的影响
- 对 mie-f 中涉及多层/渐变折射率粒子的多极展开有重要参考价值

### 3.6 无限长圆柱

第 8.4 节提供了无限长圆柱的散射系数 $a_{0n},b_{0n}$ 的柱 Bessel 函数表达式（Eq. 8.38-8.40）：
- **对 mie-f 的价值**: 圆柱是二维问题，mie-f 的 3D 多极展开在退化为 2D 结构时应与圆柱 Mie 理论一致
- 圆柱散射的对角散射矩阵 $S_3=S_4=0$（远场）与球形 Mie 理论共享 $S_3=S_4=0$ 的性质
- 正入射圆柱的 TM/TE 模是 $a_n/b_n$ 的二维类比

### 3.7 波长相关性与光学常数的物理正确性

第 4.4.2 节（以及全书的核心论点之一）特别强调了 $x$ 和 $m$ 不是独立变量——波长变化时折射率 $m(\lambda)=N_1(\lambda)/N(\lambda)$ 也随之变化。这对 mie-f 有多项意义：
- **对球形检验**: 不能用固定 $m$ 随 $x$ 变化的曲线来验证 mie-f——必须用真实光学常数计算
- **多极共振的色散**: 各阶多极共振出现的波长位置由 $\epsilon(\omega)$ 的频率依赖性决定，不能从固定 $m$ 的 $x$ 扫描简单推断
- **材料数据库**: mie-f 应包含 Johnson & Christy (1972)、Palik (1985) 等光学常数数据库，以确保计算使用正确波长依赖的光学常数
- **对非球形多极展开**: 光学常数的频率色散 $\epsilon(\omega)$ 是 $a_n,b_n$ 中复数的来源之一，在处理非球形粒子的多极矩时必须一致使用

---

## 4. 可信度注意事项

### 4.1 OCR 整体可信度：B 级

基于 `README-OCR.md` 和 `_pdf_review/` 评估：

- **总体评价**：大多数页面可用。多处确定性 OCR 错误已修。
- **已修复问题**：标题层级符号、`1/l` 下标混淆、公式符号错误等
- **建议**：普通阅读/检索可直接用；关键公式使用前应先看原书扫描页
- **与 B 级一致的行为**：文本段落和简单公式的 OCR 质量较高（>95% 可用）；复杂多层公式的保真度参差不齐
- **已知已修正的具体错误**：标题中的"#"层级丢失（已补）、正文和公式中数字"1"与小写"l"的混淆（已全面替换）、部分公式中罗马数字下标被 OCR 识别为阿拉伯数字（如 p212 的 $b_{nI}\to b_{n1}$）
- **页码错位**：源 PDF 的页码与印刷版页码存在偏移（PDF 页面编号 = 印刷页+10，已在各引用中标注为印刷版页号）

### 4.2 UNCERTAIN 页段清单 & 所属章节

以下页段的 OCR 被标记为 UNCERTAIN，关键公式需人工核验原 PDF：

| 页段 | 所属章节 | 主题 | 风险等级 |
|------|---------|------|---------|
| 124–140 | Ch.4 | Mie 理论角散射、Stokes 参数散射矩阵等公式密集区 | **高** |
| 142 | Ch.5.3 | 椭球体静电学近似公式推导 | **高** |
| 144–150 | Ch.5.3–5.4 | 椭球退极化因子、涂层椭球 | **高** |
| 152 | Ch.5.4–5.5 | 涂层椭球延续 + 极化率张量 | **中** |
| 154 | Ch.5.5 | 极化率张量 | **中** |
| 156 | Ch.5.6 | 各向异性球 | **中** |
| 158–160 | Ch.5.7–Ch.6 | Rayleigh 散射矩阵 / Rayleigh-Gans 开端 | **中高** |
| 188 | Ch.7.2 | 虹角推导（棱镜折射公式 OCR 漂移） | **中** |
| 195 | Ch.7.3 | 冰晶晕 | **中** |
| 197–200 | Ch.7.3–Ch.8.1 | 冰晶晕 / 涂层球推导 | **中高** |
| 202–203 | Ch.8.3–8.3.1 | 旋光性粒子 / 矩阵元与截面 | **高** |
| 208 | Ch.8.3.1–8.3.2 | 矩阵元与截面 / 圆二色性与旋光 | **中高** |
| 210 | Ch.8.4 | 无限长圆柱散射 | **中** |
| 212–215 | Ch.8.4.3–8.4.4 | 圆柱截面推导、正入射光（已由 continued 报告重新确认为 PASS） | **已解决** |

### 4.3 具体风险举例

1. **第 124–140 页**: 包含 Ch.4 散射矩阵公式（Eq. 4.73–4.78）、不对称参数（4.80）、雷达后向散射截面（4.82–4.83）、热发射（4.85–4.87）、散射系数计算（4.88–4.89）—— 全是 mie-f 引用时的关键公式。**使用前必须核验原书**。具体地：
   - Eq. 4.73-4.75: $S_1,S_2$ 的角度函数求和
   - Eq. 4.76: $S_{11},S_{12},S_{33},S_{34}$ 与 $S_1,S_2$ 的关系
   - Eq. 4.80: 不对称参数 $g$ 与 $a_n,b_n$ 的求和公式
   - Eq. 4.85-4.87: 发射率与吸收率的关系（基尔霍夫定律）
   - Eq. 4.88-4.89: 对数导数形式的 $a_n,b_n$ 表达式

2. **第 142–150 页**: Ch.5.3 椭球体退极化因子和涂层椭球的公式推导——mie-f 涉及非球粒子时直接依赖。含长椭球/扁椭球退极化因子 $L_j$ 的解析表达式

3. **第 158–160 页**: Rayleigh 散射矩阵与 Rayleigh-Gans 过渡段，含 $S_1,S_2$ 的小球极限形式。对理解 Rayleigh 近似的适用范围（$|m-1|\ll 1$ 且 $2x|m-1|\ll 1$）非常重要

4. **第 188–200 页**: 几何光学（虹角、冰晶晕）以及涂层球 Mie 系数推导的起始。涂层球 Aden-Kerker 公式（Eq. 8.1）的推导过程在此区间

5. **第 202–208 页**: 旋光性粒子（optically active particles）的本构关系 $\mathbf{D}=\epsilon\mathbf{E}+i\xi'\mathbf{B}$, $\mathbf{B}=\mu\mathbf{H}+i\eta'\mathbf{E}$ 以及圆二色性 $\Delta C_{\mathrm{ext}}$ 公式

6. **第 14 页手写边注**：已明确标记不纳入自动基线

### 4.4 使用建议与可靠度分档

以下是针对不同的 mie-f 使用场景的具体建议：

| 使用场景 | 可直接使用的章节 | 需谨慎的章节 | 强烈建议核验原书的页面 |
|---------|----------------|-------------|---------------------|
| 理解 Mie 理论框架 | Ch.1-3 全文、Ch.4 叙述性文字 | Ch.4 公式正文 | 124-140 |
| $a_n,b_n$ 系数实现 | Ch.4.3.3 公式、Ch.4.8 算法 | Eq. 4.53, 4.56-4.57 的精确形式 | 106-110 (第 4 章) |
| 截面公式引用 | Ch.4.4.1 | — | — |
| 散射矩阵计算 | Ch.4.4.4 叙述 | Eq. 4.73-4.78 | 124-128 |
| Rayleigh 极限 | Ch.5.1-5.2 | Ch.5.3-5.7 | 142-160 |
| 表面模 / Fröhlich 模 | Ch.12.1 理论 | Eq. 12.6-12.14 | 124-140, 326-340 |
| 光学常数参数化 | Ch.9 | 数值表格/谱线数据 | 228-280 |
| 涂层球公式 | Ch.8.1 叙述性 | Eq. 8.1 Aden-Kerker 系数 | 197-200 |
| 无限长圆柱 | Ch.8.4.1-8.4.2 | Eq. 8.38-8.40 截面公式 | 210-215 |
| 消光数据分析 | Ch.11 | 消光曲线数值 | — |

```
对于 mie-f 工作：
  1. Ch.4 公式（a_n, b_n, 截面, S矩阵）：从本书 OCR 阅读框架和理解，
     具体公式使用时对照原书扫描页或权威来源（van de Hulst/Kerker）交叉验证。
  2. Ch.12 表面模公式：124-140 页风险集中，特别注意 Eq.12.6/12.10/12.13。
  3. Ch.9-10 光学常数：文本部分可用，数值表格需核验。
  4. 弹性模/表面模条件的推导可放心引用的部分（因为不在106/124-140等密集公式页）：
     - Ch.9 经典模型公式
     - 简单展开式如 $Q_{\mathrm{abs}} = 4x\Im\{(m^2-1)/(m^2+2)\}$
  5. Appendix A 的 FORTRAN 代码：这是最可靠的部分——印刷版代码可直接用（代码文本 OCR 对比数学公式更可靠）
```

---

## 5. 与核心论文的关联

### 5.1 与 Grahn 2012 的关系

Grahn (2012) "Electromagnetic Multipole Theory for Optical Nanomaterials" 直接引用并扩展了 Bohren & Huffman (1983)：

- **引用方式**：Grahn 2012 参考文献表中包含 Kerker (1969) 和 Bohren & Huffman (1983)。该书为 Grahn 提供了 Mie 散射系数的标准公式和基本电磁理论框架。
- **衔接点**：
  - Grahn 将 Bohren & Huffman 的 Mie 系数 $a_n,b_n$ 从单个球推广到 **任意形状纳米结构** 的电磁多极理论
  - Grahn 的散射截面公式 $(C_{\mathrm{sca}} = \frac{1}{2\eta_0|E_0|^2}\sum_l{|p_l|^2+|m_l|^2+\dots})$ 与 BH 的 Eq. (4.61) 一致，但以多极矩形式重新表达
  - Grahn 的散射矩阵公式 $(S_1,S_2)$ 的多极展开同样继承自 BH Ch.4.4.4 的框架
  - Grahn 讨论的散射矩阵特性源自 BH Ch.3 的一般处理
- **关键差异**：
  - Grahn 的完整多极理论（含电/磁偶极、电/磁四极、电/磁八极及 toroidal 偶极）超出了 BH 仅对球形成立的范围
  - Grahn 引入了 Cartesian 多极矩 $p_\alpha, m_\alpha, Q_{\alpha\beta}^{(e)}, Q_{\alpha\beta}^{(m)}, O_{\alpha\beta\gamma}^{(e)},\dots$，BH 只用球谐函数展开
  - Grahn 的公式中包含了 toroidal 偶极项，BH 中没有显式处理（虽然 toroidal 响应可通过 BH 的 $a_1,b_1$ 的辐射修正隐式包含）
- **对应表：Grahn 多极矩 vs BH Mie 系数**
  | Grahn (2012) 符号 | BH (1983) 对应 | 适用结构 |
  |---|---|---|
  | 电偶极 $p_\alpha$ | $a_1$ 的 Rayleigh 极限：$p = \frac{4\pi\epsilon_0\epsilon_m}{-2i k^3}a_1$ | 任意 (球形闭合解) |
  | 磁偶极 $m_\alpha$ | $b_1$ 的 Rayleigh 极限：$m = \frac{4\pi}{-2i\mu_0 k^3}b_1$ | 任意 (球形闭合解) |
  | 电四极 $Q_{\alpha\beta}^{(e)}$ | $a_2$ | 任意 |
  | 磁四极 $Q_{\alpha\beta}^{(m)}$ | $b_2$ | 任意 |
  | 散射截面 | $\frac{2\pi}{k^2}\sum_n(2n+1)(\|a_n\|^2+\|b_n\|^2)$ | $\frac{k^4}{12\pi\epsilon_0^2|E_0|^2}(\|p\|^2+\cdots)$ |

**对 mie-f 的意义**：先读 BH Ch.4 建立 Mie 系数框架，再读 Grahn 2012 理解如何从 $a_n,b_n$ 映射到多极矩的现代表述。BH 提供了**验证基准**（球形封闭解），Grahn 提供了**扩展框架**（任意形状的多极展开）。

### 5.2 与 Alaee 2018 的关系

Alaee (2018) "An Electromagnetic Multipole Expansion Beyond the Long-Wavelength Approximation" 对 Bohren & Huffman 的关系：

- **直接引用**：Alaee 引用该书为标准教科书 Mie 理论参考（[25]）。Eq. (7.20) 在 BH 中给出多极矩的精确表达式。
- **核心衔接**：
  - Alaee 的新多极矩公式（在电流密度积分中引入球 Bessel 函数核）通过 Mie 理论验证其正确性——对球形粒子，Alaee 的精确公式与 Mie 理论（即 BH Ch.4）的结果**完全一致**
  - BH 的 Eq. (4.61) $C_{\mathrm{sca}} = \frac{2\pi}{k^2}\sum_n(2n+1)(\|a_n\|^2+\|b_n\|^2)$ 是 Alaee 验证工作的**金标准**
  - Alaee 的 Eq. (1): $P = \frac{Z_0k^4}{12\pi}\left(\sum_\alpha\|p_\alpha\|^2+\frac{1}{c^2}\sum_\alpha\|m_\alpha\|^2+\frac{k^2}{20}\sum_{\alpha\beta}\|Q_{\alpha\beta}^{(e)}\|^2+\cdots\right)$
  - Alaee Table 1（长波近似公式）对应 BH Ch.5 Rayleigh 近似：$p_\alpha^{(LW)}=\int r_\alpha\rho(r)d^3r$（仅电荷密度，无 Bessel 修正）
  - Alaee Table 2（精确公式）对应 BH Ch.4 Mie 理论，区别是 Alaee 以电流密度积分形式表达而非 Bessel 函数封闭形式：$p_\alpha^{(exact)}=-\frac{1}{i\omega}\int J_0(kr) r_\alpha\nabla\cdot\mathbf{J}d^3r+\frac{1}{i\omega k^2}\int J_2(kr)\nabla\cdot\{r_\alpha\nabla\cdot\mathbf{J}+\cdots\}d^3r$
  - 对金属纳米粒子 $(x\ll1)$，Alaee 精确多极矩与长波近似的差异可忽略；对介质纳米粒子 $(x\sim1)$，差异显著——必须用 Alaee 精确公式
- **关键差异**：
  - BH 给出的是球形的**封闭形式解析解**（Bessel 函数比的形式）；Alaee 给出的是**任意形状粒子**的通用多极矩积分表达式（需数值计算电流密度分布）
  - Alaee 的精确表达式涉及球 Bessel 函数 $j_0(kr),j_2(kr),j_4(kr)$ 的核，而非 BH 的 Riccati-Bessel 函数 $\psi_n,\xi_n$
  - Alaee 统一了多极矩的**积分数值法**与 BH 的**解析法**——两者对球形应完全一致

**对 mie-f 的意义**：
- BH Ch.4 = Mie 理论封闭解，可作为 mie-f 多极展开的验证基准
- Alaee 2018 = 从电流密度积分计算多极矩的通用公式，与 BH 互补
- 结合两者：用 BH 球形解验证 mie-f 实现，用 Alaee 精确公式扩展到非球结构
- 验证工作流：mie-f 对球形输出的 $C_{\mathrm{sca}}, C_{\mathrm{ext}}, S_1,S_2$ → 与 BH Mie 理论的对应值对比 → 若一致则证明多极展开实现正确
- 对高折射率介质粒子（Si, TiO₂）：由于 $|m|$ 大且 $x$ 不可忽略（$x\sim1$），必须使用 BH 精确级数（Ch.4.8）而非 Rayleigh 近似（Ch.5）作为验证基准

### 5.3 总结：三者在 mie-f 中的定位

```
Bohren & Huffman 1983 (本书)
  ├─ 基础：Mie 系数 a_n,b_n；截面公式 S 矩阵；光学常数
  │
  ├─ Grahn 2012：将 a_n,b_n 映射到多极矩理论；
  │   从球形推广到任意形状的电磁多极框架
  │
  └─ Alaee 2018：提供精确多极矩积分数值公式；
     以 BH 的 Mie 理论为验证标准
```

**对 mie-f 复现工作的直接指导**：
1. BH Eq. (4.53)/(4.56-4.57) 的 $a_n,b_n$ → 球形粒子多极展开系数的解析表达式
2. BH Eq. (4.61)-(4.62) 的 $C_{\mathrm{sca}}, C_{\mathrm{ext}}$ → 各阶多极对散射/消光的分离贡献
3. BH Eq. (4.45) 的 $\mathbf{E}_s$ 展开 → 多极散射场的完备基（矢量球谐函数）
4. BH Ch.9 的 Lorentz/Drude 模型 → 材料光学常数的参数化
5. BH Ch.12 的表面模 → 共振多极增强的物理机制

### 5.4 数值算例参考对照

以下给出几个关键算例的页码和参数，便于在 mie-f 中复现比较：

| 算例 | 参数 | 输出 | 页码 |
|------|------|------|------|
| 水微粒消光（Fig. 4.6） | $a=0.05,0.2,1.0\mu$m，真实 $n(\lambda),k(\lambda)$ | $Q_{\mathrm{ext}}$ vs $1/\lambda$ | p106-107 |
| 偏振幅值 $S_1,S_2$（Fig. 4.10-4.11） | $x=5$, $m=1.33$, $m=1.5$ | 角散射图（对数尺度） | p115-116 |
| Rayleigh 小球散射（Fig. 5.1-5.2） | $x\ll1$, $m$ 变化 | $Q_{\mathrm{sca}},Q_{\mathrm{abs}}/x$ | p131-133 |
| 椭球随机取向消光（Fig. 12.17） | $\epsilon=-4.6+1.8i$（SiC 12μm） | $Q_{\mathrm{abs}}$ vs 形状比 | p352 |
| 表面模 $a$ 系数的分母（Fig. 12.1） | Drude $\omega_p/\gamma=100$ | $\mathrm{Im}\{a_1\}$ vs $\omega/\omega_p$ | p327 |
| 涂层 $a_n$ 共振（Fig. 12.4） | 各种核壳比 | 模条件位移 | p332 |
| Al 球消光（Fig. 12.24） | 半径 10-100nm | $Q_{\mathrm{ext}}$ vs $\lambda$ | p368 |
| 圆柱散射强度（Fig. 8.7-8.10） | $x=2\pi a/\lambda$, $m$ | 角散射图 | p199-206 |

这些算例都可直接作为 mie-f 输出的验证基准——任一算例在球形极限下的 mie-f 结果应与 BH 计算结果定量一致。

### 5.5 推荐阅读顺序

对 mie-f 相关工作，建议的研读顺序：

```
Step 1: BH Ch.4 (Mie 理论) → 掌握 a_n,b_n, 截面, S 矩阵
    ↓
Step 2: BH Ch.9-10 (光学常数) → 明白材料色散的影响
    ↓
Step 3: BH Ch.5 (Rayleigh/静电学) + Ch.12 (表面模) → 小粒子/共振行为
    ↓
Step 4: Alaee 2018 → 通用多极矩积分公式（对比 BH 验证）
    ↓
Step 5: Grahn 2012 → 电磁多极理论的形式化扩展
    ↓
Step 6: BH Ch.8 (涂层球, 圆柱) → 非球验证案例
```

---

*总结生成日期: 2026-07-26 | 基于 OCR 文本 `Bohren_Huffman_1983.md` (11146 行) 及 `_pdf_review/` 报告*
