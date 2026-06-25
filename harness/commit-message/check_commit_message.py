#!/usr/bin/env python3
"""Shared commit message checker for project-local policies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_MESSAGES = {
    "usage_error": "[commit-msg] 用法错误，请检查 hook 或脚本接线",
    "missing_message_file": "[commit-msg] 找不到提交信息文件: {message_file}",
    "invalid_policy_file": "[commit-msg] 提交信息策略文件缺失或无效: {policy_file}",
    "empty_subject": "[commit-msg] 提交信息不能为空",
    "invalid_subject": "[commit-msg] 提交信息格式不符合约束。",
    "missing_chinese_description": "[commit-msg] 提交描述必须包含中文说明。",
    "missing_detail_lines": "[commit-msg] 普通提交不能只有简短标题，必须补充详细正文。",
    "detail_too_short": "[commit-msg] 提交正文信息量不足，请补充更具体的变更说明。",
    "missing_task_binding": "[commit-msg] 当前存在激活中的任务 gate，提交正文必须显式带上 task slug。",
    "forbidden_co_authored_by": "[commit-msg] 提交信息包含禁止的 Co-Authored-By trailer。\n默认禁止添加 Co-Authored-By，除非：\n  1. 用户明确要求添加，或\n  2. 项目 commit policy 显式允许（在 policy.json 中设置 \"allow_co_authored_by\": true）\n详见 ~/.agents/skills/committing-changes/SKILL.md",
}


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        fail("invalid_policy_file", policy_file=str(path))
        raise AssertionError("unreachable")


def build_messages(policy: dict) -> dict[str, str]:
    messages = dict(DEFAULT_MESSAGES)
    messages.update(policy.get("messages", {}))
    return messages


def fail(message_key: str, **kwargs: str) -> None:
    template = ACTIVE_MESSAGES.get(message_key, DEFAULT_MESSAGES[message_key])
    print(template.format(**kwargs), file=sys.stderr)
    raise SystemExit(1)


def collect_body_lines(lines: list[str]) -> list[str]:
    body_lines: list[str] = []
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\r")
        if line.startswith("#"):
            continue
        stripped = line.strip()
        if stripped:
            body_lines.append(stripped)
    return body_lines


def is_metadata_line(line: str, ignored_prefixes: list[str]) -> bool:
    return any(line.startswith(prefix) for prefix in ignored_prefixes)


def visible_char_count(lines: list[str]) -> int:
    return sum(len("".join(ch for ch in line if not ch.isspace())) for line in lines)


def validate_subject(subject: str, policy: dict) -> None:
    if not subject:
        fail("empty_subject")

    if subject.startswith("Merge ") or subject.startswith("Revert "):
        raise SystemExit(0)

    allowed_types = policy["allowed_types"]
    scope_pattern = policy.get("scope_pattern", r"[^)]+")
    type_pattern = "|".join(re.escape(item) for item in allowed_types)
    pattern = rf"^({type_pattern})(\({scope_pattern}\))?: .+$"
    if not re.match(pattern, subject):
        fail("invalid_subject")

    if policy.get("require_chinese_description"):
        description = subject.split(": ", 1)[1]
        if not re.search(r"[\u4e00-\u9fff]", description):
            fail("missing_chinese_description")


def validate_body(body_lines: list[str], policy: dict) -> None:
    body_policy = policy.get("body", {})
    ignored_prefixes = list(body_policy.get("ignored_prefixes", []))
    task_prefix = policy.get("task", {}).get("line_prefix")
    if task_prefix and task_prefix not in ignored_prefixes:
        ignored_prefixes.append(task_prefix)

    detail_lines = [line for line in body_lines if not is_metadata_line(line, ignored_prefixes)]
    min_detail_lines = int(body_policy.get("min_detail_lines", 0))
    if len(detail_lines) < min_detail_lines:
        fail("missing_detail_lines")

    min_visible_chars = int(body_policy.get("min_visible_chars", 0))
    if visible_char_count(detail_lines) < min_visible_chars:
        fail("detail_too_short")


def validate_task_binding(body_lines: list[str], policy: dict, active_task_slug: str | None) -> None:
    task_policy = policy.get("task", {})
    if not active_task_slug or not task_policy.get("required_when_active", False):
        return

    line_prefix = task_policy.get("line_prefix", "Task:")
    matched = any(
        line.startswith(line_prefix) and line[len(line_prefix) :].strip() == active_task_slug
        for line in body_lines
    )
    if not matched:
        fail(
            "missing_task_binding",
            task_slug=active_task_slug,
            task_line_prefix=line_prefix,
        )


def validate_no_co_authored_by(body_lines: list[str], policy: dict) -> None:
    """Check for forbidden Co-Authored-By trailers.

    Default: Co-Authored-By is forbidden unless project explicitly allows it.
    Projects can opt-in by setting "allow_co_authored_by": true in policy.json.

    Rationale: Per ~/.agents/skills/committing-changes/SKILL.md, Co-Authored-By
    should only be added when:
    1. User explicitly requests it, OR
    2. Project commit policy explicitly allows it

    Without either condition, it should be blocked.
    """
    if policy.get("allow_co_authored_by", False):
        return

    for line in body_lines:
        if line.startswith("Co-Authored-By:") or line.startswith("Co-authored-by:"):
            fail("forbidden_co_authored_by")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message-file", required=True)
    parser.add_argument("--policy-file", required=True)
    parser.add_argument("--active-task-slug")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    message_file = Path(args.message_file)
    if not message_file.is_file():
        fail("missing_message_file", message_file=str(message_file))

    policy_file = Path(args.policy_file)
    policy = load_json(policy_file)

    global ACTIVE_MESSAGES
    ACTIVE_MESSAGES = build_messages(policy)

    lines = message_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    subject = lines[0].rstrip("\r") if lines else ""

    validate_subject(subject, policy)
    body_lines = collect_body_lines(lines)
    validate_body(body_lines, policy)
    validate_no_co_authored_by(body_lines, policy)
    validate_task_binding(body_lines, policy, args.active_task_slug)
    return 0


ACTIVE_MESSAGES = dict(DEFAULT_MESSAGES)


if __name__ == "__main__":
    raise SystemExit(main())
