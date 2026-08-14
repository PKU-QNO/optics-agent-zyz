---
name: magnus-submit
description: Magnus 集群（gustation.phybench.cn）作业提交与监控——用 Python `magnus` SDK 走「save blueprint → launch → monitor」链路，显式声明资源（CPU/内存/临时盘/优先级），SSH 直放挂载路径分发输入文件，COMSOL 批处理 + Parasolid 内核库处理。Use when 要提交/监控/排障一个 Magnus 集群作业（COMSOL batch、训练、任意 blueprint job），或要判断该走空白任务还是 blueprint 提交、要声明多少资源、要绕过 FileSecret 用挂载路径、要处理 ENOSPC/OOM/写文件被拦。
---

# Magnus Submit — 集群作业提交

> 从 zotero mie-f Fig.3 COMSOL 批处理 + PHY-LLM submit_sft.py 沉淀。
> 完整可跑示例见 `references/submit-pattern.md`。

## 1. 三种提交方式（关键区分，用错就白跑）

| 方式 | 行为 | 结论 |
|------|------|------|
| **空白任务提交**（CLI 不带资源） | CLI 忽略资源参数，记录成默认 A2 未启动 | ❌ 禁用 |
| **save blueprint** | 只把 blueprint 定义保存到服务器 | 定义，非跑 job |
| **save → launch blueprint** | 保存定义 → wait 2s → launch（args 显式资源）→ monitor | ✅ 唯一正确方式 |

## 2. Python magnus SDK 流程

```python
import magnus
magnus.configure(address=MAGNUS_ADDRESS, token=MAGNUS_TOKEN)   # token 只经环境变量/配置传入，不写落盘
# 1. 读 blueprint 文件（.magnus），blueprint_id = 文件名去后缀
magnus.save_blueprint(blueprint_id=bp_id, title=..., description=..., code=blueprint_code)
# 2. 显式资源 args 启动
job_id = magnus.launch_blueprint(bp_id, args={
    "gpu_count": 0, "gpu_type": "cpu", "cpu_count": 64,
    "memory_demand": "900G", "ephemeral_storage": "1024G", "priority": "B2",
    # ... 其他 blueprint 自定义参数
})
# 3. 监控 + 取结果
magnus.get_job(job_id)  # status == "Success" 才取 result
magnus.get_job_result(job_id)
```

## 3. 资源声明（args 显式，别信默认）

| 参数 | 含义 | mie-f 实例 |
|------|------|-----------|
| `gpu_count` / `gpu_type` | GPU 数 / 型号（a100 或 cpu） | 0 / cpu（电磁散射纯 CPU） |
| `cpu_count` | CPU 核数 | 64（128 核集群） |
| `memory_demand` | 内存 | 900G（FEM 0.3 网格）/ 128G（BEM） |
| `ephemeral_storage` | 临时盘 | 1024G（**必须显式声明，否则 ENOSPC**） |
| `priority` | A1/A2/B1/B2（依次降低） | B2 |

> **ENOSPC 教训**：临时盘声明不足时，solver 扫到 50% 报 "No space left"——临时盘要显式给大，不是自动分配。

## 4. SSH 直放挂载路径（绕开 FileSecret）

- 集群 32 个成功 COMSOL job 全走挂载路径，不用 magnus receive（comsol-runtime 镜像 baked 旧 SDK 与平台新 SDK 冲突 → receive 不可用）。
- 输入文件放 `/data/public/<user>/...`，job 里用绝对路径读。已验证：job 能读 `/data/public` 挂载内容。
- Parasolid 几何内核 `libpskernel.so`（87MB，从 COMSOL 6.2 官方 ISO 提取）也放 `/data/public/.../libs/` 供 job 加载。

## 5. 红线（不可违反）

1. **不刷新/重启 comsol-runtime docker**（ssh 注入的，刷新即不可恢复）。
2. **不提交 >256G 单任务 / GPU / A 类 job**（默认 CPU/B 类；单任务 ≤256G，总量 973G/128 核）。
3. **token/license 不写任何落盘文件**——只经环境变量传给进程。
4. 提交前先估算 DOF → 内存（FEM 直接求解器 O(DOF^1.5)），再定 `memory_demand`，别拍脑袋。

## 6. 关键坑（都踩过）

1. **Git Bash 路径转换**：远端 `/data/public/...` 被转成 `C:/Program Files/Git/data/...` → 用 `MSYS_NO_PATHCONV=1`。
2. **SSL 环境变量**：`SSL_CERT_FILE` 是 Git Bash 格式 `/c/...`，Python 不认 → `unset SSL_CERT_FILE REQUESTS_CA_BUNDLE CURL_CA_BUNDLE`。
3. **写文件被安全沙箱拦**（COMSOL 侧）：`PrintWriter` 写 CSV 失败 → `comsol.prefs` 设 `security.external.filepermission=full`。
4. **HOME 只读**：集群 `$HOME=/magnus` 只读 → `export HOME=/home/magnus`。
5. **空白任务提交**：CLI 忽略资源 → 记成默认 A2 未启动，白等。必须走 blueprint launch。

## 7. references

- `references/submit-pattern.md` — 完整 submit_sft.py 派生的可跑示例（save → launch → monitor → 取 result）
