# Magnus 技术交流 0604：对 optics_agent 有用的部分

更新日期：2026-06-12

来源文件：

```text
D:\Download\xwechat_files\wxid_kgunfixqi5yn22_fae1\msg\file\2026-06\Magnus技术交流-0604.pdf
```

## 一句话结论

这份文档大部分是在给多个项目组讲计算机系统、容器、云原生任务和平台抽象。对 optics_agent 真正有用的，不是这些通用科普，而是 Magnus 怎么把一次计算沉淀成：

```text
Image 负责环境可复现
Blueprint 负责可调用的工作流
Job 负责一次具体执行
Skill 负责领域知识沉淀
File custody 负责输入输出托管
```

所以我们现在的 COMSOL 镜像只是底座。下一阶段重点不应该继续折腾镜像，而是把 COMSOL runtime 接成稳定蓝图，再用 case/DSL/Skill 把论文复现、扫参和新问题探索沉淀下来。

## 对当前项目最有用的内容

### 1. Magnus 的五个一等公民

文档把 Magnus 收敛成五个核心对象：

```text
Blueprint
Job
Skill
Image
Service
```

对 optics_agent 的解释是：

- `Image`：把 COMSOL、Python 依赖、系统环境钉死，保证可复现。当前就是 `docker://magnus-local/comsol-runtime:latest`。
- `Blueprint`：公开、简洁、可审计的 typed Python 入口。它不应该塞 license、token、复杂业务代码。
- `Job`：一次真实运行，包含资源申请、排队、运行、成功/失败和产物。
- `Skill`：给人和 AI 读的领域知识包，用来减少下一次从零摸索。
- `Service`：长驻服务形态，目前对 COMSOL batch 不是主线。

对我们来说，路线应该是：

```text
COMSOL image
  -> COMSOL runtime blueprint
  -> paper/case runner
  -> reusable Skill
  -> DSL/schema for scientific tasks
```

### 2. Blueprint 是“表单”和“函数”的同一个东西

文档里最值得记住的一点：Blueprint 不是普通脚本，而是一个名为 `blueprint` 的 Python 函数，函数签名会被 Magnus 解析成 Web 表单；函数体里必须调用 `submit_job(...)`。

这对我们写蓝图有两个要求：

- 蓝图要简洁，公开可读，只暴露参数和 `submit_job`。
- 私有内容放到服务器个人/公共存储的代码文件夹里，例如 `/data/public/zhangyuanzheng/comsol-runtime`，license 放长期挂载路径。

参数设计上，Magnus 会根据类型生成 UI：

```text
bool -> switch
int/float -> number input
str -> text input
Literal[...] -> dropdown
FileSecret -> file upload
Annotated[...] -> label/description/min/max/options 等元数据
```

这说明我们后续写蓝图时，要把 AI 需要决策的内容显式做成 typed 参数，例如：

```text
run_mode
domain_preset
case_bundle
license_mode
cpu_count
memory_demand
ephemeral_storage
```

### 3. Job 生命周期可以直接用于排障

Magnus Job 的主链路是：

```text
Preparing -> Pending -> Queued -> Running -> Success / Failed
```

还有两条重要岔路：

```text
Paused      被高优先级任务抢占，资源释放后可自动重新排队
Terminated  用户取消，资源释放后才是真正结束
```

排障时可以这样理解：

- 卡在 `Preparing`：通常看镜像、代码 clone、工作目录、挂载、文件准备。
- 卡在 `Pending`：Magnus 已准备好，下一步是提交到 SLURM/Docker 后端。
- 卡在 `Queued`：后端已经接受，主要看资源是否够、队列是否繁忙。
- `Running` 后失败：看 runner 日志、license、COMSOL exit code、输出文件是否生成。
- `Success` 不只看后端退出码，还可能依赖工作目录里的 `.magnus_success` marker。
- `Paused`/`Terminated` 如果还带 backend job id，说明远端资源可能还在释放，不能立刻当成完全终态。

这对 COMSOL 特别重要，因为 COMSOL job 经常大内存、长运行，失败不一定是代码错，也可能是 license、内存、ephemeral storage、队列抢占或输出 contract 没写对。

### 4. 调度优先级要保守使用

文档说明 Magnus 调度大致是：

```text
A1 > A2 > B1 > B2
```

A 类任务可以抢占 B 类任务；被抢占的 job 会进入 `Paused` 并等待自动重排。调度还会使用类似 EASY backfill 的策略，让不影响队头任务的小任务先跑。

对 optics_agent 的实际原则：

