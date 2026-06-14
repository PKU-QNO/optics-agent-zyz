# COMSOL Runtime Capability Probe Plan

Updated: 2026-06-13

## Summary

This note preserves the execution plan for checking what the current Magnus COMSOL runtime can actually solve.

Target image:

```text
docker://magnus-local/comsol-runtime:latest
```

This image is administrator-imported and must be treated as immutable. Do not refresh, pull, retag, overwrite, rebuild, or replace it while running these probes.

The goal is to turn "COMSOL can start" into a concrete capability table:

```text
capability | status | evidence job id | output directory | notes
```

The final report should be written to:

```text
comsol/docs/reports/comsol_runtime_capability_report.md
```

## Hard Rules

- Use CPU only. Every submitted job must set `gpu_type=cpu` and `gpu_count=0`.
- Do not use GPU queues or GPU resources for these probes.
- Before every job submission, query the cluster and confirm that planned CPU and memory usage will not push total cluster usage above one half of available CPU cores or memory.
- If cluster CPU/memory totals or current usage cannot be checked reliably, fail closed: do not submit automatically, and report that resource confirmation is blocked.
- Before every job submission, query existing Magnus jobs to avoid duplicate submissions.
- During waiting/polling, use read-only status/result/log queries only. Do not submit duplicates and do not terminate jobs unless the user explicitly asks.
- Keep all COMSOL license content, tokens, SSH keys, and passwords out of docs, blueprints, job names, and logs.

## Campaign

Use a stable campaign id so the run can resume after context compaction:

```text
campaign_id = comsol-capability-20260613-v1
```

Use stable `run_id` values:

```text
comsol-capability-20260613-v1-envcheck
comsol-capability-20260613-v1-core-pde-eigenmode
comsol-capability-20260613-v1-optics-helmholtz
comsol-capability-20260613-v1-wave-optics-probe
comsol-capability-20260613-v1-fluid-laminar-probe
comsol-capability-20260613-v1-fluid-pde-fallback
```

The corresponding `task_name` should include the same `run_id`. This makes deduplication possible with `magnus.list_jobs(..., search=<run_id>)`.

## Probe Jobs

Use the existing blueprint:

```text
Optics_COMSOL_Runtime_zyz
```

Use the current runtime defaults unless a probe explicitly needs different input:

```text
container_image=docker://magnus-local/comsol-runtime:latest
code_root=/data/public/zhangyuanzheng/comsol-runtime
license_mode=server_env
license_path=/opt/comsol-license/license.dat
output_root=/home/magnus/data/optics_agent/comsol/runs
priority=B2
cpu_count=8
memory_demand=32G
ephemeral_storage=100G
gpu_type=cpu
gpu_count=0
```

Planned probes:

| Probe | Purpose | Expected result |
|---|---|---|
| `envcheck` | Confirm COMSOL version, `comsol batch`, Python imports, license environment, and mount visibility. | `manifest.json` completed. |
| `core-pde-eigenmode` | Confirm generic PDE/eigenmode solving still works through the current blueprint path. | `.mph` output and numeric eigenvalue evidence. |
| `optics-helmholtz` | Confirm a minimal optics-like scalar field problem can solve with core PDE tools. | Field solve succeeds; mark as core PDE optics capability. |
| `wave-optics-probe` | Test whether Wave Optics/RF-style professional interfaces are installed and licensed. | Only mark Wave Optics/RF available if the probe succeeds. |
| `fluid-laminar-probe` | Test whether Laminar Flow/CFD/Microfluidics interfaces are installed and licensed. | Only mark fluid module available if the probe succeeds. |
| `fluid-pde-fallback` | Confirm whether core PDE tools can still solve a simple flow-like fallback problem. | Mark only as PDE fallback, not as CFD. |

## Submission Guard

Every probe submission must follow this order:

1. Configure Magnus with credentials from `C:\Users\27370\Desktop\project\secret.json`, preferring `magnus_address-gu` and `magnus_token-gu`.
2. Check old and current campaign jobs with:

   ```python
   magnus.list_jobs(limit=100, search=run_id)
   ```

3. Apply dedupe rules:
   - `Preparing`, `Pending`, `Queued`, `Running`, `Paused`: reuse the existing job id; do not submit.
   - `Success`: reuse the existing result; do not submit.
   - `Failed`, `Terminated`: do not automatically resubmit. Record the failure. Resubmit only with an explicit `--force-rerun-failed` option.
   - No matching job: continue to resource checks.
4. Query cluster CPU and memory state before submission.
5. Compute:

   ```text
   cpu_after = current_cluster_cpu_used + planned_cpu_count
   mem_after = current_cluster_mem_used + planned_memory_gb
   ```

6. Submit only if both are true:

   ```text
   cpu_after <= total_cluster_cpu_cores * 0.5
   mem_after <= total_cluster_memory_gb * 0.5
   ```

7. If resource totals or current usage are unavailable, stop before submission and write a blocked note to the TODO file.
8. Submit the job only after both dedupe and resource checks pass.
9. Record `case_id`, `run_id`, `job_id`, `status`, `dedupe_action`, `resource_check`, and `output_dir`.

## Waiting Policy

After all jobs are either submitted, reused, skipped, or blocked, the agent waits by polling. It should not keep submitting jobs during the wait phase.

Use adaptive polling:

- Fast checks such as `envcheck`:
  - first poll after 60 seconds;
  - then every 2 to 5 minutes;
  - if still not terminal after 30 minutes, switch to 30-minute polling.
- Small solver probes:
  - first poll after 5 minutes;
  - then every 10 minutes for the first 30 minutes;
  - then every 30 minutes.
- Maximum total wait for this campaign: 12 hours.

Terminal states:

```text
Success
Failed
Terminated
```

Nonterminal states:

```text
Preparing
Pending
Queued
Running
Paused
```

If all jobs reach terminal states, stop waiting and write the report. If the 12-hour limit is reached, write a partial report and leave unfinished jobs as `pending_or_timeout`.

## Report Contract

The final capability report should include:

- campaign id and timestamp;
- active image and blueprint id;
- resource policy used;
- all job ids and statuses;
- confirmed capabilities;
- unconfirmed or failed capabilities;
- whether failure looks like module missing, license missing, solver failure, resource failure, or infrastructure failure;
- output directories under `/home/magnus/data/optics_agent/comsol/runs`.

## Current Known Evidence

These jobs are known-good historical evidence for the active image:

```text
de368ea77db7da7f  comsol-smoke-minimal                  Success
deb10848cb99128a  comsol-universal-licensemount-solve   Success
3681f26d40ccbf7b  comsol-Lmembrane-eigenmodes           Success
f1442f2403e37150  updated blueprint env_check            Success
```

They confirm COMSOL 6.3 headless runtime, `comsol batch`, Python imports, license-mounted solving, and a generic PDE/eigenmode example. They do not yet confirm professional Wave Optics, RF, CFD, Laminar Flow, or Microfluidics modules.

