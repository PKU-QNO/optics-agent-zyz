# Fig.1 gate④ historical closure receipt (immutable record)

Receipt ID: `FIG1-G4-20260809-PASS_WITH_LIMITATIONS`

This file records the prior user-approved closure that is referenced by the
workspace handoff. It is a historical receipt, not a replacement for the B1
metric re-gate. Do not edit in place; superseding decisions must be recorded in
a new receipt.

| Field | Recorded value |
|---|---|
| Scope | Alaee 2018 Fig.1(a), dielectric sphere, $ε_r=6.25$, $s=2a/\lambda\in[0.2,1.0]$ |
| Decision date | 2026-08-09 (Asia/Shanghai) |
| User decision recorded in | `WORK_LOG.md` 2026-08-09 entry (final approval) |
| Gate result | `PASS_WITH_LIMITATIONS` |
| Closed path | Mie/B&H baseline, Table2 implementation, 3-layer verification, gate①–③ |
| Explicit limitation | No promotion to unrestricted `physical_reproduction_success`; later A1 audit found the paper-moment vs C-metric wording drift |
| Frozen evidence | `data/fig1a_multipole_{mie,table2,table1}.csv` (200 rows each) |
| B1 superseding evidence | `codex-prompts/out/B1-fig1-s075-evidence.json` |

Integrity protocol: this receipt and its `.sha256` sidecar are written once.
The sidecar hash covers the exact bytes of this file. Any changed scope or
metric requires a new receipt ID and a new hash; the old receipt remains
historical evidence.
