---
name: optics-agent-core
description: Core index for the optics_agent project. Use when the user mentions project structure, workflow, credentials, SSH, GitHub, Magnus, Docker, COMSOL, blueprints, or asks which project-local skill should handle a task.
---

# Optics Agent Core

## Project Goal

optics_agent is the meta-workspace for designing SEPR (self-evolving paper reproduction) and for this repository's own COMSOL/Magnus runtime work:

```text
optics_agent designs SEPR framework + COMSOL/Magnus optics infrastructure
SEPR executes paper reproductions in ../self-evo-paper-repro
```

Treat paper reproduction as regression tests for reusable scientific-computing blueprints, not as the endpoint. The longer arc is:

```text
paper reproduction -> reusable blueprint -> case/DSL -> parameter sweeps -> new scientific exploration
```

Group-meeting direction:

- Treat optics as the current funding/use-case entry point, not the project boundary; AI should transfer to unfamiliar scientific and engineering domains.
- Build general blueprints that expose sweepable mathematical, physical, numerical, and compute parameters.
- Aim for one complete blueprint to cover multiple paper reproductions and then support new-case exploration.
- Develop a small case/DSL layer so papers, parameters, sweeps, metrics, resources, and failures are machine-readable instead of scattered across scripts and notes.

## Recent Work (2026-06)

- **SEPR sister workspace split**: optics_agent is the design/meta workspace; `C:\Users\27370\Desktop\project\self-evo-paper-repro` is the execution workspace for agent paper reproduction. Human pretraining loop: OA designs -> SEPR reproduces -> SEPR experience returns to OA -> OA manually improves design -> rerun.
- **SEPR design phase complete**: `.human/`, `.claude/skills/`, `CLAUDE.md`, and `WORK_LOG.md` are in place in the SEPR workspace; 94-paper v3 review and 16 risk items landed.
- **Agent skill & workflow self-iteration survey**: `notes/agent_skill_self_iteration/` — covers skill system design, self-improving agents, tool use, meta-cognition, SWE agents, framework comparison, and scientific computing agents.
- **Workflow engine design v2**: `notes/workflow_v2_plan-CN.md`, `notes/project_flow_plan-CN.md`, and `notes/workflow_v2_risks-CN.md` — fixed topology and human-gated experience-layer self-iteration. The v1 self-evolving DSL is archived under `project/to-do-future/DSL/` and is not the active plan.
- **Mie theory reproduction**: infrastructure moved to SEPR execution; plan remains at `reproduction_test/mie/mie_reproduction_plan-FINAL-CN.md`. Verification is 3-layer physical hard constraints + known limits + quantitative paper-figure comparison; PyMieScatt is deprecated as a hard dependency. Bohren & Huffman textbook is available in SEPR as `.paper/scattering.pdf`.

Keep local development in:

```text
C:\Users\27370\Desktop\project\optics_agent
```

Canonical GitHub repository:

```text
https://github.com/PKU-QNO/optics-agent-zyz
```

Use Gustation/Magnus for containerized compute jobs.

## Skill Routing

| User intent | Load |
|---|---|
| SEPR framework/workspace boundary, project routing, credentials, important files | `optics-agent-core` |
| Mie analytical/semi-analytical scattering benchmarks and physical verifiers | `optics-mie-reproduction` |
| Non-Mie paper figure reproduction, parameter extraction, missing-info tables, optics-group standard answers, reproduction reports, COMSOL/Magnus reproduction | `optics-paper-reproduction` |
| COMSOL runtime image, active `magnus-local` image, license mount, runtime folder, admin handoff | `optics-comsol-runtime` |
| COMSOL `batch`, `.java`, `.mph`, `.m`, smoke tests, manifest contract | `optics-comsol-batch` |
| COMSOL Java API syntax, GUI-exported Java, feature tags, study/solver syntax, results API, Java templates | `comsol-java-api` |
| Magnus jobs, logs, blueprint save/launch, FileSecret, MAGNUS_RESULT/ACTION, mounts, `/data/public/zhangyuanzheng` staging | `optics-magnus-platform` |
| Magnus artifact formats, `.magnus.yaml`, `.magnus.skill.yaml`, blueprint/skill import-export packaging, suffix conventions | `optics-magnus-artifacts` |
| Docker images, archive, ACR, PKU registry, image size/hash | `optics-docker-images` |
| Creating or updating project skills | `skill-creator` |

