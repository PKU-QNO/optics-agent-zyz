# Fig.3 Mie surrogate verification

本文件记录 B7 的解析代理路径和可审计数值回执。它不是 COMSOL/FEM 双纳米盘的独立真值。

## 物理范围

论文 Fig.3 caption 与正文将对象定义为两个耦合金纳米盘（$a=250\,\mathrm{nm}$、$t=80\,\mathrm{nm}$、$g=120\,\mathrm{nm}$），比较 Table 1 长波近似与 Table 2 精确多极矩对 $C_{\mathrm{sca}}$ 的 ED、MD、EQ、MQ 分通道贡献，并画相对误差。论文没有给出 Fano $q$、共振中心、线宽、观测方向或复远场；Fano 只在引言中作为多极干涉应用被提及。因此，本轮的 `result_class` 是 `surrogate_fallback`。

全角、均匀无界背景下的四个正交 VSH 通道使用 $(2l+1)|a_l|^2$ 或 $(2l+1)|b_l|^2$ 的正项；方向和偏振固定时，模块保存复振幅 $S_1,S_2$，并显式输出

$$
I_{\mathrm{cross}}=|S_1|^2+|S_2|^2-\sum_l\left(|S_{1,l}|^2+|S_{2,l}|^2\right).
$$

这一区分避免把 Fig.3 的角积分通道功率误称为 Fano 干涉。

## 实现

- `code/fig3_mie_fano.py` 复用已验证的 `baseline_mie.mie_coefficients` 与 Wiscombe 截断。
- 每个等效单盘取 JC 复折射率 $m=n+i\kappa$，并计算 $a_1,b_1,a_2,b_2$；两盘代理使用中心距 $t+g=200\,\mathrm{nm}$ 的对称 retarded pair factor 和有界弱耦合分母。
- “exact”保留完整 Mie 系数；“approx”由相同材料在 $x_{\mathrm{ref}}=10^{-4}$ 的 Rayleigh 系数按 $x^3,x^5,x^5,x^7$ 延拓，作为 Table 1-like 诊断，不冒充论文 Table 1 的非球形电流积分。
- `jc_refractive_index` 对 `data/gold_epsilon.csv` 的 JC 有限域（400–1935 nm）做线性插值，严禁外推；请求 $x=0.25$ 对应 $\lambda=2000\,\mathrm{nm}$ 的 4 个点标为缺失。
- `code/generate_fig3_outputs.py` 生成 CSV、PNG 和 JSON 回执。

## Layer1/Layer2/诊断回执

| 检查 | 数值 | 判定 |
|---|---:|---|
| 光学定理残差 $C_{\rm ext}-C_{\rm sca}-C_{\rm abs}$（$x=0.7,m=1.5$） | $0.0$（双精度） | PASS |
| Rayleigh exact-vs-leading amplitude（$x=0.02,m=1.5$）最大相对误差 | $0.003809\%$（EQ 最大） | PASS |
| $n_{\max}$ 收敛（$x_{\rm Mie}=1.9635$, $m=0.15+4.9i$） | $n_{\max}=2,4,6,8$：5.7784403, 5.8386380, 5.8386383, 5.8386383；末两者相对差 $0$ | PASS |
| 方向交叉项（$\lambda=800\,$nm，$\theta=\pi/2$） | 最小/最大（全 JC 域扫描）$-24.9256 / +4.48683$ | PASS：相长/相消均出现 |
| 错误注入（角度由 $\pi/2$ 改为 $0.7$，相位路径） | 交叉项 $-6.03348\rightarrow18.6002$ | PASS：触发 `INTERFERENCE_PHASE_FAIL` 预期信号 |

## Fano / 文献对标

Tribelsky 2016 的 strict-feature comparator 用标准 $F(\epsilon)=(\epsilon+q)^2/(1+\epsilon^2)$，取 $q=-1$、$x_0=1.34$、$\Gamma=0.04$，得到网格峰 $x=1.32002$、谷 $x=1.35998$；相对文献 $1.32/1.36$ 的误差均为 $2\times10^{-5}$，远小于 A6 建议的 0.01 容差。这是独立公式回归，不是 Alaee 双盘拟合。

Fu 2013 仅作 `sanity_only`：$r=75\,$nm、固定实部 $n=3.5$ 的 Mie 球在 660 nm 得 $F/B=11.0443$，相对文献约 $8$ 偏差 $+38.05\%$。该结构、材料和 observable 均不同，故不作 Fig.3 gate。

## 运行与产物

在仓库根运行 `python code/generate_fig3_outputs.py`；当前回执为 `data/fig3_mie_surrogate_summary.json`。全量回归命令 `python -m pytest tests -q`：`124 passed, 1 skipped`（99.20 s）。

