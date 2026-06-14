#  Magnus 新服务器独立部署指南

> 在一台硬件和软件环境与已有站点**完全不同**的新服务器上，从零部署一个**完全独立**的 Magnus 实例。
>
> 新站点拥有**自己的端口、自己的用户体系、自己的权限边界**——与主站完全隔离。

---

## 一、认清差异：新服务器 ≠ 旧服务器

每台服务器的硬件和软件条件都不同。部署前必须逐项摸清，**不能照搬旧配置**：

| 维度 | 旧站点可能是 | 新站点可能是 | 影响 |
|------|------------|------------|------|
| **GPU 型号** | RTX 5090 (Blackwell) | A100 (Ampere) / H100 (Hopper) | 容器镜像 CUDA 版本不兼容→运行时崩溃 |
| **GPU 数量** | 8 卡/节点 | 4 卡/节点 | `cluster.gpus[].limit` 需重设 |
| **SLURM Gres 名** | `gpu:rtx5090` | `gpu:a100` | `cluster.gpus[].value` 不匹配→提交报 400 |
| **CPU 核数** | 192 核 | 64 核 | `cluster.max_cpu_count` 需重设 |
| **内存大小** | 512GB | 256GB | `cluster.max_memory_demand` 需重设 |
| **存储路径** | `/home:/home` NFS | `/mnt/nfs/home:/home` | Job 容器内找不到数据→运行失败 |
| **服务器 IP** | `192.168.1.100` | `10.0.0.50` | 回调地址不通→Job 状态永不更新 |
| **SLURM 版本** | 21.08 | 24.11 | JSON 字段格式不同（int vs dict） |
| **OS** | Ubuntu 22.04 | Rocky Linux 9 | 包管理器、systemd 路径不同 |
| **用户群体** | 团队 A | 团队 B | 认证/权限完全隔离 |

**核心原则**：每台新服务器的配置都从零采集信息。不假设任何默认值是正确的。不与主站共享任何运行时状态。

---

## 二、端口隔离：必须与主站不同

新站点拥有**独立的用户群体**，不同的人有权限访问。因此端口**必须**与主站区分——这不是可选项。

### 为什么端口必须不同

```
主站  :3011  ──── 团队 A 用户 ──── 飞书应用 A（或 local 用户 A）
新站点 :3021  ──── 团队 B 用户 ──── 飞书应用 B（或 local 用户 B）
```

- 不同端口 = 不同的访问入口 = 不同的用户边界
- 同一台物理服务器上，端口自然不能冲突
- 即使部署在不同物理服务器上，**也应使用不同端口**：SDK 通过 `site` 切换站点时，端口是区分站点的关键标识

### 端口选择

| 含义 | 主站 | 新站点 |
|------|------|--------|
| 前端页面入口 | 3011 | **3021**（选一个不同的） |
| 后端 API | 8017 | **8027**（选一个不同的） |

**规则**：确保在部署服务器上未被占用：

```bash
ss -tlnp | grep -E ":(3011|3021|3031|8017|8027|8037)"
```

### 端口在系统中的传播

端口数字在以下位置生效，**全部由 `magnus_config.yaml` 驱动**，不需要改源代码：

```
magnus_config.yaml
  ├── server.front_end_port
  │     ├── next.config.mjs → NEXT_PUBLIC_FRONT_END_PORT
  │     ├── next.config.mjs → NEXT_PUBLIC_BACK_END_PORT
  │     ├── next.config.mjs → allowedDevOrigins
  │     ├── npm run start -p {front_end_port}
  │     ├── SLURM 模式: MAGNUS_ADDRESS = {address}:{front_end_port}
  │     │     └── wrapper.py → Job 回调报告状态
  │     └── cors_origins 必须包含此端口
  │
  ├── server.back_end_port
  │     ├── uvicorn.run(port=back_end_port)
  │     └── Docker 模式: MAGNUS_ADDRESS = {address}:{back_end_port}
  │
  └── server.address
        └── 与端口拼接为 Job 回调地址
```

> 端口配错的症状：前端 404、API CORS 报错、Job 状态永远 RUNNING。

---

## 三、权限隔离：独立的用户体系

新站点的核心特征之一是**与主站不是同一批人有权限**。这要求认证配置完全独立。

### 两种认证模式下的隔离方式

#### 方式一：local 模式（推荐新部署首选）

```yaml
server:
  auth:
    provider: local
```

- Magnus 自动以当前 OS 用户创建账户
- 仅此 OS 用户可登录（以及能 SSH 到此服务器的人）
- **权限边界 = OS 用户边界**：有服务器账号的人才有 Magnus 权限
- 不同服务器自然拥有不同的 OS 用户 → 天然隔离

#### 方式二：feishu 模式（多用户场景）

```yaml
server:
  auth:
    provider: feishu
    feishu_client:
      app_id: cli_NEW_SITE_APP_ID          # ★ 使用独立的飞书应用
      app_secret: xxxxxxxxxxxxxxxxxxxxxx
      admins:
        - ou_NEW_SITE_ADMIN_OPEN_ID        # ★ 新站点的管理员
      refresh_interval: 3600
```

- **必须使用独立的飞书应用**（不能与主站共用），否则主站用户可直接登录新站点
- 飞书应用的**安全域名**配置为新服务器的 IP:端口
- `admins` 列表是**新站点的管理员**，与主站管理员互不重叠

### 主站 vs 新站点：用户体系完全隔离

| | 主站 | 新站点 |
|---|------|--------|
| 前端入口 | `http://IP_A:3011` | `http://IP_B:3021` |
| 认证方式 | feishu App A | feishu App B（或 local） |
| 管理员 | 团队 A 的 open_id | 团队 B 的 open_id |
| 数据库 | `/data/magnus/database/magnus.db` | `/data/magnus-new/database/magnus.db` |
| JWT 密钥 | `secret_key_A` | `secret_key_B`（必须不同） |
| 用户记录 | 团队 A 的飞书用户 | 团队 B 的飞书用户 |

**关键**：两个站点的 JWT `secret_key` 必须不同。否则一个站点的 token 可以被另一个站点接受。

---

## 四、部署流程总览

