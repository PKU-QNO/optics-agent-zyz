#!/usr/bin/bash
# compile.sh — LATEX 编译链（vector-multipole-derivation）
# 用法: ./compile.sh   （输出到 main_aux/）

DOC=main
OUT="${DOC}_aux"
DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"
mkdir -p "$OUT"
# \include 的章节 aux 会写到 $OUT/sections/ 下，需预建
mkdir -p "$OUT/sections"

export PATH="/d/Download/texlive/2026/bin/windows:$PATH"

echo "[1/2] XeLaTeX (first pass)..."
xelatex -interaction=nonstopmode -output-directory="$OUT" "$DOC" > "$OUT/pass1.log" 2>&1

echo "[2/2] XeLaTeX (second pass)..."
xelatex -interaction=nonstopmode -output-directory="$OUT" "$DOC" > "$OUT/pass2.log" 2>&1

if [ -f "$OUT/$DOC.pdf" ]; then
    echo "Done. PDF: $OUT/$DOC.pdf"
else
    echo "FAILED. Errors:"
    grep -n "^!" "$OUT/$DOC.log" | head -20
fi
