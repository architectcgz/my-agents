#!/usr/bin/env bash
set -euo pipefail

cwd="."

if [[ "${1:-}" == "--cwd" ]]; then
  cwd="${2:?missing cwd value}"
  shift 2
fi

exec python3 "$HOME/.agents/harness/skill-sync/remind_skill_sync.py" --cwd "$cwd" "$@"
