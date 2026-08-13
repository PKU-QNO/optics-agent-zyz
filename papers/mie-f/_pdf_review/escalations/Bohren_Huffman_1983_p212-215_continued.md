# Escalation: Bohren_Huffman_1983 pages 212-215 continued review

- source_file: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- page_range: `212-215`

## Issue

- The OCR baseline line 5361 on PDF page 212 misreads Roman numeral subscripts in the matrix-form scattering expansion, using `1`/`11` where the rendered page clearly shows `I`/`II`.

## Impact

- This is a baseline transcription defect, not a page-image legibility problem.
- Downstream verbatim reuse should not copy the OCR line for the page 212 formula block without checking the render.

## Resolution

- PDF pages `212-215` are treated as `PASS` after the high-resolution render review.
- The only issue that remains is the OCR baseline drift on page 212, which should be corrected from the render if a clean verbatim transcription is needed.
