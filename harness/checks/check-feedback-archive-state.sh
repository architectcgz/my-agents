#!/usr/bin/env bash
set -euo pipefail

cwd="."

if [[ "${1:-}" == "--cwd" ]]; then
  cwd="${2:?missing cwd value}"
  shift 2
fi

exec python3 "$HOME/.agents/harness/skill-sync/check_feedback_archive_state.py" --cwd "$cwd" "$@"
