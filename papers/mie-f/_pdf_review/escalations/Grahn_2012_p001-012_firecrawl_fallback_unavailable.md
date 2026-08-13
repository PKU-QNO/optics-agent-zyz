# Grahn 2012 fallback note

- Fallback parser: `firecrawl_parse`.
- Observed issue: the tool rejected the request because `FIRECRAWL_API_URL` is not set in this environment.
- Impact: the secondary document-parse fallback could not be used for this recheck run.
