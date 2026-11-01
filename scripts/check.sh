#!/bin/bash
# Fast repository checks. Run before every commit (see AGENTS.md).
set -uo pipefail
cd "$(dirname "$0")/.."
status=0

echo "== ruff"
ruff check . || status=1

echo "== shell syntax"
while IFS= read -r f; do
  bash -n "$f" || status=1
done < <(git ls-files --cached --others --exclude-standard -- '*.sh' .githooks)

echo "== em dash scan"
if git grep --untracked -nI $'\xe2\x80\x94' -- .; then
  echo "Found em dashes (U+2014) above. Replace them with a plain dash \"-\"."
  status=1
fi

if [ "$status" -eq 0 ]; then echo "All checks passed."; else echo "Checks failed."; fi
exit "$status"
