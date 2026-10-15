#!/usr/bin/env bash
# Build dist/index.html from Oxford's licensed files. Usage: ./build.sh [path to the Oxford data folder]
# The data folder must hold "Global Cities Index data.xlsx", "City reference.xlsx" and "City reference.gpkg".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA="$(cd "${1:-$ROOT/..}" && pwd)"
WORK="$ROOT/build"; mkdir -p "$WORK"; cd "$WORK"
for f in "Global Cities Index data.xlsx" "City reference.xlsx"; do ln -sf "$DATA/$f" "$f"; done
cp "$ROOT"/scripts/*.py .
python3 city_xy.py "$DATA/City reference.gpkg"
python3 gen_v6.py          # conn_data.json: Oxford 2026 scores, raw values, fitted pillar weights
python3 model_params.py    # model_params.json: fitted raw-to-score curves (post-hoc)
python3 story_data.py      # story_data.json: what the page needs
python3 assemble.py "$ROOT"
echo "Done. Open dist/index.html in a browser."
