#!/usr/bin/env python3
"""Harness initializer templates for staged-file pre-commit checks."""

from __future__ import annotations


def pre_commit_guard_script() -> str:
    return r"""#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../../.." && pwd)"
cd "$root"

mode="auto"
explain=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --explain)
      explain=1
      shift
      ;;
    --full)
      mode="full"
      shift
      ;;
    -h|--help)
      echo "Usage: bash .arccgz-harness/scripts/hooks/check-pre-commit.sh [--explain|--full]"
      exit 0
      ;;
    *)
      echo "[pre-commit] unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "${HARNESS_PRE_COMMIT_FULL:-0}" == "1" ]]; then
  mode="full"
fi

changed=()
while IFS= read -r -d '' path; do
  changed+=("$path")
done < <(git diff --cached --name-only --diff-filter=ACMR -z)

if [[ "${#changed[@]}" -eq 0 ]]; then
  echo "[pre-commit] no staged files; skipped harness checks"
  exit 0
fi

has_path() {
  local path pattern
  for path in "${changed[@]}"; do
    for pattern in "$@"; do
      if [[ "$path" == $pattern ]]; then
        return 0
      fi
    done
  done
  return 1
}

structural_check=0
if has_path \
  'AGENTS.md' '*/AGENTS.md' 'CLAUDE.md' '*/CLAUDE.md' '.githooks/*' '.arccgz-harness/*' \
  '.codex/*' '.claude/*' 'scripts/check-*' 'harness/*'; then
  structural_check=1
fi

cpp_check=0
if has_path '*.c' '*.cc' '*.cpp' '*.cxx' '*.h' '*.hh' '*.hpp' '*.hxx' \
  && [[ -f .arccgz-harness/scripts/checks/check-cpp-format.py ]]; then
  cpp_check=1
fi

if [[ "$explain" -eq 1 ]]; then
  echo "[pre-commit] staged files: ${#changed[@]}"
  for path in "${changed[@]}"; do
    echo "  - $path"
  done
  if [[ "$mode" == "full" ]]; then
    echo "[pre-commit] run: full consistency (--full or HARNESS_PRE_COMMIT_FULL=1)"
  elif [[ "$structural_check" -eq 1 ]]; then
    echo "[pre-commit] run: staged consistency (child checks route by staged path)"
  else
    echo "[pre-commit] skip: full consistency (no harness-related staged path)"
  fi
  if [[ "$cpp_check" -eq 1 ]]; then
    echo "[pre-commit] run: project C++ format check"
  else
    echo "[pre-commit] skip: project C++ format check"
  fi
  echo "[pre-commit] run: skill sync reminder (non-blocking)"
  exit 0
fi

if [[ "$mode" == "full" ]]; then
  exec bash .arccgz-harness/scripts/checks/check-harness-consistency.sh
fi

if [[ "$structural_check" -eq 1 ]]; then
  if [[ -f .arccgz-harness/scripts/checks/check-harness-consistency.sh ]]; then
    bash .arccgz-harness/scripts/checks/check-harness-consistency.sh --staged
  fi
else
  echo "[pre-commit] structural harness checks skipped (no harness-related staged paths)"
fi

if [[ "$cpp_check" -eq 1 ]]; then
  python3 .arccgz-harness/scripts/checks/check-cpp-format.py
fi

# This is intentionally advisory: reusable harness knowledge can stay project-local.
if [[ -f .arccgz-harness/scripts/checks/check-skill-sync-reminder.sh ]]; then
  bash .arccgz-harness/scripts/checks/check-skill-sync-reminder.sh --staged || \
    echo "[pre-commit] skill sync reminder unavailable; skipped" >&2
fi
"""


def project_hooks_check_script() -> str:
    return r"""#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../../.." && pwd)"
agents_home="${AGENTS_HOME:-$HOME/.agents}"
exec bash "$agents_home/harness/checks/check-project-hooks.sh" "$root" "$@"
"""
