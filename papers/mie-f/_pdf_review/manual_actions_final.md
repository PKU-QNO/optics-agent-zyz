# PDF Review Manual Actions Final

This file consolidates the evidence-backed Markdown fixes and the review tasks that still require human action. It does not modify source PDFs, OCR baselines, original Markdown, or project rules.

## Already Applied Earlier

- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md:3`
  - `#of Light by Small Particles` -> `# of Light by Small Particles`
- `papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md:29`
  - `# II. EVALUATION OF OPTICAL CONTANTS` -> `# II. EVALUATION OF OPTICAL CONSTANTS`

## Evidence-Backed Markdown Corrections Still Worth Applying

### Bohren_Huffman_1983

- Page 1 title block spacing defect has already been corrected in source.
- Pages `101-120` `1` vs `l` mode-label confusion has already been corrected in source.
- Additional report-backed fixes from continued review have now been applied in source:
  - page `185` / PDF page `195`: `\varepsilon_\mu` -> `\varepsilon_n`, `k_I` -> `k_L`, `liandedness` -> `handedness`
  - page `192` / PDF page `202`: equation `(8.22)` `E_R` line `\mathcal{R}` -> `\mathfrak{N}`
  - page `198` / PDF page `208`: `\xi = x \sin \xi` -> `\xi = x \sin \zeta`, `x = \mathrm{\~k\~} a` -> `x = ka`, `a_{n1}` / `b_{n1}` -> `a_{nI}` / `b_{nI}`
- The report-noted malformed Chapter 4 opener around `#by a Sphere` remains intentionally unedited because the evidence still does not prove the exact target text.

### Jackson_1999_Ch4_9_10

- Page 2 / 41 equation `(4.3)`:
  - replace `r^{\prime\prime}` with `r^{\prime l}`
- Page 32:
  - rebuild the long electric multipole coefficient equation from the rendered page
- Page 38:
  - rebuild Table 9.1 from the render rather than trusting the OCR table
- Page 39:
  - replace `Y_{I0}` with `Y_{l0}`
- Page 41:
  - same `r^{\prime\prime}` -> `r^{\prime l}` issue appears again in the later batch
- Page 45:
  - replace `Y_{I0}` with `Y_{l0}`
- Page 56:
  - restore `e^{i m \phi} e^{i \beta z - i \omega t}`
- Page 73:
  - fix the helicity-dependent multipole coefficient labels
- Page 74:
  - fix the corrupted plane-wave expansion block
- Page 77:
  - fix the impedance-boundary equations and symbol labels
- Page 80:
  - restore the optical-theorem field decomposition
- Page 84:
  - replace `\epsilon^2` with `e^2`
- Page 85:
  - restore printed reference-list line breaks

### Johnson_Christy_1972

- Page 1 `CONTANTS` -> `CONSTANTS` has already been corrected in source.
- Additional report-backed fixes from the continued review have now been applied in source:
  - author/affiliation line spacing restored
  - Table II header `m 0` -> `$m_0$`
  - page 19 `\epsilon_s` -> `\epsilon_2`
  - page 19 `\omega_{\rho}` -> `\omega_p`

## Do Not Auto-Edit

These items should stay human-reviewed because the current evidence is insufficient for automatic Markdown patching:

- `Bohren_Huffman_1983` page 14 handwritten marginal note
- `Bohren_Huffman_1983` pages `124-140`
- `Bohren_Huffman_1983` pages `142`, `144-150`, `152`, `154`, `156`, `158-160`
- `Bohren_Huffman_1983` pages `188`, `197-200`
- `Bohren_Huffman_1983` pages `203`, `210`, `212-215`
- `Johnson_Christy_1972` pages `4` and `5-10` until a usable OCR baseline is restored
- `Johnson_Christy_1972` pages `11-12` only if a different source PDF proves they should exist
- `Grahn_2012` until the OCR baseline is restored and the pdf-mcp workflow is available again
- `Alaee_2018` until the strict `pdf-mcp` workflow can be rerun
- `Muhlig_2014` pages `21-40` if verbatim OCR comparison is required, because the OCR baseline was access-denied

## Coverage Gaps That Still Need Review

- `Johnson_Christy_1972` pages `11-12` only if a different source PDF is supplied; the current file ends at page `10`

## Operational Notes

- `Grahn_2012_review.md` contains an internal conflict between an older zero-page failure note and a later completed 12-page review.
- `pdf-mcp` was unavailable for `Grahn_2012` and `Alaee_2018`.
- `Muhlig_2014` `21-40` could not compare against the OCR baseline because PowerShell reported access denied.
- The source PDFs and OCR baselines remain untouched; only report-backed Markdown source fixes were applied.
