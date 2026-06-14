# 开发架构笔记：本地 ↔ Gustation 交互拓扑

> 学长建议的架构：Claude、Docker 都在你的 PC 上，SSH 传文件，Magnus 跑任务和交付。

---

## 一、整体拓扑

```
你的 PC（控制中心）                    Gustation 服务器（算力中心）
┌─────────────────────────┐         ┌──────────────────────────┐
│  Claude (LobeHub/CLI)   │  ───→   │  Magnus 集群              │
│  VS Code + Remote SSH   │  SSH    │  ├── 容器 Job 执行        │
│  Docker Desktop         │  ←───   │  ├── /data/ 持久存储      │
│  Magnus SDK (Python)    │  SDK    │  ├── 模型/数据集存放       │
│  git push/pull          │  ───→   │  └── 镜像从 Registry 拉取  │
└─────────────────────────┘         └──────────────────────────┘
         │                                  │
         │  Registry (ACR / git.pku)         │
         └────────── docker push ────────────┘
```

### 一句话总结

> **PC 是大脑，Gustation 是肌肉。** 你在 PC 上写代码、构建镜像、提交任务，Gustation 负责计算和执行。

---

## 二、核心交互方式（4 种）

### 方式 1：SSH — 命令行操作和传文件

**用途**：登录 GU 站，查看目录、传文件、执行简单命令。

**怎么做：**

```powershell
# VS Code Remote-SSH（推荐的图形化方式）
# 左下角 >< → Connect to Host → Gustation
# 安装 Remote-SSH 插件，配置在 .ssh/config

# 或命令行 SSH
ssh zhangyuanzheng@162.105.21.26

# 传文件到 GU 站
scp local_file.txt zhangyuanzheng@162.105.21.26:/data/zhangyuanzheng/

# 从 GU 站下载文件
scp zhangyuanzheng@162.105.21.26:/data/zhangyuanzheng/result.json .
```

**Agent 怎么做：** → `lobe-local-system` 的 `runCommand` 执行 `ssh` 或 `scp` 命令

---

### 方式 2：Magnus SDK — 任务提交和监控

**用途**：提交 Job、创建 Service、检查状态、获取结果。**这是最主要的交互方式。**

**怎么做：**

```python
# Python 脚本中（如 deploy_service.py / download_model_auto.py）
import json
import requests

# 读取凭据
secret = json.load(open("C:/Users/27370/Desktop/project/secret.json"))
addr = secret["magnus_address-gu"]   # https://gustation.phybench.cn/
token = secret["magnus_token-gu"]

# 提交 Job
requests.post(f"{addr}/api/jobs", headers={"Authorization": f"Bearer {token}"},
              json={...}, verify=False)

# 创建 Service
requests.post(f"{addr}/api/services", ...)
```

**Agent 怎么做：** → 用 `runInClient=true` 的 `executeAgentTask` 执行 Python 脚本，或直接调用 Magnus SDK

**你（zyz）怎么做：** → 双击运行 Python 脚本，或 Agent 提交后你去检查结果

---

### 方式 3：Docker — 镜像构建和推送

**用途**：本地构建 Docker 镜像，推送到 Registry（ACR / git.pku），GU 站拉取使用。

**怎么做：**

```powershell
# 1. 构建镜像（在 PC 上，用 Docker Desktop）
cd /d C:\Users\27370\Desktop\project
python train/tools/push_to_acr.py --type cpu --tag v4

# 2. 推送镜像（推送到阿里云 ACR）
python train/tools/push_to_acr.py --type cpu --tag v4

# 3. 同时推送北大 GitLab（校园内网更快）
docker tag crpi-.../zyz25/sft-base:v4 git.pku.edu.cn/rise-agi/sft-base:v4
docker push git.pku.edu.cn/rise-agi/sft-base:v4
```

**完整镜像地址：**
```yaml
# 阿里云 ACR（外网可用）
docker://crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/sft-base:v4

# 北大 GitLab（校园内网更快，开源项目推荐）
docker://git.pku.edu.cn/rise-agi/sft-base:v4
```

**Agent 怎么做：** → `runCommand` 执行 `docker build` / `docker push` 命令（需要 Docker Desktop 运行中）

**你（zyz）怎么做：** → 确保 Docker Desktop 开着，Agent 会调用本地的 Docker 命令行

---

### 方式 4：Git — 代码同步到 GitHub

**用途**：代码修改后通过 GitHub 同步，Magnus 容器在启动时从 GitHub 拉取。

**怎么做：**

