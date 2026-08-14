# A2 W3 Grahn 核心实现对抗性审计

- `role`: W-sub，只读核心实现审计员
- `verdict`: `BLOCKED`
- `result_class`: `method_consistency`
- `scope`: 仅审核 `grahn.yaml` v4 的解析基准、kernel paths、依赖图、验收合同及其在 `scattering.py`、`test_grahn.py`、runner、现有报告中的消费；未修改实现。
- `artifact`: `papers/mie-f/reproduction/sub-report/a2-w3-core-audit.md`

## 结论

当前核心实现不能据 v4 spec 判为通过。存在三个可证伪的实现/覆盖缺陷和一个报告诚实性缺陷：$l=2$ 的小宗量 $j_2''$ 分支写成了 $j_2'$ 的级数；结构化 spec 列出的 `double_blob` 没有实现、闭式量、积分、测试或 runner 消费；Eq.(13)/(14) 与 Eq.(15)/(16) 的比较只覆盖唯一非零的 $a_E(1,0)$；runner 随后把这两个不完整集合硬编码成 `PASS`/`PASS_WITH_NOTES`。这些问题均属于 W3 核心解析基准，不依赖 W4--W6 的正式重跑。

## 缺陷 D1：$l=2$ 小宗量二阶导数级数错误

- `file:line`: `code/scattering.py:124-151`，具体错误在 `code/scattering.py:144-145`；漏检测试在 `tests/test_grahn.py:119-128`，弱错误注入在 `tests/test_grahn.py:215-217`。
- `spec`: `formalization/grahn.yaml:159-162` 要求 $j_l''$ 用递推或零点级数，并由 $\Psi_l''=2j_l'+\rho j_l''$ 构造。

解析展开为

$$
j_2(\rho)=\frac{\rho^2}{15}-\frac{\rho^4}{210}+\frac{\rho^6}{7560}+O(\rho^8),
$$

$$
j_2'(\rho)=\frac{2\rho}{15}-\frac{2\rho^3}{105}+\frac{\rho^5}{1260}+O(\rho^7),
$$

$$
j_2''(\rho)=\frac{2}{15}-\frac{2\rho^2}{35}+\frac{\rho^4}{252}+O(\rho^6).
$$

因此

$$
\Psi_2''(\rho)=\frac{2\rho}{5}-\frac{2\rho^3}{21}+\frac{\rho^5}{180}+O(\rho^7).
$$

当前 `l == 2` 分支却赋值 `2*rho/15 - 2*rho**3/105`，即把 $j_2'$ 的前两项放进变量 `jpp`。代回后错误结果的首项为 $4\rho/15$，正确首项为 $2\rho/5$，故 $\rho\to0^+$ 时相对误差趋于 $1/3$；而且在阈值 $10^{-7}$ 两侧产生人为不连续。

只读 80 位 `mpmath` oracle 反例：

| $\rho$ | 当前 `psipp` | 高精度 $\Psi_2''$ | 绝对误差 |
|---:|---:|---:|---:|
| $10^{-10}$ | $2.6666666667999612\times10^{-11}$ | $3.99999999999999999999\times10^{-11}$ | $1.3333333332000388\times10^{-11}$ |
| $10^{-8}$ | $2.6666666800000033\times10^{-9}$ | $3.9999999999999999\times10^{-9}$ | $1.3333333199999966\times10^{-9}$ |
| $9\times10^{-8}$ | $2.4000001080000181\times10^{-8}$ | $3.5999999999999931\times10^{-8}$ | $1.1999998919999750\times10^{-8}$ |
| $10^{-6}$（递推分支） | $3.9999999999990533\times10^{-7}$ | $3.9999999999990476\times10^{-7}$ | $5.64\times10^{-22}$ |

现有定向测试仍显示 `1 passed`，原因是 `tests/test_grahn.py:121` 虽放入 $10^{-10}$，但 `:128` 仅断言有限；真正的二阶差分 oracle 只检查索引 1，即 $\rho=0.2$，走正确的递推分支。`tests/test_grahn.py:215-217` 又只检查 $l=1,\rho=0.4$ 下 `psip != psipp`，不是 $l=2$ 小宗量 oracle。

- `影响`: 任意直接调用或未来含原点节点/极小 $kR$ 的积分会污染 Eq.(15) 电通道；当前生产 Gauss 内点可能恰未落入该分支，但这不能使错误实现满足 spec。
- `最小修复`: 把 `l == 2` 的 `jpp` 级数改为上式，至少保留到 $O(\rho^4)$；用统一级数同时构造 $j,j',j''$，避免同一分支混用 SciPy 与手写阶次。

## 缺陷 D2：`double_blob` 在实现链中完全缺失，且默认距离违约

