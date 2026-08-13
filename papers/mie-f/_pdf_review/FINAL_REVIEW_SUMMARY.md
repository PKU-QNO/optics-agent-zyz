# mie-f PDF Review Final Summary

Generated from:
- `papers/mie-f/_pdf_review/reports/`
- `papers/mie-f/_pdf_review/reports/chunks/`
- `papers/mie-f/_pdf_review/escalations/`
- `papers/mie-f/_pdf_review/manual_actions.md`

No source PDF, OCR baseline, original Markdown, `AGENTS.md`, `CLAUDE.md`, or skill file was modified while producing this summary.

## Executive Summary

- The review set is partially complete and uneven across papers.
- No fully missing Bohren chunk remains; the earlier `161-180` gap was superseded by a later PASS chunk.
- The main remaining Johnson coverage issue is not a missing report for `5-20`, but the lack of a usable OCR baseline for pages `5-10`; pages `11-12` do not exist in the current source PDF.
- Several papers are fully covered but not all of them are equally strong:
  - `Fernandez-Corbaton_2015` and `Fernandez-Corbaton_2017` are clean, OCR-backed reviews.
  - `Muhlig_2014` is fully covered and mostly clean, but some batches used fallback text extraction or had OCR-baseline access issues.
  - `Grahn_2012` and `Alaee_2018` are visually inspected fallback reviews because `pdf-mcp` was unavailable or the OCR baseline was missing.
- `UNCERTAIN` is not treated as `PASS` anywhere in this summary.

## Coverage Matrix

| Paper | Reports present | Coverage status | Notes |
|---|---|---|---|
| `Bohren_Huffman_1983` | `1-20`, `21-40`, `41-60`, `61-80`, `81-100`, `101-120`, `121-140`, `141-160`, `161-180`, `181-200`, `201-220` | Complete, with partial uncertainty in later spans | `161-180` is fully PASS; several later spans still contain reviewed FAIL or unresolved pages |
| `Fernandez-Corbaton_2015` | `1-14` | Complete | No fail or uncertain pages |
| `Fernandez-Corbaton_2017` | `1-8` | Complete | OCR symbol noise noted, but no page-level fail |
| `Grahn_2012` | `1-12` | Complete but fallback-based | `pdf-mcp` unavailable; OCR baseline missing; report conflict exists |
| `Johnson_Christy_1972` | `1-4`, `5-10` continued, `13-20` continued, `21-40`, `41-60`, `61-80`, `81-85` | Partial | Pages `5-10` are only visually checked because the OCR baseline is unusable; pages `11-12` do not exist in the current source PDF; pages `13-20` have report-backed OCR defects |
| `Muhlig_2014` | `1-20`, `21-40`, `41-60`, `61-80`, `81-100`, `101-120`, `121-140`, `141-147` | Complete | No fail pages; some batches used fallback text extraction or had OCR access issues |
| `Alaee_2018` | `1-5` | Complete but fallback-based | `pdf-mcp` unavailable; exact formula fidelity remains uncertain |

## Missing Chunks / Uncovered Ranges

- `Johnson_Christy_1972`: no current evidence supports the existence of pages `11-12` in the reviewed source PDF; if another source was intended, that file must be supplied.

## Definite FAILs

### Bohren_Huffman_1983

- `1-20`: minor Markdown syntax defect in the title block, `#of Light by Small Particles` instead of `# of Light by Small Particles`.
- `101-120`: repeated `1` vs `l` subscript confusion in mode labels such as `\psi_{oln}` / `\psi_{eln}`, `B_{oln}`, `A_{eln}`, `\mathbf{M}_{oln}`, and `\mathbf{N}_{eln}`.
- `201-220`: none.

### Johnson_Christy_1972

