# COMSOL Runtime Capability Report

Updated: 2026-06-13

Campaign: `comsol-capability-20260613-v1`

Image:

```text
docker://magnus-local/comsol-runtime:latest
```

Blueprint:

```text
Optics_COMSOL_Runtime_zyz
```

## One Sentence

The current Magnus COMSOL image can run COMSOL 6.3 headless, compile and run Java API models through `comsol batch`, solve generic PDE/eigenmode problems, solve a scalar Helmholtz-like optics field problem, and pass minimal Wave Optics/RF-style and Laminar Flow/Creeping Flow-style professional module probes.

## Resource Policy Used

- GPU was not used: every submitted job used `gpu_type=cpu`, `gpu_count=0`.
- Before each submission, the agent queried existing jobs with `magnus.list_jobs(limit=100, search=<run_id>)`.
- Before each submission, the agent queried cluster resources with `magnus.get_cluster_stats()`.
- Cluster resources at dry-run time: `128` CPU cores and about `973GB` memory free.
- The six-job campaign requested at most `56/128` CPU cores and `224/973GB` memory during staged submission checks, below the one-half limit.

## Jobs

| Case | Job ID | Status | What It Proves |
|---|---|---|---|
| `envcheck` | `f2c00784c24041eb` | Success | COMSOL 6.3.0.290, `comsol batch`, Python imports, license env. |
| `core-pde-eigenmode` | `6752b0d0afb11f7a` | Success | Generic Coefficient Form PDE eigenmode solve through blueprint runner. |
| `optics-helmholtz` | `42ce2ba174d5b9a6` | Success | Scalar Helmholtz-like optics field solve using core PDE tools. |
| `wave-optics-probe` | `1d9a03b77815f140` | Success | Minimal electromagnetic Wave Optics/RF-style Java API probe compiled, solved, and wrote `.mph`. |
| `fluid-laminar-probe` | `a43412fc80ab0608` | Success | Minimal Laminar Flow/Creeping Flow-style Java API probe compiled, solved, and wrote `.mph`. |
| `fluid-pde-fallback` | `993a3c1a90b69429` | Success | Flow-like scalar PDE fallback solved with core PDE tools. |

## Confirmed Capabilities

- COMSOL headless runtime is usable on Magnus.
- `comsol batch` is usable in the active image.
- Java API model files can be compiled with `comsol compile` and run through `comsol batch`.
- Python postprocessing dependencies are present: `numpy`, `scipy`, `pandas`, `matplotlib`, `h5py`, `meshio`, `mph`, `jpype`.
- License forwarding via `/opt/comsol-license/license.dat` works for solves.
- Generic PDE and eigenvalue problems work.
- A minimal optics field problem works through scalar Helmholtz-style Coefficient Form PDE.
- A minimal electromagnetic professional-module probe works.
- A minimal fluid professional-module probe works.

## Caveats

- The professional module probes were intentionally tiny. They prove that the runtime can create, solve, and save minimal electromagnetic and fluid models, not that large production Wave Optics/CFD workflows are fully validated.
- The current runner version at submission time wrote `metrics: {}` for Java probes, although each job succeeded and wrote `.mph`. The runner has since been updated to capture future stdout success markers in manifests.
- Exact selected professional interface names should be read from raw stdout if needed; the current high-level Magnus result records success, compile status, output paths, and failure-free manifests.

## Output Roots

All runs wrote under:

```text
/home/magnus/data/optics_agent/comsol/runs/comsol-capability-20260613-v1-*
```

Each run directory contains the standard runner contract:

```text
manifest.json
command.json
env_report.json
compile.json
raw/
results/
errors/
```

## Next Step

Use this campaign as the new baseline. The next useful upgrade is not more image work; it is a more realistic optics case, such as a waveguide or plasmonic scattering model, plus a more realistic microfluidic channel model with quantitative postprocessing.