- `file:line`: `formalization/grahn.yaml:231-239`；`code/scattering.py:411-426`、`code/scattering.py:429-462`；`tests/test_grahn.py:131-143`；`code/run_grahn_verification.py:105-121`；`sub-report/verify-grahn.md:17,24`。
- `spec`: `cases` 序列实际有六项：`bump_polarized_sphere`、`double_blob`、`circulating_current`、`MQ_m0`、`MQ_m2`、`MQ_m1`。其中 `double_blob` 要求 $d=2.5R$、两半径 $R$ 的 support 不重叠、积分包围盒半宽 $d/2+R=2.25R$，并验证

$$
p=0,\qquad M2_{zz}=\frac{iJ_0d}{\omega}I_0.
$$

结构化 `cases` 明确列出六项，但 `case_count_note` 文本误写“5 个案例”；实现不应据错误计数文字静默丢掉序列中的实体。

可证伪事实：

1. `analytic_bump_current` 的默认 `d=0.5`，违反 $d=2.5R$，且函数没有 `double_blob` 分支，调用会落到 `ValueError("unknown analytic benchmark: double_blob")`。
2. `analytic_bump_closed_forms` 没有 `M2_zz` 或 $d$；`integrate_analytic_current` 只在原点球 $r\le R$ 上积分，也没有 `d`/`omega` 参数，无法覆盖两个移位 support。
3. runner 明列五个名字并遗漏 `double_blob`；测试只检查 `bump_polarized_sphere`、`circulating_current`、`MQ_m2` 的部分闭式，没有 `double_blob`。

解析反例无需数值拟合：正斑中心 $+d/2$ 对 $\int J_z z\,d^3r$ 贡献 $J_0(d/2)I_0$，负斑中心 $-d/2$ 贡献同号的 $J_0(d/2)I_0$，总和为 $J_0dI_0$；而两斑的 $\int J_z\,d^3r$ 正负抵消。因此当前缺失的闭式目标确为非零 $M2_{zz}$ 与零 $p$，不是可忽略的重复案例。

- `影响`: STF/迹分解的非零、零偶极基准未被执行；“每个 spec case 均通过”的证据不成立。
- `最小修复`: 新增 `double_blob` 电流并把默认距离设为 `d=2.5*R`；按两个局部球分别积分或使用覆盖 $[-2.25R,2.25R]^3$ 的合适求积，避免继续套用原点单球；在 closed forms 返回 `double_blob_M2_zz`；runner 从单一 case 清单迭代并逐案输出状态。并将 spec 的 `case_count_note` 计数改为 6（此为 spec 文本纠错，需主 agent/human gate 处理）。

## 缺陷 D3：raw-direct 与 clean-form 只互证一个电分量

- `file:line`: `code/scattering.py:207-265`；`tests/test_grahn.py:146-154`；`code/run_grahn_verification.py:128-130,144`；`sub-report/verify-grahn.md:18,24,26`；相应覆盖要求见 `formalization/grahn.yaml:147-163,170,246-257`。
- `现状`: raw adapter 只允许 `bump_polarized_sphere`，测试和 runner 只比较 `a_E[(1,0)]`。该球对称径向 bump 的只读数值结果中，唯一高信号分量为 $|a_E(1,0)|=4.2923829225847\times10^{-3}$；其余 $a_E/a_M$、$l=1/2$、所有其它 $m$ 均仅为约 $10^{-21}$ 或更小的求积噪声。测试甚至只对 `a_M(1,0)` 做零断言。
- `反证`: 这一 fixture 对电 $l=2$、磁 $l=1,2$、$m=\pm1,\pm2$ 没有非零信号，故即使这些通道的相位、$\tau/\pi$、$\Psi$ 导数或磁公式整体错误，当前 `a_E(1,0)` 比较仍会通过。runner 在只计算该标量后直接写 `status: PASS`。
- `影响`: Eq.(13)/(14) 与 Eq.(15)/(16) 的完整公式等价性没有证据；不能从一个电偶极分量外推到两个通道、两个阶数和全 $m$。
- `最小修复`: 增加全空间 $C^2$ 的解析 bump 电流基，解析给出 `div J`、$r\partial_r divJ$、`curl J`；至少让电/磁两通道在 $l=1,2$ 的每个允许 $m$（含 $m=0$ 与 $m\ne0$）分别有高信号 fixture。逐 `(branch,l,m)` 比较 raw/clean 复数系数：非零目标用相对阈值，暗通道用 spec 的 absolute-zero tolerance；runner 必须保存逐分量结果和未覆盖计数。

## 缺陷 D4：runner/报告把不完整覆盖硬编码为通过

