#!/usr/bin/env bash
# Build cv.pdf from cv.tex. Pass --publish to copy it to the site root (../cv.pdf).
set -euo pipefail
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error cv.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error cv.tex >/dev/null
rm -f cv.aux cv.log cv.out
echo "built cv/cv.pdf"
if [[ "${1:-}" == "--publish" ]]; then
  cp cv.pdf ../cv.pdf
  echo "copied to ../cv.pdf"
fi
