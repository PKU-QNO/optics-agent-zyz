# Johnson & Christy 1972 continued report: pages 13-20

source_file:
- PDF: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Johnson_Christy_1972_Optical_Constants_of_the_Noble_Metals.pdf`
- OCR/Markdown baseline: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md`

page_range:
- `13-20`

processed_pages:
- `13-20`

PASS:
- Pages `13-20` preserve the article flow, two-column layout, section headings, and the placement of Figures 1-8 and Tables I-II.
- The rendered pages are cleanly readable with no rotation, crop loss, duplicated pages, or missing-page break.
- The main body text across the introduction, experimental method, results, and discussion remains faithful to the rendered PDF.

FAIL:
- Page `13`: the title/author block is run together in the OCR baseline, with `ChristyDepartment` missing the expected word break before the affiliation line.
- Page `18`: Table II loses the subscripted mass notation in the header, reading `m 0` instead of `m_0`.
- Page `19`: the free-electron derivation mistranscribes the dielectric notation, reading `\epsilon_s` where the rendered page shows the corresponding `\epsilon_2` term.
- Page `19`: the same derivation also mistranscribes the plasma-frequency symbol as `\omega_{\rho}` instead of the rendered `\omega_p`.

UNCERTAIN:
- None established for this span after render-vs-OCR comparison.

text_formula_findings:
- Pages `13-14`: the introduction and Section II prose line up with the rendered pages; Figure 1 and the discussion of contour intersections are placed correctly.
- Pages `15-16`: Section III and Figure 2 are intact, and Table I is preserved as a readable markdown table with the copper/silver/gold values in order.
- Pages `17-18`: the start of Section V, Figures 3-5, and the transition into the free-electron discussion are all present in the right order.
- Pages `18-20`: Table II, Figures 6-8, and the copper/silver/gold comparison paragraphs remain legible; the only clear formula-level fidelity issues in this span are the `m_0`, `\epsilon_2`, and `\omega_p` substitutions noted above.

layout_findings:
- The rendered PDF keeps the expected Physical Review B journal header/footer, page numbering, and two-column composition throughout the span.
- Table I spans the page cleanly, and Table II plus Figures 6-8 do not clip or overlap surrounding prose.
- Captions for Figures 1-8 are in the correct locations relative to their plots and remain readable at page scale.

manual_actions:
- `pdf-mcp` OCR could not be used directly because `tesseract` is missing in this environment; the review therefore used the OCR baseline plus rendered-page inspection for fidelity checks.
- The source PDF path contains non-ASCII characters that `pdf_mcp` did not resolve directly, so a temporary ASCII-named copy was used for render verification only.
- No source PDF, OCR baseline, or original Markdown file was modified.

next_pages:
- `21-22`
