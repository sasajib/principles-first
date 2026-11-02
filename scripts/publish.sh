#!/usr/bin/env bash
# Check, render diagrams, commit and push one course.
# Usage: bash scripts/publish.sh <slug> [commit message]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:?usage: publish.sh <slug> [message]}"
MSG="${2:-course: ${SLUG}}"
DIR="$ROOT/courses/$SLUG"
[ -d "$DIR" ] || { echo "no such course: $DIR"; exit 1; }

python3 "$ROOT/scripts/check_course.py" "$DIR"
if [ -d "$ROOT/node_modules/beautiful-mermaid" ]; then
  node "$ROOT/scripts/render_diagrams.mjs" "$DIR" || echo "warning: some diagrams failed to render"
else
  echo "note: run 'npm install' in $ROOT to render diagrams to SVG"
fi

cd "$ROOT"
git add "courses/$SLUG"
if git diff --cached --quiet; then
  echo "nothing to commit for $SLUG"
else
  git commit -q -m "$MSG"
  echo "committed: $MSG"
fi
if git remote get-url origin >/dev/null 2>&1; then
  git push -q origin HEAD && echo "pushed to $(git remote get-url origin)"
else
  echo "no git remote configured; commit is local only"
fi
