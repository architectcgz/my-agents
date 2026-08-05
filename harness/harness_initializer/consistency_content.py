#!/usr/bin/env python3
"""Consistency script templates for harness initializer."""

from __future__ import annotations

from .consistency_routing import staged_check_routing
from .scaffold import HARNESS_CHECKS, HARNESS_HOOKS, HARNESS_ROOT


def current_check_script() -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$script_dir/../../.."   # repo root

{staged_check_routing()}

fail=0

red() {{ printf '\\033[31m%s\\033[0m' "$1"; }}
green() {{ printf '\\033[32m%s\\033[0m' "$1"; }}

check_file() {{
  if [[ -f "$1" ]]; then
    echo "  $(green PASS) — $1"
  else
    echo "  $(red FAIL) — missing $1"
    fail=1
  fi
}}

check_dir() {{
  if [[ -d "$1" ]]; then
    echo "  $(green PASS) — $1"
  else
    echo "  $(red FAIL) — missing $1"
    fail=1
  fi
}}

check_contains() {{
  local file="$1" pattern="$2" label="$3"
  if [[ ! -f "$file" ]]; then
    echo "  $(red FAIL) — $label: missing $file"
    fail=1
  elif grep -qE "$pattern" "$file"; then
    echo "  $(green PASS) — $label"
  else
    echo "  $(red FAIL) — $label"
    fail=1
  fi
}}

echo "[C1] current-task and durable harness directories exist"
check_dir "{HARNESS_ROOT}/state"
check_dir "{HARNESS_ROOT}/state/reuse-decisions"
check_file "{HARNESS_ROOT}/state/reuse-decisions/.gitkeep"
check_dir "{HARNESS_ROOT}/harness"
check_dir "{HARNESS_ROOT}/harness/policies"
check_dir "{HARNESS_ROOT}/harness/templates"
check_dir "{HARNESS_ROOT}/harness/prompts"
check_dir "{HARNESS_ROOT}/harness/checks"
check_dir "{HARNESS_ROOT}/feedback"

echo "[C2] all harness artifacts are gitignored"
if grep -qx '/{HARNESS_ROOT}/' ".gitignore"; then
  echo "  $(green PASS) — .gitignore reserves /{HARNESS_ROOT}/"
else
  echo "  $(red FAIL) — .gitignore must ignore /{HARNESS_ROOT}/"
  fail=1
fi

echo "[C3] project harness assets exist"
check_file "{HARNESS_ROOT}/harness/policies/reuse-first.yaml"
check_file "{HARNESS_ROOT}/harness/policies/project-patterns.yaml"
check_file "{HARNESS_ROOT}/harness/templates/reuse-decision.md"
check_file "{HARNESS_ROOT}/harness/prompts/AGENTS.md"
check_file "{HARNESS_ROOT}/harness/prompts/harness-router.md"
check_file "{HARNESS_ROOT}/harness/checks/common.py"
check_file "{HARNESS_ROOT}/feedback/AGENTS.md"
check_file "{HARNESS_ROOT}/docs/documentation-rules.md"
check_file "{HARNESS_ROOT}/docs/README.md"
check_file "{HARNESS_CHECKS}/check-open-todos.sh"
check_file "{HARNESS_CHECKS}/check-todo-governance.sh"
check_file "{HARNESS_CHECKS}/check-skill-sync-reminder.sh"
for dir in contracts spec design todo architecture plan reviews; do
  check_dir "{HARNESS_ROOT}/docs/$dir"
done

echo "[C4] root navigation references current harness shape"
check_contains "AGENTS.md" '{HARNESS_ROOT}/state/' "AGENTS references current-task harness"
check_contains "AGENTS.md" '{HARNESS_ROOT}/state/reuse-index/' "AGENTS references local private reuse index"
check_contains "AGENTS.md" '{HARNESS_ROOT}/harness/policies/' "AGENTS references harness policies"
check_contains "AGENTS.md" '{HARNESS_ROOT}/harness/prompts/' "AGENTS references harness prompts"
check_contains "AGENTS.md" '{HARNESS_ROOT}/harness/checks/' "AGENTS references harness checks"
check_contains "AGENTS.md" '{HARNESS_ROOT}/feedback/' "AGENTS references feedback"
check_contains "AGENTS.md" '{HARNESS_ROOT}/docs/documentation-rules\\.md' "AGENTS references documentation rules"
check_contains "AGENTS.md" '{HARNESS_ROOT}/docs/README\\.md' "AGENTS references documentation index"
check_contains "AGENTS.md" '{HARNESS_CHECKS}/check-open-todos\\.sh' "AGENTS references todo reminder"
check_contains "{HARNESS_ROOT}/docs/documentation-rules.md" 'Pre-Edit Reading Protocol' "documentation rules define pre-edit reading"
check_contains "{HARNESS_ROOT}/docs/documentation-rules.md" 'New Path Registration' "documentation rules define new path registration"
check_contains "{HARNESS_ROOT}/docs/documentation-rules.md" 'No Circular References' "documentation rules forbid circular references"

