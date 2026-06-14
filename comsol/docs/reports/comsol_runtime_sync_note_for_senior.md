# COMSOL 镜像与 Magnus 蓝图同步笔记

更新时间：2026-06-10

## 一句话结论

COMSOL 在 Magnus/Gustation 上已经有一个能跑的 headless runtime 镜像了，当前实际使用的是管理员导入的本地镜像：

```text
docker://magnus-local/comsol-runtime:latest
```

这个镜像大小约 `1.38G`，不是我们最早自己构建并上传的 24.5GB/11GB archive 那条路线。管理员用了更轻量的方式把 COMSOL runtime 装进了 Magnus 本地镜像系统。现在最重要的原则是：不要刷新、覆盖、重新 pull、retag 或 rebuild 这个镜像，除非管理员明确要求。

## 给学长的短版

学长好，COMSOL 镜像这边现在进展如下：

1. COMSOL 6.3 headless runtime 已经在 Magnus 上可用，当前镜像是：

   ```text
   docker://magnus-local/comsol-runtime:latest
   ```

2. 这个镜像是管理员导入/构建到 Magnus 本地镜像系统里的，大小约 `1.38G`。它不是我们最开始计划推到 `git.pku.edu.cn` 或从 Docker archive 直接导入的那个大镜像。

3. 镜像已经通过几组实际 Magnus job 验证：

   - 能输出 COMSOL 版本：`COMSOL Multiphysics 6.3.0.290`
   - `comsol batch -help` 可用
   - Python 后处理依赖可 import
   - license mount 后可以求解
   - 一个 L-shaped membrane eigenmodes 示例已经跑通，特征值接近参考值

4. 我们已经把 Magnus 蓝图默认镜像更新为：

   ```text
   docker://magnus-local/comsol-runtime:latest
   ```

   蓝图 ID 是：

   ```text
   Optics_COMSOL_Runtime_zyz
   ```

5. 现在运行代码和 license 放在公共数据区：

   ```text
   /data/public/zhangyuanzheng/comsol-runtime
   /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
   ```

   结果输出默认写到：

   ```text
   /home/magnus/data/optics_agent/comsol/runs
   ```

6. 目前下一步不是再折腾镜像，而是基于这个现成镜像，把蓝图 runner 跑通，再补光学和流体两个 smoke case，确认它能支撑后续论文复现。

## 目前已经做完的事

### 1. 本地曾经构建过完整 COMSOL runtime 镜像

我们本地从 COMSOL 6.3 Linux 安装介质做过 headless Docker 镜像，目标是多用途 runtime，至少支持光学和流体方向。

当时镜像信息：

```text
ACR image:
crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1

Digest:
sha256:1715c2f1d2929669325f2067650ce1a3efeca2ce2ab0dab873cfcc6dc2508671

本地 Docker image size:
约 24.5GB
```

本地验证过：

```text
comsol -version
comsol batch -help
Python imports: numpy scipy pandas matplotlib h5py meshio mph jpype
runner env_check
```

这个路线证明了“COMSOL 可以被做成非 GUI Docker runtime”，但镜像比较大。

### 2. 推 PKU registry 遇到 413

原计划是把镜像推到：

```text
git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1
```

但 push 时遇到：

```text
413 Request Entity Too Large
```

失败 endpoint 是：

```text
https://git.pku.edu.cn/v2/rise-agi/comsol-runtime/blobs/uploads/
```

判断不是镜像坏了，而是 PKU registry 或前置代理对 Docker Registry v2 上传体积有限制。这个问题后来没有继续卡住我们，因为管理员走了另一条本地镜像导入路线。

### 3. 给管理员交接过一份 Docker archive

为了绕开 registry，我们把本地镜像导出成 archive，上传到了公共数据区：

```text
/data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar
```

校验信息：

```text
size: 11451059712 bytes
sha256: 33c8dfb5df07722143d043e653e72299f3ac0d9b9145ac9736818f16e1ea55a4
```

同时上传了：

