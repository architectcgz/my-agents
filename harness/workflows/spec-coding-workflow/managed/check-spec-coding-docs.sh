#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF' >&2
Usage:
  bash scripts/check-spec-coding-docs.sh [--dir <docs-dir>]

Description:
  Verify that the spec-coding workflow docs scaffold exists.

Default docs directory:
  docs/spec
EOF
}

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
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "FAIL: check-spec-coding-docs must run inside a git repository" >&2
  exit 1
fi

cd "$repo_root"

required_files=(
  "$docs_dir/PRD.md"
  "$docs_dir/DESIGN.md"
  "$docs_dir/ARCHITECTURE.md"
  "$docs_dir/TODO.md"
  "$docs_dir/LAUNCH-READINESS.md"
)

failed=0
for file in "${required_files[@]}"; do
  if [[ -s "$file" ]]; then
    echo "PASS: $file exists"
  else
    echo "FAIL: missing or empty spec workflow file: $file" >&2
    failed=1
  fi
done

if [[ "$failed" -eq 0 ]]; then
  echo "PASS: spec-coding docs scaffold exists"
else
  echo "FAIL: spec-coding docs scaffold is incomplete" >&2
fi

exit "$failed"