```
信息采集 → 环境准备 → SLURM 验证 → 配置编写 → 构建启动 → 验证测试
                                            ↑
                                     最关键的步骤——
                               端口 + 认证 + GPU + SLURM
                               全部在此集中体现
```

下面先讲 SLURM（依赖最复杂、与硬件耦合最紧的环节），然后按流程逐步展开。

---

## 五、SLURM 部署与 GPU 资源配置

Magnus 依赖 SLURM 作为作业调度器。新服务器的 SLURM 必须正确安装、正确配置 GPU GRES，Magnus 才能发现 GPU 并提交 GPU Job。这是整个部署中**对硬件耦合最紧**的一环。

### 5.1 SLURM 架构与 Magnus 的关系

```
┌─────────────────────────────────────────────────┐
│                  Magnus 服务器                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 前端 3021 │  │ 后端 8027 │  │ slurm-client  │  │
│  │          │  │          │  │ (sbatch,       │  │
│  │          │  │          │  │  squeue,       │  │
│  │          │  │          │  │  scancel,      │  │
│  │          │  │          │  │  sinfo,        │  │
│  │          │  │          │  │  scontrol)     │  │
│  └──────────┘  └──────────┘  └───────┬───────┘  │
│                                      │           │
└──────────────────────────────────────┼───────────┘
                                       │ SLURM 协议
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
            ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
            │ slurmctld     │  │  计算节点 1    │  │  计算节点 2    │
            │ (控制器)       │  │  slurmd       │  │  slurmd       │
            │               │  │  GPU: A100 x4  │  │  GPU: A100 x8  │
            └───────────────┘  └───────────────┘  └───────────────┘
```

**Magnus 服务器只需要 `slurm-client`**（`sbatch`/`squeue`/`scancel`/`sinfo`/`scontrol`），不需要运行 `slurmctld` 或 `slurmd`。它通过 SLURM 命令行工具与集群控制器通信。

**计算节点**需要 `slurmd` 守护进程和 GPU 驱动程序。

### 5.2 安装 SLURM

#### Magnus 服务器节点（只需客户端）

```bash
# Debian/Ubuntu
apt-get install -y slurm-client munge

# RHEL/Rocky/Alma
dnf install -y slurm-client munge
```

#### 计算节点（需要 slurmd + GPU 驱动）

```bash
# Debian/Ubuntu
apt-get install -y slurmd munge nvidia-driver-570

# RHEL/Rocky
dnf install -y slurmd munge nvidia-driver
```

### 5.3 slurm.conf 关键配置

SLURM 的主配置文件（通常位于 `/etc/slurm/slurm.conf`）。以下是 Magnus 依赖的关键字段：

```ini
# /etc/slurm/slurm.conf

ClusterName=my-cluster
SlurmctldHost=controller-node-name

# ── 调度策略 ──
SelectType=select/linear
# Magnus 使用 EASY backfill，但调度决策在 Magnus 侧完成。
# SLURM 侧保持简单：select/linear 即可。

# ── 记账/资源采集 ──
AccountingStorageType=accounting_storage/none
JobAcctGatherType=jobacct_gather/none
# Magnus 自己追踪 Job 状态，不需要 SLURM 记账。

# ── 节点定义 ──
# ★★★ 关键：Gres 字段声明 GPU 资源 ★★★
NodeName=node[01-04] CPUs=128 RealMemory=515000 Gres=gpu:a100:8 State=UNKNOWN

# ── 分区定义 ──
PartitionName=batch Nodes=node[01-04] Default=YES MaxTime=INFINITE State=UP
```

#### Gres 字段格式

```
Gres=gpu:<型号名>:<数量>
```

| 集群 GPU | Gres 写法 | 说明 |
|---------|---------|------|
| 8×RTX 5090 | `Gres=gpu:rtx5090:8` | 型号名自定义，建议用小写简写 |
| 4×A100 | `Gres=gpu:a100:4` | 同上 |
| 8×H100 | `Gres=gpu:h100:8` | 同上 |
| 混合节点（不推荐） | `NodeName=node01 Gres=gpu:a100:4` | 不同节点不同类型需分开声明 |

**型号名是自定义的**，但一旦确定，必须在以下三处保持一致：

```
slurm.conf Gres 名  →  gres.conf 设备绑定  →  magnus_config.yaml cluster.gpus[].value
     ↓                        ↓                           ↓
  gpu:a100           Name=gpu Type=a100            value: a100
```

如果三处不一致，SLURM 无法分配 GPU 或 Magnus 提交时报 400 错误。

### 5.4 gres.conf —— GPU 设备绑定

`/etc/slurm/gres.conf` 将 SLURM 的 Gres 名称与物理 GPU 设备绑定：

```ini
# /etc/slurm/gres.conf
# 格式：Name=<Gres类型> Type=<型号> File=<设备路径>

# === 4×A100 节点示例 ===
# node01: 4 张 A100
Name=gpu Type=a100 File=/dev/nvidia0
Name=gpu Type=a100 File=/dev/nvidia1
Name=gpu Type=a100 File=/dev/nvidia2
Name=gpu Type=a100 File=/dev/nvidia3

# === 8×RTX 5090 节点示例 ===
# Name=gpu Type=rtx5090 File=/dev/nvidia0
# Name=gpu Type=rtx5090 File=/dev/nvidia1
# ...
# Name=gpu Type=rtx5090 File=/dev/nvidia7
```

**关键规则**：
- `Name=gpu` — 固定写 `gpu`，表示这是 GPU 类资源。Magnus 提交时用 `--gres=gpu:...`
- `Type=xxx` — 型号名，**必须与 slurm.conf 中 Gres 冒号后面的型号名一致**（如 `a100`、`rtx5090`）
- `File=/dev/nvidiaN` — 物理 GPU 设备路径，每张卡一行

**多节点场景**：每个节点的 gres.conf 只写自己的 GPU 设备。SLURM 控制器汇总所有节点信息。

### 5.5 验证 SLURM + GPU 配置

在新服务器上逐项检查（这些也是 Magnus 启动时的系统依赖检查项）：

