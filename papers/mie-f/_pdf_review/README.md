# PDF review staging area

This directory stores the intermediate audit trail for PDF-to-text/Markdown review.

- reports/: reports written by pdf_short_proofreader and pdf_long_proofreader.
- escalations/: pages requiring single-page high-resolution review or human action.
- manual_actions.md: consolidated requests for rescanning or human confirmation, written by pdf_report_applier.

The review agents must not modify source PDFs, .ocr files, or source Markdown outside this directory. The final agent may modify source Markdown only when a report contains sufficient evidence.
