# Bohren_Huffman_1983 PDF Review

- source_file: `C:\Users\27370\Desktop\project\optics_agent\papers\mie-f\03-参考与工具\Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- page_range: `101-120`
- processed_pages: `101-120`
- PASS: `17`
- FAIL: `2`
- UNCERTAIN: `1`

## text_formula_findings

- The chapter transition into Chapter 4 is present and the main section flow is intact: `4.1 Solutions to the Vector Wave Equations`, `4.2 Expansion of a Plane Wave in Vector Spherical Harmonics`, and the opening of `4.3 The Internal and Scattered Fields` all appear in order.
- The OCR Markdown preserves the displayed equations for the vector wave equation, the scalar wave equation in spherical coordinates, the Bessel-function definitions, the vector spherical harmonics, the plane-wave expansion, and the boundary-condition system for the sphere.
- Clear OCR formula errors are present in this batch: several subscripts that should be `1` are rendered as lowercase `l`, e.g. `\psi_{o1n}` / `\psi_{e1n}` become `\psi_{oln}` / `\psi_{eln}`, and the same substitution repeats in `B_{oln}`, `A_{eln}`, `\mathbf{M}_{oln}`, `\mathbf{N}_{eln}`, and the later rotation identity for `\mathbf{M}` / `\mathbf{N}`.
- Because those subscripts are part of the mode labels, the error is not cosmetic; it changes the mathematical notation in the OCR Markdown and should be treated as a FAIL for formula fidelity.
- The text reference to Fig. 4.2 is present in the prose, but a standalone figure caption block for Fig. 4.2 was not found in the OCR Markdown for this batch.

## layout_findings

- Page order through the start of Chapter 4 is consistent, and the long derivation in Section 4.2 continues without obvious page jumps.
- Figure captions that are explicitly present in the OCR Markdown, such as Figure 4.1, Figure 4.3, Figure 4.4, and Figure 4.5, are in the expected narrative positions.
- The Chapter 4 opener uses a Markdown heading split that looks slightly malformed in the OCR source (`#by a Sphere`), but the surrounding content is still readable and in the correct location.
- I could not complete independent visual OCR on the rendered PNGs in this session because the available vision OCR path timed out on the page images.

## manual_actions

- Re-run a single-page OCR/visual check on the rendered page that contains Fig. 4.2 if its caption or placement must be confirmed.
- If this batch is later used for source Markdown correction, normalize the repeated `1` vs `l` subscript confusion in the `o1n` / `e1n` mode labels before applying any edits.

## next_pages

- `121-140`
