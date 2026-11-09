#!/usr/bin/env bash
# Check, render diagrams, and build the uploadable bundle (md/pdf/tex) for one course.
# Usage: bash scripts/build_bundle.sh <slug>
# Generated courses are ignored by this repo, so this script never touches git.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:?usage: build_bundle.sh <slug>}"
DIR="$ROOT/courses/$SLUG"
[ -d "$DIR" ] || { echo "no such course: $DIR"; exit 1; }

python3 "$ROOT/scripts/check_course.py" "$DIR"
if [ -d "$ROOT/node_modules/beautiful-mermaid" ]; then
  node "$ROOT/scripts/render_diagrams.mjs" "$DIR" || echo "warning: some diagrams failed to render"
else
  echo "note: run 'npm install' in $ROOT to render diagrams to SVG"
fi

python3 "$ROOT/scripts/build_course.py" "$DIR"
echo "bundle: $DIR/dist"
