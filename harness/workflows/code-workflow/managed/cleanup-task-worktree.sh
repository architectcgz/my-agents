#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
workflow_enter_repo
exec python3 "$SCRIPT_DIR/cleanup_task_worktree.py" --repo-root "$WORKFLOW_REPO_ROOT" "$@"
