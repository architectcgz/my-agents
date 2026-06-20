#!/usr/bin/env python3
"""Trigger-rate reporting."""

from __future__ import annotations

from typing import Dict


def generate_report(results: Dict[str, Dict]) -> str:
    """生成触发率报告。"""
    report = []
    report.append("=" * 70)
    report.append("Skill Description Trigger Rate Report")
    report.append("=" * 70)
    report.append("")

    total_tasks = len(results)
    total_tests = sum(r["total"] for r in results.values())
    total_hits = sum(r["hits"] for r in results.values())

    for task_type, data in results.items():
        rate = (data["hits"] / data["total"] * 100) if data["total"] > 0 else 0
        status = "✓" if rate >= 80 else "✗"

        report.append(f"{status} {task_type}")
        report.append(f"   Skill: {', '.join(data['skills'])}")
        report.append(f"   Trigger Rate: {data['hits']}/{data['total']} ({rate:.1f}%)")

        if rate < 80:
            report.append(f"   ⚠ Low trigger rate! Recommendation:")
            report.append(f"      - Review skill description")
            report.append(f"      - Add more keywords")
            report.append(f"      - Consider user's natural language")

        report.append("")

    report.append("-" * 70)
    overall_rate = (total_hits / total_tests * 100) if total_tests > 0 else 0
    report.append(f"Overall Trigger Rate: {total_hits}/{total_tests} ({overall_rate:.1f}%)")
    report.append("=" * 70)

    return "\n".join(report)
