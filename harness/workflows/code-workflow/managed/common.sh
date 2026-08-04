#!/usr/bin/env bash

# Shared helpers for the global code-workflow runtime.  These scripts always
# execute from ~/.agents; only task state and project-specific checks live in
# the target repository.

CODE_WORKFLOW_MANAGED_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_WORKFLOW_PACKAGE_ROOT="$(cd "$CODE_WORKFLOW_MANAGED_DIR/.." && pwd)"
CODE_WORKFLOW_SESSION_GATES_REL=".arccgz-harness/state/session-gates"
CODE_WORKFLOW_LEGACY_SESSION_GATES_REL=".harness/session-gates"

workflow_repo_root() {
  local requested="${WORKFLOW_REPO_ROOT:-}"
  if [[ -z "$requested" ]]; then
    requested="$(pwd)"
  fi

  if [[ ! -d "$requested" ]] || ! git -C "$requested" rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "FAIL: target is not a git repository: $requested" >&2
    return 1
  fi

  git -C "$requested" rev-parse --show-toplevel
}

workflow_enter_repo() {
  WORKFLOW_REPO_ROOT="$(workflow_repo_root)"
  export WORKFLOW_REPO_ROOT
  cd "$WORKFLOW_REPO_ROOT"
}

workflow_entry() {
  printf '%s/workflow.sh' "$CODE_WORKFLOW_PACKAGE_ROOT"
}
