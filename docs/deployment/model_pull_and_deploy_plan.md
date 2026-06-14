# DeepSeek-R1-Distill-Qwen-7B：ModelScope 拉取与 Magnus GU Service 部署计划

> 本文档只给出代码与计划，不执行任何下载、构建或部署命令。所有新增文件位于 `project/optics_agent/` 下，未修改 `project/train/`。

## 1. 目标与约束

### 目标

将 `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` 从 ModelScope 拉取到 Magnus GU 站持久存储 `/data/`，并以 Magnus Service 形式部署为 OpenAI 兼容 API 服务。

### 关键约束

- 不修改 `project/train/` 下任何文件。
- 只读取 `project/train/tools/download_model_auto.py` 作为参考。
- 下载脚本迁移到 `project/optics_agent/python/download_model_auto.py`。
- 所有新增文件放在 `project/optics_agent/` 下。
- 本轮不运行任何代码。

## 2. 已创建文件

```text
project/optics_agent/python/download_model_auto.py
project/optics_agent/python/deploy_service.py
project/optics_agent/python/service_config.json
project/optics_agent/model_pull_and_deploy_plan.md
```

## 3. 模型拉取方案

### 3.1 下载来源

- ModelScope 页面：`https://modelscope.cn/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- ModelScope SDK 模型 ID：`deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- SDK：`modelscope.snapshot_download`

### 3.2 持久存储路径

下载脚本默认将模型保存到：

```text
/data/$USER/models/DeepSeek-R1-Distill-Qwen-7B
```

缓存默认放到：

```text
/data/$USER/.cache/modelscope
/data/$USER/.cache/huggingface
```

这样避免把大模型权重写入 Magnus job 的临时盘。

### 3.3 下载脚本特性

`python/download_model_auto.py` 包含：

1. 通过 Magnus SDK 提交 CPU 下载 Job。
2. GU 地址默认 `https://gustation.phybench.cn`。
3. 模型 ID 默认 `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`。
4. 使用 `/data/` 下的持久目录保存模型和缓存。
5. 使用 `snapshot_download(..., local_dir=...)`，保留中间文件以支持断点续传。
6. 失败自动重试，默认 5 次，指数式增加等待时间。
7. 下载完成后检查 `config.json` 和权重文件是否存在。

### 3.4 未来实际执行命令（本轮不执行）

```bash
export MAGNUS_ADDRESS=https://gustation.phybench.cn
export MAGNUS_TOKEN='<your-token>'
python project/optics_agent/python/download_model_auto.py
```

可选参数：

```bash
python project/optics_agent/python/download_model_auto.py \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --target-root /data \
  --cpu-count 8 \
  --memory-demand 32G \
  --max-retries 5 \
  --max-workers 8
```

## 4. Magnus Service 部署方案

### 4.1 Magnus Services 机制摘要

根据 `references/services.md`：

- Service 是一个长期 HTTP endpoint 配置，本质上按需 revive 一个 Magnus Job。
- 外部访问 `/api/services/{service_id}/{path}` 时，Magnus 后端会启动或复用对应 Job。
- Job 必须监听环境变量 `$MAGNUS_PORT` 指定的端口。
- 服务最好提供 `/health`；llama.cpp server 通常可对非 5xx health 检查通过。
- `POST /api/services` 是 create/update/upsert。
- 新建 Service 会被后端强制设为 inactive，因此创建后需要再次 POST 同一配置启用。
- `idle_timeout=0` 表示不自动缩容。

### 4.2 推理框架选择

推荐使用 **llama.cpp server**，原因：

1. 纯 CPU 推理路径成熟，适合 `gpu_count=0`。
2. 提供 OpenAI 兼容接口，例如 `/v1/chat/completions`。
3. 相比 vLLM CPU 模式，部署依赖更轻、对 CPU-only 环境更稳。
4. 支持连续批处理和多并发参数：`--parallel`, `--cont-batching`。

