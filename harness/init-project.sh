#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/init-project.sh <repo-root> [--project-name <name>] [--mode <default|strict-reference>] [--workflow <name>] [--skip-workflow] [--full-check]

Description:
  Initialize project-local harness scaffolding, then optionally enable checks and a shared workflow package.

Defaults:
  - mode: default
  - checks: skipped; pass --with-checks to generate checks and hooks
  - workflow: skipped; pass --workflow <name> to activate one
  - full check: skipped; pass --full-check to generate and run checks
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

repo_root=""
project_name=""
mode="default"
workflow_name=""
skip_workflow=1
with_checks=0
full_check=0
agents_home="${AGENTS_HOME:-$(cd "$SCRIPT_DIR/.." && pwd)}"
export AGENTS_HOME="$agents_home"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      [[ $# -ge 2 ]] || { echo "FAIL: --project-name requires a value" >&2; exit 1; }
      project_name="$2"
      shift 2
      ;;
    --mode)
      [[ $# -ge 2 ]] || { echo "FAIL: --mode requires a value" >&2; exit 1; }
      mode="$2"
      shift 2
      ;;
    --workflow)
      [[ $# -ge 2 ]] || { echo "FAIL: --workflow requires a value" >&2; exit 1; }
      workflow_name="$2"
      skip_workflow=0
      shift 2
      ;;
    --with-checks)
      with_checks=1
      shift
      ;;
    --skip-workflow)
      skip_workflow=1
      shift
      ;;
    --full-check)
      full_check=1
      with_checks=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "FAIL: unknown arg: $1" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -n "$repo_root" ]]; then
        echo "FAIL: repo root already set to $repo_root" >&2
        usage
        exit 1
      fi
      repo_root="$1"
      shift
      ;;
  esac
done

if [[ -z "$repo_root" ]]; then
  usage
  exit 1
fi

repo_root="$(cd "$repo_root" && pwd)"
if [[ ! -d "$repo_root/.git" ]] && ! git -C "$repo_root" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "FAIL: target is not a git repository: $repo_root" >&2
  exit 1
fi

repo_root="$(git -C "$repo_root" rev-parse --show-toplevel)"
if [[ -z "$project_name" ]]; then
  project_name="$(basename "$repo_root")"
fi

case "$mode" in
  default|strict-reference)
    ;;
  *)
    echo "FAIL: unsupported mode: $mode" >&2
    exit 1
    ;;
esac

echo "[init-project] initialize harness"
initializer_args=(
  --repo "$repo_root" \
  --project-name "$project_name" \
  --mode "$mode"
)
if [[ "$with_checks" -eq 1 ]]; then
  initializer_args+=(--with-checks)
fi
python3 "$agents_home/harness/harness-initializer.py" "${initializer_args[@]}"

if [[ "$skip_workflow" -eq 0 && -n "$workflow_name" ]]; then
  echo "[init-project] sync workflow package: $workflow_name"
  bash "$agents_home/harness/workflow-sync.sh" "$repo_root" "$workflow_name"
else
  echo "[init-project] skip workflow installation"
fi

if [[ "$full_check" -eq 1 && -x "$repo_root/.arccgz-harness/scripts/checks/check-harness-consistency.sh" ]]; then
  echo "[init-project] run project harness consistency check"
  bash "$repo_root/.arccgz-harness/scripts/checks/check-harness-consistency.sh"
else
  echo "[init-project] skip full harness consistency check (use --full-check to run it)"
fi

echo "[init-project] done"
echo "- repo: $repo_root"
echo "- mode: $mode"
if [[ "$with_checks" -eq 1 ]]; then
  echo "- checks: enabled"
else
  echo "- checks: skipped"
fi
if [[ "$skip_workflow" -eq 0 && -n "$workflow_name" ]]; then
  echo "- workflow: $workflow_name"
else
  echo "- workflow: skipped"
fi
if [[ "$full_check" -eq 1 ]]; then
  echo "- full-check: enabled"
else
  echo "- full-check: skipped"
fi
