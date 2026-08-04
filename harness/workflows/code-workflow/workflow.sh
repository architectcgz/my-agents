#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGED_DIR="$SCRIPT_DIR/managed"
source "$MANAGED_DIR/common.sh"
AGENTS_HOME="${AGENTS_HOME:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
export AGENTS_HOME
SCAFFOLD_VERSION="$(python3 -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["version"])' "$SCRIPT_DIR/manifest.json")"

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> <command> [args...]

Commands:
  install [--dry-run]       Register the global workflow for a repository; no workflow files are copied.
  sync [--dry-run]          Remove legacy managed copies, then register the global workflow.
  --check                   Verify global runtime availability and that no managed copies remain in the repository.
  intake                    Run the project todo/intake reminder.
  start <topic-or-slug>     Create a task worktree, implementation plan, and startup gate.
  gate [args...]            Validate or inspect the startup gate.
  task-group [args...]      Validate a task-group dependency index.
  stage <name> [args...]    Run optional project-local plugins for a workflow stage.
  archive [args...]         Archive completed task artifacts.
  cleanup [args...]         Safely close an already-merged task worktree.
EOF
}

resolve_repo_root() {
  local target="$1"
  if [[ ! -d "$target" ]] || ! git -C "$target" rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "FAIL: target is not a git repository: $target" >&2
    exit 1
  fi
  git -C "$target" rev-parse --show-toplevel
}

required_files=(
  "managed/common.sh"
  "managed/check-task-intake.sh"
  "managed/start-implementation.sh"
  "managed/check-startup-gate.sh"
  "managed/check-task-group-dependencies.sh"
  "managed/run-workflow-stage.sh"
  "managed/archive-task-artifacts.sh"
  "managed/cleanup-task-worktree.sh"
  "managed/cleanup_task_worktree.py"
  "managed/check_startup_gate.py"
  "managed/implementation-plan-skeleton.md"
  "managed/task-group-index-skeleton.md"
)

legacy_paths=(
  "scripts/workflows/check-task-intake.sh"
  "scripts/workflows/start-implementation.sh"
  "scripts/workflows/check-startup-gate.sh"
  "scripts/workflows/check-task-group-dependencies.sh"
  "scripts/archive-task-artifacts.sh"
  "harness/workflow-plugins/code-workflow/run_workflow_stage.sh"
  "harness/workflow-plugins/code-workflow/archive_task_artifacts.sh"
  "harness/workflow-plugins/code-workflow/cleanup_task_worktree.sh"
  "harness/workflow-plugins/code-workflow/cleanup_task_worktree.py"
  "harness/checks/check_startup_gate.py"
  "harness/templates/implementation-plan-skeleton.md"
  "harness/templates/task-group-index-skeleton.md"
  ".arccgz-harness/scripts/workflows/check-task-intake.sh"
  ".arccgz-harness/scripts/workflows/start-implementation.sh"
  ".arccgz-harness/scripts/workflows/check-startup-gate.sh"
  ".arccgz-harness/scripts/workflows/check-task-group-dependencies.sh"
  ".arccgz-harness/harness/workflow-plugins/code-workflow/run_workflow_stage.sh"
  ".arccgz-harness/harness/workflow-plugins/code-workflow/archive_task_artifacts.sh"
  ".arccgz-harness/harness/workflow-plugins/code-workflow/cleanup_task_worktree.sh"
  ".arccgz-harness/harness/workflow-plugins/code-workflow/cleanup_task_worktree.py"
  ".arccgz-harness/harness/checks/check_startup_gate.py"
  ".arccgz-harness/harness/templates/implementation-plan-skeleton.md"
  ".arccgz-harness/harness/templates/task-group-index-skeleton.md"
)

check_runtime() {
  local relative
  local fail=0
  for relative in "${required_files[@]}"; do
    if [[ -f "$SCRIPT_DIR/$relative" ]]; then
      echo "PASS: global workflow asset exists: $relative"
    else
      echo "FAIL: missing global workflow asset: $SCRIPT_DIR/$relative" >&2
      fail=1
    fi
  done
  return "$fail"
}

