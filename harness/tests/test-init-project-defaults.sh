#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agents_home="$(cd "$script_dir/../.." && pwd)"
init_script="$agents_home/harness/init-project.sh"
sync_check="$agents_home/harness/workflow-sync-check.sh"
sync_script="$agents_home/harness/workflow-sync.sh"
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

[[ -d "$tmp_repo/.arccgz-harness/state/session-gates" ]] || {
  echo "FAIL: workflow state directory was not initialized" >&2
  exit 1
}

legacy_gate_dir="$tmp_repo/.harness/session-gates"
legacy_gate_path="$legacy_gate_dir/2026-08-04-state-migration.json"
mkdir -p "$legacy_gate_dir"
printf '{"task_slug":"2026-08-04-state-migration"}\n' > "$legacy_gate_path"
printf '/.harness/session-gates/\n/.harness/session-gates/\n' >> "$tmp_repo/.gitignore"

bash "$sync_script" "$tmp_repo" code-workflow >/dev/null

[[ -f "$tmp_repo/.arccgz-harness/state/session-gates/2026-08-04-state-migration.json" ]] || {
  echo "FAIL: workflow sync did not migrate legacy startup gate state" >&2
  exit 1
}
[[ ! -e "$tmp_repo/.harness/session-gates" ]] || {
  echo "FAIL: workflow sync left the legacy startup gate directory behind" >&2
  exit 1
}
if grep -qxF '/.harness/session-gates/' "$tmp_repo/.gitignore"; then
  echo "FAIL: workflow sync left the legacy gitignore rule behind" >&2
  exit 1
fi

WORKTREE_PARENT="$tmp_repo/.test-worktrees" \
  bash "$workflow_entry" "$tmp_repo" start global-runtime --dry-run > "$tmp_repo/start.out"
if ! grep -q 'DRY RUN: implementation workspace would be initialized' "$tmp_repo/start.out"; then
  echo "FAIL: global start command did not execute" >&2
  exit 1
fi
if ! grep -q -- '- gate: .arccgz-harness/state/session-gates/' "$tmp_repo/start.out"; then
  echo "FAIL: global start command did not target the harness state directory" >&2
  exit 1
fi

bash "$sync_check" "$tmp_repo" code-workflow >/dev/null

echo "PASS: init-project default skips full check and keeps code-workflow global"
