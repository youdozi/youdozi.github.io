#!/bin/sh
set -eu
MONITOR_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$MONITOR_ROOT"
if [ "$(git symbolic-ref --quiet --short HEAD)" != main ]; then
  echo 'Weekly search monitor deferred: checkout must be on main.'
  exit 75
fi
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo 'Weekly search monitor deferred: tracked worktree changes are present.'
  exit 75
fi
exec "$MONITOR_ROOT/.venv-search-console/bin/python" -B "$MONITOR_ROOT/scripts/search_monitor.py" weekly --live --scheduled
