# Escalation: Johnson_Christy_1972 pages 5-12 toolchain defect

- source_file: `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Johnson_Christy_1972_Optical_Constants_of_the_Noble_Metals.pdf`
- requested_pages: `5-12`
- observed_pages: `5-10`
- issue_type: `toolchain_defect`

## Details

- `pdf-mcp` was not available in this session, so the required PDF-to-OCR/Markdown verification path could not be executed.
- `firecrawl_parse` failed because `FIRECRAWL_API_URL` is not configured for a self-hosted Firecrawl instance in this environment.
- The OCR baseline file exists at `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr`, but it could not be used as a reliable verbatim baseline in this session.
- The PDF itself has only 10 pages, so the requested pages 11-12 are out of range.

## Action

- Rebuild or restore the OCR baseline, then rerun the 5-10 page batch with a working `pdf-mcp` or equivalent OCR backend and update the continued report with page-level PASS/FAIL/UNCERTAIN results.

