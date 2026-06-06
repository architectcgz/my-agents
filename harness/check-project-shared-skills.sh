#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF' >&2
Usage:
  bash ~/.agents/harness/check-project-shared-skills.sh [project-root]

Checks:
- <root>/.agents/skills exists
- <root>/.agents/skills/README.md exists
- every direct child directory under .agents/skills contains SKILL.md
EOF
}

root="${1:-$(pwd)}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

root="$(readlink -f "$root")"
shared_skills_dir="$root/.agents/skills"
shared_readme="$shared_skills_dir/README.md"

echo "[shared-skills] check project: $root"

if [[ ! -d "$shared_skills_dir" ]]; then
  echo "FAIL: missing shared skills dir $shared_skills_dir" >&2
  exit 1
fi

if [[ ! -f "$shared_readme" ]]; then
  echo "FAIL: missing shared skills README $shared_readme" >&2
  exit 1
fi

echo "PASS: $shared_readme"

while IFS= read -r skill_dir; do
  skill_file="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "FAIL: missing skill source $skill_file" >&2
    exit 1
  fi
  echo "PASS: $skill_file"
done < <(find "$shared_skills_dir" -mindepth 1 -maxdepth 1 -type d | sort)
