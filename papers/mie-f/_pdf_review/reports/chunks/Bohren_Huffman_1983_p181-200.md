# Bohren_Huffman_1983 p181-200

- source_file: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- page_range: `181-200`
- processed_pages: `181-200` with partial verification on `188`, `195`, `197-200`

## PASS

- `181-187`
- `189-194`
- `196`

## FAIL

- None confirmed.

## UNCERTAIN

- `188`
- `195`
- `197-200`

## Page Log

| PDF page | Status | Notes |
|---|---|---|
| 181 | PASS | Section 7.1 start; Fig. 7.3; Eq. (7.5), (7.6), (7.7) captured. |
| 182 | PASS | Section 7.1.1; Fig. 7.4; Eq. (7.8) context; table/value discussion. |
| 183 | PASS | Section 7.1.2; Table 7.1; Eq. (7.8) series for transmission. |
| 184 | PASS | Section 7.2 start; rainbow-angle derivation; Eq. (7.9), (7.10), (7.11), (7.12), (7.13), (7.14), (7.15). |
| 185 | PASS | Section 7.2 continuation; Eq. (7.14)-(7.15) evaluation and rainbow-angle discussion. |
| 186 | PASS | Section 7.2 continuation; halo widths, Alexander's dark band, and supernumerary bows. |
| 187 | PASS | Section 7.3 start; Eq. (7.16); prism/ice-crystal halo discussion; Fig. 7.6. |
| 188 | UNCERTAIN | Upper half OCR timed out; lower half only recovered Fig. 7.5 prism diagram and labels. |
| 189 | PASS | Section 7.3 continuation; halo-angle evaluation and Notes/Comments transition. |
| 190 | PASS | Notes and Comments for Chapter 7; end of chapter. |
| 191 | PASS | Chapter 8 opener and 8.1 Coated Sphere introduction. |
| 192 | PASS | Fig. 8.1 coated sphere; field expansions; boundary conditions; Eq. (8.1). |
| 193 | PASS | Coated-sphere coefficients; Eq. (8.2); reduction checks. |
| 194 | PASS | Section 8.2 Anisotropic Sphere; average cross section Eq. (8.3). |
| 195 | UNCERTAIN | 8.3 Optically Active Particles introduction captured only in part; lower half timed out. |
| 196 | PASS | Optical activity Maxwell equations and matrix form; Eq. (8.6) to (8.9). |
| 197 | UNCERTAIN | Full-page OCR timeout at lower DPI. |
| 198 | UNCERTAIN | Full-page OCR timeout. |
| 199 | UNCERTAIN | Not fully extracted in this batch. |
| 200 | UNCERTAIN | Not fully extracted in this batch. |

## text_formula_findings

- `181-183`: Chapter 7.1/7.1.1/7.1.2 are consistent with the PDF render. Eq. (7.5) reflection efficiency, Eq. (7.6) asymptotic scattering efficiency, Eq. (7.7) absorption limit, and Table 7.1 values were read cleanly.
- `184-186`: Rainbow-angle derivation is consistent. Eq. (7.9)-(7.15) were recovered, including the minimum-deviation condition, primary/secondary rainbow angles, and Alexander's dark band.
- `187-190`: Prisms and ice-crystal haloes are consistent with the render. Fig. 7.5 and Fig. 7.6 are present; Eq. (7.16) and the chapter notes/comments are legible.
- `191-193`: Chapter 8 coated-sphere setup is consistent. Fig. 8.1, the layered-sphere field expansions, boundary conditions, and Eq. (8.1)-(8.2) were extracted, including the reduction checks for `m_1 = m_2`, `a -> 0`, and `m_2 = 1`.
- `194-196`: Anisotropic-sphere and optically active-particle sections are consistent. Eq. (8.3), (8.4), (8.6), (8.7), (8.8), and (8.9) were recovered, including the `k_L`/`k_R` definitions and the matrix form of the electromagnetic field equations.
- `188`, `195`, `197-200`: Page-level text/formula confirmation is incomplete because OCR timed out on the dense regions.

## layout_findings

- The pages are predominantly single-column textbook layout with centered display equations and right-aligned equation numbers.
- Figures and tables are full-width or near full-width: Fig. 7.3, Fig. 7.4, Table 7.1, Fig. 7.5, Fig. 7.6, Fig. 8.1.
- Chapter transitions are visually clear: Chapter 8 opens on page 191, followed by subsection headers `8.1`, `8.2`, and `8.3`.
- The dense derivation pages around the coated sphere and optical activity sections are the hardest for OCR, especially where several centered equations appear in succession.

## manual_actions

- Re-run page `188` with an upper-half crop or smaller quadrants; the upper half timed out.
- Re-run page `195` with a lower-half crop; the lower half timed out.
- Re-run pages `197-200` with lower DPI plus quarter-page crops, or switch to a different OCR backend if available.
- Do not overwrite the original PDF, OCR directory, or any source Markdown; keep follow-up outputs in the chunk-report/escalation area only.

## next_pages

- No next pages within the assigned scope.
- If continuing this batch, start with `188` upper crop, then `195` lower crop, then `197-200` quarter crops.
