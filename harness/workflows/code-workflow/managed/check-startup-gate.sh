#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"
workflow_enter_repo

python3 "$script_dir/check_startup_gate.py" --repo-root "$WORKFLOW_REPO_ROOT" "$@"
