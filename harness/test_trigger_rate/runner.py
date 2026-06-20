#!/usr/bin/env python3
"""Command runner for trigger-rate checks."""

from __future__ import annotations

import argparse
from pathlib import Path

from .report import generate_report
from .routing import extract_skill_names, parse_quick_routing_table
from .skills import find_skill_description, is_project_local_skill, test_trigger
from .variations import TASK_VARIATIONS


def main():
    parser = argparse.ArgumentParser(
        description="Test skill description trigger rates"
    )
    parser.add_argument(
        "--agents-md",
        type=Path,
        default=Path.cwd() / "AGENTS.md",
        help="Path to AGENTS.md (default: ./AGENTS.md)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed test results"
    )

    args = parser.parse_args()

    if not args.agents_md.exists():
        print(f"Error: {args.agents_md} not found")
        return 1

    # 解析 Quick Routing 表
    routing_table = parse_quick_routing_table(args.agents_md)

    if not routing_table:
        print("Error: Could not find Quick Routing table in AGENTS.md")
        return 1

    print(f"Found {len(routing_table)} task types in Quick Routing table\n")

    repo = args.agents_md.resolve().parent

    # 测试每个任务类型
    results = {}
    exempt = 0

    for task_type, required_reads, workflow_skill in routing_table:
        # 跳过 "Other" 类型
        if "Other" in task_type:
            continue

        # 占位/FILL 行豁免：项目尚未补充真实文件与 skill，不计入触发率
        if "FILL" in workflow_skill or "FILL" in required_reads:
            exempt += 1
            if args.verbose:
                print(f"– 豁免占位行: {task_type}")
            continue

        # 提取 skill 名称
        skills = extract_skill_names(workflow_skill)

        if not skills:
            if args.verbose:
                print(f"⚠ No skills found for: {task_type}")
            continue

        # 获取用户表达方式
        variations = TASK_VARIATIONS.get(task_type, [])

        if not variations:
            if args.verbose:
                print(f"⚠ No variations defined for: {task_type}")
            continue

        # 测试触发率
        hits = 0
        total = len(variations)

        for variation in variations:
            triggered = False
            for skill_name in skills:
                description = find_skill_description(skill_name)
                if test_trigger(variation, description):
                    triggered = True
                    break

            if triggered:
                hits += 1
            elif args.verbose:
                print(f"  ✗ Not triggered: \"{variation}\"")

        results[task_type] = {
            "skills": skills,
            "hits": hits,
            "total": total,
            "local": any(is_project_local_skill(s, repo) for s in skills),
        }

        if args.verbose:
            print(f"✓ Tested: {task_type} ({hits}/{total})\n")

    # 生成报告
    report = generate_report(results)
    print(report)

    # 返回状态码：只对项目自有 skill 把关；指向全局 skill 的标准行只报告、不计入退出码
    local_rows = {k: v for k, v in results.items() if v.get("local")}
    global_rows = [k for k, v in results.items() if not v.get("local")]
    gated_total = sum(v["total"] for v in local_rows.values())
    gated_hits = sum(v["hits"] for v in local_rows.values())
    gated_rate = (gated_hits / gated_total * 100) if gated_total > 0 else 0

    if exempt:
        print(f"\n（已豁免 {exempt} 个占位/FILL 行，未计入触发率；补充真实 skill 后再测）")
    if global_rows:
        print(f"（{len(global_rows)} 行指向全局 skill，只报告不作为退出码依据：{', '.join(global_rows)}）")

    # 没有任何项目自有 skill 可测（如刚 init 的占位薄壳）→ 不判失败
    if gated_total == 0:
        print("没有指向项目自有 skill 的已填充行，跳过触发率门禁判定。")
        return 0

    # 仅当项目自有 skill 的触发率 < 80% 才返回 1
    return 0 if gated_rate >= 80 else 1
