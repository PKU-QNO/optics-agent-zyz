# Workflow State Files

此目录存储工作流执行状态文件，每 session 一个 `.yaml` 文件。

## 文件命名
`<session_id>.yaml` — session_id 由 workflow engine 生成 UUID。

## 注意事项
- 状态文件是临时性的，session 完成后保留 30 天
- 状态文件包含 session 级别的中间产物路径
- 不要手动修改状态文件