echo "[C4a] project agent entrypoints stay aligned"
check_file "{HARNESS_CHECKS}/check-agent-entrypoints.sh"
if should_run_entrypoints; then
  if [[ -x "{HARNESS_CHECKS}/check-agent-entrypoints.sh" ]]; then
    run_check_once entrypoints bash {HARNESS_CHECKS}/check-agent-entrypoints.sh
  else
    echo "  $(red FAIL) — {HARNESS_CHECKS}/check-agent-entrypoints.sh is not executable"; fail=1
  fi
elif [[ "$staged_mode" -eq 1 ]]; then
  echo "  $(green SKIP) — entrypoint check (no staged entrypoint paths)"
elif [[ ! -x "{HARNESS_CHECKS}/check-agent-entrypoints.sh" ]]; then
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-agent-entrypoints.sh is not executable"; fail=1
fi

echo "[C5] hooks and commit message guard are wired"
check_file "{HARNESS_HOOKS}/check-commit-message.sh"
check_file "{HARNESS_HOOKS}/check-pre-commit.sh"
check_file "{HARNESS_HOOKS}/check-hooks.sh"
check_file "{HARNESS_CHECKS}/check-architecture.sh"
check_file "{HARNESS_CHECKS}/check-test-workflow.sh"
check_file "{HARNESS_CHECKS}/check-script-guard.sh"
check_file "{HARNESS_ROOT}/harness/policies/script-guard.json"
if [[ -f ".githooks/pre-commit" ]]; then
  check_contains ".githooks/pre-commit" '{HARNESS_HOOKS}/check-pre-commit\\.sh' "pre-commit runs {HARNESS_HOOKS}/check-pre-commit.sh"
else
  echo "  $(red FAIL) — missing .githooks/pre-commit"
  fail=1
fi
if [[ -f ".githooks/commit-msg" ]]; then
  check_contains ".githooks/commit-msg" '{HARNESS_HOOKS}/check-commit-message\\.sh' "commit-msg runs {HARNESS_HOOKS}/check-commit-message.sh"
else
  echo "  $(red FAIL) — missing .githooks/commit-msg"
  fail=1
fi
if [[ -x "{HARNESS_HOOKS}/check-hooks.sh" ]]; then
  bash {HARNESS_HOOKS}/check-hooks.sh
else
  echo "  $(red FAIL) — {HARNESS_HOOKS}/check-hooks.sh is not executable"
  fail=1
fi

echo "[C6] architecture guard is surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-architecture.sh" ]]; then
  bash {HARNESS_CHECKS}/check-architecture.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-architecture.sh is not executable"
  fail=1
fi

echo "[C7] test workflow guard is surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-test-workflow.sh" ]]; then
  bash {HARNESS_CHECKS}/check-test-workflow.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-test-workflow.sh is not executable"
  fail=1
fi

echo "[C8] open todos are surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-open-todos.sh" ]]; then
  bash {HARNESS_CHECKS}/check-open-todos.sh --quiet-if-empty
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-open-todos.sh is not executable"
  fail=1
fi

echo "[C9] script guard stays consistent"
if should_run_script_guard; then
  if [[ -x "{HARNESS_CHECKS}/check-script-guard.sh" ]]; then
    run_check_once script_guard bash {HARNESS_CHECKS}/check-script-guard.sh
  else
    echo "  $(red FAIL) — {HARNESS_CHECKS}/check-script-guard.sh is not executable"; fail=1
  fi
elif [[ "$staged_mode" -eq 1 ]]; then
  echo "  $(green SKIP) — script guard (no staged operator/script policy paths)"
elif [[ ! -x "{HARNESS_CHECKS}/check-script-guard.sh" ]]; then
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-script-guard.sh is not executable"; fail=1
fi

