#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/workflow-installer.sh <repo-root> <workflow-name> [--dry-run]

Description:
  Prepare a repository to use a shared workflow package from ~/.agents/harness/workflows.

  code-workflow runs directly from ~/.agents and does not copy workflow implementation
  files into the repository. Other package types retain their own install semantics.
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

repo_root="$1"
workflow_name="$2"
shift 2

agents_home="${AGENTS_HOME:-$(cd "$SCRIPT_DIR/.." && pwd)}"
workflow_root="$agents_home/harness/workflows/$workflow_name"
workflow_script="$workflow_root/workflow.sh"

if [[ ! -d "$workflow_root" ]]; then
  echo "FAIL: workflow package not found: $workflow_root" >&2
  exit 1
fi

if [[ ! -x "$workflow_script" ]]; then
  echo "FAIL: workflow entrypoint is missing or not executable: $workflow_script" >&2
  exit 1
fi

if [[ "$workflow_name" == "code-workflow" ]]; then
  exec bash "$workflow_script" "$repo_root" --install "$@"
fi

exec bash "$workflow_script" "$repo_root" "$@"
