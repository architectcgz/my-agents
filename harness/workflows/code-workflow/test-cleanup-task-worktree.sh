#!/usr/bin/env bash
set -euo pipefail

tmp_repo="$(mktemp -d /tmp/code-workflow-cleanup-test.XXXXXX)"
cleanup() {
  rm -rf "$tmp_repo"
}
trap cleanup EXIT

git init "$tmp_repo" >/dev/null
git -C "$tmp_repo" config user.email "agent@example.invalid"
git -C "$tmp_repo" config user.name "Agent Test"
printf 'initial\n' > "$tmp_repo/README.md"
git -C "$tmp_repo" add README.md
git -C "$tmp_repo" commit -m "chore: initial" >/dev/null

bash "$(dirname "${BASH_SOURCE[0]}")/../../workflow-installer.sh" "$tmp_repo" code-workflow >/dev/null

cleanup_script="$tmp_repo/harness/workflow-plugins/code-workflow/cleanup_task_worktree.sh"
cleanup_helper="$tmp_repo/harness/workflow-plugins/code-workflow/cleanup_task_worktree.py"

[[ -x "$cleanup_script" ]] || {
  echo "FAIL: cleanup shell entry is missing or not executable" >&2
  exit 1
}
[[ -f "$cleanup_helper" ]] || {
  echo "FAIL: cleanup Python helper is missing" >&2
  exit 1
}

bash "$(dirname "${BASH_SOURCE[0]}")/../../workflow-sync-check.sh" "$tmp_repo" code-workflow >/dev/null
git -C "$tmp_repo" add .
git -C "$tmp_repo" commit -m "chore: install workflow" >/dev/null

task_slug="2026-06-20-cleanup-test"
gate_dir="$tmp_repo/.harness/session-gates"
gate_path="$gate_dir/$task_slug.json"
mkdir -p "$gate_dir"
cat > "$gate_path" <<EOF
{
  "task_slug": "$task_slug",
  "status": "ready_to_merge",
  "branch": "task/$task_slug",
  "worktree_path": "$tmp_repo"
}
EOF

(
  cd "$tmp_repo"
  bash "$cleanup_script" \
    --task-slug "$task_slug" \
    --branch "task/$task_slug" \
    --worktree "$tmp_repo" \
    --merged-into HEAD \
    --keep-branch >/dev/null
)

python3 - "$gate_path" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "archived", payload
assert payload["merged_into"] == "HEAD", payload
assert payload["removed_worktree"] is False, payload
assert "closed_at" in payload, payload
PY

task_slug="2026-06-20-dedicated-cleanup"
task_branch="task/$task_slug"
task_worktree="$(mktemp -d /tmp/code-workflow-task-worktree.XXXXXX)"
rm -rf "$task_worktree"
git -C "$tmp_repo" worktree add -b "$task_branch" "$task_worktree" HEAD >/dev/null

gate_dir="$task_worktree/.harness/session-gates"
gate_path="$gate_dir/$task_slug.json"
mkdir -p "$gate_dir"
cat > "$gate_path" <<EOF
{
  "task_slug": "$task_slug",
  "status": "ready_to_merge",
  "branch": "$task_branch",
  "worktree_path": "$task_worktree"
}
EOF

(
  cd "$tmp_repo"
  bash "$cleanup_script" \
    --task-slug "$task_slug" \
    --branch "$task_branch" \
    --worktree "$task_worktree" \
    --merged-into HEAD >/dev/null
)

[[ ! -d "$task_worktree" ]] || {
  echo "FAIL: dedicated task worktree was not removed" >&2
  exit 1
}
if git -C "$tmp_repo" rev-parse --verify --quiet "$task_branch" >/dev/null; then
  echo "FAIL: merged task branch was not deleted" >&2
  exit 1
fi

echo "PASS: cleanup task worktree package test passed"
