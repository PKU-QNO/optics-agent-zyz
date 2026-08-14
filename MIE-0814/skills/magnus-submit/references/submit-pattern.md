# Magnus 提交可跑示例（submit_sft.py 派生精简版）

> 源：`PHY-LLM-Basic-Algorithm/train_zyz/submit_sft.py`。这是「save blueprint → wait → launch → monitor → 取 result」的标准骨架，改 CONFIG 段即可复用。

```python
import argparse, os, sys, time
import magnus

# ===== CONFIG —— 只改这里 =====
MAGNUS_ADDRESS = "https://gustation.phybench.cn"     # 覆盖 --address
MAGNUS_TOKEN   = os.environ.get("MAGNUS_TOKEN", "")  # 永不写死落盘
BLUEPRINT_FILE = os.path.join("blueprints", "MyJob_zyz.magnus")

# 资源（显式，别信默认）
GPU_COUNT  = 0
GPU_TYPE   = "cpu"
CPU_COUNT  = 64
MEMORY     = "128G"
STORAGE    = "1024G"     # ephemeral_storage，必须显式，防 ENOSPC
PRIORITY   = "B2"

# blueprint 自定义参数（对应 .magnus 里的 {{param}}）
BP_ARGS = {
    "gpu_count": GPU_COUNT, "gpu_type": GPU_TYPE,
    "cpu_count": CPU_COUNT, "memory_demand": MEMORY,
    "ephemeral_storage": STORAGE, "priority": PRIORITY,
    # ... 其他自定义参数，如 model_path / output_dir / container_image
}
# =============================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--address", default=MAGNUS_ADDRESS)
    ap.add_argument("--token", default=MAGNUS_TOKEN)
    args = ap.parse_args()

    magnus.configure(address=args.address, token=args.token)

    # 1. save blueprint：blueprint_id = 文件名去后缀
    bp_id = os.path.splitext(os.path.basename(BLUEPRINT_FILE))[0]
    with open(BLUEPRINT_FILE, encoding="utf-8") as f:
        code = f.read()
    try:
        magnus.save_blueprint(blueprint_id=bp_id, title=bp_id,
                              description=f"synced from {BLUEPRINT_FILE}", code=code)
    except Exception as e:
        print(f"save 返回 {e}，继续用服务器已有版本")

    # 2. wait（blueprint 传播，GitHub CDN 场景 wait 10s；一般 2s 够）
    time.sleep(2)

    # 3. launch（显式 args）
    job_id = magnus.launch_blueprint(bp_id, args=BP_ARGS)
    print("Job ID:", job_id)

    # 4. monitor（poll）
    while True:
        job = magnus.get_job(job_id)
        st = job.get("status")
        print("status:", st)
        if st in ("Success", "Failed", "Cancelled"):
            break
        time.sleep(60)

    # 5. 取 result（Success 才取）
    if job.get("status") == "Success":
        try:
            result = magnus.get_job_result(job_id)
            print("result:", str(result)[:200])
        except Exception as e:
            print("result 获取失败:", e)

if __name__ == "__main__":
    main()
```

## 排障速查

| 症状 | 根因 | 修 |
|------|------|----|
| 任务启动但资源不对 / 记成默认 A2 | 空白任务提交，CLI 忽略资源 | 走 save→launch，args 显式 |
| solver 扫到一半 "No space left" | ephemeral_storage 没显式声明 | 声明大临时盘（如 1024G） |
| 远端路径被转成 `C:/Program Files/Git/...` | Git Bash path conversion | `MSYS_NO_PATHCONV=1` |
| Python 报 SSL 证书错 | SSL_CERT_FILE 是 Git Bash 格式 | `unset SSL_CERT_FILE REQUESTS_CA_BUNDLE CURL_CA_BUNDLE` |
| 写文件被拦（COMSOL 内） | 安全沙箱 | comsol.prefs `security.external.filepermission=full` |
| COMSOL 几何内核报缺 libpskernel.so | Parasolid 内核库缺 | 从 COMSOL 官方 ISO 提取放 /data/public/.../libs/ |
| OOM | 内存估少了 | 先估 DOF→内存再定 memory_demand；BEM 用表面 DOF 估算 |

## 红线速记

- 不刷新/重启 comsol-runtime docker（ssh 注入，刷新即不可恢复）
- 不提交 >256G 单任务 / GPU / A 类 job
- token/license 不写任何落盘文件
