# COMSOL Mie-like Time-domain Scattering Run

Updated: 2026-06-14T11:55:41

## Summary

- Method: 2D time-domain scalar wave FEM, FDTD-like pulse scattering.
- Image: `docker://magnus-local/comsol-runtime:latest`
- Blueprint: `Optics_COMSOL_Runtime_zyz`
- GPU: not used (`gpu_type=cpu`, `gpu_count=0`).

## Jobs

| Case | Job ID | Status | Action | Output |
|---|---|---|---|---|
| `smoke` | `481676c76fd1cba3` | `Success` | `reused_success` | `/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1` |
| `medium` | `037c91e27444170a` | `Success` | `submitted` | `/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1` |

## Verification Notes

- Both cases compiled Java successfully and completed through `comsol batch`.
- Both cases produced `raw/model_output.mph` according to `$MAGNUS_RESULT`.
- Resource policy was respected: CPU only, no GPU, and the medium job requested `24/128` CPU cores plus `128/973GB` memory.
- The Java-side stdout marker and sidecar `metrics.json` were not captured by the current COMSOL batch execution path, so `metrics` and `success_markers` are empty in the manifest. Treat this as an output-contract limitation, not as a solver failure.

## Raw Records

```json
[
  {
    "case": "smoke",
    "run_id": "comsol-mie-td-20260613-smoke-v1",
    "job_id": "481676c76fd1cba3",
    "status": "Success",
    "dedupe_action": "reused_success",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/mie_scattering/MieScatteringTimeDomain2DSmoke.java",
    "output_dir": "/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1",
    "cpu_count": 8,
    "memory_demand": "32G",
    "ephemeral_storage": "100G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": null,
    "result": "{\n  \"status\": \"completed\",\n  \"backend\": \"batch_java\",\n  \"domain_preset\": \"optics\",\n  \"run_id\": \"comsol-mie-td-20260613-smoke-v1\",\n  \"run_dir\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1\",\n  \"timestamp_unix\": 1781408995,\n  \"comsol\": {\n    \"version\": \"COMSOL Multiphysics 6.3.0.290\"\n  },\n  \"artifacts\": {\n    \"manifest\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/manifest.json\",\n    \"command\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/command.json\",\n    \"env_report\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/env_report.json\",\n    \"batch_log\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/comsol.log\",\n    \"stdout\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/stdout.txt\",\n    \"stderr\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/stderr.txt\",\n    \"output_mph\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/model_output.mph\",\n    \"results_dir\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/results\"\n  },\n  \"failure\": null,\n  \"compile\": {\n    \"source\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/MieScatteringTimeDomain2DSmoke.java\",\n    \"compiled\": true,\n    \"returncode\": 0,\n    \"stdout\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/compile.stdout.txt\",\n    \"stderr\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/compile.stderr.txt\",\n    \"class_file\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-smoke-v1/raw/MieScatteringTimeDomain2DSmoke.class\"\n  },\n  \"metrics\": {},\n  \"success_markers\": []\n}"
  },
  {
    "case": "medium",
    "run_id": "comsol-mie-td-20260613-medium-v1",
    "job_id": "037c91e27444170a",
    "status": "Success",
    "dedupe_action": "submitted",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/mie_scattering/MieScatteringTimeDomain2DMedium.java",
    "output_dir": "/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1",
    "cpu_count": 24,
    "memory_demand": "128G",
    "ephemeral_storage": "200G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": {
      "ok": true,
      "cpu_total": 128,
      "cpu_free": 128,
      "cpu_used": 0,
      "cpu_after": 24,
      "cpu_limit_half": 64.0,
      "mem_total_gb": 973.461,
      "mem_free_gb": 973.461,
      "mem_used_gb": 0.0,
      "mem_after_gb": 128.0,
      "mem_limit_half_gb": 486.73
    },
    "task_name": "COMSOL-comsol-mie-td-20260613-medium-v1",
    "result": "{\n  \"status\": \"completed\",\n  \"backend\": \"batch_java\",\n  \"domain_preset\": \"optics\",\n  \"run_id\": \"comsol-mie-td-20260613-medium-v1\",\n  \"run_dir\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1\",\n  \"timestamp_unix\": 1781409086,\n  \"comsol\": {\n    \"version\": \"COMSOL Multiphysics 6.3.0.290\"\n  },\n  \"artifacts\": {\n    \"manifest\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/manifest.json\",\n    \"command\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/command.json\",\n    \"env_report\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/env_report.json\",\n    \"batch_log\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/comsol.log\",\n    \"stdout\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/stdout.txt\",\n    \"stderr\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/stderr.txt\",\n    \"output_mph\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/model_output.mph\",\n    \"results_dir\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/results\"\n  },\n  \"failure\": null,\n  \"compile\": {\n    \"source\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/MieScatteringTimeDomain2DMedium.java\",\n    \"compiled\": true,\n    \"returncode\": 0,\n    \"stdout\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/compile.stdout.txt\",\n    \"stderr\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/compile.stderr.txt\",\n    \"class_file\": \"/home/magnus/data/optics_agent/comsol/runs/comsol-mie-td-20260613-medium-v1/raw/MieScatteringTimeDomain2DMedium.class\"\n  },\n  \"metrics\": {},\n  \"success_markers\": []\n}"
  }
]
```