```text
/data/public/zhangyuanzheng/README.md
/data/public/zhangyuanzheng/Optics_COMSOL_Runtime_zyz.magnus
/data/public/zhangyuanzheng/comsol-runtime-image-manifest.json
/data/public/zhangyuanzheng/comsol_blueprint_runtime_plan.md
/data/public/zhangyuanzheng/comsol-runtime/
```

这套 archive 现在主要作为 provenance/fallback 保留，不要拿它覆盖当前 active 镜像。

### 4. 管理员实际导入了更轻量的 active image

现在真正的 active image 是：

```text
docker://magnus-local/comsol-runtime:latest
```

它是管理员采用不同方式构建/导入的镜像，大小约 `1.38G`。这和我们最初 24.5GB 镜像明显不是同一形态。

这件事的好处是：

- Magnus 已经能直接识别这个本地镜像。
- 不依赖 `git.pku.edu.cn` registry。
- 不依赖阿里云 ACR。
- 镜像小很多，调度和缓存压力应该低很多。

需要注意的地方是：

- 这个镜像到底包含哪些 COMSOL 模块，需要继续通过具体 case 验证。
- 目前已验证 core batch 和 PDE/eigenmode 任务，不等于所有光学/流体模块都一定可用。
- 后续不要覆盖它，否则可能把管理员已经配好的轻量环境弄坏。

## 已验证 job

### 当前 active image 的验证

这些 job 使用的是当前真实 active image：

```text
docker://magnus-local/comsol-runtime:latest
```

| Job ID | 任务 | 状态 | 说明 |
|---|---|---|---|
| `de368ea77db7da7f` | `comsol-smoke-minimal` | Success | COMSOL 6.3.0.290、batch help、Python imports 都 OK |
| `deb10848cb99128a` | `comsol-universal-licensemount-solve` | Success | license 挂载后 solve 成功 |
| `3681f26d40ccbf7b` | `comsol-Lmembrane-eigenmodes` | Success | L-shaped membrane eigenmodes 求解成功，特征值接近参考 |

其中 `3681f26d40ccbf7b` 的日志里有一组特征值：

```text
9.643792200055644
15.197285124521734
19.73922125217245
29.521534394291308
31.922576407774837
41.4820467570536
```

参考第一特征值约：

```text
9.6397238
```

说明这个镜像不仅能启动 COMSOL，还能实际求解并输出合理结果。

### 早期 comparison jobs

下面几个 job 用的是早期对照镜像 `docker://simulation-runtime:latest`，不是现在 active image：

```text
973e8c9bd19298ad
909944d000b92a09
3cd1d9e8abac4115
```

它们说明早期 COMSOL runtime 方向是通的，但当前后续工作应以 `magnus-local/comsol-runtime:latest` 为准。

## 当前蓝图和运行目录

蓝图 ID：

```text
Optics_COMSOL_Runtime_zyz
```

本地蓝图文件：

```text
comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
```

服务器公共目录里的蓝图文件：

```text
/data/public/zhangyuanzheng/Optics_COMSOL_Runtime_zyz.magnus
```

蓝图默认镜像已经更新为：

```text
docker://magnus-local/comsol-runtime:latest
```

runtime code：

```text
/data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py
```

license：

```text
/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

输出目录：

```text
/home/magnus/data/optics_agent/comsol/runs
```

蓝图挂载：

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
```

## License 情况

license 当前放在：

