# B2：独立光学定理 $S(0)$ 实现

## 结论

`code/optical_theorem.py` 增加了两条不共享前向收缩的路径：

1. `s0_series`：显式 Mie 前向式得到 $S(0)$；
2. `s0_from_angular_quadrature`：先构造角分辨远场 $S_1(\theta),S_2(\theta)$，再用 Legendre 重构核对角度积分并取 $\mu=\cos\theta=1$。

两条路径均使用已验证的 `baseline_mie.mie_coefficients` 作为散射系数输入，但路径 2 不调用路径 1，也不执行 $\sum_n(2n+1)\operatorname{Re}(a_n+b_n)$ 的消光收缩。

## 约定与推导

对 $e^{-i\omega t}$、外辐射 $e^{ikr}$，先定义无量纲 Mie 角振幅

$$
S_1^{(d)}(\theta)=\sum_{n=1}^{N}\frac{2n+1}{n(n+1)}\left[a_n\pi_n(\mu)+b_n\tau_n(\mu)\right],
$$

$$
S_2^{(d)}(\theta)=\sum_{n=1}^{N}\frac{2n+1}{n(n+1)}\left[a_n\tau_n(\mu)+b_n\pi_n(\mu)\right],\qquad \mu=\cos\theta.
$$

角函数按 Bohren--Huffman 递推计算：$\pi_1=1$，
$\pi_n=((2n-1)\mu\pi_{n-1}-n\pi_{n-2})/(n-1)$，
$\tau_n=n\mu\pi_n-(n+1)\pi_{n-1}$。在前向方向
$\pi_n(1)=\tau_n(1)=n(n+1)/2$，所以独立的闭式路径为

$$
S_\mathrm{fwd}^{(d)}=S_1^{(d)}(0)=S_2^{(d)}(0)
 =\frac12\sum_{n=1}^{N}(2n+1)(a_n+b_n).
$$

为严格匹配 formalization 中的 $C_\mathrm{ext}=(4\pi/k)\operatorname{Im}S(0)$，模块将物理振幅定义为

$$
S(\theta)=\frac{i}{k}S^{(d)}(\theta).
$$

于是

$$
C_\mathrm{ext}^{\rm phys}=\frac{4\pi}{k}\operatorname{Im}S(0)
 =\frac{4\pi}{k^2}\operatorname{Re}S_\mathrm{fwd}^{(d)}.
$$

仓库基线去掉公共面积因子 $2\pi/k^2$，记为 $C'_\mathrm{ext}$。因此测试比较的是

$$
C'_\mathrm{ext}=\frac{k^2}{2\pi}C_\mathrm{ext}^{\rm phys}
 =2\operatorname{Re}S_\mathrm{fwd}^{(d)}.
$$

`c_ext_from_s0` 返回物理截面，`c_ext_dimless_from_s0` 返回与
`baseline_mie.cross_sections` 同一的 $C'_\mathrm{ext}$。

## 路径 2：角分辨数值投影

角路径在 $N_\mu$ 个 Gauss--Legendre 节点 $\mu_j$ 上计算复数
$S_1(\mu_j),S_2(\mu_j)$，并对两种偏振、$N_\phi$ 个均匀方位角作平均。对最高阶为 $N$ 的有限球谐展开，角振幅是 $\mu$ 的至多 $N$ 次多项式。使用

$$
p(1)=\int_{-1}^{1}p(\mu)K_N(\mu)\,d\mu,\qquad
K_N(\mu)=\frac12\sum_{\ell=0}^{N}(2\ell+1)P_\ell(\mu),
$$

并以 $N_\mu\ge N+1$ 点 Gauss--Legendre 求积，数值积分在理论上对该有限展开精确，实际误差由浮点舍入决定。实现默认 $N_\mu=N+4$、$N_\phi=8$（测试用 12）。这条路径只消费角分辨振幅，不从前向级数直接读出 $C_\mathrm{ext}$。

