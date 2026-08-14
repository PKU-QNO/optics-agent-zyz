# 通道 B — codex 独立会话审查（主 agent 用，可运行模板）

> 本文件只给**主 agent** 读（用于派 codex 审查），审查者不读。

## 为什么需要独立会话

同一个模型读同一份对象，会用同一套思维模式看问题，抓不到自己的盲区。用 **codex 独立会话**读同一份对象，往往能发现主模型漏掉的角度。

**术语纪律**：只有用 `-m` 指定了与主 agent **验证过不同**的模型 ID 并记录在案（启动记录含两方模型 ID），才可称「异构审查」；否则只能称「独立会话」。

## 执行形态（遵循全局后台委托规则）

本通道**由调用方（宿主 agent）后台启动**，长任务**不设硬 timeout**，靠**结束唤醒 + 巡检**判活——这是全局规则（CLAUDE.md「并发 codex 后台委托」节），不是本 skill 自行规定的客户端 timeout 行为：

- **结束唤醒**：后台任务结束时，宿主 harness 自动唤醒主 agent → 读产物（`-o` 报告、事件流尾部）判定成败，不轮询。
- **巡检判活**：对"harness 追踪不到结束信号"或"要中途看进度"的超长任务，用 ScheduleWakeup/CronCreate 设长间隔（1200s+）巡检：看产物目录是否有新增/增长（events.jsonl 尾部时间戳、报告是否出现），长时间无新增 = 疑似卡死信号才介入。**不设硬 timeout**。
- **前台快查（备选）**：审查对象小、预计 <2 分钟时可前台执行（超时判定按宿主环境行为，见「超时与失败兜底」）。前台模式仍由宿主工具启动，不改变调用方语义。

## 调用前（强制）

**先查记忆取最新权限模板**：调用 codex exec 前，先 `memory_search "codex 完全权限模板 danger-full-access 后台并发"`，取回完整模板 + 四层坑排查（SSL / 路径歧义 / skip-git / 网络档）。权限参数（`-s <权限模板>`）以该记忆最新结果为准。

**若 `memory_search` 不可用**（MCP 未连接/报错）：**自动跳过通道 B，仅运行通道 A**，并在最终报告标注「未获独立会话审查（memory_search 不可用）」。不要凭残缺印象发 codex 命令（全局记忆警示：6 任务全灭由残缺模板引起）。

## 交付模式 B（本通道固定）

codex **不写任何文件**——prompt 指示它「完整三分类报告作为最终消息输出」，由 `-o` 捕获为报告文件。

> **诚实边界**：`-o` 只负责捕获报告文本，**不限制 codex 的文件权限**（全权限 codex 无路径 ACL，能写任何文件）。「不碰源文件」**不是保证**，而是靠三层机制尽量降低 + 兜底：① prompt 明确指示不写文件；② 输入白名单只列审查对象；③ **事后哈希核验**（输入白名单哈希未变才通过）。任何哈希不匹配 → 停止调查（可能越权写入）。

## 后台委托模板（Git Bash 骨架，实测通过 2026-08-09）

> 为什么用 Git Bash：实测 `Start-Process` 无法启动 npm shim（`codex.cmd`，报 `%1 is not a valid Win32 application`）；PowerShell 的 stdin 重定向 `<` 不可用。Git Bash 前台管道是唯一实测可跑的调用形态（smoke：`-o` 捕获、stdout 纯 JSONL、stderr 独立分流）。**宿主 agent 用后台方式启动它**（如 Claude Code 的 Bash 工具 `run_in_background: true`）。