echo "[C10] todo governance stays consistent"
if [[ -x "{HARNESS_CHECKS}/check-todo-governance.sh" ]]; then
  bash {HARNESS_CHECKS}/check-todo-governance.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-todo-governance.sh is not executable"
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo "$(green '\\u2713 all harness consistency checks passed')"
else
  echo "$(red '\\u2717 harness consistency checks failed')"
fi

exit "$fail"
"""


def check_script() -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$script_dir/../../.."   # repo root

{staged_check_routing()}

fail=0

red() {{ printf '\\033[31m%s\\033[0m' "$1"; }}
green() {{ printf '\\033[32m%s\\033[0m' "$1"; }}

check_file() {{
  if [[ -f "$1" ]]; then
    echo "  $(green PASS) — $1"
  else
    echo "  $(red FAIL) — missing $1"
    fail=1
  fi
}}

check_dir() {{
  if [[ -d "$1" ]]; then
    echo "  $(green PASS) — $1"
  else
    echo "  $(red FAIL) — missing $1"
    fail=1
  fi
}}

check_contains() {{
  local file="$1" pattern="$2" label="$3"
  if [[ ! -f "$file" ]]; then
    echo "  $(red FAIL) — $label: missing $file"
    fail=1
  elif grep -qE "$pattern" "$file"; then
    echo "  $(green PASS) — $label"
  else
    echo "  $(red FAIL) — $label"
    fail=1
  fi
}}

echo "[C1] strict harness directories exist"
for dir in concepts thinking practice feedback works prompts references; do
  check_dir "{HARNESS_ROOT}/$dir"
  check_file "{HARNESS_ROOT}/$dir/AGENTS.md"
done

echo "[C2] root navigation references strict harness"
check_contains "AGENTS.md" '{HARNESS_ROOT}/concepts/' "AGENTS references concepts"
check_contains "AGENTS.md" '{HARNESS_ROOT}/thinking/' "AGENTS references thinking"
check_contains "AGENTS.md" '{HARNESS_ROOT}/practice/' "AGENTS references practice"
check_contains "AGENTS.md" '{HARNESS_ROOT}/feedback/' "AGENTS references feedback"
check_contains "AGENTS.md" '{HARNESS_ROOT}/works/' "AGENTS references works"
check_contains "AGENTS.md" '{HARNESS_ROOT}/prompts/' "AGENTS references prompts"
check_contains "AGENTS.md" '{HARNESS_ROOT}/references/' "AGENTS references references"

echo "[C2a] project agent entrypoints stay aligned"
check_file "{HARNESS_CHECKS}/check-agent-entrypoints.sh"
if should_run_entrypoints; then
  if [[ -x "{HARNESS_CHECKS}/check-agent-entrypoints.sh" ]]; then
    run_check_once entrypoints bash {HARNESS_CHECKS}/check-agent-entrypoints.sh
  else
    echo "  $(red FAIL) — {HARNESS_CHECKS}/check-agent-entrypoints.sh is not executable"; fail=1
  fi
elif [[ "$staged_mode" -eq 1 ]]; then
  echo "  $(green SKIP) — entrypoint check (no staged entrypoint paths)"
elif [[ ! -x "{HARNESS_CHECKS}/check-agent-entrypoints.sh" ]]; then
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-agent-entrypoints.sh is not executable"; fail=1
fi

echo "[C3] articles.md numbering is contiguous 1..N"
nums=$(grep -nE '^### [0-9]+\\.' {HARNESS_ROOT}/references/articles.md | sed -E 's/^[0-9]+:### ([0-9]+)\\..*/\\1/' || true)
count=$(echo "$nums" | sed '/^$/d' | wc -l | tr -d ' ')
if [[ "$count" -eq 0 ]]; then
  echo "  $(red FAIL) — {HARNESS_ROOT}/references/articles.md has no numbered entries"
  fail=1
else
  sorted=$(echo "$nums" | sort -n)
  expected=$(seq 1 "$count")
  if [[ "$sorted" = "$expected" ]]; then
    echo "  $(green PASS) — $count contiguous entries"
  else
    echo "  $(red FAIL) — article numbering is not contiguous"
    fail=1
  fi
fi

echo "[C4] article count claim matches numbered entries"
claim=$(grep -oE '权威计数：[0-9]+ 篇' {HARNESS_ROOT}/references/articles.md | head -1 | grep -oE '[0-9]+' || true)
if [[ -z "$claim" || "$claim" != "$count" ]]; then
  echo "  $(red FAIL) — {HARNESS_ROOT}/references/articles.md claims ${{claim:-none}}, actual $count"
  fail=1
else
  echo "  $(green PASS) — count claim $claim"
fi

echo "[C5] hooks and commit message guard are wired"
check_file "{HARNESS_HOOKS}/check-commit-message.sh"
check_file "{HARNESS_HOOKS}/check-pre-commit.sh"
check_file "{HARNESS_HOOKS}/check-hooks.sh"
check_file "{HARNESS_CHECKS}/check-architecture.sh"
check_file "{HARNESS_CHECKS}/check-test-workflow.sh"
check_file "{HARNESS_CHECKS}/check-script-guard.sh"
check_file "{HARNESS_ROOT}/harness/policies/script-guard.json"
if [[ -f ".githooks/pre-commit" ]]; then
  check_contains ".githooks/pre-commit" '{HARNESS_HOOKS}/check-pre-commit\\.sh' "pre-commit runs {HARNESS_HOOKS}/check-pre-commit.sh"
else
  echo "  $(red FAIL) — missing .githooks/pre-commit"
  fail=1
fi
if [[ -f ".githooks/commit-msg" ]]; then
  check_contains ".githooks/commit-msg" '{HARNESS_HOOKS}/check-commit-message\\.sh' "commit-msg runs {HARNESS_HOOKS}/check-commit-message.sh"
else
  echo "  $(red FAIL) — missing .githooks/commit-msg"
  fail=1
fi
if [[ -x "{HARNESS_HOOKS}/check-hooks.sh" ]]; then
  bash {HARNESS_HOOKS}/check-hooks.sh
else
  echo "  $(red FAIL) — {HARNESS_HOOKS}/check-hooks.sh is not executable"
  fail=1
fi

echo "[C6] documentation architecture exists"
check_file "{HARNESS_ROOT}/docs/documentation-rules.md"
check_file "{HARNESS_ROOT}/docs/README.md"
check_file "{HARNESS_CHECKS}/check-open-todos.sh"
check_file "{HARNESS_CHECKS}/check-todo-governance.sh"
check_file "{HARNESS_CHECKS}/check-skill-sync-reminder.sh"
check_contains "{HARNESS_ROOT}/docs/documentation-rules.md" 'No Circular References' "documentation rules forbid circular references"
check_contains "AGENTS.md" '{HARNESS_CHECKS}/check-open-todos\\.sh' "AGENTS references todo reminder"

echo "[C7] architecture guard is surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-architecture.sh" ]]; then
  bash {HARNESS_CHECKS}/check-architecture.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-architecture.sh is not executable"
  fail=1
fi

echo "[C8] test workflow guard is surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-test-workflow.sh" ]]; then
  bash {HARNESS_CHECKS}/check-test-workflow.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-test-workflow.sh is not executable"
  fail=1
fi

echo "[C9] open todos are surfaced to the operator"
if [[ -x "{HARNESS_CHECKS}/check-open-todos.sh" ]]; then
  bash {HARNESS_CHECKS}/check-open-todos.sh --quiet-if-empty
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-open-todos.sh is not executable"
  fail=1
fi

echo "[C10] script guard stays consistent"
if should_run_script_guard; then
  if [[ -x "{HARNESS_CHECKS}/check-script-guard.sh" ]]; then
    run_check_once script_guard bash {HARNESS_CHECKS}/check-script-guard.sh
  else
    echo "  $(red FAIL) — {HARNESS_CHECKS}/check-script-guard.sh is not executable"; fail=1
  fi
elif [[ "$staged_mode" -eq 1 ]]; then
  echo "  $(green SKIP) — script guard (no staged operator/script policy paths)"
elif [[ ! -x "{HARNESS_CHECKS}/check-script-guard.sh" ]]; then
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-script-guard.sh is not executable"; fail=1
fi

echo "[C11] todo governance stays consistent"
if [[ -x "{HARNESS_CHECKS}/check-todo-governance.sh" ]]; then
  bash {HARNESS_CHECKS}/check-todo-governance.sh
else
  echo "  $(red FAIL) — {HARNESS_CHECKS}/check-todo-governance.sh is not executable"
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo "$(green '\\u2713 all harness consistency checks passed')"
else
  echo "$(red '\\u2717 harness consistency checks failed')"
fi

exit "$fail"
"""