- `1-4`: page 1 section-title typo, `CONTANTS` instead of `CONSTANTS`.
- `21-40`: page 32 long electric multipole equation is structurally broken; page 38 Table 9.1 is materially corrupted; page 39 misreads `Y_{l0}` as `Y_{I0}`.
- `41-60`: page 41 misreads `r^{\prime l}` as `r^{\prime\prime}`; page 45 misreads `Y_{l0}` as `Y_{I0}`; page 56 corrupts the TM-waveguide phase factors.
- `61-80`: page 73 mislabels multipole coefficients; page 74 corrupts the plane-wave expansion block; page 77 corrupts the impedance-boundary equations; page 80 misreads the optical-theorem field decomposition.
- `81-85`: page 84 misreads `e^2` as `\epsilon^2`; page 85 collapses reference-list line breaks.

### Grahn_2012

- No page-level content fail was established in the completed 12-page review, but the workflow-level fail remains because `pdf-mcp` could not be used and the expected OCR baseline is missing.

### Alaee_2018

- No direct page-level content fail was proven, but the strict workflow requirement failed because `pdf-mcp` was unavailable and exact formula fidelity was not established.

## UNCERTAIN / Incomplete Spans

### Bohren_Huffman_1983

- `1-20`: page 14 handwritten marginal note is outside plain OCR scope.
- `121-140`: pages `124-140` were rendered, but OCR/vision confirmation timed out repeatedly.
- `141-160`: only pages `141, 143, 151, 153, 155, 157` were fully confirmed; the rest of the span remained uncertain.
- `181-200`: pages `188` and `197-200` remained uncertain; page `195` was later rechecked and upgraded from uncertain to definite FAIL.
- `201-220`: pages `202` and `208` were later rechecked and shown to contain definite OCR defects; page `203` and page `210` were later confirmed PASS; pages `212-215` remain unresolved.

### Jackson_1999_Ch4_9_10

- `1-20`: page 2 equation `(4.3)` has the `r^{\prime\prime}` vs `r^{\prime l}` error.
- `41-60`: pages `64` and `71-72` are uncertain.
- No other uncertainty was reported for the remaining reviewed spans.

### Grahn_2012

- The later 12-page review is visually complete, but exact OCR fidelity is still unresolved because the OCR baseline is missing.

### Muhlig_2014

- `21-40`: OCR baseline could not be read because PowerShell returned access denied.

### Alaee_2018

- Formula fidelity on pages `2-4` remains uncertain because the required `pdf-mcp` path was unavailable.

## Verification Mode

### 已逐字核对

These spans explicitly compare rendered pages against an OCR/text baseline and complete a page-level review:

- `Fernandez-Corbaton_2015` `1-14`
- `Fernandez-Corbaton_2017` `1-8`
- `Bohren_Huffman_1983` `1-20`, `21-40`, `41-60`, `61-80`, `81-100`, `101-120`
- `Bohren_Huffman_1983` `121-123`, `181-187`, `189-194`, `196`, `201-220` sampled pages
- `Jackson_1999_Ch4_9_10` `1-20`, `21-40`, `41-60`, `61-80`, `81-85`
- `Muhlig_2014` `41-60`, `81-100`, `101-120`, `121-140`, `141-147`

### 仅视觉核对 / fallback

These spans relied on rendered pages and fallback extraction because the preferred OCR workflow was incomplete:

- `Grahn_2012` `1-12`
- `Alaee_2018` `1-5`
- `Muhlig_2014` `1-20`, `21-40`, `61-80`

### 未完成

These are genuine report gaps or incomplete spans, not just lower-confidence review:

- `Johnson_Christy_1972` has no strict OCR-backed reconciliation for `5-10`, and no page `11-12` exists in the current reviewed PDF
- `Bohren_Huffman_1983` partial uncertainty on `124-140`, `142/144-150/152/154/156/158-160`, `188`, `197-200`, `212-215`

## Report Conflicts and Tool Issues

