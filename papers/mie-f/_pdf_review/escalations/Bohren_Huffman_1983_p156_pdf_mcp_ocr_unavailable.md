# Escalation: Bohren_Huffman_1983 page 156 pdf-mcp OCR unavailable

- source_file: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- affected_pages: `156`
- reason: `pdf-mcp` OCR could not run in this session because the local Tesseract backend is missing, so `ocr_page()` raised `RuntimeError: No tessdata specified and Tesseract is not installed`.
- action: Install or point `pdf-mcp` at a working Tesseract/tessdata backend, then rerun the page-level OCR verification before relying on fresh OCR output for this page.
- current_status: PDF text extraction and render succeeded; OCR verification is blocked by the missing local OCR backend.