注意：llama.cpp 最佳输入是 GGUF。`service_config.json` 的 `entry_command` 设计为：

1. 检查 `/data/$USER/models/DeepSeek-R1-Distill-Qwen-7B/config.json`。
2. 在 `/data/$USER/apps/llama.cpp` 构建 llama.cpp。
3. 首次服务启动时将 safetensors 转换为 f16 GGUF。
4. 再量化为 Q4_K_M GGUF。
5. 后续启动复用 `/data/$USER/models/DeepSeek-R1-Distill-Qwen-7B-GGUF/deepseek-r1-distill-qwen-7b-q4_k_m.gguf`。
6. 启动 `llama-server` 并监听 `$MAGNUS_PORT`。

### 4.3 Service 资源规格

配置文件采用：

```json
{
  "gpu_count": 0,
  "gpu_type": "cpu",
  "cpu_count": 32,
  "memory_demand": "256G",
  "max_concurrency": 50,
  "request_timeout": 900,
  "idle_timeout": 0
}
```

#### 内存估算

以 llama.cpp + Q4_K_M GGUF 为基础：

- 7B Q4_K_M 权重：约 4.5–5.5 GB。
- llama.cpp runtime / mmap / tokenizer / graph buffer：约 4–12 GB，视构建和上下文而定。
- KV cache：取决于上下文长度、层数、隐藏维度和并发槽位。`--ctx-size 4096 --parallel 50` 在最坏情况下会显著增加内存占用。
- 50 并发并不等于 50 个长上下文请求同时满载；若全部满上下文，CPU 服务延迟会非常高。

因此选择 `256G` 作为保守规格：

- 能覆盖权重 + GGUF 转换/量化临时开销。
- 给 50 并发的 KV cache 和运行时留足空间。
- 避免因首次转换和服务启动同时发生而 OOM。

如果 GU 节点资源紧张，可以后续降档测试：

- `memory_demand=128G`
- `--ctx-size 2048`
- `--parallel 16` 或 `--parallel 32`

但与“最大支持 50 并发”的目标相比，当前 `256G` 更稳。

### 4.4 Service 关键字段

`python/service_config.json` 中主要字段：

- `id`: `deepseek-r1-distill-qwen-7b-cpu`
- `entry_command`: 构建/转换/量化/启动 llama.cpp server，监听 `$MAGNUS_PORT`
- `container_image`: `python:3.11-bookworm`
- `max_concurrency`: `50`
- `request_timeout`: `900`
- `idle_timeout`: `0`
- `gpu_count`: `0`
- `cpu_count`: `32`
- `memory_demand`: `256G`

## 5. Service 创建代码

`python/deploy_service.py` 通过 raw HTTP API 操作 GU：

1. `GET /api/services` 搜索服务 ID。
2. 若服务已存在且配置相同：跳过。
3. 若服务已存在但配置不同：`DELETE /api/services/{service_id}` 删除后重建。
4. `POST /api/services` 创建 Service。
5. 再次 `POST /api/services`，解决新建时强制 inactive 的坑，确保 `is_active=true`。
6. 请求使用 `requests(..., verify=False)`。

### 5.1 未来实际执行命令（本轮不执行）

```bash
export MAGNUS_ADDRESS=https://gustation.phybench.cn
export MAGNUS_TOKEN='<your-token>'
python project/optics_agent/python/deploy_service.py \
  --config project/optics_agent/python/service_config.json
```

可先 dry-run：

```bash
python project/optics_agent/python/deploy_service.py \
  --config project/optics_agent/python/service_config.json \
  --dry-run
```

## 6. 服务调用与验证步骤

部署完成后，首次请求会触发 Service revive。由于首次启动可能包含 llama.cpp 编译、GGUF 转换和量化，冷启动耗时可能很长。建议第一次触发后观察 job logs。

### 6.1 健康检查

```bash
curl -k \
  -H "Authorization: Bearer $MAGNUS_TOKEN" \
  "$MAGNUS_ADDRESS/api/services/deepseek-r1-distill-qwen-7b-cpu/health"
```

