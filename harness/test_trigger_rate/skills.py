#!/usr/bin/env python3
"""Skill lookup and trigger matching helpers."""

from __future__ import annotations

import re
from pathlib import Path


def find_skill_description(skill_name: str) -> str:
    """
    查找 skill 的 description。

    优先从 ~/.agents/skills/ 查找，其次从 ~/.codex/skills/ 查找。
    """
    skill_dirs = [
        Path.home() / ".agents" / "skills" / skill_name,
        Path.home() / ".codex" / "skills" / skill_name,
    ]

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            # 提取 frontmatter 中的 description
            match = re.search(r"description:\s*(.+)", content)
            if match:
                return match.group(1).strip()

    return ""


def is_project_local_skill(skill_name: str, repo: Path) -> bool:
    """skill 是否是当前项目自有（位于 <repo>/.agents/skills/<name>/SKILL.md）。

    test-trigger 只应对项目自有 skill 的 description 质量把关；指向全局 skill 的标准行
    只报告、不作为退出码依据，避免刚 init 的项目因全局 skill 描述风格而必然失败。
    """
    return (repo / ".agents" / "skills" / skill_name / "SKILL.md").exists()


def test_trigger(user_input: str, skill_description: str) -> bool:
    """
    测试用户输入是否能触发 skill description。

    简化版：检查 description 中的关键词是否在用户输入中。
    实际应该使用更复杂的语义匹配。
    """
    if not skill_description:
        return False

    # 提取 description 中的关键词
    keywords = re.findall(r"\b[a-zA-Z一-龥]{2,}\b", skill_description.lower())
    user_lower = user_input.lower()

    # 如果用户输入包含任意关键词，视为匹配
    for keyword in keywords:
        if keyword in user_lower or keyword.replace("-", "") in user_lower:
            return True

    return False
