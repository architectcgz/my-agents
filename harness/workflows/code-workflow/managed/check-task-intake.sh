#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"
workflow_enter_repo

todo_check="$WORKFLOW_REPO_ROOT/.arccgz-harness/scripts/checks/check-open-todos.sh"
if [[ ! -x "$todo_check" ]]; then
  todo_check="$WORKFLOW_REPO_ROOT/scripts/checks/check-open-todos.sh"
fi

if [[ -x "$todo_check" ]]; then
  bash "$todo_check" --quiet-if-empty
fi

echo "PASS: task intake reminder completed"
echo "- non-trivial or protected implementation should start with: bash $(workflow_entry) $WORKFLOW_REPO_ROOT start <topic-or-slug>"
echo "- before finalizing the plan, run the intake analysis gate: relevant analysis skill first, then grill-with-docs"
