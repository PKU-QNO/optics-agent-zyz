# optics_agent Collaboration Guide

This repo is the local control workspace for the optics_agent project.

Current direction:

```text
paper reproduction
  -> reusable scientific blueprint
  -> case/DSL + parameter sweeps
  -> new scientific exploration
```

Paper reproduction is the starting regression test for blueprint iteration, not the final goal. Optics is the current funding/use-case entry point; the framework should transfer to unfamiliar scientific and engineering domains.

## Skills

Claude project skills live in:

```text
.claude/skills/
```

Implementation detail: `.claude/skills` is a Windows junction to the canonical skills directory:

```text
.codex/skills/
```

Edit either path and you are editing the same files. Treat `.codex/skills` as the canonical source when documenting paths. Read the relevant `SKILL.md` before acting.

| Task | Skill |
|---|---|
| Project routing, goals, credentials, important files | `optics-agent-core` |
| COMSOL runtime image, active Magnus-local image, license mounts, runtime folder | `optics-comsol-runtime` |
| COMSOL batch/headless jobs, `.java`/`.mph`/`.m`, smoke cases, manifest contract | `optics-comsol-batch` |
| Magnus/Gustation jobs, logs, blueprint save/launch, staging paths | `optics-magnus-platform` |
| Magnus artifact formats, `.magnus.yaml`, `.magnus.skill.yaml`, import/export packaging | `optics-magnus-artifacts` |
| Docker image build/push/archive/handoff, ACR/PKU registry, image size/hash | `optics-docker-images` |

If COMSOL and Magnus are both involved, read `optics-comsol-runtime` first, then `optics-magnus-platform`.

## Current COMSOL Runtime

Active Magnus image:

```text
docker://magnus-local/comsol-runtime:latest
```

Important rules:

- This image was imported by the administrator and is about `1.38G`.
- Do not refresh, pull, overwrite, retag, rebuild, or replace it unless explicitly requested.
- The original Docker archive is provenance/fallback only.

Important paths:

```text
runtime folder: /data/public/zhangyuanzheng/comsol-runtime
runner:         /data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py
staged license: /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
output root:    /home/magnus/data/optics_agent/comsol/runs
blueprint id:   Optics_COMSOL_Runtime_zyz
blueprint file: comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
```

Validated active-image jobs:

```text
de368ea77db7da7f  comsol-smoke-minimal
deb10848cb99128a  comsol-universal-licensemount-solve
3681f26d40ccbf7b  comsol-Lmembrane-eigenmodes
```

For real COMSOL solves, the proven license mount is:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Forward license variables into the container with `APPTAINERENV_LM_LICENSE_FILE` and `APPTAINERENV_COMSOL_LICENSE_FILE`; see `optics-comsol-runtime` for the full `system_entry_command`.

## Magnus Rules

Use credentials from:

```text
C:\Users\27370\Desktop\project\secret.json
```

Prefer GU/Gustation keys when present:

```text
magnus_address-gu
magnus_token-gu
```

Never hard-code tokens, registry passwords, SSH keys, or COMSOL license contents in code, docs, blueprints, or skills.

For diagnosis, prefer read-only calls:

```python
job = magnus.get_job(job_id)
logs = magnus.get_job_logs(job_id, page=-1)
```

Default COMSOL smoke resources:

```text
gpu_type=cpu
gpu_count=0
cpu_count=8
memory_demand=32G
ephemeral_storage=40G-100G
job_type=B2
```

Do not launch large jobs, GPU jobs, or A-class jobs unless the user explicitly asks and the resource impact is reviewed.

When a job needs `/data/public`, `/home/magnus/data`, or the COMSOL license, always provide `system_entry_command`. Otherwise the container may not see the host paths.

## Blueprint Rules

Magnus blueprints should be small public interfaces:

- Define a function named `blueprint`.
- Use typed parameters and `typing.Annotated` metadata.
- Call `submit_job(...)` in the function body.
- Keep license files, tokens, private runner logic, and long case code outside the blueprint.

After editing the COMSOL blueprint, save it with:

```powershell
python comsol\automation\submit_comsol.py --save-only
```

The runtime code and license live in mounted storage; the blueprint should mostly select image, resources, mounts, runner, and input/output paths.

## Storage And Handoff

Use the public staging area for COMSOL/Magnus handoff:

```text
/data/public/zhangyuanzheng
```

Do not switch back to `/home/zhangyuanzheng` or registry-first delivery unless the user explicitly changes the deployment target.

Keep long logs, plans, and meeting notes in `docs/*.md`; summarize only the high-signal lines in chat.

## Important Files

```text
.claude/skills/
.codex/skills/
comsol/runtime/
comsol/automation/submit_comsol.py
comsol/automation/sync_comsol_runtime_to_gustation.py
comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
comsol/docs/admin/COMSOL_ADMIN_README.md
comsol/manifests/comsol-runtime-image-manifest.json
comsol/docs/plans/comsol_blueprint_runtime_plan.md
docs/magnus/magnus_ai4s_0604_useful_notes.md
docs/meetings/blueprint_research_vision_group_meeting.md
```