如果 `/health` 返回非 5xx，Magnus readiness 通常可继续通过。

### 6.2 OpenAI 兼容模型列表

```bash
curl -k \
  -H "Authorization: Bearer $MAGNUS_TOKEN" \
  "$MAGNUS_ADDRESS/api/services/deepseek-r1-distill-qwen-7b-cpu/v1/models"
```

### 6.3 Chat Completions 测试

```bash
curl -k \
  -H "Authorization: Bearer $MAGNUS_TOKEN" \
  -H "Content-Type: application/json" \
  "$MAGNUS_ADDRESS/api/services/deepseek-r1-distill-qwen-7b-cpu/v1/chat/completions" \
  -d '{
    "model": "deepseek-r1-distill-qwen-7b",
    "messages": [
      {"role": "user", "content": "用一句话介绍你自己。"}
    ],
    "temperature": 0.6,
    "max_tokens": 128
  }'
```

## 7. 资源监控建议

### 7.1 启动阶段

重点观察：

- llama.cpp clone/build 是否成功。
- `convert_hf_to_gguf.py` 是否支持该模型结构。
- 量化是否成功生成 Q4_K_M 文件。
- `llama-server` 是否监听 `$MAGNUS_PORT`。
- Service job 是否进入 RUNNING。

### 7.2 运行阶段

重点观察：

- 内存峰值：确认 256G 是否充足，是否可降到 128G。
- CPU 利用率：32 核是否跑满。
- 首 token latency 和 tokens/s。
- 50 并发下排队情况、429/503 错误比例。
- Magnus `request_timeout=900` 是否足够覆盖长请求。

### 7.3 压测建议

逐步压测，不要直接打满 50 并发：

1. 单请求短输出。
2. 5 并发，`max_tokens=128`。
3. 10 并发，`max_tokens=256`。
4. 25 并发。
5. 50 并发。

每级记录：

- 成功率。
- P50/P95/P99 延迟。
- tokens/s。
- 内存峰值。
- CPU 利用率。

## 8. 风险与备选方案

### 8.1 llama.cpp 转换兼容性

风险：当前 llama.cpp 的转换脚本可能对 Qwen/DeepSeek distill 模型结构或 tokenizer 有版本要求。

应对：

- 保持 llama.cpp 使用最新 main 分支。
- 若转换失败，改用预转换 GGUF 模型，或单独创建 GGUF 转换 job。

### 8.2 50 并发 CPU 推理性能

风险：CPU-only 7B 50 并发可以“接入”，但吞吐和延迟可能不理想。

应对：

- 限制每请求 `max_tokens`。
- 降低 `--ctx-size`。
- 将 `--parallel` 从 50 降到 16/32，并在 Magnus 层保留 `max_concurrency=50` 作为排队上限。
- 若性能不能接受，改用 GPU vLLM 或 llama.cpp CUDA。

### 8.3 首次服务启动过慢

风险：Service 第一次被调用时才编译/转换/量化，可能超过 `request_timeout`。

应对：

- 先通过一次请求触发冷启动，然后看 job logs。
- 更稳的做法是把 GGUF 转换/量化拆成独立 Magnus job，提前生成 GGUF，再让 Service 只负责启动 server。

## 9. 推荐执行顺序（未来）

1. 确认 GU token 可用。
2. 提交模型下载 job：运行 `python/download_model_auto.py`。
3. 等待下载 job 成功，确认 `/data/$USER/models/DeepSeek-R1-Distill-Qwen-7B` 存在。
4. dry-run 检查 service 配置。
5. 运行 `deploy_service.py` 创建/更新 Service。
6. 调 `/health` 触发冷启动。
7. 查看 Service job 日志，等待 llama.cpp 构建和 GGUF 转换完成。
8. 调 `/v1/models` 和 `/v1/chat/completions` 验证。
9. 做逐级并发压测，必要时调小上下文或并行槽位。