check_project_state() {
  local root="$1"
  local relative path
  local fail=0

  if [[ -d "$root/$CODE_WORKFLOW_SESSION_GATES_REL" ]]; then
    echo "PASS: workflow state directory exists"
  else
    echo "FAIL: missing workflow state directory: $root/$CODE_WORKFLOW_SESSION_GATES_REL" >&2
    fail=1
  fi

  if [[ -f "$root/.gitignore" ]] && { grep -qxF '/.arccgz-harness/' "$root/.gitignore" || grep -qxF '/.arccgz-harness/state/session-gates/' "$root/.gitignore"; }; then
    echo "PASS: .gitignore keeps workflow state local"
  else
    echo "FAIL: .gitignore must contain /.arccgz-harness/ or /.arccgz-harness/state/session-gates/" >&2
    fail=1
  fi

  if [[ -e "$root/$CODE_WORKFLOW_LEGACY_SESSION_GATES_REL" ]]; then
    echo "FAIL: legacy workflow state directory remains: $root/$CODE_WORKFLOW_LEGACY_SESSION_GATES_REL" >&2
    fail=1
  fi

  for relative in "${legacy_paths[@]}"; do
    path="$root/$relative"
    if [[ ! -e "$path" ]]; then
      continue
    fi
    if [[ -f "$path" ]] && grep -qF 'Managed by code-workflow package' "$path"; then
      echo "FAIL: legacy managed workflow copy remains: $relative" >&2
    else
      echo "FAIL: legacy workflow path requires manual migration: $relative" >&2
    fi
    fail=1
  done
  return "$fail"
}

ensure_project_state() {
  local root="$1"
  local dry_run="$2"
  local gitignore="$root/.gitignore"
  local state_dir="$root/$CODE_WORKFLOW_SESSION_GATES_REL"
  local legacy_state_dir="$root/$CODE_WORKFLOW_LEGACY_SESSION_GATES_REL"
  local entry destination
  local -a legacy_entries=()

  if [[ -e "$legacy_state_dir" && ! -d "$legacy_state_dir" ]]; then
    echo "FAIL: legacy workflow state path is not a directory: $legacy_state_dir" >&2
    return 1
  fi

  if [[ -d "$legacy_state_dir" ]]; then
    while IFS= read -r -d '' entry; do
      legacy_entries+=("$entry")
    done < <(find "$legacy_state_dir" -mindepth 1 -maxdepth 1 -print0)

    for entry in "${legacy_entries[@]}"; do
      destination="$state_dir/$(basename "$entry")"
      if [[ -e "$destination" ]]; then
        echo "FAIL: cannot migrate legacy workflow state because destination already exists: $destination" >&2
        return 1
      fi
    done
  fi

  if [[ "$dry_run" -eq 1 ]]; then
    echo "DRY RUN: would create $state_dir"
    if [[ -d "$legacy_state_dir" ]]; then
      echo "DRY RUN: would migrate legacy workflow state from $legacy_state_dir to $state_dir"
    fi
    echo "DRY RUN: would ensure .gitignore keeps $CODE_WORKFLOW_SESSION_GATES_REL local"
    return 0
  fi

  mkdir -p "$state_dir"
  if [[ -d "$legacy_state_dir" ]]; then
    for entry in "${legacy_entries[@]}"; do
      mv -- "$entry" "$state_dir/"
    done
    rmdir "$legacy_state_dir"
    rmdir "$root/.harness" 2>/dev/null || true
    echo "PASS: migrated legacy workflow state to $CODE_WORKFLOW_SESSION_GATES_REL"
  fi

  touch "$gitignore"
  if ! grep -qxF '/.arccgz-harness/' "$gitignore" && ! grep -qxF '/.arccgz-harness/state/session-gates/' "$gitignore"; then
    printf '%s\n' '/.arccgz-harness/state/session-gates/' >> "$gitignore"
  fi
  python3 - "$gitignore" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
original = path.read_bytes()
updated = b"".join(
    line
    for line in original.splitlines(keepends=True)
    if line.rstrip(b"\r\n") != b"/.harness/session-gates/"
)
if updated != original:
    path.write_bytes(updated)
PY
}

