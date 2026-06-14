# COMSOL Runtime Image and Magnus Blueprint Plan

## Summary

Build a reusable COMSOL runtime image for Magnus jobs, then expose it through an AI-friendly Magnus blueprint. The current staging target is Aliyun ACR because PKU Git registry quota is not confirmed yet. Gustation cannot pull from Aliyun ACR, so the final Magnus production image must still be retagged and pushed to PKU Git registry after quota is approved.

Deliverables:

- Staging Docker image: `crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:<tag>`
- Production Docker image: `git.pku.edu.cn/rise-agi/comsol-runtime:<tag>`
- Magnus image URI: `docker://git.pku.edu.cn/rise-agi/comsol-runtime:<tag>`
- Build tooling: `comsol/docker/comsol-runtime.Containerfile`, `comsol/docker/build_comsol_runtime.py`, `comsol/docker/comsol-setupconfig.template.ini`
- Blueprint: `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`
- Submit helper: `comsol/automation/submit_comsol.py`
- Skill: build last, after image and blueprint smoke tests pass

Current staging image:

- URI: `crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1`
- Digest: `sha256:1715c2f1d2929669325f2067650ce1a3efeca2ce2ab0dab873cfcc6dc2508671`
- Local size: `24.5GB`
- Registry status: pushed to Aliyun ACR.
- Smoke: `comsol -version`, `comsol batch -help`, Python imports, and image secret scan passed.
- Blueprint: `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`
- Submit helper: `comsol/automation/submit_comsol.py`

Current PKU push status:

- Target: `git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1`
- Command attempted: retag the ACR image and run `docker push`.
- Result on 2026-06-09: failed with `413 Request Entity Too Large`.
- Failure endpoint:
  `https://git.pku.edu.cn/v2/rise-agi/comsol-runtime/blobs/uploads/`
- Interpretation: the COMSOL image itself is valid. PKU Git registry is rejecting Docker Registry v2 blob uploads before the image can be stored, most likely due to reverse proxy request-size limits and/or registry quota settings.
- Required admin action: increase the upload/body limit for the registry `/v2/` path and allocate enough package/container-registry storage for `Rise-AGI`.

Current public-data staging status:

- Staging root: `/data/public/zhangyuanzheng`
- Runtime folder: `/data/public/zhangyuanzheng/comsol-runtime`
- Docker archive: `/data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar`
- Docker archive size: `11451059712` bytes, about `11GB`
- Docker archive SHA256: `33c8dfb5df07722143d043e653e72299f3ac0d9b9145ac9736818f16e1ea55a4`
- Blueprint file: `/data/public/zhangyuanzheng/Optics_COMSOL_Runtime_zyz.magnus`
- Image manifest: `/data/public/zhangyuanzheng/comsol-runtime-image-manifest.json`
- Admin notes: `/data/public/zhangyuanzheng/comsol-runtime/ADMIN_INSTALL.md`
- License path: `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`
- License permissions: `600`; `secrets/` and `secrets/comsol/` permissions: `700`
- Server blueprint `Optics_COMSOL_Runtime_zyz` has been saved with defaults pointing to `/data/public/zhangyuanzheng`.
- This route bypasses both `git.pku.edu.cn` registry and `/home/zhangyuanzheng`; administrator can load the Docker archive directly into Magnus.

Current active Magnus image status:

- Active image: `docker://magnus-local/comsol-runtime:latest`
- Reported size: `1.38G`
- Origin: administrator-imported local Magnus image, built/installed through a route different from this original Docker archive plan.
- Policy: do not refresh, pull, overwrite, retag, or rebuild this image unless the administrator explicitly asks for it.
- Server blueprint `Optics_COMSOL_Runtime_zyz` has been updated to default to `docker://magnus-local/comsol-runtime:latest`.
- The original archive `comsol-runtime-6.3-zyz-v1.docker.tar` remains in `/data/public/zhangyuanzheng` for provenance and fallback only.

Validated active-image jobs:

| Job ID | Task | Image | Status | Evidence |
|---|---|---|---|---|
| `de368ea77db7da7f` | `comsol-smoke-minimal` | `docker://magnus-local/comsol-runtime:latest` | Success | COMSOL 6.3.0.290, batch help, Python imports |
| `deb10848cb99128a` | `comsol-universal-licensemount-solve` | `docker://magnus-local/comsol-runtime:latest` | Success | license mounted at `/opt/comsol-license/license.dat`, solve completed |
| `3681f26d40ccbf7b` | `comsol-Lmembrane-eigenmodes` | `docker://magnus-local/comsol-runtime:latest` | Success | L-shaped membrane eigenmodes solved; eigenvalues close to reference |

Earlier comparison jobs used `docker://simulation-runtime:latest`: `973e8c9bd19298ad`, `909944d000b92a09`, `3cd1d9e8abac4115`.

## Current Responsibility Split

User-owned deployment tasks:

- After PKU registry is fixed, push the validated COMSOL image from Aliyun ACR/local Docker to PKU Git registry:
  `git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1`
- Pull or preheat the PKU image on Gustation after quota is approved.
- Upload the official runtime license to Gustation personal storage:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`

Codex-owned blueprint/runtime tasks:

- Keep the public Magnus blueprint concise and non-sensitive.
- Put all COMSOL execution logic in a private server-side code folder.
- Provide a SFT-style blueprint save/launch script.
- Provide a Python scp uploader for the private code folder and optional license upload.

## Four Deliverables

1. Concise public blueprint:
   `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`

2. Private code folder:
   `comsol/runtime/`

   Server target:
   `/data/public/zhangyuanzheng/comsol-runtime`

   Runtime license target:
   `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`

3. Blueprint submit script:
   `comsol/automation/submit_comsol.py`

4. Code-folder scp uploader:
   `comsol/automation/sync_comsol_runtime_to_gustation.py`

## Blueprint Privacy Design

The `.magnus` file is treated as public server content. It only defines typed parameters and calls:

```text
python /data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py ...
```

The private runner writes `manifest.json`, `command.json`, `env_report.json`, raw COMSOL logs, stdout/stderr, and optional postprocess outputs under:

```text
/home/magnus/data/optics_agent/comsol/runs/<run_id>/
```

The blueprint does not embed license contents, registry credentials, private SSH keys, or model/case logic.

## COMSOL Source

COMSOL software must come from the official COMSOL download channel, not from the `permafrost-paper2016-agent-repo-main` reference project. That project is only useful as a low-quality reference for non-GUI COMSOL wrapping patterns.

Download target:

- COMSOL Multiphysics Linux installer from the official COMSOL Product Download page.
- Use a COMSOL Access account with a valid license or an official trial issued by COMSOL.
- Install enough modules for frontier multiphysics work, at least optical and fluid workflows. The image should not hard-code a single domain.

Recommended module coverage:

- Optical: Wave Optics, RF, Ray Optics if available.
- Fluid: CFD, Microfluidics, Heat Transfer if available.
- Generic multiphysics: core Multiphysics features and Java batch support.

## Secret and License Policy

`C:\Users\27370\Desktop\project\secret.json` is the unified local credential source. Scripts should read keys from there and avoid embedding credentials in code, Markdown, Dockerfiles, or blueprints.

Required credential sections:

- `docker_registry_git_pku`: PKU Git registry login.
- `acr`: retained for older tools, but not used by Gustation COMSOL runtime.
- `magnus_address` / `magnus_token`: current train scripts.
- `magnus_address-gu` / `magnus_token-gu`: current optics-agent scripts.

COMSOL license handling:

- Use Gustation personal storage as the default license path.
- Recommended remote path: `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`
- The concise public blueprint passes the path to the private runner; the runner sets:
  - `COMSOL_LICENSE_FILE`
  - `LM_LICENSE_FILE`
- `license_file_secret` can remain as an optional emergency path, but the normal production path is personal server storage.
- Never bake license files, activation files, trial codes, or tokens into the Docker image.

## Docker Image Plan

Create `comsol/docker/comsol-runtime.Containerfile` and `comsol/docker/build_comsol_runtime.py`.

Image design:

- Base: local `python:3.11-slim-bookworm`.
- COMSOL install root: `/opt/comsol/COMSOL63/Multiphysics`.
- Add `comsol` to `PATH` and symlink `/usr/local/bin/comsol`.
- Install Python runtime packages for broad numerical post-processing:
  - `numpy`
  - `scipy`
  - `pandas`
  - `matplotlib`
  - `h5py`
  - `meshio`
  - `mph`
  - `JPype1`

Security checks:

- Reject or remove `license.dat`.
- Reject or remove `license.trial`.
- Reject or remove `licenseinfo.ini`.
- Reject user preferences, private server tokens, and local machine activation markers.

Registry:

- Push first to Aliyun ACR while PKU registry quota is pending:
  `crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:<tag>`.
- Retag and push to `git.pku.edu.cn/rise-agi/comsol-runtime:<tag>` after PKU quota is approved.
- Use Docker login with `--password-stdin`, reading credentials from `secret.json`.
- Blueprint default image should be `docker://git.pku.edu.cn/rise-agi/comsol-runtime:6.x-zyz-v1`.