```bash
# 1. SLURM 集群是否正常
sinfo
# 预期：
# PARTITION  AVAIL  TIMELIMIT  NODES  STATE  NODELIST
# batch*        up   infinite      4  idle   node[01-04]

# 2. GPU 资源是否被 SLURM 识别
scontrol show node node01 | grep Gres
# 预期：Gres=gpu:a100:4
# ★ 这里冒号后面的名字就是 magnus_config.yaml 中 cluster.gpus[].value 应填的值

# 3. 手动提交一个 GPU Job 测试
cat > /tmp/test_gpu.sh << 'EOF'
#!/bin/bash
nvidia-smi
EOF

sbatch --gres=gpu:a100:1 --job-name=test-gpu --output=/tmp/test_gpu_%j.log /tmp/test_gpu.sh

# 查看 Job 状态
squeue

# 查看输出（Job 完成后）
cat /tmp/test_gpu_*.log
```

### 5.6 SLURM 与 Magnus 的交互细节

当用户在 Magnus 中提交 GPU Job 时，Magnus 执行以下 SLURM 命令：

**① 资源发现** — 后端启动时和每 300 秒：

```bash
# 获取集群总 GPU 容量
scontrol show node --future          # 解析 Gres= 行

# 获取当前 GPU 占用
squeue --states=RUNNING,COMPLETING --format="%D %b" --noheader
# 输出示例: 2 gpu:a100:4     → 2节点 × 4卡 = 8 GPU used

# 获取运行中 Job 的详细 GPU 信息
squeue --states=RUNNING,COMPLETING --json
# 解析 gres_detail 字段: "gpu:a100:1(IDX:0)" → model=a100, count=1
```

**② Job 提交** — 用户提交 GPU Job 时：

```bash
sbatch --parsable \
  --job-name=<task_name> \
  --output=<workspace>/jobs/<id>/slurm/output.txt \
  --gres=gpu:a100:2 \              # ← 来自 job.gpu_type + job.gpu_count
  --mem=3200M \                    # ← 来自 job.memory_demand
  --cpus-per-task=8 \              # ← 来自 job.cpu_count
  # 脚本内容（stdin 传入）：
  #   #!/bin/bash
  #   trap '' TERM
  #   exec python3 <workspace>/jobs/<id>/wrapper.py
```

**③ 状态同步** — 每 2 秒心跳：

```bash
squeue -h -j <slurm_job_id> -o "%t"
# R → RUNNING, PD → PENDING, CG → RUNNING
# CD → COMPLETED, F/CA/TO → FAILED
```

**④ 终止 Job**：

```bash
scancel --signal=KILL --full <slurm_job_id>   # 立即杀
scancel <slurm_job_id>                        # 标记取消
```

### 5.7 cgroup 配置（推荐）

SLURM 需要 cgroup 支持来限制 Job 资源使用和采集 OOM 事件。Magnus 通过 wrapper.py 读取 cgroup 信息来检测 OOM。

```bash
# 确认 cgroup v1 或 v2 可用
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2  → v2（推荐）
# cgroup on /sys/fs/cgroup/...            → v1

# slurm.conf 中启用 cgroup（可选但推荐）
# ProctrackType=proctrack/cgroup
# TaskPlugin=task/cgroup
```

### 5.8 单节点测试环境

如果新服务器是单节点（无独立 SLURM 集群），可以用项目自带的脚本快速搭建：

```bash
# 启动单节点 SLURM（CPU only）
bash /opt/magnus-new/scripts/setup_single_node_slurm.sh --cpus 16 --memory-mb 32000

# 验证
sinfo
# PARTITION  AVAIL  TIMELIMIT  NODES  STATE  NODELIST
# batch*        up   infinite      1  idle   localhost
```

此脚本在 Magnus 运行时容器的 Dockerfile 中也用于搭建嵌套 SLURM（"Child Magnus"场景）。

### 5.9 常见 SLURM 问题

| 问题 | 症状 | 排查 |
|------|------|------|
| GPU 未被 SLURM 识别 | `scontrol show node` 无 Gres 行 | 检查 `gres.conf` 是否存在且路径正确 |
| Gres 名不匹配 | Magnus 提交报 400: `gpu_type not available` | 用 `scontrol show node \| grep Gres` 核对实际名 |
| Job 永久 PENDING (Resources) | `squeue` 显示 `(Resources)` 原因 | GPU 数量不够或 Gres 型号名写错 |
| Job 永久 PENDING (PartitionConfig) | `squeue` 显示配置错误 | 分区配置有问题，检查 `slurm.conf` |
| slurmctld 未运行 | `sinfo` 报连接错误 | `systemctl status slurmctld` |
| 计算节点 drain/down | `sinfo` 显示 `drain*` 或 `down*` | 在控制器上 `scontrol update NodeName=xxx State=RESUME` |
| slurm.conf 修改后不生效 | 配置变更无效 | 需要重启 slurmctld + 所有 slurmd，或 `scontrol reconfigure` |
| Magnus 启动失败 | "系统依赖缺失: sbatch..." | Magnus 服务器上安装 `slurm-client` |

```
信息采集 → 环境准备 → 配置编写 → 构建启动 → 验证测试
                                 ↑
                          最关键的步骤——
                    所有差异在此体现
                端口 + 认证 + GPU 三项
                必须与主站完全不同
```

---

## 六、第一步：信息采集

在新服务器上运行以下命令，记录所有输出。

### 6.1 硬件信息

```bash
# === GPU 型号和数量（最关键） ===
scontrol show node --future | grep -E "NodeName|Gres|CPUTot|RealMemory"

# 示例输出（A100 集群）:
#   NodeName=node01 CPUTot=128 RealMemory=515000 Gres=gpu:a100:4(S:0-1)
# 从中提取：CPU=128核, 内存=515000MB, GPU=a100×4

# 如果 scontrol 输出中 Gres 格式不同，也可以在计算节点上直接查
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
```

将采集结果填入下表：

| 采集项 | 实际值（记录） | 对应配置字段 |
|--------|-------------|-----------|
| GPU Gres 名 | `_______` (如 `gpu:a100`) | `cluster.gpus[].value` |
| GPU 显存 | `_______` (如 80GB) | `cluster.gpus[].meta` |
| GPU 架构 | `_______` (如 Ampere) | 决定容器镜像 CUDA 版本 |
| 单节点 GPU 数 | `_______` (如 4) | `cluster.gpus[].limit` |
| CPU 总核数 | `_______` (如 128) | `cluster.max_cpu_count` |
| 内存总量 (MB) | `_______` (如 515000) | `cluster.max_memory_demand` |

