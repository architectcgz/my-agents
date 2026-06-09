#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REQUIRES_ARCHIVE_STATUS_MARKERS = (
    "已沉淀",
    "已机械化",
    "agent-recorded",
)

FEEDBACK_EXCLUDES = {
    "feedback/AGENTS.md",
    "feedback/improvements-index.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when changed feedback records declare an absorbed/mechanized state but are not switched "
            "into an archived status."
        )
    )
    parser.add_argument("--cwd", default=".", help="Repository root or any path inside the repository")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Inspect staged feedback files only")
    mode.add_argument("--working", action="store_true", help="Inspect working tree feedback files only")
    mode.add_argument("--all", action="store_true", help="Inspect staged and working tree feedback files")
    return parser.parse_args()


def resolve_repo_root(cwd: str) -> Path:
    return Path(
        subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )


def run_git(repo_root: Path, args: list[str]) -> str:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def select_mode(args: argparse.Namespace) -> str:
    if args.staged:
        return "staged"
    if args.working:
        return "working"
    if args.all:
        return "all"
    return "head"


def changed_feedback_files(repo_root: Path, mode: str) -> list[str]:
    if mode == "staged":
        tracked = run_git(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "feedback/*.md"]).splitlines()
        return sorted({path for path in tracked if path and path not in FEEDBACK_EXCLUDES})

    if mode == "working":
        tracked = run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR", "--", "feedback/*.md"]).splitlines()
        return sorted({path for path in tracked if path and path not in FEEDBACK_EXCLUDES})

    if mode == "all":
        staged = run_git(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "feedback/*.md"]).splitlines()
        working = run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR", "--", "feedback/*.md"]).splitlines()
        return sorted({path for path in [*staged, *working] if path and path not in FEEDBACK_EXCLUDES})

    tracked = run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR", "HEAD", "--", "feedback/*.md"]).splitlines()
    untracked = run_git(repo_root, ["ls-files", "--others", "--exclude-standard", "--", "feedback/*.md"]).splitlines()
    return sorted({path for path in [*tracked, *untracked] if path and path not in FEEDBACK_EXCLUDES})


def read_status(path: Path) -> str | None:
    content = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^- 状态：\s*(.+?)\s*$", content)
    if match is None:
        return None
    return match.group(1).strip()


def requires_archive_status(status: str | None) -> bool:
    if not status:
        return False
    return any(marker in status for marker in REQUIRES_ARCHIVE_STATUS_MARKERS)


def is_archived_status(status: str | None) -> bool:
    if not status:
        return False
    lowered = status.lower()
    return "archived" in lowered or "归档" in status


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.cwd)
    files = changed_feedback_files(repo_root, select_mode(args))

    violations: list[tuple[str, str]] = []
    for relative_path in files:
        absolute_path = repo_root / relative_path
        if not absolute_path.is_file():
            continue
        status = read_status(absolute_path)
        if requires_archive_status(status) and not is_archived_status(status):
            violations.append((relative_path, status or ""))

    if not violations:
        return 0

    print("[feedback-archive-state] absorbed feedback must switch to archived status")
    print()
    for relative_path, status in violations:
        print(f"- {relative_path}: 状态为 {status}")
    print()
    print("这些条目已经声明为已沉淀/已机械化，但还没有切换到 archived/归档 状态。")
    print("请在吸收完成后把反馈文件改成归档状态，并在沉淀状态里指向实际 owner。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