## 数值交叉验证

下表的 `route_rel` 是两条 $S(0)$ 路径的对称相对差，`series_rel` / `angular_rel` 是各自转换到 $C'_\mathrm{ext}$ 后与现有 `cross_sections` 的相对差。$S(0)$ 为物理振幅（测试中 $k=1$）。

### 介电球 $m=2.5$

| $x=ka$ | $N$ | $S_\mathrm{series}(0)$ | $S_\mathrm{angular}(0)$ | $C'_\mathrm{ext}$ 基线 | route_rel | series_rel | angular_rel |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 5 | 0.0103652301452+0.00006849872249i | 0.0103652301452+0.00006849872249i | 1.3699744497e-4 | 4.18e-15 | 0 | 4.15e-15 |
| 0.50 | 6 | 0.0933171273181+0.00490166295580i | 0.0933171273181+0.00490166295580i | 9.8033259116e-3 | 1.78e-15 | 1.77e-16 | 1.95e-15 |
| 1.00 | 7 | 1.09628685755+0.463686031364i | 1.09628685755+0.463686031364i | 0.927372062728 | 6.10e-15 | 0 | 6.23e-15 |
| 1.75 | 9 | −1.37376901897+4.04191320213i | −1.37376901897+4.04191320213i | 8.08382640426 | 1.14e-14 | 2.20e-16 | 1.14e-14 |
| 2.50 | 10 | 1.32254622769+3.46980414835i | 1.32254622769+3.46980414835i | 6.93960829670 | 1.58e-15 | 1.28e-16 | 1.66e-15 |

### 金球（Olmon-EV 复折射率，$\operatorname{Im}m>0$）

| $\lambda$ (nm) | $x=\pi(500/\lambda)$ | $m$ | $N$ | $C'_\mathrm{ext}$ 基线 | route_rel | series_rel | angular_rel | $C'_\mathrm{abs}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 550 | 2.85599332145 | 0.3256+2.507i | 11 | 15.1755123119 | 6.21e-15 | 1.17e-16 | 6.20e-15 | 2.13814454907 |
| 1000 | 1.57079632679 | 0.1559+6.613i | 9 | 3.20221271775 | 1.20e-14 | 1.39e-16 | 1.23e-14 | 0.04039892278 |
| 1700 | 0.923997839291 | 0.377+11.64i | 7 | 0.940760948551 | 6.19e-15 | 1.18e-16 | 6.49e-15 | 0.01283434125 |

Across the eight cases, the largest complex route discrepancy is $1.20\times10^{-14}$; the largest angular-path discrepancy against the existing $C'_\mathrm{ext}$ is $1.23\times10^{-14}$, well below the required $10^{-6}$ and $10^{-8}$ gates. The explicit $\phi$ audit has maximum absolute difference $0$ for the sampled sphere amplitudes.

## Formalization alignment and status

- `formalization/alaee2018-fig1.yaml:142-145`：新增实现满足 Layer1 optical-theorem 条款要求的“从角分辨散射振幅独立算 $S(0)$”；未修改 YAML。
- `formalization/alaee2018-fig2.yaml:204-210`：同一接口覆盖复介电率金球，并保留 $C_\mathrm{abs}>0$ 检查；未修改 YAML。
- 旧 `tests/test_mie.py:102-117` 的无损等价式仍保留为历史回归；B2 独立测试位于 `tests/test_optical_theorem.py`。

`result_class: PASS_WITH_NOTES`：B2 实现、数值门槛和项目测试集均通过；`pytest -q tests` 为 **123 passed, 1 skipped**。工作区根目录裸跑 `pytest -q` 会额外收集旧审计产物 `codex-prompts/out/A3-file-secret-hardening/tests/`，因其内部相对导入缺失而在收集阶段失败；该目录不属于项目 `tests/` 回归，也未在本任务范围内修改。
