#!/usr/bin/bash
# compile.sh — LATEX 完整编译链（report-round1）
# 用法: ./compile.sh [main|DOCNAME]

DOC=${1:-main}
OUT="${DOC}_aux"
DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"
mkdir -p "$OUT"

echo "[1/4] XeLaTeX (first pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="$OUT" "$DOC" > /dev/null 2>&1

echo "[2/4] BibTeX..."
bibtex "$OUT/$DOC" > /dev/null 2>&1

echo "[3/4] XeLaTeX (second pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="$OUT" "$DOC" > /dev/null 2>&1

echo "[4/4] XeLaTeX (final pass)..."
xelatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="$OUT" "$DOC" > /dev/null 2>&1

echo "Done. PDF: $OUT/${DOC}.pdf"
ls -la "$OUT/${DOC}.pdf"
