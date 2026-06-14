# git.pku.edu.cn Docker Registry 推送故障报告

## 基本信息

| 项 | 值 |
|---|---|
| 服务器 | `git.pku.edu.cn` |
| 实际平台 | **Gitea 1.22.0**（非 GitLab，前端伪装为 GitLab 界面） |
| Registry API | Docker Distribution API v2 |
| 测试仓库 | `2200011363/sft-base` |
| PAT Token | 已配置并有 push 权限 |

## 故障现象

`docker push` 到 `git.pku.edu.cn/2200011363/sft-base:v4` 返回：

```
unknown: unexpected status from POST request to
https://git.pku.edu.cn/v2/2200011363/sft-base/blobs/uploads/: 413 Request Entity Too Large
```

## 诊断结果

| 测试 | 结果 | 结论 |
|------|------|------|
| `docker login` | ✅ 成功 | 认证正常 |
| `docker push alpine:latest`（7MB） | ❌ **413** | 不是镜像体积问题 |
| `docker push v4`（2.1GB） | ❌ **413** | 同样错误 |
| `GET /v2/` | ✅ 200 | Registry 服务在线 |
| `GET /v2/token` | ✅ 200 | Token 签发正常 |
| `POST /blobs/uploads/`（curl） | ⚠️ 401→跳转→**413** | 上传端点直接返回 413 |
| `api/v1/version` | ✅ 200 | Gitea 1.22.0 |
| `api/v1/settings/attachment` | ✅ max_size=2048MB | 附件上传限制 2GB（正常） |

## 根因分析

**413 发生在 blob upload 端点，且 7MB 的 alpine 镜像同样失败**，说明不是磁盘配额或镜像大小问题，而是 **Gitea 前置的 nginx 反向代理对 /v2/ 路径的 `client_max_body_size` 设置过小**。

具体技术细节：

```
Gitea 前置 nginx → client_max_body_size 过小
     ↓
POST /v2/<repo>/blobs/uploads/ 时请求体被 nginx 拦截
     ↓
返回 413 Request Entity Too Large
```

Gitea 本身 Container Registry 的 blob upload 没有问题，是 nginx 层在 /v2/ 路径上限制了上传大小。当前 `client_max_body_size` 很可能小于 1MB（7MB 镜像都失败），需要管理员调整。

## 修复要求

请管理员在 nginx 配置中为 Container Registry 的 `/v2/` 路径设置充足的 `client_max_body_size`，例如：

```nginx
location /v2/ {
    client_max_body_size 10g;
    proxy_pass http://gitea:3000;
}
```

或者全局设置：

```nginx
client_max_body_size 10g;
```

## Docker Registry 的实际工作流

理解为什么需要大 body：

1. `POST /v2/<repo>/blobs/uploads/` — 启动上传会话（可能包含起始数据块）
2. `PATCH /v2/<repo>/blobs/uploads/<uuid>` — 上传实际 blob 数据（大 body）
3. `PUT /v2/<repo>/blobs/uploads/<uuid>?digest=<sha>` — 完成上传

对于 Container Registry，blob 上传的 body 大小等于镜像层的实际大小。一个镜像由多个 layer 组成，每个 layer 从几 KB 到几百 MB 不等。因此 nginx 不能限制 /v2/ 路径的 body 大小。

## 本地环境

| 项 | 值 |
|---|---|
| Docker Desktop | 运行正常 |
| Docker login | ✅ 已登录 git.pku.edu.cn |
| 本地镜像 | 已构建并推送到阿里云 ACR |
| 操作系统 | Windows 11 |
| 代理 | 127.0.0.1:7897（系统代理） |
## COMSOL Runtime Push Update - 2026-06-09

The validated COMSOL runtime image was retagged from Aliyun ACR to the PKU registry target:

```powershell
docker tag crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1 git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1
docker push git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1
```

The push failed with:

```text
The push refers to repository [git.pku.edu.cn/rise-agi/comsol-runtime]
unknown: unexpected status from POST request to https://git.pku.edu.cn/v2/rise-agi/comsol-runtime/blobs/uploads/: 413 Request Entity Too Large
```

COMSOL image details:

| Item | Value |
|---|---|
| ACR staging image | `crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1` |
| PKU target image | `git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1` |
| ACR digest | `sha256:1715c2f1d2929669325f2067650ce1a3efeca2ce2ab0dab873cfcc6dc2508671` |
| Local image size | `24.5GB` |
| Local validation | `comsol -version`, `comsol batch -help`, Python imports, and secret scan passed |

This confirms the COMSOL image is already valid and staged. The blocker is PKU registry upload acceptance. Please ask the administrator to:

1. Increase or disable the reverse-proxy request body limit for Docker Registry v2 paths, especially `/v2/`.
2. Confirm package/container registry quota for `Rise-AGI`.
3. Allocate at least `100GB`; `150GB` is safer for multiple COMSOL image tags.

Suggested nginx-side setting if PKU uses nginx in front of Gitea:

```nginx
location /v2/ {
    client_max_body_size 0;
    proxy_request_buffering off;
    proxy_pass http://gitea:3000;
}
```

If the administrator prefers a finite limit, use a value comfortably above the largest compressed layer, for example `50g`, plus enough backend registry storage quota.
