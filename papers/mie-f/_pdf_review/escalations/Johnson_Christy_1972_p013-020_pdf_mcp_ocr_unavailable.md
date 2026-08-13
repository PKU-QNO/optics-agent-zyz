# Johnson & Christy 1972 escalation

- Scope: pages `13-20` of `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Johnson_Christy_1972_Optical_Constants_of_the_Noble_Metals.pdf`
- Defect 1: `pdf_mcp.server.pdf_read_pages(..., ocr=True)` returned an OCR toolchain error because `tesseract` is not installed in this environment.
- Defect 2: the direct non-ASCII source path was not accepted by `pdf_mcp` in this session, so a temporary ASCII copy was required for render verification.
- Impact: the review could not perform a true `pdf-mcp` OCR-vs-PDF reconciliation for this span; the OCR baseline file had to serve as the text reference instead.
- Status: rendered-page inspection still completed successfully, and no source artifact was modified.
