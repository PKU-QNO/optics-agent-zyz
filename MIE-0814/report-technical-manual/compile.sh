#!/usr/bin/bash
set -euo pipefail
DOC=${1:-main}
OUT="${DOC}_aux"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
mkdir -p "$OUT"
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"
if grep -q '\\bibdata' "$OUT/$DOC.aux"; then bibtex "$OUT/$DOC"; fi
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"
echo "Done. PDF: $OUT/${DOC}.pdf"
pdfinfo "$OUT/${DOC}.pdf" | grep -E 'Pages|Page size'
