#!/usr/bin/env python3
"""Shared staged-path routing fragment for consistency script templates."""

from __future__ import annotations

from .scaffold import HARNESS_CHECKS, HARNESS_ROOT


def staged_check_routing() -> str:
    return r"""staged_mode=0
if [[ "${1:-}" == "--staged" ]]; then
  staged_mode=1
  shift
fi
if [[ "$#" -gt 0 ]]; then
  echo "unknown argument: $1" >&2
  exit 2
fi

staged_paths=()
if [[ "$staged_mode" -eq 1 ]]; then
  while IFS= read -r -d '' path; do
    staged_paths+=("$path")
  done < <(git diff --cached --name-only --diff-filter=ACMR -z)
fi

staged_path_matches() {
  local path pattern
  for path in "${staged_paths[@]}"; do
    for pattern in "$@"; do
      if [[ "$path" == $pattern ]]; then
        return 0
      fi
    done
  done
  return 1
}

run_check_once() {
  local name="$1"
  shift
  if [[ "${executed_checks[$name]:-0}" == "1" ]]; then
    return 0
  fi
  executed_checks["$name"]=1
  "$@"
}

should_run_entrypoints() {
  [[ "$staged_mode" -eq 0 ]] || staged_path_matches \
    'AGENTS.md' '*/AGENTS.md' 'CLAUDE.md' '*/CLAUDE.md' \
    '.claude/*' '*/.claude/*' '.codex/*' '*/.codex/*' \
    '__HARNESS_CHECKS__/check-agent-entrypoints.sh'
}

should_run_script_guard() {
  [[ "$staged_mode" -eq 0 ]] || staged_path_matches \
    '__HARNESS_CHECKS__/*' '__HARNESS_ROOT__/scripts/hooks/*' \
    '__HARNESS_ROOT__/scripts/tests/*' '__HARNESS_ROOT__/scripts/workflows/*' \
    '__HARNESS_ROOT__/harness/policies/script-guard.json' \
    '__HARNESS_ROOT__/harness/checks/*' 'harness/*' 'tools/*'
}

declare -A executed_checks=()
""".replace("__HARNESS_ROOT__", HARNESS_ROOT).replace("__HARNESS_CHECKS__", HARNESS_CHECKS)
