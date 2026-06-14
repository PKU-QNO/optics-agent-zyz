# COMSOL Runtime Capability Probe TODO

Updated: 2026-06-13

Campaign:

```text
comsol-capability-20260613-v1
```

Hard rules used:

- CPU only: `gpu_type=cpu`, `gpu_count=0`.
- Before every job submission, query existing jobs and dedupe.
- Before every job submission, query cluster CPU and memory usage.
- Do not submit if planned total usage would exceed one half of cluster CPU cores or one half of cluster memory.
- If resource usage cannot be confirmed, stop before submitting.
- Use adaptive polling: fast tasks do not need 30-minute polling unless they stay nonterminal for more than 30 minutes.

## TODO

- [x] Magnus connection precheck

  ```text
  status: done
  job_id:
  run_id:
  output_dir:
  notes: get_cluster_stats and list_jobs worked after network escalation.
  ```

- [x] Query historical jobs and confirm old evidence

  ```text
  status: done
  job_id: de368ea77db7da7f, deb10848cb99128a, 3681f26d40ccbf7b, f1442f2403e37150
  run_id:
  output_dir:
  notes: old evidence confirms image health, license-mounted solve, and L-membrane eigenmodes.
  ```

- [x] Implement or upload env inventory probe

  ```text
  status: success
  job_id: f2c00784c24041eb
  run_id: comsol-capability-20260613-v1-envcheck
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-envcheck
  notes: COMSOL 6.3.0.290, batch, Python imports, and license env passed.
  ```

- [x] Implement or upload core PDE/eigenmode probe

  ```text
  status: success
  job_id: 6752b0d0afb11f7a
  run_id: comsol-capability-20260613-v1-core-pde-eigenmode
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-core-pde-eigenmode
  notes: Java compiled, COMSOL batch solved, output .mph exists.
  ```

- [x] Implement or upload optics scalar Helmholtz case

  ```text
  status: success
  job_id: 42ce2ba174d5b9a6
  run_id: comsol-capability-20260613-v1-optics-helmholtz
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-optics-helmholtz
  notes: Scalar Helmholtz-like field solve succeeded through core PDE tools.
  ```

- [x] Implement or upload Wave Optics/RF probe

  ```text
  status: success
  job_id: 1d9a03b77815f140
  run_id: comsol-capability-20260613-v1-wave-optics-probe
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-wave-optics-probe
  notes: Minimal electromagnetic professional-module probe compiled, solved, and wrote .mph.
  ```

- [x] Implement or upload Laminar Flow/CFD/Microfluidics probe

  ```text
  status: success
  job_id: a43412fc80ab0608
  run_id: comsol-capability-20260613-v1-fluid-laminar-probe
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-fluid-laminar-probe
  notes: Minimal Laminar Flow/Creeping Flow-style probe compiled, solved, and wrote .mph.
  ```

- [x] Implement or upload fluid PDE fallback probe

  ```text
  status: success
  job_id: 993a3c1a90b69429
  run_id: comsol-capability-20260613-v1-fluid-pde-fallback
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-fluid-pde-fallback
  notes: Flow-like scalar PDE fallback solved with core PDE tools.
  ```

- [x] Implement batch submit script with dedupe

  ```text
  status: done
  job_id:
  run_id:
  output_dir: comsol/automation/probe_comsol_capabilities.py
  notes: Calls magnus.list_jobs(limit=100, search=run_id) before each submit.
  ```

- [x] Implement cluster resource precheck

  ```text
  status: done
  job_id:
  run_id:
  output_dir: comsol/automation/probe_comsol_capabilities.py
  notes: Uses magnus.get_cluster_stats and blocks if planned CPU/memory exceed 50%.
  ```

- [x] Implement adaptive wait loop

  ```text
  status: done
  job_id:
  run_id:
  output_dir: comsol/automation/probe_comsol_capabilities.py
  notes: Fast tasks poll early; only switch to 30 minutes after 30 minutes nonterminal.
  ```

- [x] Submit or reuse all campaign jobs

  ```text
  status: done
  job_id: f2c00784c24041eb, 6752b0d0afb11f7a, 42ce2ba174d5b9a6, 1d9a03b77815f140, a43412fc80ab0608, 993a3c1a90b69429
  run_id: comsol-capability-20260613-v1-*
  output_dir: /home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-*
  notes: dedupe_action=submitted for all campaign jobs.
  ```

- [x] Wait for terminal states or timeout

  ```text
  status: done
  job_id: all campaign jobs
  run_id: comsol-capability-20260613-v1-*
  output_dir:
  notes: All six jobs reached Success before long polling was needed.
  ```

- [x] Summarize each job result

  ```text
  status: done
  job_id: all campaign jobs
  run_id: comsol-capability-20260613-v1-*
  output_dir:
  notes: Results and logs queried through Magnus SDK.
  ```

- [x] Generate capability report

  ```text
  status: done
  job_id:
  run_id:
  output_dir: comsol/docs/reports/comsol_runtime_capability_report.md
  notes:
  ```

- [x] Update skills with verified/unverified module status

  ```text
  status: done
  job_id:
  run_id:
  output_dir: .codex/skills/optics-comsol-runtime/SKILL.md, .codex/skills/optics-comsol-batch/SKILL.md
  notes: Update after this TODO item is patched into skills.
  ```

