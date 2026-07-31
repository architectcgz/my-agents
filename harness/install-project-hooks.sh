#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: bash ~/.agents/harness/install-project-hooks.sh <project-root>" >&2
  exit $([[ $# -gt 1 ]] && echo 1 || echo 0)
fi

root="${1:-$(pwd)}"
root="$(git -C "$root" rev-parse --show-toplevel)"
if [[ ! -d "$root/.githooks" ]]; then
  echo "FAIL: missing .githooks directory: $root/.githooks" >&2
  exit 1
fi

configured="$(git -C "$root" config --get core.hooksPath 2>/dev/null || true)"
if [[ -n "$configured" && "$configured" != ".githooks" && "$configured" != "./.githooks" ]]; then
  echo "FAIL: refusing to replace existing core.hooksPath=$configured" >&2
  exit 1
fi

git -C "$root" config --local core.hooksPath .githooks
exec bash "$HOME/.agents/harness/checks/check-project-hooks.sh" "$root"
