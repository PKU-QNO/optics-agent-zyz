# PDF Review Manual Actions

## Scope

- Reports read: `reports/Bohren_Huffman_1983_review.md`, `reports/Fernandez-Corbaton_2015_review.md`, `reports/Fernandez-Corbaton_2017_review.md`, `reports/Grahn_2012_review.md`, `reports/Johnson_Christy_1972_review.md`, `reports/Jackson_1999_Ch4_9_10_review.md`, `reports/Muhlig_2014_review.md`, `reports/Alaee_2018_review.md`
- Continued reports read: `reports/continued/Johnson_Christy_1972_p005-012_continued.md`, `reports/continued/Johnson_Christy_1972_p013-020_continued.md`, `reports/continued/Bohren_Huffman_1983_p195-195_continued.md`, `reports/continued/Bohren_Huffman_1983_p202-203_continued.md`, `reports/continued/Bohren_Huffman_1983_p208-208_continued.md`, `reports/continued/Bohren_Huffman_1983_p210-210_continued.md`, `reports/continued/Grahn_2012_recheck_A.md`, `reports/continued/Grahn_2012_recheck_B.md`
- Escalations read: `escalations/Bohren_Huffman_1983_uncertain.md`, `escalations/Bohren_Huffman_1983_p014_handwritten_note.md`, `escalations/Jackson_1999_Ch4_9_10_p02_formula_ocr.md`

## Changed Files

- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md`
- `papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md`

## Applied Fixes

- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md:3`
  - Changed `#of Light by Small Particles` to `# of Light by Small Particles`.
  - Evidence: `reports/Bohren_Huffman_1983_review.md` explicitly identified this Markdown syntax defect in the first title block.
- `papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md:29`
  - Changed `# II. EVALUATION OF OPTICAL CONTANTS` to `# II. EVALUATION OF OPTICAL CONSTANTS`.
  - Evidence: `reports/Johnson_Christy_1972_review.md` explicitly called out this section-title transcription error.
- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md:2482,2485,2520,2550,2556,2652,2670,4779,4783,4931,4937,4941`
  - Changed the report-backed `1` vs `l` OCR confusions in the mode labels from `o l n` / `e l n` to `o 1 n` / `e 1 n`, including `B_{oln}` -> `B_{o1n}`.
  - Evidence: `reports/chunks/Bohren_Huffman_1983_p101-120.md`.
- `papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md:3,173,177,201`
  - Restored the page-13 author/affiliation spacing, corrected the Table II mass header from `m 0` to `$m_0$`, and corrected the page-19 formula symbols `\epsilon_s` -> `\epsilon_2` and `\omega_{\rho}` -> `\omega_p`.
  - Evidence: `reports/continued/Johnson_Christy_1972_p013-020_continued.md`.
- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md:4842,4846,4858,5079,5250-5258`
  - Corrected continued-review FAILs: `\varepsilon_\mu` -> `\varepsilon_n`, `liandedness` -> `handedness`, `k_I` -> `k_L`, `(8.22)` `E_R` line `\mathcal{R}` -> `\mathfrak{N}`, and the cylinder-scattering page fixes `\xi = x \sin \zeta`, `x = ka`, `a_{n1}/b_{n1}` -> `a_{nI}/b_{nI}`.
  - Evidence: `reports/continued/Bohren_Huffman_1983_p195-195_continued.md`, `reports/continued/Bohren_Huffman_1983_p202-203_continued.md`, and `reports/continued/Bohren_Huffman_1983_p208-208_continued.md`.

## Rejected Or Uncertain Findings

- `reports/Jackson_1999_Ch4_9_10_review.md` and `escalations/Jackson_1999_Ch4_9_10_p02_formula_ocr.md`
  - The escalation claims page 2 has `r^{\prime\prime}` in equation (4.3), but the current OCR Markdown already contains `r^{\prime l}` at the corresponding location.
  - No source Markdown change was made because the report and the current OCR file conflict.
- `reports/Bohren_Huffman_1983_review.md` and `escalations/Bohren_Huffman_1983_p014_handwritten_note.md`
  - The handwritten marginal note on page 14 is outside the plain-text OCR scope.
  - No transcription was attempted because the report itself recommends a higher-resolution re-scan if that note must be captured.
- `reports/continued/Bohren_Huffman_1983_p210-210_continued.md`
  - Page 210 was rechecked and is PASS; no source change was needed.
- `reports/continued/Grahn_2012_recheck_A.md`, `reports/continued/Grahn_2012_recheck_B.md`
  - The visual rechecks are complete, but the OCR baseline is still missing, so no source Markdown patch is justified.
- `reports/continued/Johnson_Christy_1972_p005-012_continued.md`
  - The current source PDF ends at page 10. Pages 5-10 remain visual-only because the OCR baseline is unusable, so no verbatim patch was applied there.
- `reports/Grahn_2012_review.md`
  - The report says the expected OCR baseline was missing and `pdf-mcp` was unavailable.
  - No Markdown fix was safe to apply without a verified OCR source.
- `reports/Alaee_2018_review.md`
  - The report marks formula fidelity as uncertain because `pdf-mcp` was unavailable for the required workflow.
  - No direct Markdown error was proven, so no change was made.
- `reports/Fernandez-Corbaton_2015_review.md`, `reports/Fernandez-Corbaton_2017_review.md`, and `reports/Muhlig_2014_review.md`
  - These reports did not identify direct Markdown defects requiring source edits.

## Unprocessed Items

- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md:2189`
  - `#by a Sphere` was left untouched because the review only described it as a slightly malformed heading, not a deterministic source error.
- `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md`
  - The page-14 handwritten marginal note was not transcribed because the report explicitly places it outside plain OCR scope.

## Notes

- No source PDF or OCR baseline artifact was modified.
- Only report-backed text defects were applied to the source Markdown.
