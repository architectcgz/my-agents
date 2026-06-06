#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


DEFAULT_WATCH_PATTERNS = [
    r"^feedback/.*\.md$",
    r"^harness/(prompts|policies|templates|checks)/",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print a non-blocking reminder when project harness knowledge changed and may need "
            "synchronization into shared global skills or harness assets."
        )
    )
    parser.add_argument("--cwd", default=".", help="Repository root or any path inside the repository")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Inspect staged changes only")
    mode.add_argument("--working", action="store_true", help="Inspect working tree changes only")
    mode.add_argument("--all", action="store_true", help="Inspect both staged and working tree changes")
    parser.add_argument(
        "--watch-regex",
        action="append",
        dest="watch_regexes",
        default=None,
        help="Additional regex used to decide whether a changed path should trigger the reminder",
    )
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


def changed_files(repo_root: Path, mode: str) -> list[str]:
    if mode == "staged":
        output = run_git(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        return [line for line in output.splitlines() if line]

    if mode == "working":
        output = run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR"])
        return [line for line in output.splitlines() if line]

    staged = run_git(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"]).splitlines()
    working = run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR"]).splitlines()
    return sorted({line for line in [*staged, *working] if line})


def select_mode(args: argparse.Namespace) -> str:
    if args.working:
        return "working"
    if args.all:
        return "all"
    return "staged"


def matching_files(paths: list[str], regexes: list[str]) -> list[str]:
    compiled = [re.compile(pattern) for pattern in regexes]
    matches: list[str] = []
    for path in paths:
        if any(pattern.search(path) for pattern in compiled):
            matches.append(path)
    return matches


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.cwd)
    mode = select_mode(args)
    watch_regexes = list(DEFAULT_WATCH_PATTERNS)
    if args.watch_regexes:
        watch_regexes.extend(args.watch_regexes)

    changed = changed_files(repo_root, mode)
    if not changed:
        return 0

    matches = matching_files(changed, watch_regexes)
    if not matches:
        return 0

    print("[skill-sync-reminder] Harness knowledge changed.\n")
    print("The following files may contain reusable agent lessons, anti-patterns, or workflow rules:")
    for path in matches:
        print(f"  - {path}")

    print(
        "\nPlease decide whether any durable, cross-project rule should be synchronized to the shared global agent layer:\n"
        "  - skills: /home/azhi/.agents/skills/\n"
        "  - harness prompts/workflows/tools: /home/azhi/.agents/harness/\n"
    )
    print("Guideline:")
    print("  - feedback records are a sedimentation pool, not a behavior entrypoint by themselves.")
    print("  - If the change is only a project-local incident note or one-off context, it may stay in feedback without further projection.")
    print("  - Project fact or CTF-only path/policy -> keep in project harness.")
    print("  - Cross-project method, anti-pattern, checklist, or workflow -> update the relevant global skill or harness asset.")
    print("  - Current-task evidence -> keep in .harness/reuse-decisions/<task-slug>.md only.")
    print("\nThis is a reminder only and does not block the commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
