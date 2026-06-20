#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGED_DIR="$SCRIPT_DIR/managed"
SCAFFOLD_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$SCRIPT_DIR/manifest.json")"

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/workflow-installer.sh <repo-root> spec-coding-workflow [--dry-run]
  bash ~/.agents/harness/workflow-sync-check.sh <repo-root> spec-coding-workflow

Description:
  Install or verify repo-local assets for the shared spec-coding-workflow package.
EOF
}

repo_root=""
dry_run=0
check_mode=0
check_fail=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    --check)
      check_mode=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "FAIL: unknown argument: $1" >&2
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

if [[ "$dry_run" -eq 1 && "$check_mode" -eq 1 ]]; then
  echo "FAIL: --dry-run and --check cannot be used together" >&2
  exit 1
fi

repo_root="$(cd "$repo_root" && pwd)"

if [[ ! -d "$repo_root/.git" ]] && ! git -C "$repo_root" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "FAIL: target is not a git repository: $repo_root" >&2
  exit 1
fi

repo_root="$(git -C "$repo_root" rev-parse --show-toplevel)"

with_managed_header() {
  local kind="$1"
  local content="$2"
  local marker="Managed by spec-coding-workflow package (version: $SCAFFOLD_VERSION)"
  local first_line=""
  local rest=""

  case "$kind" in
    shell)
      first_line="${content%%$'\n'*}"
      if [[ "$content" == *$'\n'* ]]; then
        rest="${content#*$'\n'}"
      fi
      printf '%s\n' "$first_line"
      printf '%s\n' "# $marker"
      if [[ -n "$rest" ]]; then
        printf '%s\n' "$rest"
      fi
      ;;
    markdown)
      printf '<!-- %s -->\n' "$marker"
      printf '%s\n' "$content"
      ;;
    *)
      echo "FAIL: unsupported managed header kind: $kind" >&2
      exit 1
      ;;
  esac
}

write_file() {
  local path="$1"
  local content="$2"
  local tmp_file=""

  if [[ "$check_mode" -eq 1 ]]; then
    if [[ ! -f "$path" ]]; then
      echo "FAIL: missing managed workflow file: $path" >&2
      check_fail=1
      return 0
    fi
    tmp_file="$(mktemp)"
    printf '%s\n' "$content" > "$tmp_file"
    if cmp -s "$path" "$tmp_file"; then
      echo "PASS: $path matches shared spec-coding-workflow baseline"
    else
      echo "FAIL: $path drifted from shared spec-coding-workflow baseline" >&2
      check_fail=1
    fi
    rm -f "$tmp_file"
    return 0
  fi

  if [[ "$dry_run" -eq 1 ]]; then
    echo "DRY RUN: would write $path"
    return 0
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" > "$path"
}

read_managed_source() {
  local relative_path="$1"
  local path="$MANAGED_DIR/$relative_path"
  if [[ ! -f "$path" ]]; then
    echo "FAIL: missing managed workflow source: $path" >&2
    exit 1
  fi
  cat "$path"
}

START_SPEC_CODING="$(with_managed_header shell "$(read_managed_source "start-spec-coding.sh")")"
CHECK_SPEC_CODING_DOCS="$(with_managed_header shell "$(read_managed_source "check-spec-coding-docs.sh")")"
PRD_TEMPLATE="$(with_managed_header markdown "$(read_managed_source "PRD.md")")"
DESIGN_TEMPLATE="$(with_managed_header markdown "$(read_managed_source "DESIGN.md")")"
ARCHITECTURE_TEMPLATE="$(with_managed_header markdown "$(read_managed_source "ARCHITECTURE.md")")"
TODO_TEMPLATE="$(with_managed_header markdown "$(read_managed_source "TODO.md")")"
LAUNCH_TEMPLATE="$(with_managed_header markdown "$(read_managed_source "LAUNCH-READINESS.md")")"

write_file "$repo_root/scripts/start-spec-coding.sh" "$START_SPEC_CODING"
write_file "$repo_root/scripts/check-spec-coding-docs.sh" "$CHECK_SPEC_CODING_DOCS"
write_file "$repo_root/harness/templates/spec-coding-workflow/PRD.md" "$PRD_TEMPLATE"
write_file "$repo_root/harness/templates/spec-coding-workflow/DESIGN.md" "$DESIGN_TEMPLATE"
write_file "$repo_root/harness/templates/spec-coding-workflow/ARCHITECTURE.md" "$ARCHITECTURE_TEMPLATE"
write_file "$repo_root/harness/templates/spec-coding-workflow/TODO.md" "$TODO_TEMPLATE"
write_file "$repo_root/harness/templates/spec-coding-workflow/LAUNCH-READINESS.md" "$LAUNCH_TEMPLATE"

if [[ "$check_mode" -eq 1 ]]; then
  if [[ "$check_fail" -eq 0 ]]; then
    echo "PASS: shared spec-coding-workflow package is in sync for $repo_root"
  else
    echo "FAIL: shared spec-coding-workflow package drift detected in $repo_root" >&2
  fi
  exit "$check_fail"
elif [[ "$dry_run" -eq 1 ]]; then
  echo "DRY RUN: spec-coding-workflow package install checked"
else
  chmod +x \
    "$repo_root/scripts/start-spec-coding.sh" \
    "$repo_root/scripts/check-spec-coding-docs.sh"
  echo "PASS: spec-coding-workflow package installed in $repo_root"
fi
