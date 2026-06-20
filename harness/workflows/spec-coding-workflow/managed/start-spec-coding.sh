#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF' >&2
Usage:
  bash scripts/start-spec-coding.sh <topic-or-slug> [--dir <docs-dir>]

Description:
  Create the spec-first docs scaffold for PRD, design, architecture, TODO, and launch readiness.

Default docs directory:
  docs/spec
EOF
}

topic=""
docs_dir="docs/spec"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)
      if [[ $# -lt 2 ]]; then
        echo "FAIL: --dir requires a value" >&2
        exit 1
      fi
      docs_dir="$2"
      shift 2
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
      if [[ -n "$topic" ]]; then
        echo "FAIL: topic already set to $topic" >&2
        usage
        exit 1
      fi
      topic="$1"
      shift
      ;;
  esac
done

if [[ -z "$topic" ]]; then
  usage
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "FAIL: start-spec-coding must run inside a git repository" >&2
  exit 1
fi

cd "$repo_root"

template_dir="harness/templates/spec-coding-workflow"
if [[ ! -d "$template_dir" ]]; then
  echo "FAIL: missing spec-coding templates: $template_dir" >&2
  echo "Hint: run: bash ~/.agents/harness/workflow-installer.sh $repo_root spec-coding-workflow" >&2
  exit 1
fi

mkdir -p "$docs_dir"

copy_if_missing() {
  local template_name="$1"
  local target_name="$2"
  local target_path="$docs_dir/$target_name"

  if [[ -f "$target_path" ]]; then
    echo "KEEP: $target_path already exists"
    return 0
  fi

  cp "$template_dir/$template_name" "$target_path"
  echo "CREATE: $target_path"
}

copy_if_missing "PRD.md" "PRD.md"
copy_if_missing "DESIGN.md" "DESIGN.md"
copy_if_missing "ARCHITECTURE.md" "ARCHITECTURE.md"
copy_if_missing "TODO.md" "TODO.md"
copy_if_missing "LAUNCH-READINESS.md" "LAUNCH-READINESS.md"

echo
echo "PASS: spec-coding scaffold ready for: $topic"
echo
echo "Next steps:"
echo "  1. Fill docs/spec/PRD.md before implementation."
echo "  2. Fill docs/spec/DESIGN.md for UI or interaction work."
echo "  3. Fill docs/spec/ARCHITECTURE.md with boundaries and invariants."
echo "  4. Convert the spec into docs/spec/TODO.md task slices."
echo "  5. For non-trivial implementation, enter code-workflow per repository rules."
