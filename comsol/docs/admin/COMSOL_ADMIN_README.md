# COMSOL Runtime Magnus Admin Handoff

Staging directory:

```text
/data/public/zhangyuanzheng
```

This directory contains the original COMSOL 6.3 headless Docker image archive,
the Magnus blueprint, and the runtime code folder used by the blueprint.

Important current status:

```text
Active Magnus image: docker://magnus-local/comsol-runtime:latest
Reported size: 1.38G
Status: administrator-imported local image, not pulled from git.pku.edu.cn
Policy: do not refresh, pull, overwrite, retag, or rebuild this image unless the administrator explicitly asks for it
```

The administrator used a different image construction path from the original
archive plan. The local Magnus image above is the active runtime target.

## Files

```text
/data/public/zhangyuanzheng/
  README.md
  comsol-runtime-6.3-zyz-v1.docker.tar
  comsol-runtime-image-manifest.json
  Optics_COMSOL_Runtime_zyz.magnus
  comsol_blueprint_runtime_plan.md
  comsol-runtime/
    ADMIN_INSTALL.md
    README.md
    comsol_runner.py
    secrets/comsol/license.dat
```

## Integrity

Docker archive:

```text
comsol-runtime-6.3-zyz-v1.docker.tar
size: 11451059712 bytes
sha256: 33c8dfb5df07722143d043e653e72299f3ac0d9b9145ac9736818f16e1ea55a4
```

The image was locally validated before upload:

```text
COMSOL Multiphysics 6.3.0.290
comsol batch -help
Python imports: numpy scipy pandas matplotlib h5py meshio mph jpype
comsol_runner.py env_check
```

## Active Image Evidence

The active image has passed these Magnus jobs:

| Job ID | Task | Image | Status | Evidence |
|---|---|---|---|---|
| `de368ea77db7da7f` | `comsol-smoke-minimal` | `docker://magnus-local/comsol-runtime:latest` | Success | COMSOL 6.3.0.290, `batch_help_ok`, `imports_ok`, `COMSOL_SMOKE_OK` |
| `deb10848cb99128a` | `comsol-universal-licensemount-solve` | `docker://magnus-local/comsol-runtime:latest` | Success | license mounted at `/opt/comsol-license/license.dat`, solve completed |
| `3681f26d40ccbf7b` | `comsol-Lmembrane-eigenmodes` | `docker://magnus-local/comsol-runtime:latest` | Success | L-shaped membrane eigenmode solve completed; first eigenvalue near reference |

Earlier comparison jobs used `docker://simulation-runtime:latest` and also
showed COMSOL 6.3 batch/runtime health:

| Job ID | Task | Status | Evidence |
|---|---|---|---|
| `973e8c9bd19298ad` | `comsol-smoke-minimal` | Success | COMSOL 6.3.0.290, batch help, imports |
| `909944d000b92a09` | `comsol-envcheck` | Success | container started successfully |
| `3cd1d9e8abac4115` | `comsol-real-solve` | Success | stationary CoefficientFormPDE 1D solve wrote `.mph` |

## Original Archive Install

This section is retained for provenance only. Do not use it to overwrite the
active `magnus-local/comsol-runtime:latest` image unless explicitly requested.

Load the image on the target Docker/Magnus image host:

```bash
cd /data/public/zhangyuanzheng
sha256sum comsol-runtime-6.3-zyz-v1.docker.tar
docker load -i comsol-runtime-6.3-zyz-v1.docker.tar
docker image inspect comsol-runtime:6.3-zyz-v1
```

The original archive blueprint image was:

```text
docker://comsol-runtime:6.3-zyz-v1
```

The current blueprint default image is:

```text
docker://magnus-local/comsol-runtime:latest
```

If Magnus image policy changes later, update/pass `container_image` accordingly
without refreshing the current local image.

## Runtime Paths

The blueprint currently expects:

```text
code_root=/data/public/zhangyuanzheng/comsol-runtime
license_path=/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
output_root=/home/magnus/data/optics_agent/comsol/runs
```

The blueprint mounts:

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
```

## License Permissions

Please keep the license private:

```bash
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol
chmod 600 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

Current upload already has these permissions.

## Notes

Detailed installation notes:

```text
/data/public/zhangyuanzheng/comsol-runtime/ADMIN_INSTALL.md
```

Full implementation plan:

```text
/data/public/zhangyuanzheng/comsol_blueprint_runtime_plan.md
```
