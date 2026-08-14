#!/usr/bin/bash
# compile.sh — LATEX 完整编译链（report-round2）
# 用法: ./compile.sh [main|DOCNAME]

set -euo pipefail

DOC=${1:-main}
OUT="${DOC}_aux"
DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"
mkdir -p "$OUT"

echo "[1/4] XeLaTeX (first pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"

echo "[2/4] BibTeX..."
if grep -q '\\bibdata' "$OUT/$DOC.aux"; then
  bibtex "$OUT/$DOC"
else
  echo "No bibliography declared; skipping BibTeX."
fi

echo "[3/4] XeLaTeX (second pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"

echo "[4/4] XeLaTeX (final pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$DOC"

echo "Done. PDF: $OUT/${DOC}.pdf"
ls -la "$OUT/${DOC}.pdf"