### 6.2 软件环境

```bash
# === SLURM 版本 ===
sinfo --version

# === 操作系统 ===
cat /etc/os-release | head -4

# === 容器运行时 ===
apptainer --version

# === Python & Node.js ===
uv python install 3.14
uv python find 3.14
node --version
```

### 6.3 存储与路径

```bash
df -h | grep -E "nfs|cifs|ceph|weka|beegfs|lustre"
echo $HOME
ls /data/ 2>/dev/null || echo "无 /data 目录"
```

### 6.4 网络信息

```bash
hostname -I                           # 服务器 IP
ss -tlnp | grep -E ":(30[0-9]|80[0-9])"  # 端口占用情况
```

---

## 七、第二步：环境准备

### 7.1 安装系统依赖

**Debian/Ubuntu**：
```bash
apt-get update
apt-get install -y slurm-client apptainer git ffmpeg acl curl ca-certificates
```

**RHEL/Rocky/Alma Linux**：
```bash
dnf install -y slurm-client apptainer git ffmpeg acl curl ca-certificates
```

**验证**：
```bash
for cmd in sbatch squeue scancel sinfo scontrol apptainer git ffmpeg setfacl; do
    which $cmd >/dev/null 2>&1 && echo "✅ $cmd" || echo "❌ $cmd 缺失"
done
```

### 7.2 安装 Node.js 20

```bash
# Debian/Ubuntu
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# RHEL/Rocky
dnf module install -y nodejs:20
```

### 7.3 创建数据目录

```bash
# 与主站完全分离的数据目录
MAGNUS_ROOT="/data/magnus-new"

mkdir -p ${MAGNUS_ROOT}/{database,workspace,uv_cache,file_custody}
chmod 755 ${MAGNUS_ROOT}
```

### 7.4 拉取 Magnus 代码

```bash
git clone https://github.com/rise-agi/magnus.git /opt/magnus-new
cd /opt/magnus-new
```

---

## 八、第三步：编写配置文件

这是**整个部署中最关键的步骤**。端口、认证、GPU 三项集中在此配置。

### 8.1 从模板开始

```bash
cp /opt/magnus-new/configs/magnus_config.yaml.example /opt/magnus-new/configs/magnus_config.yaml
```

### 8.2 完整配置（新站点专用）

```yaml
# /opt/magnus-new/configs/magnus_config.yaml

client:
  jobs:
    poll_interval: 2

# ═══════════════════════════════════════════════════════════════
# server 段
# ═══════════════════════════════════════════════════════════════
server:
  # ★ 新服务器 IP
  address: http://10.0.0.50

  # ★★★ 端口必须与主站不同 ★★★
  front_end_port: 3021           # 主站用 3011，新站点用 3021
  back_end_port: 8027            # 主站用 8017，新站点用 8027

  # ★ 新站点专用数据目录
  root: /data/magnus-new

  cors_origins:
    - http://10.0.0.50:3021      # 新站点前端（生产）
    - http://10.0.0.50:3023      # 新站点前端（开发，port+2）
    - http://localhost:3023

  database:
    pool_size: 8
    max_overflow: 16
    pool_timeout: 10
    pool_recycle: 3600

  # ★★★ 认证——独立的用户体系 ★★★
  auth:
    # 新站点使用独立的认证配置
    provider: local
    jwt_signer:
      # 生成随机密钥: python3 -c "import secrets; print(secrets.token_hex(32))"
      # ★ 必须与主站的 secret_key 不同！
      secret_key: <新站点专属随机密钥>
      algorithm: HS256
      expire_minutes: 10080

    # 如果用飞书认证——使用独立的飞书应用
    # provider: feishu
    # feishu_client:
    #   app_id: cli_NEW_SITE_APP          # ★ 独立的飞书应用
    #   app_secret: xxxxxxxxxxxxxxxxxx
    #   admins:
    #     - ou_NEW_ADMIN_OPEN_ID           # ★ 新站点的管理员
    #   refresh_interval: 3600

  scheduler:
    heartbeat_interval: 2
    snapshot_interval: 300

  service_proxy:
    max_concurrency: 1024

  file_custody:
    max_size: 10G
    max_file_size: 2G
    max_processes: 128
    default_ttl_minutes: 60
    max_ttl_minutes: 1440

  explorer:
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    model_name: qwen3-235b-a22b
    visual_model_name: qwen-vl-max
    small_fast_model_name: qwen-turbo
    stt_model_name: whisper-1
    api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ═══════════════════════════════════════════════════════════════
# execution 段
# ═══════════════════════════════════════════════════════════════
execution:
  backend: slurm
  container_runtime: apptainer
  allow_root: false
  resource_cache:
    container_cache_size: 80G
    repo_cache_size: 20G

# ═══════════════════════════════════════════════════════════════
# cluster 段：★ 新服务器硬件差异全部集中在这里 ★
# ═══════════════════════════════════════════════════════════════
cluster:
  name: "新站点集群"

  # ── GPU 配置（填入 5.1 节采集的数据） ──
  gpus:
    - value: a100                       # ★ 必须与 SLURM Gres 名完全一致（小写）
      label: NVIDIA A100 80GB
      meta: 80GB • Ampere
      limit: 4                          # 单 Job 最大 GPU 数

  # ── 集群资源上限（填入 5.1 节采集的数据） ──
  max_cpu_count: 128
  max_memory_demand: 256G

  # ── Job 默认资源 ──
  default_cpu_count: 4
  default_memory_demand: 1600M
  default_runner: root
  default_ephemeral_storage: 10G

  # ★ 容器镜像——与新 GPU 的 CUDA 架构匹配（见 7.4）
  default_container_image: docker://pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

  registry_mirror: null

  # ★ 容器挂载——填入 5.3 节采集的实际存储路径
  default_system_entry_command: |-
    mounts=(
      "/home:/home"
      "/data:/data"
    )
    export APPTAINER_BIND=$(IFS=,; echo "${mounts[*]}")
    export UV_CACHE_DIR=/data/magnus-new/uv_cache
```

