# Bohren & Huffman 1983 chunk report: pages 141-160

source_file:
- PDF: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- OCR/Markdown baseline: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md`

page_range:
- Book pages `141-160`
- Note: the scanned PDF is offset by `+10` pages relative to the printed page numbers, so the verified PDF pages were `151-170`.

processed_pages:
- `141-160`

PASS:
- `141`
- `143`
- `151`
- `153`
- `155`
- `157`

FAIL:
- None found in the rendered pages or OCR cross-checks.

UNCERTAIN:
- `142`
- `144`
- `145`
- `146`
- `147`
- `148`
- `149`
- `150`
- `152`
- `154`
- `156`
- `158`
- `159`
- `160`

text_formula_findings:
- Page `141`: section `5.3 Ellipsoid in the Electrostatic Approximation` opens correctly; the prose about using electrostatics to compute polarizability is intact.
- Page `142`: the Rayleigh-scattering matrix block and figure labels are present, but the OCR tool only confirmed the page top / figure area; the dense math block needs higher-granularity recheck if exact glyph validation is required.
- Page `143`: the Rayleigh dimensional argument and equation `(5.6)` paragraph were recovered successfully; the wording around the inverse-fourth-power law is intact.
- Pages `144-150`: continuation of the ellipsoid / electrostatics derivation; page headers align with the expected section flow, but the body text was not fully re-OCRed at a confident level, so these remain `UNCERTAIN`.
- Page `151`: section transition into `5.5 The Polarizability Tensor` is correct; the surrounding prose about arbitrary particles in the electrostatic approximation matches the baseline.
- Page `153`: ellipsoidal-coordinate / octant discussion is readable and consistent with the baseline.
- Page `155`: section heading `5.7 Scattering Matrix` is correct.
- Page `157`: repeated section header for `5.7 Scattering Matrix` is correct and the page number progression is consistent.
- Pages `152`, `154`, `156`, `158-160`: OCR either only confirmed the page header or returned noise / timeout; no contradiction with the rendered page was found, but exact character-level verification is still incomplete.

layout_findings:
- The PDF renders cleanly with no obvious crop failures or missing scans in the target range.
- The printed-page offset is consistent across the inspected span, so the book-page range and PDF-page range are aligned once the `+10` offset is applied.
- Dense formula pages need smaller crops for OCR; full-page OCR is too slow or noisy on several pages, especially near the end of the chunk.

manual_actions:
- For exact glyph-level proofing, re-run pages `142`, `144-150`, `152`, `154`, `156`, `158-160` with finer crops or higher-resolution subimages.
- If the goal is a strict line-by-line OCR audit, the next pass should split those pages into smaller text blocks instead of whole-page or quarter-page slices.

next_pages:
- None for this assigned chunk.