When COMSOL and Magnus are both mentioned, load `optics-comsol-runtime` first, then `optics-magnus-platform`.
SEPR's `main-agent`, `sub-agent`, `evolution-agent`, and `sub-E-agent` live only in the SEPR workspace and are not copied into optics_agent.

## Current COMSOL Runtime Facts

- Active image: `docker://magnus-local/comsol-runtime:latest`.
- Image was administrator-imported and is about `1.38G`.
- Do not refresh, pull, overwrite, retag, rebuild, or replace it unless explicitly requested.
- Runtime folder:
  `/data/public/zhangyuanzheng/comsol-runtime`.
- License:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
- Output root:
  `/home/magnus/data/optics_agent/comsol/runs`.
- Blueprint id:
  `Optics_COMSOL_Runtime_zyz`.

## Current Paper-Reproduction Status

Degiron 2009 Fig. 3 has two private rehearsal folders:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

Use them as workflow evidence, not as successful physical reproduction evidence:

- V1 proved paper reading, parameter extraction, Magnus submission, Java batch cleanup, stdout parsing, CSV/plot generation, and final reporting. Its final sweep is `surrogate_fallback`.
- V2 proved scalar TM-like PDE diagnostics and ran an isolated SU-8 Wave Optics/RF mode-analysis probe. The probe reached the eigensolver after explicit mesh construction but failed matrix factorization and produced zero physical `neff` rows.
- The current blocker is missing COMSOL 6.3 GUI-exported Wave Optics/RF mode-analysis physics/study/solver/result settings.

## Credentials

- Store credentials in `C:\Users\27370\Desktop\project\secret.json`.
- Do not hard-code tokens, registry passwords, SSH keys, or license content in repo files, blueprints, or skills.
- SSH target commonly used in this project:
  `zhangyuanzheng@Gustation`.

## Important Files

```text
AGENTS.md
CLAUDE.md
.codex/skills/
.claude/skills -> .codex/skills
.agents/skills -> .codex/skills
comsol/runtime/
comsol/automation/submit_comsol.py
comsol/automation/sync_comsol_runtime_to_gustation.py
comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
comsol/docs/admin/COMSOL_ADMIN_README.md
comsol/manifests/comsol-runtime-image-manifest.json
comsol/docs/plans/comsol_blueprint_runtime_plan.md
docs/magnus/magnus_ai4s_0604_useful_notes.md
```

## Working Rules

- Prefer read-only Magnus queries for diagnosis unless the user asks to launch or change jobs.
- Never mutate the active COMSOL image accidentally.
- Use `python comsol\automation\submit_comsol.py --save-only` after changing the COMSOL blueprint.
- For Magnus file flow, prefer: temporary user files via `FileSecret`, persistent code/license/results via mounts, admin handoff via SSH/SCP to `/data/public/zhangyuanzheng`.
- Keep long logs and plans in Markdown files; summarize only the high-signal lines to the user.
- Treat `AGENTS.md` as the always-on project rulebook. `CLAUDE.md` should be a hard link to `AGENTS.md`; if project rules change, update `AGENTS.md` and the relevant `.codex/skills/*/SKILL.md` together. `.codex/skills` is canonical; `.claude/skills` and `.agents/skills` should remain junctions to it.
- For long-running reproductions, keep the report state current enough that a PI-facing WeChat update can be generated from `final_report.md`, `workflow_handoff*.md`, and `todo.md` without rereading raw logs.
