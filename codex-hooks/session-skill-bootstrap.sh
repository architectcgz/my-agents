#!/usr/bin/env bash
set -euo pipefail

# Bootstrap 纪律 skill：只注入路径和最小纪律摘要，正文按需从磁盘读取。
skill_path="${CODEX_SKILL_BOOTSTRAP_PATH:-$HOME/.agents/skills/superpowers/using-superpowers/SKILL.md}"

if [[ ! -f "$skill_path" && -f "$HOME/.agents/skills/using-superpowers/SKILL.md" ]]; then
  skill_path="$HOME/.agents/skills/using-superpowers/SKILL.md"
fi

if [[ -f "$skill_path" ]]; then
  bootstrap_status="Bootstrap skill path: $skill_path"
else
  bootstrap_status="Bootstrap skill missing: $skill_path"
fi

# 定位“当前项目”：Codex SessionStart hook 通过 stdin JSON 传入 cwd；取不到则回退 $PWD。
# 不依赖 jq（本机无 jq），用 sed 抽取首个 "cwd": "..." 值。
hook_input="$(cat 2>/dev/null || true)"
cwd=""
if [[ -n "$hook_input" ]]; then
  cwd="$(printf '%s' "$hook_input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
fi
[[ -z "$cwd" ]] && cwd="${PWD:-$(pwd)}"

# 从 cwd 向上查找项目级 skill 目录：优先 <repo>/.agents/skills，回退 <repo>/.claude/skills。
# 这对齐 Claude 在项目内通过 .claude/skills 自动加载项目 skill 的行为。
# 关键排除：home 下的 .agents/skills 本身就是全局 root，.claude/skills 又软链到它；
# 用 realpath 比较，凡指向全局 root 的入口目录都不算“项目”，避免把 $HOME 误判成项目根。
global_root="${CODEX_SKILLS_ROOT:-$HOME/.agents/skills}"
global_real="$(readlink -f "$global_root" 2>/dev/null || printf '%s' "$global_root")"

is_global_entry() {
  local cand_real
  cand_real="$(readlink -f "$1" 2>/dev/null || printf '%s' "$1")"
  [[ "$cand_real" == "$global_real" ]]
}

project_skills_root=""
project_root=""
dir="$cwd"
while [[ -n "$dir" && "$dir" != "/" ]]; do
  if [[ -d "$dir/.agents/skills" ]] && ! is_global_entry "$dir/.agents/skills"; then
    project_skills_root="$dir/.agents/skills"; project_root="$dir"; break
  fi
  if [[ -d "$dir/.claude/skills" ]] && ! is_global_entry "$dir/.claude/skills"; then
    project_skills_root="$dir/.claude/skills"; project_root="$dir"; break
  fi
  dir="$(dirname "$dir")"
done

# 构建 skill 索引（name + description + 路径）。索引即路由表：抗上下文压缩，
# Codex 命中 description 后再按需读对应 SKILL.md（激活优于存储 / 按需加载）。
# 排除 .system/：Codex 系统级 skill，有独立加载路径。
build_skill_index() {
  local root="$1"
  local lines="" md name desc
  if [[ -d "$root" ]]; then
    while IFS= read -r md; do
      name="$(read_frontmatter_field name "$md")"
      [[ -z "$name" ]] && continue
      desc="$(read_frontmatter_field description "$md")"
      lines+="- ${name}: ${desc} [${md}]"$'\n'
    done < <(find "$root" -name SKILL.md -not -path '*/.system/*' | sort)
  fi
  printf '%s' "$lines"
}

read_frontmatter_field() {
  local key="$1"
  local file="$2"
  awk -v key="$key" '
    BEGIN { found = 0; folded = 0; value = "" }
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" {
      if (found && folded) print value
      exit
    }
    !in_frontmatter { next }
    !found && $0 ~ "^" key ":[[:space:]]*" {
      line = $0
      sub("^" key ":[[:space:]]*", "", line)
      if (line == ">" || line == "|") {
        found = 1
        folded = 1
        next
      }
      gsub(/^"|"$/, "", line)
      gsub(/^'\''|'\''$/, "", line)
      print line
      exit
    }
    found && folded {
      if ($0 ~ /^[[:space:]]+/) {
        sub(/^[[:space:]]+/, "", $0)
        value = value (value == "" ? "" : " ") $0
        next
      }
      print value
      exit
    }
  ' "$file"
}

# 默认注入“当前项目”的说明性/约束性 skill；不在任何项目内时才回退全局共享 skill 作为发现兜底。
index_root=""
scope_label=""
skill_index_lines=""
if [[ -n "$project_skills_root" ]]; then
  skill_index_lines="$(build_skill_index "$project_skills_root")"
  index_root="$project_skills_root"
  scope_label="当前项目 ($project_root)"
fi

if [[ -z "$skill_index_lines" ]]; then
  index_root="${CODEX_SKILLS_ROOT:-$HOME/.agents/skills}"
  skill_index_lines="$(build_skill_index "$index_root")"
  scope_label="全局共享（未检测到项目 skill，回退）"
fi

if [[ -z "$skill_index_lines" ]]; then
  skill_index_lines="(No skills were found under $index_root)"
fi

session_context="$(cat <<EOF
<codex-skill-bootstrap>
SessionStart discipline reminder: this thread may have just started, resumed,
cleared, or compacted, so previously loaded skill bodies may be absent.

$bootstrap_status

Rules:
- Before non-trivial work, re-run skill matching from the current user request.
- If a skill is named or its description matches, read its current SKILL.md from
  disk before acting; do not rely on remembered content.
- Do not invoke superpowers or using-superpowers as a default fallback; use them
  only when the request matches their descriptions.
- Keep context minimal: read only the matching skill and required references.
- User instructions still override skill process rules.

<available-skills scope="$scope_label">
Indexed from disk under $index_root. This is a routing table only; read the
matched SKILL.md body on demand.

$skill_index_lines
</available-skills>
</codex-skill-bootstrap>
EOF
)"

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

escaped_context="$(escape_for_json "$session_context")"

printf '{\n'
printf '  "hookSpecificOutput": {\n'
printf '    "hookEventName": "SessionStart",\n'
printf '    "additionalContext": "%s"\n' "$escaped_context"
printf '  }\n'
printf '}\n'
