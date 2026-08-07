#!/usr/bin/env python3
"""检查目标状态迁移规则是否仍存在于共享 prompt 和 skills。"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

REQUIREMENTS = {
    # 目标状态与提问规则的正文归属在 collaboration-basics，不在全局入口重复校验。
    ROOT / "docs/agent-rules/collaboration-basics.md": [
        "用户明确、无歧义的目标、范围和完成标准",
        "用户明确、无歧义的目标、范围和完成标准优先于项目既有实现习惯与 minimal diff",
        "minimal diff 指达到用户目标状态所需的最小完整改动",
        "目标状态迁移",
        "哪些旧 import、constructor、adapter、wrapper、配置和依赖完成后必须消失",
        "提问前必须先完成可自行完成的调查",
        "不要询问用户可以通过这些证据回答的技术事实",
        "推荐方案及理由、可行备选及代价",
        "研究问题定义",
    ],
    ROOT / "skills/architect-agent/SKILL.md": [
        "smallest complete target-state change",
        "Migration Target-State Gate",
        "Required removals",
        "Research before escalating ambiguity",
        "research-question brief",
    ],
    ROOT / "skills/brainstorming/SKILL.md": [
        "Framework Adoption Depth",
        "old default path that must disappear",
        "official-document/Web research",
        "research-question brief",
    ],
    ROOT / "skills/writing-plans/SKILL.md": [
        "For migrations, replacements, standardization, or framework adoption, define:",
        "negative acceptance",
        "old default path is gone",
        "target state",
        "positive acceptance",
        "Before freezing scope or asking the user to choose an implementation direction:",
        "Ask only about boundaries evidence cannot decide",
    ],
    ROOT / "skills/development-pipeline/references/review-gates.md": [
        "legacy initialization, driver/provider, runtime owner",
        "negative acceptance",
    ],
    ROOT / "skills/development-pipeline/rules/core.md": [
        "final initialization path, driver/provider, runtime owner",
        "Minimal diff is evaluated inside that target state",
    ],
}


def main() -> int:
    failures: list[str] = []
    for path, needles in REQUIREMENTS.items():
        if not path.is_file():
            failures.append(f"missing file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                failures.append(f"{path}: missing required rule: {needle}")

    if failures:
        print("target-state prompt rules failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"target-state prompt rules ok ({len(REQUIREMENTS)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