## Size Estimate

Ask administrators for both a registry upload-size fix and at least `100GB` registry quota before pushing COMSOL images.

| Image shape | Registry compressed size | Gustation cache size |
|---|---:|---:|
| Minimal COMSOL core + Python runtime | 10-18GB | 14-25GB |
| Multipurpose optics + fluid install | 18-30GB | 25-45GB |
| Near-full COMSOL module install | 25-45GB | 40-70GB |

Minimum practical quota: `60GB`.
Recommended quota: `100GB`.
Comfortable quota for multiple tags: `150GB`.

Admin request draft:

```text
We need to push a COMSOL runtime Docker image to:

  git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1

The image has already been built and validated locally. It is staged at Aliyun ACR with digest:

  sha256:1715c2f1d2929669325f2067650ce1a3efeca2ce2ab0dab873cfcc6dc2508671

Local Docker image size is about 24.5GB. The push to PKU currently fails at:

  POST https://git.pku.edu.cn/v2/rise-agi/comsol-runtime/blobs/uploads/

with:

  413 Request Entity Too Large

Could you please increase the reverse-proxy upload/body limit for the Docker Registry v2 endpoint `/v2/`, and allocate container/package registry quota for `Rise-AGI`? A practical quota is 100GB minimum; 150GB is safer if we need to keep multiple COMSOL tags.
```

## Blueprint Plan

Create `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`, following the style of `train/blueprints/OpenFundus_SFT_zyz.magnus`.

Blueprint characteristics:

- Use `typing.Annotated` for AI-readable parameters.
- Call `submit_job(...)`.
- Always provide `system_entry_command`.
- Mount `/data:/data` and `/home:/home`.
- Write structured results to `$MAGNUS_RESULT`.

Core parameters:

- `run_mode`: `env_check | batch_java | batch_mph | batch_mfile`
- `domain_preset`: `optics | fluid | generic`
- `code_root`: default `/data/public/zhangyuanzheng/comsol-runtime`
- `case_bundle_secret`: optional uploaded tar bundle containing `case.json`, model file, and optional `postprocess.py`
- `case_path`: persistent `/data` case path for production use
- `input_file`: persistent `/data` model path, usually `.java`, `.mph`, or `.m`
- `license_mode`: `personal_storage | server_env | file_secret | env_check_only`
- `license_path`: default `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`
- `license_file_secret`: optional fallback
- `output_root`: default `/home/magnus/data/optics_agent/comsol/runs`
- `container_image`: default PKU Git registry COMSOL runtime image
- `cpu_count`, `memory_demand`, `ephemeral_storage`, `priority`

Default resources:

