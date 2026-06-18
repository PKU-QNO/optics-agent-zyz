# 更新工件：蓝图、SKILL、工作流

## 目标
从本次复现中提取可复用的经验，更新项目工件，实现自迭代。

## 输入
- 本次复现全过程的产物和日志
- `workflows/paper_reproduction.workflow.yaml`
- 相关 SKILL.md 文件

## 输出
- 更新的 SKILL.md 文件
- 更新的 `paper_reproduction.workflow.yaml`
- 更新的蓝图文件

## 更新指南

### 1. 蓝图更新
- 成功复现：更新蓝图的默认参数
- 失败复现：在蓝图注释中记录失败模式
- 新发现的参数组合

### 2. SKILL 更新
检查以下内容是否需要更新：

**`optics-paper-reproduction` Skill**：
- 新的失败模式 → 追加到 lessons 部分
- 新的标准答案模板

**`comsol-java-api` Skill**：
- 新的 Java API 用法
- 新的模板建议
- 新的错误处理模式

**`optics-comsol-batch` Skill**：
- 新的批处理参数组合
- 新的错误码

**`optics-magnus-platform` Skill**：
- 新的资源需求模式
- 新的挂载路径经验

### 3. 工作流自迭代
评估当前工作流拓扑：

**检查项**：
- 节点顺序是否最优？
- 分支条件是否完备？
- 是否有冗余节点？
- 是否需要新增节点？

**修改规则**：
- 递增 version（如 0.1.0 → 0.2.0）
- 递增 iteration_count
- 在 history 中追加变更日志
- 运行 `python .codex/scripts/validate_all_skills.py`

### 4. AGENTS.md 同步
- 如有新的 Skill 依赖关系
- 更新 AGENTS.md 的路由表
- 确认 `.claude/skills` 和 `.agents/skills` 同步