### 8.3 GPU 配置——最容易出错的环节

`cluster.gpus[].value` 必须是 SLURM 中 Gres 配置的类型名（小写）：

```bash
# 验证方法：在服务器上运行
scontrol show node --future | grep Gres
```

| 输出结果 | `value` 应填 | `label` 建议 |
|---------|-------------|-------------|
| `Gres=gpu:rtx5090:8` | `rtx5090` | NVIDIA GeForce RTX 5090 |
| `Gres=gpu:a100:4` | `a100` | NVIDIA A100 80GB |
| `Gres=gpu:h100:8` | `h100` | NVIDIA H100 80GB |
| `Gres=gpu:geforcertx4090:8` | `geforcertx4090` | NVIDIA GeForce RTX 4090 |
| `Gres=gpu:A800:8` | `a800` | NVIDIA A800 80GB |

Magnus 提交 Job 时执行 `sbatch --gres=gpu:<value>:<count>`，如果 `value` 与 SLURM Gres 类型名不匹配，SLURM 无法调度 GPU 资源，Job 会永久 PENDING。

### 8.4 GPU 架构 → CUDA 版本 → 容器镜像

| GPU | 架构 | Compute Capability | 推荐镜像 |
|-----|------|-------------------|---------|
| A100 | Ampere | sm_80 | `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime` |
| A800 | Ampere | sm_80 | 同上 |
| H100/H800 | Hopper | sm_90 | `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime` |
| RTX 4090 | Ada Lovelace | sm_89 | `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime` |
| RTX 5090 | Blackwell | sm_120 | `pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime` |

> 在计算节点上 `nvidia-smi` 查看驱动版本。驱动版本需 ≥ 镜像 CUDA 版本（如 CUDA 12.8 需要 driver ≥ 570）。

---

## 九、第四步：构建与启动

### 9.1 安装依赖

```bash
cd /opt/magnus-new/back_end && uv sync
cd /opt/magnus-new/front_end && npm install
```

### 9.2 构建前端

```bash
cd /opt/magnus-new/front_end
MAGNUS_DELIVER=TRUE npm run build
```

### 9.3 手动启动验证

```bash
# 终端 1 — 后端
cd /opt/magnus-new/back_end
uv run -m server.main --deliver

# 终端 2 — 前端（端口与主站不同！）
cd /opt/magnus-new/front_end
MAGNUS_DELIVER=TRUE npm run start -- -p 3021 -H 0.0.0.0
```

**预期启动日志**：

```
✅ 系统依赖检查通过 (HPC (SLURM))
🔑 Admin: 本地模式，所有用户均为管理员
🏠 Created local user: ...
🚀 Scheduler loop started.
INFO:     Uvicorn running on http://127.0.0.1:8027
```

### 9.4 生产环境：systemd 服务

后端 `/etc/systemd/system/magnus-new-backend.service`：

```ini
[Unit]
Description=Magnus New Site Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/magnus-new/back_end
ExecStart=/root/.local/bin/uv run -m server.main --deliver
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

前端 `/etc/systemd/system/magnus-new-frontend.service`：

```ini
[Unit]
Description=Magnus New Site Frontend
After=network.target magnus-new-backend.service

[Service]
Type=simple
WorkingDirectory=/opt/magnus-new/front_end
ExecStart=/usr/bin/npm run start -- -p 3021 -H 0.0.0.0
Restart=on-failure
RestartSec=5
Environment=MAGNUS_DELIVER=TRUE

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now magnus-new-backend
systemctl enable --now magnus-new-frontend
```

---

## 十、第五步：验证

### 10.1 基础检查

```bash
# 健康检查（注意是新站点的后端端口）
curl http://10.0.0.50:8027/health
# 预期: {"status":"ok"}

# 集群资源
curl http://10.0.0.50:8027/api/cluster/stats
```

### 10.2 SDK 配置

```bash
# 添加新站点
magnus site add newsite http://10.0.0.50:3021
magnus site use newsite
magnus cluster
```

### 10.3 Job 验证

```bash
# CPU Job
magnus run test-cpu -- echo "new site deployment success"

# GPU Job（确认 GPU 类型正确）
magnus run test-gpu --gpu 1 --gpu-type a100 -- nvidia-smi
```

### 10.4 权限验证

```bash
# 确认主站的 token 不能访问新站点
# 用主站 site 的 token 请求新站点 API，预期返回 401
curl -H "Authorization: Bearer <主站token>" http://10.0.0.50:8027/api/cluster/stats
```

### 10.5 查看日志

```bash
journalctl -u magnus-new-backend -f
journalctl -u magnus-new-frontend -f
```

---

## 十一、主站与新站点的隔离边界

```
 主站 (团队 A)                          新站点 (团队 B)
 ─────────────────────────────────────────────────────────────
 前端 :3011                              前端 :3021    ← 不同端口
 后端 :8017                              后端 :8027    ← 不同端口
 数据 /data/magnus/                      数据 /data/magnus-new/  ← 不同目录
 认证 feishu App A                       认证 feishu App B       ← 不同应用
 管理员 ou_teamA_xxx                     管理员 ou_teamB_xxx     ← 不同人员
 JWT secret_key_A                        JWT secret_key_B       ← 不同密钥
 用户表 teamA_users                      用户表 teamB_users      ← 不同数据库
```

**互不感知**：主站用户无法通过主站 URL 访问新站点，反之亦然。前端入口不同、API 端口不同、JWT 互不信任。两个站点可以调度同一个 SLURM 集群的 GPU 资源（资源层面共享），但**管理层面完全隔离**。

---

## 十二、常见问题排查

### 启动失败：系统依赖缺失

```
❌ 系统依赖缺失（请安装后重启）:
  SLURM 调度: sbatch, squeue, scancel, sinfo, scontrol
