#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  bash ~/.agents/harness/checks/check-project-hooks.sh [project-root]

Checks that the project routes Git hooks through its .githooks directory.
EOF
}

root="${1:-$(pwd)}"
if [[ "$root" == "-h" || "$root" == "--help" ]]; then
  usage
  exit 0
fi

root="$(git -C "$root" rev-parse --show-toplevel)"
configured="$(git -C "$root" config --get core.hooksPath 2>/dev/null || true)"
if [[ -z "$configured" ]]; then
  echo "FAIL: core.hooksPath is not configured for $root" >&2
  echo "Run: bash ~/.agents/harness/install-project-hooks.sh $root" >&2
  exit 1
fi

expected="$(cd "$root/.githooks" && pwd)"
configured_path="$configured"
if [[ "$configured_path" != /* && ! "$configured_path" =~ ^[A-Za-z]:[\\/] ]]; then
  configured_path="$root/$configured_path"
fi
actual="$(cd "$configured_path" 2>/dev/null && pwd || true)"
if [[ "$actual" != "$expected" ]]; then
  echo "FAIL: core.hooksPath=$configured does not resolve to $expected" >&2
  exit 1
fi

for hook in pre-commit commit-msg; do
  path="$expected/$hook"
  if [[ ! -f "$path" ]]; then
    echo "FAIL: missing hook: $path" >&2
    exit 1
  fi
  if ! grep -q "BEGIN HARNESS ENGINEERING: $hook" "$path"; then
    echo "FAIL: hook is not managed by harness: $path" >&2
    exit 1
  fi
done

echo "PASS: $root routes Git hooks through $expected"