remove_legacy_copies() {
  local root="$1"
  local dry_run="$2"
  local relative path
  local fail=0

  for relative in "${legacy_paths[@]}"; do
    path="$root/$relative"
    if [[ ! -e "$path" ]]; then
      continue
    fi
    if [[ ! -f "$path" ]] || ! grep -qF 'Managed by code-workflow package' "$path"; then
      echo "FAIL: legacy workflow path is not a managed copy; migrate it manually: $relative" >&2
      fail=1
      continue
    fi
    if [[ "$dry_run" -eq 1 ]]; then
      echo "DRY RUN: would remove legacy managed workflow copy: $relative"
    else
      rm -f -- "$path"
      echo "PASS: removed legacy managed workflow copy: $relative"
    fi
  done
  return "$fail"
}

run_install() {
  local root="$1"
  shift
  local dry_run=0
  if [[ "${1:-}" == "--dry-run" ]]; then
    dry_run=1
    shift
  fi
  if [[ $# -gt 0 ]]; then
    echo "FAIL: unknown install argument: $1" >&2
    exit 1
  fi
  ensure_project_state "$root" "$dry_run"
  if [[ "$dry_run" -eq 1 ]]; then
    echo "DRY RUN: code-workflow stays global at $SCRIPT_DIR"
  else
    echo "PASS: code-workflow is ready through the global runtime ($SCAFFOLD_VERSION)"
    echo "- entry: bash ~/.agents/harness/workflows/code-workflow/workflow.sh $root <command>"
  fi
}

run_sync() {
  local root="$1"
  shift
  local dry_run=0
  if [[ "${1:-}" == "--dry-run" ]]; then
    dry_run=1
    shift
  fi
  if [[ $# -gt 0 ]]; then
    echo "FAIL: unknown sync argument: $1" >&2
    exit 1
  fi
  remove_legacy_copies "$root" "$dry_run"
  if [[ "$dry_run" -eq 1 ]]; then
    run_install "$root" --dry-run
  else
    run_install "$root"
  fi
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -eq 0 ]]; then
  usage
  exit 0
fi

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

repo_root="$(resolve_repo_root "$1")"
shift
command="$1"
shift
export WORKFLOW_REPO_ROOT="$repo_root"

case "$command" in
  install|--install)
    check_runtime
    run_install "$repo_root" "$@"
    ;;
  sync|--sync)
    check_runtime
    run_sync "$repo_root" "$@"
    ;;
  check|--check)
    [[ $# -eq 0 ]] || { echo "FAIL: --check accepts no additional arguments" >&2; exit 1; }
    check_runtime
    check_project_state "$repo_root"
    echo "PASS: global code-workflow is ready for $repo_root"
    ;;
  intake|check-task-intake)
    exec bash "$MANAGED_DIR/check-task-intake.sh" "$@"
    ;;
  start|start-implementation)
    exec bash "$MANAGED_DIR/start-implementation.sh" "$@"
    ;;
  gate|check-startup-gate)
    exec bash "$MANAGED_DIR/check-startup-gate.sh" "$@"
    ;;
  task-group|check-task-group-dependencies)
    exec bash "$MANAGED_DIR/check-task-group-dependencies.sh" "$@"
    ;;
  stage|run-stage)
    exec bash "$MANAGED_DIR/run-workflow-stage.sh" "$@"
    ;;
  archive)
    exec bash "$MANAGED_DIR/archive-task-artifacts.sh" "$@"
    ;;
  cleanup)
    exec bash "$MANAGED_DIR/cleanup-task-worktree.sh" "$@"
    ;;
  *)
    echo "FAIL: unknown code-workflow command: $command" >&2
    usage
    exit 1
    ;;
esac