- `Grahn_2012_review.md` is internally inconsistent:
  - an older zero-page failure note says no review could be done,
  - a later section reports a completed 12/12-page review.
  - The later 12-page review matches the rendered-page evidence, but the workflow remains fallback-based because `pdf-mcp` was unavailable and the OCR baseline is missing.
- `Grahn_2012_p001-012_pdf_mcp_transport_closed.md` explicitly records the transport failure.
- `Alaee_2018_review.md` explicitly states that the `pdf-mcp` workflow could not be completed.
- `Muhlig_2014_p021-040.md` reports OCR-baseline access denied.

## Evidence-Backed Markdown Errors

The following Markdown defects have explicit report evidence and are suitable for manual source correction when the relevant source Markdown is allowed to change:

- `Bohren_Huffman_1983` page 1 title block: `#of Light by Small Particles` -> `# of Light by Small Particles`
- `Bohren_Huffman_1983` pages `101-120`: `1` vs `l` mode-label confusion in `\psi`, `B`, `A`, `\mathbf{M}`, and `\mathbf{N}` notation
- `Bohren_Huffman_1983` page `185` / PDF page `195`: `\varepsilon_\mu` -> `\varepsilon_n`, `k_I` -> `k_L`, and `liandedness` -> `handedness`
- `Bohren_Huffman_1983` page `192` / PDF page `202`: equation `(8.22)` `E_R` line uses `\mathcal{R}` where the rendered page shows the same particle-density symbol used in the `E_L` line
- `Bohren_Huffman_1983` page `198` / PDF page `208`: `\xi = x \sin \xi` -> `\xi = x \sin \zeta`, `x = \mathrm{\~k\~} a` -> `x = ka`, and `a_{n1}` -> `a_{nI}`
- `Jackson_1999_Ch4_9_10` page 2 / page 41 equation `(4.3)`: `r^{\prime\prime}` -> `r^{\prime l}`
- `Jackson_1999_Ch4_9_10` page 32: malformed electric multipole coefficient equation
- `Jackson_1999_Ch4_9_10` page 38: Table 9.1 needs rebuild from render
- `Jackson_1999_Ch4_9_10` page 39: `Y_{I0}` -> `Y_{l0}`
- `Jackson_1999_Ch4_9_10` page 45: `Y_{I0}` -> `Y_{l0}`
- `Jackson_1999_Ch4_9_10` page 56: phase factors should be `e^{i m \phi} e^{i \beta z - i \omega t}`
- `Jackson_1999_Ch4_9_10` page 73: helicity coefficient labels need correction
- `Jackson_1999_Ch4_9_10` page 74: plane-wave expansion block needs correction
- `Jackson_1999_Ch4_9_10` page 77: impedance-boundary equations need correction
- `Jackson_1999_Ch4_9_10` page 80: optical-theorem field decomposition needs correction
- `Jackson_1999_Ch4_9_10` page 84: `\epsilon^2` -> `e^2`
- `Jackson_1999_Ch4_9_10` page 85: reference line breaks need restoration
- `Johnson_Christy_1972` page 1: `CONTANTS` -> `CONSTANTS`
- `Johnson_Christy_1972` continued review: author block spacing restored; Table II header `m 0` -> `m_0`; page 19 `\epsilon_s` -> `\epsilon_2`; page 19 `\omega_{\rho}` -> `\omega_p`

## Bottom Line

- Fully covered and cleanest: `Fernandez-Corbaton_2015`, `Fernandez-Corbaton_2017`, `Muhlig_2014`, `Grahn_2012` at the page-appearance level.
- Needs source Markdown correction: `Bohren_Huffman_1983`, `Johnson_Christy_1972`, `Jackson_1999_Ch4_9_10`.
- Needs more review or tool recovery before claiming full fidelity: `Grahn_2012`, `Alaee_2018`, `Johnson_Christy_1972` pages `5-10` if strict OCR fidelity is required, `Muhlig_2014` batch `21-40`, and several incomplete Bohren spans.
