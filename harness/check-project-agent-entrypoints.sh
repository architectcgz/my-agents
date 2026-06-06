#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/check-project-agent-entrypoints.sh [project-root]

Checks:
- <root>/AGENTS.md exists
- <root>/CLAUDE.md exists and is a symlink to AGENTS.md
- if <root>/.agents/skills or <root>/.claude/skills exists, then .claude/skills must point to .agents/skills
EOF
}

root="${1:-$(pwd)}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

root="$(readlink -f "$root")"
agents_file="$root/AGENTS.md"
claude_file="$root/CLAUDE.md"
agents_skills_dir="$root/.agents/skills"
claude_skills_link="$root/.claude/skills"

echo "[agent-entrypoints] check project: $root"

if [[ ! -f "$agents_file" ]]; then
  echo "FAIL: missing $agents_file" >&2
  exit 1
fi

if [[ ! -L "$claude_file" ]]; then
  echo "FAIL: $claude_file must be a symlink to AGENTS.md" >&2
  exit 1
fi

if [[ "$(readlink -f "$claude_file")" != "$(readlink -f "$agents_file")" ]]; then
  echo "FAIL: $claude_file does not resolve to $agents_file" >&2
  exit 1
fi

echo "PASS: $claude_file -> AGENTS.md"

if [[ -e "$agents_skills_dir" || -e "$claude_skills_link" ]]; then
  if [[ ! -d "$agents_skills_dir" ]]; then
    echo "FAIL: missing shared skill source $agents_skills_dir" >&2
    exit 1
  fi

  if [[ ! -L "$claude_skills_link" ]]; then
    echo "FAIL: $claude_skills_link must be a symlink to .agents/skills" >&2
    exit 1
  fi

  if [[ "$(readlink -f "$claude_skills_link")" != "$(readlink -f "$agents_skills_dir")" ]]; then
    echo "FAIL: $claude_skills_link does not resolve to $agents_skills_dir" >&2
    exit 1
  fi

  echo "PASS: $claude_skills_link -> .agents/skills"
fi