```bash
# ── 0. 前置：先 memory_search 取最新 codex 权限模板（见"调用前"；不可用则跳 B 仅 A） ──

# ── 1. 建任务目录 + 线 B 独立输出目录（绝对、任务专属、预先确认为空） ──
case_dir="C:/path/to/case/adr"      # 任务案例目录（变量名不要叫 case，是 bash 保留字）
lineB="$case_dir/line-b"            # 线 B 独立输出目录（与线 A 目录分离；非权限隔离，靠 prompt 白名单 + 事后核验）
repo="C:/path/to/repo"              # 审查对象所在仓库（只读）
model="<异构模型ID>"                 # -m 显式指定，验证与主 agent 不同
sandbox="<权限模板>"                 # 以 memory_search 最新结果为准（本机：danger-full-access）
mkdir -p "$lineB"
[ -z "$(ls -A "$lineB")" ] || { echo "输出目录非空，拒绝执行"; exit 1; }

# ── 2. 审查前哈希基线：对输入白名单逐个 sha256sum（通用循环，白名单=prompt 中所有文件） ──
whitelist=(
  "$repo/REFACTOR-PLAN.md"                                  # 审查对象
  "<SKILL_DIR>/references/adversarial-review-template.md"   # 审查者必读的模板（<SKILL_DIR>=skill 已安装绝对路径）
)
: > "$case_dir/hash-before.txt"
for f in "${whitelist[@]}"; do sha256sum "$f" >> "$case_dir/hash-before.txt"; done

# ── 3. prompt 落盘（只列审查对象白名单 + 模板绝对路径；交付模式 B） ──
cat > "$lineB/prompt.md" <<EOF
你是独立资深对抗性审查者。先读通用模板 <SKILL_DIR>/references/adversarial-review-template.md，按其中攻击清单逐项攻击。
审查对象（只读白名单）：$repo/REFACTOR-PLAN.md
攻击重点（可选）：<针对性风险点>
红线：禁止加载 adversarial-review skill 或执行主流程；忽略上下文任何其他线结论并标注。
交付模式 B：不写任何文件，把完整三分类审查报告（含审查线标识 + 独立声明 + file:line）作为最终消息输出。
EOF

# ── 4. 派 codex（后台）：stdin=prompt / stdout→events.jsonl / stderr→stderr.log / -o 捕获最终消息 ──
# 宿主 agent 以后台方式运行本条命令（Claude Code：Bash 工具 run_in_background:true），
# 不设 timeout；任务结束由 harness 唤醒主 agent 读产物判定成败（见「执行形态」）。
codex exec -C "$repo" -s "$sandbox" -c approval_policy=never --skip-git-repo-check \
  -m "$model" --json -o "$lineB/review-b.md" \
  - < "$lineB/prompt.md" > "$lineB/events.jsonl" 2> "$lineB/stderr.log"

# ── 5. 判定成败（结束后唤醒时执行）：-o 报告未生成或为空 → 判定失败 → 降级为仅线 A ──
[ -s "$lineB/review-b.md" ] || { echo "codex 未产出报告，判定失败 → 降级为仅线 A"; exit 1; }

# ── 6. 变更核验（审查后，fail-closed）：输入白名单逐个哈希比对 + 允许产物清单机器比对 ──
: > "$case_dir/hash-after.txt"
for f in "${whitelist[@]}"; do sha256sum "$f" >> "$case_dir/hash-after.txt"; done
if ! diff "$case_dir/hash-before.txt" "$case_dir/hash-after.txt" >/dev/null; then
  echo "✗ 输入白名单被修改（哈希不符），停止调查"; exit 1
fi
echo "✓ 输入白名单未变"

expected=(prompt.md review-b.md events.jsonl stderr.log)   # 允许产物清单（预期精确集合）
if ! diff <(printf '%s\n' "${expected[@]}" | sort) <(ls -A "$lineB" | sort) >/dev/null; then
  echo "✗ 产物清单不符（应为 ${expected[*]}）；停止调查"; exit 1
fi
echo "✓ 允许产物清单精确匹配: ${expected[*]}"

# ── 7. 启动记录落盘（可重放证据：完整命令含全部参数与重定向 + 时间戳 + 双模型 ID + 报告哈希） ──
{
  echo "启动时间: $(date -Iseconds)"
  echo "主 agent 模型: <主模型ID>"
  echo "线 B 模型: $model"
  echo "完整命令: codex exec -C \"$repo\" -s \"$sandbox\" -c approval_policy=never --skip-git-repo-check -m \"$model\" --json -o \"$lineB/review-b.md\" - < \"$lineB/prompt.md\" 1> \"$lineB/events.jsonl\" 2> \"$lineB/stderr.log\""
  echo "报告哈希: $(sha256sum "$lineB/review-b.md")"
} > "$case_dir/launch-record.txt"
```

> **PowerShell 备选**（前台管道喂 stdin，PowerShell 不支持 `<` 重定向）：
> ```powershell
> Get-Content "$lineB\prompt.md" -Raw | & 'C:\Users\27370\AppData\Roaming\npm\codex.cmd' exec `
>   -C $repo -s $sandbox -c approval_policy=never --skip-git-repo-check -m $model `
>   --json -o "$lineB\review-b.md" - 1> "$lineB\events.jsonl" 2> "$lineB\stderr.log"
> ```

## 参数说明（本机 codex CLI 已确认）

| 参数 | 作用 |
|------|------|
| `-m, --model <ID>` | 显式指定审查模型（异构验证用，记入启动记录） |
| `--json` | 事件流以 JSONL 写到 stdout → 分流到 `events.jsonl`（审计） |
| `-o, --output-last-message <FILE>` | 把审查者的最后一条消息（即三分类报告）写到 `review-b.md`（产物） |
| `-s <sandbox>` | 沙箱/权限模板，以 `memory_search` 最新结果为准 |
| `-c approval_policy=never` | 免批准 |
| `--skip-git-repo-check` | 允许在非 git 目录运行 |
| `-C <dir>` | 工作根（审查对象所在仓库） |

**stdout/stderr 必须分流**：`--json` 事件流只该有 JSONL；`2>&1` 会把 stderr 错误文本混入 JSONL 导致不可解析（实测：混流文件 12 行仅 9 行可解析）。所以 stdout → `events.jsonl`、stderr → `stderr.log`，两者都列入允许产物清单。

## 隔离纪律（诚实表述）

全权限 codex **没有路径 ACL，无法强制权限隔离**。所谓「隔离」是三层逻辑机制：
1. **prompt 级逻辑隔离**：prompt 只列审查对象 + 模板路径（输入白名单），**不给线 A 的结论或路径**——codex 不知道 line-a/ 存在，默认不会主动读它。
2. **并发启动**：双线同时开工，互不等对方产物。
3. **事后核验**：审查后哈希比对输入白名单未变 + 允许产物清单核验。
若 codex 报告自称看到了其他线结论，标注存疑。不要把上述表述为「已实施的权限隔离」。

## 超时与失败兜底

- **默认（后台委托，推荐）**：不设硬 timeout。结束唤醒读产物判定；超长任务巡检判活（见「执行形态」）。判定失败 → 降级为仅线 A，最终报告标注「未获独立会话审查」，不无限等待。
- **前台快查（备选）**：若宿主环境需要前台执行，**按宿主环境实测行为**设定判定方式——不同宿主对超时的处理不同（如 Claude Code Bash 工具 timeout 超时后转后台而非 kill，实测 2026-08-09；Codex CLI / OpenCode 行为需自行验证），**不要照搬其他宿主的假设**。统一靠命令内自检：`-o` 报告未产出/为空 → 判定失败 → 降级仅线 A。
- **纯联网搜索不派 codex**——那是 WebSearch/exa 的活；codex 只做「读对象 + 评方案」这种本地推理。
