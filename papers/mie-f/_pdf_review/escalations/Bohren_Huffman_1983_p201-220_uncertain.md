# Escalation: Bohren_Huffman_1983 pages 201-220 partial OCR confirmation

- source_file: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Bohren_Huffman_1983_Absorption_and_Scattering_of_Light_by_Small_Particles.pdf`
- affected_pages: `202, 203, 208, 210, 212-215`
- reason: the pdf-mcp OCR/render calls in this session returned `Transport closed`, and the vision OCR service timed out on several dense pages in this range.
- observed_status: pages `201, 204-207, 209, 211, 216-220` were confirmed against rendered images and the baseline OCR Markdown; the remaining pages need a re-run for full verbatim certainty.
- action: rerun the uncertain pages with a healthier OCR/render path before marking the entire 201-220 chunk as fully confirmed.