```powershell
# 设置代理（Windows 需要）
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 日常流程
git add .
git commit -m "feat: xxx"
git push origin main     # 必须用 HTTPS，不用 SSH
```

**为什么需要 Git：** Magnus 的 Job 在容器启动时会从仓库拉取代码，所以本地修改后必须先 git push 再提交 Job。

**关键规则：** git push 失败 → 不能提交 Magnus Job，必须终止

**Agent 怎么做：** → `runCommand` 执行 `git add/commit/push`

**你（zyz）怎么做：** → 如果 Agent 推送失败，检查代理或 token 是否有问题

---

## 三、完整工作流程示例

### 场景：部署一个 CPU 推理服务

```
PC 上操作                               GU 站上操作
─────────                               ──────────

Step 1: 写代码（Claude Agent）
  ├── 设计推理逻辑
  ├── 写 deploy_service.py
  └── 保存到 project/optics_agent/python/

Step 2: 构建镜像（Docker Desktop）
  ├── Dockerfile.cpu 已就绪
  ├── docker build -t sft-base:v4
  ├── docker push 到 ACR 和 git.pku
  └── 镜像可在 Registry 上拉取

Step 3: 提交任务（Magnus SDK）                          Step 3: GU 站执行
  ├── python deploy_service.py  ──────────────────→      ├── 拉取 docker://.../sft-base:v4
  ├── 调用 POST /api/services                            ├── 启动 llama.cpp server
  └── Service 创建成功                                    ├── 监听 $MAGNUS_PORT
                                                         └── 对外提供 API

Step 4: 验证（curl / Python）
  ├── 请求 /api/services/{id}/v1/chat/completions
  ├── 检查响应是否正常
  └── 确认服务可用

Step 5: 如需修改
  ├── 改本地代码 → git commit + git push
  ├── 重建镜像 → docker build + docker push
  ├── 重新提交 Magnus Job（或更新 Service）
  └── GU 站拉取新代码和镜像执行
```

---

## 四、各 Agent 的职责分配

| Agent | 做什么 | 需要什么工具 |
|-------|--------|------------|
| **MYAI** | 方案设计、文件读写、调用 Claude Code | `lobe-local-system` |
| **Magnus-coding-Help** | Magnus 配置审查、Docker 相关建议、平台排错 | `lobe-local-system` |
| **AI 前沿追踪** | 前沿文献搜索、技术调研 | 网络搜索 |
| **Codex** | 代码实现、脚本编写、docker 构建、git 操作 | `runInClient=true` + `lobe-local-system` |
| **Supervisor（我）** | 任务分配、协调各 Agent | 群组编排工具 |
| **你（zyz）** | 确认执行、检查结果、提供反馈 | — |

### 交互规则

1. **Codex 需要运行代码时** → Supervsior 设 `runInClient=true`（可以在你电脑上跑命令）
2. **需要 Claude Code（Opus）时** → MYAI 通过本地 CLI 调用，不走 speak/executeAgentTask
3. **串行优先** → 一个 Agent 完成后再接下一个，避免并发冲突
4. **长输出存文件** → >50 行内容保存为 .md，群聊只出摘要

---

## 五、常用命令速查

### 本地（PC）

```powershell
# Docker
docker images                          # 查看本地镜像
docker build -t sft-base:v4 .          # 构建
docker push git.pku.edu.cn/rise-agi/sft-base:v4  # 推送

# Git
git status
git add .
git commit -m "msg"
git push origin main

# SSH
ssh zhangyuanzheng@162.105.21.26
scp file user@host:/path/

# 读取凭据（secret.json）
{"magnus_address-gu": "https://gustation.phybench.cn/",
 "magnus_token-gu": "sk-xxx"}
```

### 远端（GU 站）

```bash
# 查看目录
ls /data/zhangyuanzheng/
df -h /data/           # 查看磁盘空间

# 检查镜像是否已缓存
magnus login GU
magnus list            # 查看 blueprints
```

---

## 六、常见问题处理

| 问题 | 原因 | 解法 |
|------|------|------|
| Docker build 慢 | 基础镜像拉取慢 | 设代理 `127.0.0.1:7897` |
| git push 失败 | 代理不通或 token 过期 | 检查 git 代理配置 |
| Magnus job 一直 Pending | 资源不足或镜像未拉完 | `magnus list` 检查集群状态 |
| Service 启动失败 | entry_command 错误 | SSH 到 GU 看日志 |
| 413 推送失败 | 存储配额满 | 等管理员扩容 |
| Python 中文输出乱码 | cmd GBK 编码 | `set PYTHONIOENCODING=utf-8` |
