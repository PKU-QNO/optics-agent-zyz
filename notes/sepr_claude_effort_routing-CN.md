# SEPR Claude Code 思考强度路由：high / xhigh / max / ultracode

更新时间：2026-07-05

> **落地状态（2026-07-05 晚，权威口径以此为准）**：本文原正文假设 main-agent / evolution-agent / optics-lead **常驻 Fable 5**、执行层常驻 Sonnet 5（见 §裁决、§推荐默认值、§Agent frontmatter）。该"常驻 Fable"部分**已被 override**：7 个 agent frontmatter `model` 现全部 = `claude-sonnet-5[1m]`（Fable refusal-fallback 重缓存 + 太贵；Opus 4.8 malformed ~1.5%）。**effort 分级机制本身仍完全有效并已采纳**（全局 high / 复杂推导 xhigh / 最终裁决 max，跟 session 走不切 agent），只是不再区分"Fable 层"与"Sonnet 层"——所有 effort 都作用在 Sonnet 5 上。Fable 仅作 E05 反复不足时的单点临时安全阀。本文下面凡写 `claude-fable-5[1m]` 的行，读作"该停机点若临时升级时的启动参数"，不是常驻配置。落地细节见 `sepr_model_routing_gpt55_claude_code-CN.md` 顶部落地状态节。

用途：给 optics-lead-agent 讨论 SEPR/optics_agent 中 Claude Code `effort` / thinking 强度的具体选择。本文补充 `notes/sepr_model_routing_gpt55_claude_code-CN.md`：那份回答“谁干活”，本文回答“Claude 必须亲自判断时开到哪个强度”。

## 子 agent 搜索结论

截至 2026-07-05，官方文档口径是：

| 入口 | 可用值 | 备注 |
|---|---|---|
| `/effort` | `low`, `medium`, `high`, `xhigh`, `max`, `ultracode`, `auto` | `max` 与 `ultracode` 是 session-only；`auto` 回到模型默认 |
| `--effort` | `low`, `medium`, `high`, `xhigh`, `max` | 只影响当前启动 session |
| `CLAUDE_CODE_EFFORT_LEVEL` | `low`, `medium`, `high`, `xhigh`, `max`, `auto` | 优先级高，不建议全局长期设 `max` |
| `settings.json` 的 `effortLevel` | `low`, `medium`, `high`, `xhigh` | 不接受 `max` / `ultracode` |
| skill / subagent frontmatter | `effort` | 可覆盖 session 级 effort，但不覆盖环境变量 |

模型支持：

| 模型 | Claude Code effort |
|---|---|
| Fable 5 | `low`, `medium`, `high`, `xhigh`, `max` |
| Sonnet 5 / Opus 4.8 / Opus 4.7 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 4.6 / Sonnet 4.6 | `low`, `medium`, `high`, `max` |

几个容易混淆的点：

- `ultra` 不是通用 Claude Code/API effort level。
- `/effort ultracode` 是 Claude Code session-only 模式：发给模型的是 `xhigh`，同时让 Claude Code 做 dynamic workflow orchestration。
- `/code-review ultra` / `/ultrareview` 是代码审查专用云端深审，不是普通任务的 thinking effort。
- `ultrathink` 是 Claude Code 识别的一次性 prompt keyword，会加 in-context instruction，但不改变发给 API 的 effort。
- `think`、`think hard`、`think more` 在 Claude Code 里只是普通 prompt 文本，不是特殊开关。
- `alwaysThinkingEnabled` 是 thinking 显示/默认开关，不等于 effort 路由；Fable 5 thinking 不能关闭，仍由 effort 决定每步思考强度。

官方参考：

- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code settings](https://code.claude.com/docs/en/settings)

## 裁决

SEPR 不应全局固定 `xhigh` 或 `max`。默认应回到 `high` 或模型 `auto`，把 `xhigh` / `max` 留给少数高判断密度停机点。

核心原则：

```text
模型选择解决“谁干活”。
effort 选择解决“Claude 在必须亲自判断时花多少推理预算”。
```

加入 `gpt-5.5[400k]` 后更应如此：文件读写、代码实现、日志扫描、批量核对、报告初稿、cheap adversarial review 先交给 GPT-5.5/codex worker；Claude 的高 effort 只花在 gate、物理推导、result_class、规则面变更和跨报告矛盾裁决。

## 推荐默认值

| 层级 | 推荐 effort | 用途 |
|---|---|---|
| 全局 settings | `high` 或不设（`auto`） | 避免所有普通会话都吃 `xhigh` 成本 |
| Sonnet 5 普通 Claude 壳 | `high` | 普通编排、读 capsule、轻量审查、报告终审 |
| Fable 5 编排/裁决默认 | `high` | main-agent / evolution-agent / optics-lead 的常规运行 |
| 复杂推导会话 | `xhigh` | formalization 风险、物理推导、跨文件矛盾、失败归因 |
| 最终裁决会话 | `max` | gate 终裁、`result_class`、核心公式有效性、E-flow 六维裁决 |
| `ultracode` | 默认不用 | 只有明确要 Claude Code 自行组织动态 workflow 时短会话使用 |

不建议：

- 不要把 `CLAUDE_CODE_EFFORT_LEVEL=max` 设成长期环境变量。
- 不要把 `xhigh + alwaysThinkingEnabled` 当成所有 SEPR 任务的默认。
- 不要用提高 effort 解决长 session、工具密集、malformed、上下文污染问题；这些问题靠拆 session、handoff、文件化 capsule、熔断处理。

## 各强度的使用边界

### `low`

只适合极短、低风险、延迟敏感任务。SEPR 中基本不需要它，因为低判断密度任务应直接交给 GPT-5.5/codex worker。

### `medium`

适合 Claude 必须在场、但不影响 gate/物理/规则面的成本敏感工作。例如轻量格式检查、普通摘要、非关键日志扫读。SEPR 默认可不用它，避免多一档治理复杂度。

### `high`

建议作为 Claude 默认。适合：

- main-agent / sub-agent 的普通 Claude Code 编排；
- 读 GPT worker 产出的 capsule；
- 普通报告终审；
- verifier spec 初审；
- 非最终 gate 的准备性判断；
- run_manifest / report 的一致性检查。

这也是 Fable 5、Sonnet 5、Opus 4.8 的官方默认 effort，质量/成本/速度最稳。

### `xhigh`

用于“判断密度明显高，但还不是最终拍板”的任务：

- W03 formalization spec 风险审查；
- W04 物理推导口径审查；
- W05 theory_check 的关键分歧整理；
- 多份 sub-agent 报告之间的矛盾定位；
- 跨 case 失败模式归因；
- E-flow 中经验聚类、skill 改动方案设计；
- 怀疑 main/sub 存在转述漂移，需要上游重读关键证据。

`xhigh` 不应拿来跑长工具会话。若任务变成长文件读写/批量操作，应拆给 GPT worker 或脚本。

### `max`

只用于“错了会污染结果谱系或规则面”的最终裁决：

- Gate3/Gate4 终裁；
- `result_class` 定级；
- “物理复现成功 / 未成功”的最终口径；
- 核心公式、无量纲化、边界条件、verifier 判据的最终接受；
- E-flow 六维裁决；
- `.result`、active skill、CLAUDE/AGENTS 规则面变更前的最终确认；
- GPT-5.5 与 Claude 子 agent 结论冲突且影响后续路径。

`max` 应短会话、少工具、证据文件明确。它不是“更长 session 更稳”的解法。官方也提示 `max` 可能边际收益递减并更容易 overthinking，因此要按停机点使用。

### `ultracode` / `ultra`

常规 SEPR workflow 不建议默认使用。

原因：

- SEPR 的拓扑原则是“固定脊柱 + 节点内 agent 自由”，不是让 Claude Code 临场生成动态 workflow。
- 我们已有 GPT-5.5/codex cheap worker，fan-out 和机械执行不需要靠 `ultracode`。
- `ultracode` session-only 且实际模型 effort 仍是 `xhigh`，额外价值在 Claude Code 的动态编排，而不是更高 API thinking。

可考虑的少数场景：

- 对一整份复现 capsule 做独立红队审查，且不直接写规则面；
- 大规模框架 diff 之后，用 `/code-review ultra` 做深审；
- 用户明确要求 Claude Code 自行组织一段短期调查 workflow。

使用时必须新开短 session、限定 cwd、禁 secrets、禁止直接改 active 规则面，输出落盘后再由 Fable/用户 gate。

## W-flow 映射

| 步骤 | 推荐 effort / 模型 | 说明 |
|---|---|---|
| W01 PDF 预处理/抽取 | GPT-5.5；Claude 不介入或 `medium` | 机械工作，低判断密度 |
| W02 论文阅读/参数表 | GPT-5.5 多 pass；Claude `high` 审关键证据 | Claude 只亲读 gate 必需证据 |
| W03 formalization | GPT 起草；Fable `xhigh` 审 spec | spec 错会传染后续实现 |
| W04 theory + implementation | GPT 写代码/verifier；Fable `xhigh` 审物理 | 代码靠测试兜底，物理口径需 Claude |
| W05 theory_check / Gate3 | GPT cheap adversarial；Fable `max` 终裁 | 进入 gate 终裁才用 `max` |
| W06 run_and_monitor | GPT-5.5 | 不给 Claude 高 effort 跑日志 |
| W07 physical_verification | GPT 跑量化；Claude `high`/`xhigh` 解释失败 | verifier 是硬裁判 |
| W08 result_analysis / Gate4 | GPT 初稿；Fable `max` 定 `result_class` | 防止 pipeline/diagnostic 被说成物理成功 |
| W09 reproducibility_selfcheck | GPT-5.5 | 工程重跑和文件核验 |
| W10 final report | GPT 初稿；Claude `high` 终审；物理成功声明用 `max` | 只在结论口径高风险时升级 |
| W11 run_manifest / 契约文件 | Claude `high`；涉及规则面可 `max` | 契约文件必须可审计 |

## E-flow 映射

| 步骤 | 推荐 effort / 模型 | 说明 |
|---|---|---|
| E01 concurrent_review | GPT-5.5 fan-out | 成本和覆盖率优先 |
| E02 cluster_and_plan | GPT 聚类；Fable `xhigh` 裁冲突 | 聚类会影响后续 skill 演化 |
| E03 concurrent_skill_work | GPT 起草；Claude `high` 审 | 不直接进 active skill |
| E04 validate_and_replay | GPT 执行 replay；Claude `xhigh` 解读退化 | 判断退化才升级 |
| E05 六维裁决/三级治理 | Fable `max` | 自迭代最怕 reward hacking 和自我偏好 |
| E06 `.E-history` / run_manifest | Claude `high`/`max` | 若写入规则面，最终确认用 `max` |

## 实现建议

### 全局配置

建议把全局默认改为：

```json
{
  "effortLevel": "high"
}
```

或干脆不设 `effortLevel`，让模型走 `auto` 默认。不要用环境变量长期压住所有会话：

```powershell
# 不建议长期存在
$env:CLAUDE_CODE_EFFORT_LEVEL = "max"
```

### Agent frontmatter

可先保守落地：

```yaml
model: claude-fable-5[1m]
effort: high
```

对执行壳：

```yaml
model: claude-sonnet-5[1m]
effort: high
```

暂不建议把 main-agent / evolution-agent 持久设成 `xhigh`。需要升级时通过启动参数或 session 内 `/effort`：

```powershell
claude --model claude-fable-5[1m] --effort xhigh
claude --model claude-fable-5[1m] --effort max
```

### Spawn / report 字段

建议后续在 spawn 模板或 run_manifest 中记录：

```yaml
model_route:
  claude_model: claude-fable-5[1m]
  claude_effort: max
  escalation_reason: "Gate4 result_class final adjudication"
  worker_model: gpt-5.5[400k]
  evidence_claude_must_read:
    - verifier_summary.md
    - GATE4呈报.md
  session_boundary: "stop after decision; do not resume if malformed"
```

每次升级到 `xhigh` / `max` 都应写明原因。否则默认回 `high`。

## 与 Opus 4.8 malformed 风险的关系

提高 effort 不能修复 Opus 4.8 的 tool-call malformed 风险。这个风险是模型输出与 Claude Code harness 的工具调用序列化/解析问题，不是“思考不够”。

因此：

- 不因 malformed 把 Opus 4.8 升到 `max` 继续跑；
- 不 resume 已污染 session；
- 同 session 累计 2 次 malformed 立即熔断；
- 长任务每个 gate / 阶段默认断 session；
- Opus 4.8 只作 Fable 不可用时的短会话少工具 fallback。

## 一句话版本

```text
全局 high；复杂推导 xhigh；最终裁决 max；ultracode/ultra 只作短会话特殊审查；长工具活和 fan-out 交给 GPT-5.5/codex，不靠提高 Claude effort 硬顶。
```