```text
/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

权限已经设成：

```text
secrets/         700
secrets/comsol/  700
license.dat      600
```

注意：管理员测试 job 里也出现过容器内路径：

```text
/opt/comsol-license/license.dat
```

这说明管理员镜像/运行环境里可能有自己的 license mount 入口。我们当前蓝图默认走 `/data/public/zhangyuanzheng/.../license.dat`。如果后续蓝图 env_check 失败，优先检查 license 挂载路径是否和管理员镜像预期一致。

## 目前状态判断

我对当前状态的判断是：

1. COMSOL headless 跑起来了。
2. `comsol batch` 可用。
3. Python 后处理依赖可用。
4. license 挂载后能实际 solve。
5. 当前 active 镜像不是我们最初大镜像，而是管理员版轻量镜像。
6. 现在最重要的工作不是重做镜像，而是围绕这个 active 镜像把蓝图和 case 工作流稳定下来。

换句话说，现在已经过了“有没有 COMSOL Docker 可用”的阶段，进入了“如何把它变成稳定的论文复现后端”的阶段。

## 风险和注意事项

### 1. 不要覆盖管理员镜像

当前镜像：

```text
docker://magnus-local/comsol-runtime:latest
```

不要做这些操作：

```text
docker pull
docker push
docker tag 覆盖
docker load 覆盖
重新 build 替换
刷新 Magnus 镜像缓存
```

除非管理员明确说可以。

### 2. 模块覆盖范围还需要验证

现在通过的是 COMSOL core/PDE/eigenmode 类型任务。我们最初目标是多用途，至少覆盖：

- 光学
- 流体

但是 active image 只有 `1.38G`，比原始完整 runtime 小很多，所以不能默认认为所有光学和流体模块都在。下一步要用具体 case 验证：

- Wave Optics / RF / Ray Optics 相关最小 case
- Laminar Flow / CFD / Microfluidics 相关最小 case

### 3. 蓝图 runner 还需要正式 smoke 一次

管理员 job 已经验证了镜像本身能跑，但我们还需要用正式蓝图：

```text
Optics_COMSOL_Runtime_zyz
```

跑一次 `env_check`，确认：

- 蓝图参数没问题
- runner 路径没问题
- license 路径没问题
- 输出 manifest 能写到 `/home/magnus/data/...`

### 4. 原 archive 只作备份

原 archive 在：

```text
/data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar
```

不要主动让管理员 load 它覆盖当前镜像。它只是证明我们有一份本地构建过的完整镜像，以及在必要时作为 fallback。

## 下一步计划

### Step 1：用正式蓝图跑 env_check

目标：验证 `Optics_COMSOL_Runtime_zyz` 这一层也能跑通，而不只是管理员手写 job 能跑。

命令：

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode personal_storage --container-image docker://magnus-local/comsol-runtime:latest
```

预期输出：

```text
/home/magnus/data/optics_agent/comsol/runs/<run_id>/manifest.json
```

里面应包含：

```json
{
  "status": "completed",
  "comsol": {
    "version": "COMSOL Multiphysics 6.3.0.290"
  },
  "failure": null
}
```

### Step 2：补光学 smoke case

目标：确认 active image 对光学方向可用。

建议 case：

- 最小 2D waveguide
- 或简单 Helmholtz / Wave Optics frequency-domain 示例

要验证：

- 能 `comsol batch`
- 能输出 `.mph`
- 能导出关键数值或图表
- 能写 `manifest.json`

### Step 3：补流体 smoke case

目标：确认 active image 对流体方向可用。

建议 case：

- 最小 laminar flow
- 或 microfluidics channel flow

要验证：

- license 是否允许对应模块
- solver 能跑完
- 输出结果能被 runner 收集

### Step 4：稳定 case bundle 格式

后续论文复现时，最好每个 COMSOL case 都长这样：

```text
case/
  case.json
  model.java 或 model.mph 或 model.m
  postprocess.py   可选
```

提交后输出：

```text
runs/<run_id>/
  manifest.json
  command.json
  env_report.json
  raw/
  results/
  errors/
```

这样 agent 后续可以自动检查失败原因，也方便人工复核。

### Step 5：再封装 skill

这一步已经初步完成：项目本地 `.codex/skills/` 已经更新，新增了：

```text
optics-comsol-runtime
```

以后提到 COMSOL runtime、Magnus-local 镜像、license mount、蓝图提交时，会优先加载这个技能。

## 可以直接发给学长的结尾

总体来说，COMSOL 镜像现在已经不是“还没跑起来”的状态了。管理员已经在 Magnus 上放好了一个可用的本地 runtime 镜像，基础 batch 和求解都过了。我们现在要做的是：不要动这个镜像本体，基于它把蓝图、runner、光学/流体 smoke case 和后续论文复现工作流稳定下来。

我建议接下来优先跑一次正式蓝图 `env_check`，然后各补一个光学和流体最小案例。只要这三步过了，COMSOL 就可以作为 optics_agent 的正式仿真后端进入论文复现流程。