- `file:line`: `code/run_grahn_verification.py:105-121,128-146,151-169`；`sub-report/verify-grahn.md:17-18,22-26`。
- `反证`: `analytic` 字典只含五项且没有 `double_blob`；Eq.(13)/(14) gate 只有字段 `relative_error_aE_1_0`。runner 没有断言 case 集合等于 spec，也没有逐分量覆盖矩阵或阈值判定，却在 `:144` 和 `:146` 写死 `status="PASS"`、`overall_gate="PASS_WITH_NOTES"`。现有报告随后把“解析 bump”列入通过项，并称 D2 已关闭。
- `影响`: 自报状态高于实际证据上限，掩盖 D2/D3，不能作为 W3 PASS 收据。
- `最小修复`: gate 状态由 case 集合完整性、逐 case 阈值和 raw/clean 覆盖矩阵计算；缺 case/缺 branch/缺 $(l,m)$ 必须 `BLOCKED`，不得硬编码 PASS。报告逐案列名、目标、误差、网格变化、状态，并对 absolute-zero 单列最大绝对误差。

## 必须新增/修改的定向测试

1. `test_riccati_l2_small_series_against_oracle`：参数化 $\rho\in\{0,10^{-12},10^{-10},10^{-8},9\times10^{-8},10^{-7},10^{-6}\}$，分别检查 $j_2,j_2',j_2'',\Psi_2''$；非零值用相对/绝对混合容差，另测阈值两侧连续性。
2. 修改 `test_psi_double_prime_recursion_and_small_r_limit`：小宗量点必须对解析或高精度 oracle，而非仅 `isfinite`；保留 $0.2,0.7$ 递推分支检查。
3. `test_double_blob_default_geometry_and_support`：断言默认 $d=2.5R$、$d\ge2R$、两个 support 不重叠，积分域半宽至少 $d/2+R=2.25R$。
4. `test_double_blob_closed_moments`：断言 $p$ 各分量 absolute-zero，$M2_{zz}=iJ_0dI_0/\omega$，其余应零分量用 absolute-zero；同时检查粗/细网格变化小于 $10^{-3}$。
5. `test_analytic_case_registry_matches_spec`：runner/实现 case 名集合与 YAML `cases[*].name` 精确相等，防静默漏项；当前应明确暴露六项与错误计数文本。
6. 参数化 raw/clean 等价测试：覆盖 `branch in {a_E,a_M}`、$l\in\{1,2\}$、每个 $m=-l,\ldots,l$；每个通道至少有一个非零解析 fixture。非零目标用相对阈值，零目标用 `absolute_zero=1e-8`，并验证错误注入确能让对应 fixture 失败。
7. runner 单元测试：缺任一 case 或任一要求的 `(branch,l,m)` 时总状态为 `BLOCKED`；不得从单个标量构造 `PASS`。

## 推荐修复顺序

1. 先修 D1 并加入小宗量 oracle 测试；改动局部且反例确定。
2. 以 YAML `cases` 序列为权威补全 `double_blob` 的电流、积分域、闭式和测试；同时由主 agent 走 human gate 修正 `case_count_note` 的“5→6”。
3. 扩展解析 raw/clean fixture，使电/磁、$l=1/2$、全允许 $m$ 都有非零探针及 absolute-zero 暗通道检查。
4. 最后让 runner 状态由完整性和阈值计算，并重新生成逐案/逐分量 W3 报告；W4--W6 再消费已修复核心。

## `scope_boundary`

以下仅列为后续依赖，本报告不把它们作为 W3 修复条件，也未审计其成败：

- W4：远场 Eq.(3)/(4) 的真正独立性、独立 VSH/场源及半径不变性。
- W5：$200\times400$ 角投影合同与收敛。
- W6：150/200/41 点正式重跑、产物新鲜度、全量独立 verifier 与最终裁决。

## `uncertainty`

- `formalization/grahn.yaml:231` 的“5 个案例”与紧随其后的六元素 `cases` 序列自相矛盾。本审计按结构化序列为权威；这一判断置信度高，但最终应由主 agent/human gate 修正文案。
- 没有运行会改写 `data/` 和 `verify-grahn.md` 的完整 runner；W3 阻塞结论来自静态执行链与只读定向 oracle，不依赖旧产物是否新鲜。
- 未复核论文原文；本任务只判断实现是否满足已冻结 v4 spec。

## `missing_evidence`

- 缺少一个能证明 raw/clean 全覆盖的解析电流 fixture 清单及逐分量结果矩阵。
- 缺少 `double_blob` 的任何实现、数值积分或报告记录。
- skill 指向的 `agent-workflow/references/report_template.md` 在工作区未找到；本报告按本任务书规定字段组织。

## 只读验证收据

- 高精度 oracle：`mpmath` 80 位对 $\Psi_2''$ 的数值微分，反例见 D1 表。
- 定向现有测试：`PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_grahn.py::test_psi_double_prime_recursion_and_small_r_limit` → `1 passed in 0.97s`，证明该测试确会漏检 D1。
- raw/clean 信号审计：$k=0.3$、grid $28\times29\times56$；唯一高信号为 $a_E(1,0)$，其余分量均为求积噪声量级。
