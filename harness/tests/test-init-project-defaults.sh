#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agents_home="$(cd "$script_dir/../.." && pwd)"
init_script="$agents_home/harness/init-project.sh"
sync_check="$agents_home/harness/workflow-sync-check.sh"
workflow_entry="$agents_home/harness/workflows/code-workflow/workflow.sh"

tmp_repo="$(mktemp -d /tmp/init-project-defaults.XXXXXX)"
cleanup() {
  rm -rf "$tmp_repo"
}
trap cleanup EXIT

export AGENTS_HOME="$agents_home"

git init "$tmp_repo" >/dev/null
git -C "$tmp_repo" config user.email "agent@example.invalid"
git -C "$tmp_repo" config user.name "Agent Test"
printf 'initial\n' > "$tmp_repo/README.md"
git -C "$tmp_repo" add README.md
git -C "$tmp_repo" commit -m "chore: initial" >/dev/null

bash "$init_script" "$tmp_repo" > "$tmp_repo/init.out"

if grep -q 'run project harness consistency check' "$tmp_repo/init.out"; then
  echo "FAIL: init-project.sh must not run the full consistency gate by default" >&2
  exit 1
fi
if ! grep -q 'skip full harness consistency check' "$tmp_repo/init.out"; then
  echo "FAIL: init-project.sh did not report the default full-check skip" >&2
  exit 1
fi

for path in \
  "scripts/workflows/start-implementation.sh" \
  "harness/workflow-plugins/code-workflow/run_workflow_stage.sh" \
  ".arccgz-harness/scripts/workflows/start-implementation.sh" \
  ".arccgz-harness/harness/templates/implementation-plan-skeleton.md"; do
  if [[ -e "$tmp_repo/$path" ]]; then
    echo "FAIL: initializer copied global code-workflow asset into repository: $path" >&2
    exit 1
  fi
done

[[ -d "$tmp_repo/.harness/session-gates" ]] || {
  echo "FAIL: workflow state directory was not initialized" >&2
  exit 1
}

WORKTREE_PARENT="$tmp_repo/.test-worktrees" \
  bash "$workflow_entry" "$tmp_repo" start global-runtime --dry-run > "$tmp_repo/start.out"
if ! grep -q 'DRY RUN: implementation workspace would be initialized' "$tmp_repo/start.out"; then
  echo "FAIL: global start command did not execute" >&2
  exit 1
fi

bash "$sync_check" "$tmp_repo" code-workflow >/dev/null

echo "PASS: init-project default skips full check and keeps code-workflow global"