- COMSOL env check、smoke test 默认用 `B2`。
- 大型复现或扫参才考虑更高资源，但需要明确说明。
- 不要随手发 A 类任务，尤其不要让 AI 自动发 A 类大任务。
- 如果 job 被 `Paused`，不必第一反应当失败；先看是否被抢占和是否会自动恢复。

### 5. Image 在集群和本地是同一个抽象，两套后端

文档里说 Magnus 的 `Image` 在集群模式下对应 Apptainer `.sif`，在 local 模式下对应 Docker image。集群运行时会做隔离、临时可写层、镜像缓存和 LRU 淘汰。

这对当前项目的提醒是：

- `docker://magnus-local/comsol-runtime:latest` 是管理员导入后的 Magnus 可见镜像，不要在本地按普通 Docker registry 思维去刷新它。
- 镜像是可复现环境底座，不是实验逻辑本身。
- 如果作业突然因为镜像不可用失败，优先看 Magnus 侧镜像缓存/导入状态，而不是重新构建本地 Docker。

### 6. 文件托管和 secret 要分层

文档提到 Magnus 有 file custody：用户上传文件和 job 产物会用 token 寻址，有下载能力和 TTL。Web 侧走 JWT，SDK/agent 侧走 trust token，授权大致是：

```text
is_admin OR is_owner OR is_ancestor
```

对我们来说：

- 蓝图内容是公开/可审计的，不放 license、token、SSH key。
- license 走长期挂载路径，不依赖临时上传 token。
- Job 输出要写到 `/home/magnus/data/optics_agent/comsol/runs/...` 这种 Magnus job 可写区域。
- 需要临时输入包时再用 `FileSecret`，但长期运行依赖的 runtime 代码和 license 应该放稳定路径。

### 7. AI4Science 的关键不是复现，而是可前进的引擎

文档后面有一段很贴近我们组会讨论：论文复现不应该是终点，而应该是向后兼容测试；真正目标是做一个向前兼容的计算引擎。

翻译成 optics_agent 的话：

```text
复现论文 = 回归测试
Blueprint = 可复用计算引擎的接口
Skill = 人和 AI 共享的项目记忆
case/DSL = 科学问题的机器可读表达
扫参/验证 = 从复现走向发现的桥
```

所以一个好蓝图不应该只复现某一篇论文的某一张图，而应该逐渐覆盖一类问题，例如 waveguide、metasurface、cavity、scattering、microfluidics 等。

## 可以忽略或少看的部分

这份 PDF 里有不少内容对 optics_agent 当前阶段帮助不大：

- 汇编、CPU、进程、状态机的基础科普。
- Docker/Apptainer 的通用教学。
- 面向所有项目组的宏观叙事。
- 不直接影响 COMSOL 蓝图、Magnus 作业、文件存储、技能沉淀的理论铺垫。

这些内容作为背景可以理解，但不需要写进项目技能，也不需要成为当前实现任务。

## 对 COMSOL 蓝图的直接改进方向

当前 active image：

```text
docker://magnus-local/comsol-runtime:latest
```

当前重要路径：

```text
runtime: /data/public/zhangyuanzheng/comsol-runtime
license: /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
output:  /home/magnus/data/optics_agent/comsol/runs
```

下一步蓝图应该更像一个稳定接口，而不是一个“大脚本”：

```text
blueprint(...)
  -> submit_job(
       image="docker://magnus-local/comsol-runtime:latest",
       command="python /data/public/.../comsol_runner.py ...",
       mounts=[runtime, output],
       resources={cpu, memory, storage, priority},
     )
```

runner 和 case 逻辑放在代码文件夹里，蓝图只保留：

- 输入参数
- 资源需求
- 镜像选择
- 挂载路径
- 运行命令
- 输出摘要

这样蓝图公开也没关系，真正敏感的 license 和可迭代的业务代码都在服务器存储里。

## 给后续工作的 checklist

- 不刷新、不覆盖 `docker://magnus-local/comsol-runtime:latest`，除非用户或管理员明确要求。
- COMSOL smoke/env check 默认 `B2`，不要自动发 A 类任务。
- 查 job 时按 `Preparing/Pending/Queued/Running/Paused/Success/Failed/Terminated` 判断问题层级。
- 蓝图只写 typed 参数和 `submit_job`，不要把 license、token、长逻辑塞进去。
- case、sweep、postprocess 逐步沉淀成 DSL/schema。
- 每次论文复现都要反过来问：这次能不能抽象成下一篇论文也能用的蓝图能力？

