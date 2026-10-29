#!/usr/bin/env bash
# Fortnightly NDIS watch, built for cron: silent when nothing has moved.
#
# 1. check the ten official sources plus the shipped library
# 2. on change: refresh the library, commit, push, and print what moved so the cron can deliver it
#
# Run by hand any time with:  bash scripts/ndis_watch_cron.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PY=${PY:-python}
OUT=$("$PY" scripts/ndis_watch.py --json 2>&1)
CODE=$?

if [ "$CODE" -eq 0 ]; then
  exit 0                     # nothing changed: say nothing
fi

echo "$OUT" | tail -c 4000
echo

"$PY" scripts/fetch-ndis-docs.py >/dev/null 2>&1 || echo "library refresh failed; sources above still stand"

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git -c user.name="NeuroFamily NDIS watch" -c user.email="boktoday@gmail.com" \
      commit -q -m "NDIS watch: refresh library $(date +%F)"
  TOK=$(grep -o 'gh[pousr]_[A-Za-z0-9_]*' "$HOME/.git-credentials" 2>/dev/null | head -1)
  SLUG=$(git config --get remote.origin.url | sed -E 's#.*github\.com[:/]([^/]+/[^/.]+)(\.git)?#\1#')
  if [ -n "$TOK" ] && [ -n "$SLUG" ]; then
    GIT_TERMINAL_PROMPT=0 git -c credential.helper= \
      push "https://x-access-token:$TOK@github.com/$SLUG.git" HEAD:main \
      && echo "pushed to $SLUG"
  else
    echo "no token or remote found: commit made locally, push skipped"
  fi
fi