- Env check: `4 CPU`, `16G`, `20G`, `B2`
- Small 2D optics/fluid smoke: `8 CPU`, `32-64G`, `50-100G`, `B2`
- Larger 3D or sweeps: requires explicit review before using more than `32 CPU` or `250G RAM`

## Runtime Contract

Each run writes:

```text
/home/magnus/data/optics_agent/comsol/runs/<run_id>/
  manifest.json
  input_case.json
  command.json
  env_report.json
  raw/
    model_input.java | model_input.mph | model_input.m
    model_output.mph
    comsol.log
    stdout.txt
    stderr.txt
  results/
    metrics.json
    tables/
    figures/
  errors/
    failure.json
```

Failure codes:

- `COMSOL_NOT_FOUND`
- `LICENSE_UNAVAILABLE`
- `BATCH_EXIT_NONZERO`
- `OUTPUT_MPH_MISSING`
- `EXPORT_MISSING`
- `TIMEOUT`
- `OOM`
- `POSTPROCESS_FAILED`

## Test Plan

Image tests:

- `comsol -version`
- `comsol batch -help`
- Python import check for runtime dependencies
- Secret scan confirms no license/token files are baked into the image

License tests:

- With missing `/home/.../license.dat`, runner returns structured `LICENSE_UNAVAILABLE`.
- With mounted persistent license, `env_check` reports COMSOL version and license availability.

COMSOL smoke tests:

- Optics smoke: minimal 2D waveguide Java or `.mph` case.
- Fluid smoke: minimal laminar flow or microfluidics Java or `.mph` case.

Magnus tests:

- Gustation pulls `docker://git.pku.edu.cn/rise-agi/comsol-runtime:<tag>`.
- Blueprint writes `manifest.json`.
- `$MAGNUS_RESULT` contains status, run directory, key artifacts, and failure summary if any.

## Implementation Order

1. Put COMSOL license in Gustation personal storage:
   `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`
2. Download official COMSOL Linux installer locally or on an approved build host.
3. Build `comsol-runtime` Docker image locally from the approved COMSOL install tree.
4. Scan image for forbidden license/secret files.
5. Push image to Aliyun ACR as the staging artifact.
6. After PKU quota is approved, retag and push to `git.pku.edu.cn/rise-agi/comsol-runtime:<tag>`.
7. Add `Optics_COMSOL_Runtime_zyz.magnus`.
8. Add `comsol/automation/submit_comsol.py`.
9. Run `env_check` on Magnus.
10. Run optics smoke and fluid smoke.
11. Build/update skill after the runtime contract is stable.

Current local command:

```powershell
python comsol\docker\build_comsol_runtime.py --registry acr --tag 6.3-zyz-v1 --comsol-setup "D:\docker-base\COMSOL Multiphysics 6.3.0.290\Setup"
```

Use `--no-push` for a local build-only pass, and pass one of `--license-file`, `--license-server`, or `COMSOL_INSTALL_LICENSE` if the installer requires a build-time license.

Blueprint save-only command:

```powershell
python comsol\automation\submit_comsol.py --save-only
```

Upload private code folder to Gustation:

```powershell
scp -r C:/Users/27370/Desktop/project/optics_agent/comsol/runtime/ zhangyuanzheng@Gustation:~/
```

Equivalent helper script:

```powershell
python comsol\automation\sync_comsol_runtime_to_gustation.py --dry-run
python comsol\automation\sync_comsol_runtime_to_gustation.py
```

Optional license upload via the same scp script:

```powershell
python comsol\automation\sync_comsol_runtime_to_gustation.py --license-file "D:\docker-base\LMCOMSOL_Multiphysics_SSQ.lic"
```

Gustation env-check launch after PKU image is ready:

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode personal_storage --container-image docker://git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1
```

Local ACR env-check launch command, only for non-Gustation staging:

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode env_check_only --container-image docker://crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1
```

Production Gustation launch should use the PKU image after the registry quota is approved and the image has been retagged/pushed.