```

**解决**：安装 `slurm-client`。无 SLURM 时改用 `execution.backend: local`。

### Job 永久 PENDING

1. `sinfo` 确认节点状态（非 drain/down）
2. `squeue` 查看排队情况
3. GPU Job：`sbatch --gres=gpu:<type>:1 test.sh` 手动测试 GRES 名

### GPU 提交报 400

```
gpu_type='a100' not available on this station
```

`cluster.gpus[].value` 与 SLURM Gres 名不一致。用 `scontrol show node --future | grep Gres` 核对。

### Job 跑到一半崩溃

```bash
magnus logs <job-id> --pages 3
```

常见原因：CUDA 版本不兼容、挂载路径不存在、OOM。

### 前端页面空白 / CORS 错误

检查 `cors_origins` 是否包含**新站点的实际 URL**（协议+IP+**新端口**）。

### Job 跑完了但状态还是 RUNNING

`magnus_address` 配错了（或容器内网络不通）。SLURM 模式下回调地址是 `{server.address}:{front_end_port}`，**这里的端口必须是新站点的端口**。

### 新站点用户数据泄露到主站

不会。每个站点有独立的 SQLite 数据库和独立的 JWT 密钥。即使是飞书模式，只要使用不同的飞书应用，用户记录就完全隔离。

---

## 十三、部署检查清单

### 信息采集
- [ ] GPU Gres 名已从 `scontrol show node` 确认
- [ ] GPU 型号/架构/数量已记录
- [ ] CPU 核数、内存大小已记录
- [ ] NFS/共享存储路径已确认
- [ ] 服务器 IP 已确认
- [ ] 目标端口已确认空闲

### 环境准备
- [ ] `sbatch squeue scancel sinfo scontrol apptainer git ffmpeg setfacl` 全部可用
- [ ] Node.js 20+ 已安装
- [ ] Python 3.14 已安装（`uv python find 3.14`）
- [ ] 数据目录已创建且有写权限

### 配置（逐项核对）
- [ ] **端口**：`front_end_port` / `back_end_port` **与主站不同**
- [ ] **认证**：`secret_key` 是**新生成的随机值**（不是从主站复制的）
- [ ] **飞书**（如果用）：使用的是**独立的飞书应用**，`admins` 是新站点管理员
- [ ] `server.address` — 服务器 IP
- [ ] `server.root` — 新站点专用数据目录
- [ ] `cluster.gpus[].value` — 与 SLURM Gres 名一致（小写）
- [ ] `cluster.gpus[].limit` — 不超过单节点 GPU 数
- [ ] `cluster.max_cpu_count` — 不超过实际 CPU 核数
- [ ] `cluster.max_memory_demand` — 不超过实际内存
- [ ] `cluster.default_container_image` — 与 GPU 架构匹配
- [ ] `cluster.default_system_entry_command` — 挂载路径实际存在
- [ ] `cors_origins` — 包含新站点的完整 URL（含新端口）

### 验证
- [ ] `/health` 返回 200
- [ ] 新站点前端可通过**新端口**正常访问
- [ ] 主站 token **不能**访问新站点 API
- [ ] `magnus cluster` 显示正确的 GPU 数量和型号
- [ ] CPU Job 提交→运行→完成 全流程正常
- [ ] GPU Job 提交→运行→完成 全流程正常
- [ ] Job 日志可正常查看
- [ ] systemd 开机自启已配置（生产环境）

---

## 十四、Windows 服务器部署（Local / Docker 模式）

Magnus **可以在 Windows 上运行**，但仅限于 **Local (Docker) 模式**。HPC (SLURM + Apptainer) 模式不可用——SLURM、Apptainer、cgroup、`setfacl` 都是 Linux 专属组件，在 Windows 上没有等价物。

Magnus 代码在 Local 模式下**显式处理了 Windows 兼容性**：

- [Docker 网络](c:\Users\27370\Desktop\project\magnus-main\back_end\server\_scheduler\_submit.py#L226-L232)：非 Linux 平台自动使用 `host.docker.internal` 替代 `--network host`
- [路径转换](c:\Users\27370\Desktop\project\magnus-main\back_end\server\_scheduler\_submit.py#L321-L322)：Windows 盘符 (`C:\...`) 自动转换为 Docker 兼容格式 (`/c/...`)
- [依赖检查](c:\Users\27370\Desktop\project\magnus-main\back_end\server\main.py#L99-L101)：Local 模式只检查 `docker` 和 `git`，不检查 SLURM/Apptainer

### 14.1 架构概览

```
┌─ Windows Server ─────────────────────────────────────────────┐
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐    │
│  │ 前端 :3021│  │ 后端 :8027│  │      Docker Desktop       │    │
│  │ Next.js  │  │ FastAPI  │  │        (WSL2 后端)        │    │
│  │          │  │          │  │                           │    │
│  │          │  │          │  │  ┌─────────────────────┐  │    │
│  │          │  │          │  │  │ WSL2 Linux 虚拟机    │  │    │
│  │          │  │          │  │  │                     │  │    │
│  │          │◄─┤          │◄─┤  │ ┌─────────────────┐ │  │    │
│  │          │  │          │  │  │ │ magnus-job-xxx  │ │  │    │
│  │          │  │  docker  │  │  │ │ (Linux 容器)    │ │  │    │
│  │          │  │  CLI ────┼──┼─┤ │                 │ │  │    │
│  │          │  │          │  │  │ │ CUDA → GPU 直通 │ │  │    │
│  │          │  │          │  │  │ └─────────────────┘ │  │    │
│  └──────────┘  └──────────┘  │  │                     │  │    │
│                              │  └─────────────────────┘  │    │
│  Job 回调:                   │                           │    │
│  host.docker.internal:8027 ──┘                           │    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

Local 模式下：
- **没有 SLURM**：Job 直接以 Docker 容器运行在本地
- **没有 Apptainer**：容器运行时是 Docker
- **没有 GPU 调度**：Docker `--gpus all` 直通所有 GPU，不做资源分配
- **网络**：容器通过 `host.docker.internal` 回调宿主机 Magnus 后端

### 14.2 前提条件

