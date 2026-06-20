#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TASK_SLUG_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$")


def fail(message, hint=None):
    print(f"FAIL: {message}", file=sys.stderr)
    if hint:
        print(f"Hint: {hint}", file=sys.stderr)
    raise SystemExit(1)


def git(args, cwd=None, check=True, capture=True):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=capture,
        text=True,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Safely close a task worktree after the task has already been "
            "archived and merged."
        )
    )
    parser.add_argument("--task-slug", default="")
    parser.add_argument("--branch", dest="branch_name", default="")
    parser.add_argument("--worktree", dest="worktree_path", default="")
    parser.add_argument("--merged-into", default="HEAD")
    parser.add_argument("--keep-branch", action="store_false", dest="delete_branch")
    parser.add_argument("--dry-run", action="store_true")
    parser.set_defaults(delete_branch=True)
    return parser.parse_args()


def resolve_repo_root():
    result = git(["rev-parse", "--show-toplevel"])
    root = result.stdout.strip()
    if not root:
        fail("cleanup must run inside a git repository")
    return Path(root).resolve()


def active_slug_from_startup_gate(root):
    script = root / "scripts/check-startup-gate.sh"
    if not script.is_file() or not script.stat().st_mode & 0o111:
        return ""
    result = subprocess.run(
        ["bash", str(script), "--print-active-slug"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def resolve_task_context(args, root):
    task_slug = args.task_slug or active_slug_from_startup_gate(root)
    branch_name = args.branch_name

    if not branch_name and task_slug:
        branch_name = f"task/{task_slug}"

    if not task_slug and branch_name:
        match = re.fullmatch(r"task/(.+)", branch_name)
        if match:
            task_slug = match.group(1)

    if not task_slug:
        fail("unable to resolve task slug; pass --task-slug or run inside the task worktree")

    if not TASK_SLUG_RE.fullmatch(task_slug):
        fail(f"invalid task slug: {task_slug}")

    if not branch_name:
        branch_name = f"task/{task_slug}"

    return task_slug, branch_name


def verify_ref(ref):
    if git(["rev-parse", "--verify", "--quiet", ref], check=False).returncode != 0:
        fail(f"merged target ref does not exist: {ref}")


def resolve_worktree_path(branch_name, explicit_path):
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_dir():
            fail(f"worktree path not found: {explicit_path}")
        return path.resolve()

    output = git(["worktree", "list", "--porcelain"]).stdout.splitlines()
    current = {}
    entries = []
    for line in output:
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        entries.append(current)

    expected_branch = f"refs/heads/{branch_name}"
    for entry in entries:
        if entry.get("branch") == expected_branch:
            path = entry.get("worktree", "")
            if path:
                return Path(path).resolve()

    fail(f"unable to resolve worktree path for branch: {branch_name}")


def read_gate(gate_path):
    if not gate_path.is_file():
        fail(f"task gate not found: {gate_path}")
    return json.loads(gate_path.read_text(encoding="utf-8"))


def validate_gate(payload, branch_name, worktree_path):
    status = payload.get("status", "")
    if status != "ready_to_merge":
        fail(
            f"task gate must be ready_to_merge before cleanup: {status}",
            "archive task artifacts first with harness/workflow-plugins/code-workflow/archive_task_artifacts.sh",
        )

    gate_branch = payload.get("branch", "")
    if gate_branch and gate_branch != branch_name:
        fail(f"gate branch mismatch: expected {branch_name}, got {gate_branch}")

    gate_worktree_path = payload.get("worktree_path", "")
    if gate_worktree_path:
        normalized = Path(gate_worktree_path).resolve()
        if normalized != worktree_path:
            fail(f"gate worktree path mismatch: expected {worktree_path}, got {normalized}")


def validate_worktree(root, worktree_path, merged_into_ref):
    status = git(["-C", str(worktree_path), "status", "--porcelain"]).stdout
    if status:
        fail(
            f"worktree has uncommitted changes: {worktree_path}",
            "commit, move, or discard those changes before cleanup.",
        )

    task_head = git(["-C", str(worktree_path), "rev-parse", "HEAD"]).stdout.strip()
    result = git(["merge-base", "--is-ancestor", task_head, merged_into_ref], cwd=root, check=False)
    if result.returncode != 0:
        fail(f"task head is not merged into {merged_into_ref}")


def print_plan(task_slug, branch_name, worktree_path, merged_into_ref, main_worktree, delete_branch):
    print("DRY RUN: task worktree cleanup would proceed")
    print(f"- task slug: {task_slug}")
    print(f"- branch: {branch_name}")
    print(f"- worktree: {worktree_path}")
    print(f"- merged into: {merged_into_ref}")
    print("- action: mark startup gate archived in current worktree" if main_worktree else "- action: remove dedicated worktree")
    print("- action: delete merged task branch after cleanup" if delete_branch else "- action: keep branch reference after cleanup")


def mark_gate_archived(gate_path, merged_ref, removed_worktree):
    payload = read_gate(gate_path)
    payload["status"] = "archived"
    payload["closed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload["merged_into"] = merged_ref
    payload["removed_worktree"] = removed_worktree
    gate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def delete_branch_if_requested(root, branch_name, delete_branch):
    if not delete_branch:
        return
    if git(["rev-parse", "--verify", "--quiet", branch_name], cwd=root, check=False).returncode == 0:
        git(["branch", "-d", branch_name], cwd=root, capture=False)


def print_success(task_slug, branch_name, merged_into_ref, worktree_path, main_worktree, delete_branch):
    print("PASS: task worktree cleanup complete")
    print(f"- task slug: {task_slug}")
    print(f"- branch: {branch_name}")
    print(f"- merged into: {merged_into_ref}")
    print("- startup gate archived in current worktree" if main_worktree else f"- removed worktree: {worktree_path}")
    print(f"- {'deleted' if delete_branch else 'kept'} branch: {branch_name}")


def main():
    args = parse_args()
    root = resolve_repo_root()
    task_slug, branch_name = resolve_task_context(args, root)
    verify_ref(args.merged_into)

    worktree_path = resolve_worktree_path(branch_name, args.worktree_path)
    gate_path = worktree_path / ".harness/session-gates" / f"{task_slug}.json"
    payload = read_gate(gate_path)
    validate_gate(payload, branch_name, worktree_path)
    validate_worktree(root, worktree_path, args.merged_into)

    main_worktree = worktree_path == root
    if args.dry_run:
        print_plan(task_slug, branch_name, worktree_path, args.merged_into, main_worktree, args.delete_branch)
        return

    mark_gate_archived(gate_path, args.merged_into, not main_worktree)
    if not main_worktree:
        git(["worktree", "remove", str(worktree_path)], cwd=root, capture=False)
    delete_branch_if_requested(root, branch_name, args.delete_branch)
    print_success(task_slug, branch_name, args.merged_into, worktree_path, main_worktree, args.delete_branch)


if __name__ == "__main__":
    main()