| 组件 | 版本要求 | 安装方式 |
|------|---------|---------|
| Docker Desktop | 最新稳定版 | [docker.com](https://www.docker.com/products/docker-desktop/) |
| WSL2 | 内核 5.10+ | `wsl --install`（Docker Desktop 安装时会提示） |
| Git | 2.40+ | [git-scm.com](https://git-scm.com/download/win) |
| Python (uv) | 3.14 | `pip install uv` 或下载 uv 二进制 |
| Node.js | 20 LTS | [nodejs.org](https://nodejs.org/) |
| NVIDIA 驱动 | ≥ 570（如需 GPU） | [nvidia.com](https://www.nvidia.com/download/) |

**验证安装**：

```powershell
# PowerShell
docker --version
wsl --version
git --version
uv --version
node --version

# GPU 可用性（如需 GPU）
docker run --rm --gpus all nvidia/cuda:12.4.0-runtime-ubuntu22.04 nvidia-smi
```

### 14.3 配置：Windows 专属差异

与 Linux HPC 部署相比，Windows 配置有**四项关键差异**：

```yaml
# configs/magnus_config.yaml (Windows 版)

server:
  address: http://192.168.1.200         # ★ Windows 服务器 IP
  front_end_port: 3021                  # ★ 与主站不同
  back_end_port: 8027                   # ★ 与主站不同

  root: C:/magnus-new                   # ★ Windows 路径（正斜杠）

  cors_origins:
    - http://192.168.1.200:3021
    - http://192.168.1.200:3023
    - http://localhost:3023

  database:                             # SQLite 数据库会自动创建在 root 下
    pool_size: 8
    max_overflow: 16
    pool_timeout: 10
    pool_recycle: 3600

  auth:
    provider: local                     # ★ Windows 只能用 local 认证
    jwt_signer:
      secret_key: <随机生成的 64 位十六进制密钥>
      algorithm: HS256
      expire_minutes: 10080

  scheduler:
    heartbeat_interval: 2
    snapshot_interval: 300

  service_proxy:
    max_concurrency: 1024

  file_custody:
    max_size: 10G
    max_file_size: 2G
    max_processes: 128
    default_ttl_minutes: 60
    max_ttl_minutes: 1440

execution:
  backend: local                        # ★ 必须是 local
  container_runtime: docker             # ★ 必须是 docker
  allow_root: true                      # Docker Desktop 默认 root 运行
  resource_cache:
    container_cache_size: 80G
    repo_cache_size: 20G

cluster:
  name: "Windows 本地集群"
  gpus: []                              # ★ Local 模式 GPU 配置可选

  max_cpu_count: 128                    # 填入宿主机的实际 CPU 逻辑核数
  max_memory_demand: 256G               # 填入宿主机的实际内存

  default_cpu_count: 4
  default_memory_demand: 4G
  default_runner: <当前 Windows 用户名>
  default_ephemeral_storage: 10G
  default_container_image: pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

  # ★ 关键：Windows 路径映射
  # system_entry_command 中的 bind mount 会经 Windows 盘符转换：
  #   host 侧: C:/magnus-new/workspace → /c/magnus-new/workspace
  #   container 侧: 保持 Linux 路径不变
  default_system_entry_command: ""
```

**四项关键差异总结**：

| 配置项 | Linux HPC | Windows Local | 原因 |
|--------|----------|---------------|------|
| `execution.backend` | `slurm` | `local` | Windows 无 SLURM |
| `auth.provider` | `feishu` 或 `local` | **仅 `local`** | 代码强制约束 |
| `server.root` | `/data/magnus-new` | `C:/magnus-new` | Windows 路径格式 |
| `default_system_entry_command` | `mounts=(...)` + NFS 挂载 | `""`（空） | 无 NFS，直接用本地磁盘 |

> `auth.provider` 在 `local` 模式下，Magnus 以当前 Windows 用户身份自动创建账户。所有能登录此 Windows 服务器的人都有 Magnus 权限。

### 14.4 部署步骤

#### Step 1：创建目录与拉取代码

```powershell
# PowerShell
mkdir C:\magnus-new\database, C:\magnus-new\workspace, C:\magnus-new\uv_cache, C:\magnus-new\file_custody -Force

git clone https://github.com/rise-agi/magnus.git C:\magnus-new\code
cd C:\magnus-new\code
```

#### Step 2：编写配置

将 14.3 节中的配置模板复制到 `C:\magnus-new\code\configs\magnus_config.yaml`，修改以下占位符：

- `server.address` → 实际 Windows 服务器 IP
- `server.root` → `C:/magnus-new`
- `cluster.default_runner` → 当前 Windows 用户名（`whoami`）
- `server.auth.jwt_signer.secret_key` → 随机生成

```powershell
# 生成随机 secret_key
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 3：安装依赖

```powershell
cd C:\magnus-new\code\back_end
uv sync

cd C:\magnus-new\code\front_end
npm install
```

#### Step 4：构建前端

```powershell
cd C:\magnus-new\code\front_end
$env:MAGNUS_CONFIG_PATH = "C:\magnus-new\code\configs\magnus_config.yaml"
$env:MAGNUS_DELIVER = "TRUE"
npm run build
```

#### Step 5：启动

```powershell
# 终端 1 — 后端（端口 8027）
cd C:\magnus-new\code\back_end
$env:MAGNUS_CONFIG_PATH = "C:\magnus-new\code\configs\magnus_config.yaml"
uv run -m server.main --deliver --config C:\magnus-new\code\configs\magnus_config.yaml

# 终端 2 — 前端（端口 3021）
cd C:\magnus-new\code\front_end
$env:MAGNUS_DELIVER = "TRUE"
npm run start -- -p 3021 -H 0.0.0.0
```

**预期启动日志**：

```
✅ 系统依赖检查通过 (LOCAL (Docker))
🔑 Admin: 本地模式，所有用户均为管理员
🏠 Created local user: YourName
🚀 Scheduler loop started.
INFO:     Uvicorn running on http://127.0.0.1:8027
```

注意日志中显示 `LOCAL (Docker)` 而非 `HPC (SLURM)`——说明进入了 Windows 兼容路径。

### 14.5 配置为 Windows 服务（开机自启）

Windows 没有 systemd，推荐使用 **nssm** (Non-Sucking Service Manager) 将 Magnus 注册为 Windows 服务。

#### 安装 nssm

```powershell
# 方式一：scoop
scoop install nssm

# 方式二：winget
winget install nssm

# 方式三：手动下载
# https://nssm.cc/download
```

#### 创建后端服务

```powershell
# 以管理员身份运行 PowerShell
$backendScript = @"
Set-Location C:\magnus-new\code\back_end
`$env:MAGNUS_CONFIG_PATH = "C:\magnus-new\code\configs\magnus_config.yaml"
uv run -m server.main --deliver --config C:\magnus-new\code\configs\magnus_config.yaml
"@

$backendScript | Out-File -FilePath C:\magnus-new\start-backend.ps1 -Encoding UTF8

nssm install magnus-new-backend powershell.exe "-ExecutionPolicy Bypass -File C:\magnus-new\start-backend.ps1"
nssm set magnus-new-backend AppDirectory C:\magnus-new\code\back_end
nssm set magnus-new-backend DisplayName "Magnus New Site Backend"
nssm set magnus-new-backend Start SERVICE_AUTO_START
nssm set magnus-new-backend AppRestartDelay 5000
```

#### 创建前端服务

```powershell
$frontendScript = @"
Set-Location C:\magnus-new\code\front_end
`$env:MAGNUS_DELIVER = "TRUE"
npm run start -- -p 3021 -H 0.0.0.0
"@

$frontendScript | Out-File -FilePath C:\magnus-new\start-frontend.ps1 -Encoding UTF8

nssm install magnus-new-frontend powershell.exe "-ExecutionPolicy Bypass -File C:\magnus-new\start-frontend.ps1"
nssm set magnus-new-frontend AppDirectory C:\magnus-new\code\front_end
nssm set magnus-new-frontend DisplayName "Magnus New Site Frontend"
nssm set magnus-new-frontend Start SERVICE_AUTO_START
nssm set magnus-new-frontend DependOnService magnus-new-backend
nssm set magnus-new-frontend AppRestartDelay 5000
```

#### 启动与管理

```powershell
nssm start magnus-new-backend
nssm start magnus-new-frontend

# 查看状态
nssm status magnus-new-backend
nssm status magnus-new-frontend

# 查看日志（服务运行失败时排查）
nssm get magnus-new-backend AppStdout
nssm get magnus-new-backend AppStderr

# 卸载服务
nssm remove magnus-new-frontend confirm
nssm remove magnus-new-backend confirm
```

### 14.6 GPU 支持

Docker Desktop + WSL2 支持 NVIDIA GPU 直通（需满足以下条件）：

1. **NVIDIA 驱动** ≥ 570（Windows 侧安装标准 Game Ready / Studio 驱动即可）
2. **WSL2 内核** ≥ 5.10
3. **Docker Desktop** 中启用 WSL2 后端

验证 GPU 可用：

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.0-runtime-ubuntu22.04 nvidia-smi
```

如果输出 GPU 信息，说明 GPU 直通正常。Magnus 提交 GPU Job 时，DockerManager 会自动添加 `--gpus all` 参数（[`_docker_manager.py:65-66`](c:\Users\27370\Desktop\project\magnus-main\back_end\server\_docker_manager.py#L65-L66)）。

**局限性**：

- Local 模式下 `--gpus all` 是全部或全无，不能按 Job 指定 GPU 数量或型号
- 所有 Job 共享全部 GPU，没有 SLURM 那样的资源隔离和排队
- 适合单用户或小型团队的开发测试环境

### 14.7 验证

```powershell
# 1. 健康检查
curl http://localhost:8027/health
# → {"status":"ok"}

# 2. 前端页面
# 浏览器打开 http://192.168.1.200:3021
# 应看到 Magnus 登录界面

# 3. 提交 CPU Job 测试
# 通过 Magnus SDK（从任意客户端配置新站点）
magnus site add win-site http://192.168.1.200:3021
magnus site use win-site
magnus run test-cpu -- echo "Windows deployment success"

# 4. 检查容器是否正常运行
docker ps
# 应看到 magnus-job-<uuid> 容器

# 5. 查看 Job 日志
magnus logs <job-id>
```

### 14.8 Windows 部署的限制

| 限制 | 说明 | 影响 |
|------|------|------|
| 无 SLURM | 没有作业队列和资源调度 | 多个 Job 同时运行会争抢资源 |
| 无 Apptainer | 只能用 Docker 镜像 | 不能用 `.sif` 文件 |
| 无 GPU 隔离 | `--gpus all` 全部直通 | 无法按 Job 分配特定 GPU |
| 无 `setfacl` | 无文件 ACL 控制 | 多用户共享文件时权限管理受限 |
| cgroup 指标受限 | Docker 指标采集器依赖 Linux cgroup | Windows 上 CPU/内存指标可能不准确或为空 |
| 仅 local 认证 | 无飞书登录 | 权限边界 = Windows 用户边界 |
| `--network host` 不可用 | Docker Desktop 不支持 host 网络 | 代码已自动适配 `host.docker.internal` |

### 14.9 Windows 部署检查清单

#### 环境准备
- [ ] Docker Desktop 已安装且 WSL2 后端正常运行
- [ ] `docker run --rm hello-world` 成功
- [ ] Git、uv (Python 3.14)、Node.js 20+ 已安装
- [ ] (GPU) `docker run --rm --gpus all nvidia/cuda:12.4.0-runtime-ubuntu22.04 nvidia-smi` 成功

#### 配置
- [ ] `execution.backend: local` （不是 `slurm`）
- [ ] `auth.provider: local` （Windows 不支持 feishu）
- [ ] `server.root` 使用 Windows 路径格式 （`C:/magnus-new`）
- [ ] `server.address` 是 Windows 服务器的实际 IP
- [ ] `server.front_end_port` / `back_end_port` 与主站不同
- [ ] `server.auth.jwt_signer.secret_key` 是随机生成的新值
- [ ] `cors_origins` 包含正确的 IP + 端口

#### 验证
- [ ] 后端启动日志显示 `LOCAL (Docker)` 而非 `HPC (SLURM)`
- [ ] `/health` 返回 200
- [ ] 前端页面可通过新端口在浏览器中访问
- [ ] CPU Job 提交→运行→完成 全流程正常
- [ ] (GPU) GPU Job 可正常运行 `nvidia-smi`
- [ ] nssm 服务已配置且开机自启（生产环境）
