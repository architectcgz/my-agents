#!/usr/bin/env python3
"""Behavior checks for the staged-file pre-commit guard."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness_initializer.content import pre_commit_guard_script


def bash_command() -> str:
    if os.name == "nt":
        candidates = [
            Path("C:/Program Files/Git/bin/bash.exe"),
            Path(os.environ.get("ProgramFiles", "")) / "Git/bin/bash.exe",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    return shutil.which("bash") or "bash"


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def run_guard(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [bash_command(), ".arccgz-harness/scripts/hooks/check-pre-commit.sh", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-pre-commit-") as temp_dir:
        root = Path(temp_dir)
        script = root / ".arccgz-harness/scripts/hooks/check-pre-commit.sh"
        consistency = root / ".arccgz-harness/scripts/checks/check-harness-consistency.sh"
        reminder = root / ".arccgz-harness/scripts/checks/check-skill-sync-reminder.sh"
        marker = root / ".test-marker"
        script.parent.mkdir(parents=True)
        consistency.parent.mkdir(parents=True)
        script.write_text(pre_commit_guard_script(), encoding="utf-8")
        consistency.write_text(
            "#!/usr/bin/env bash\nprintf 'consistency:%s\\n' \"$*\" >> .test-marker\n",
            encoding="utf-8",
        )
        reminder.write_text(
            "#!/usr/bin/env bash\nprintf 'reminder\\n' >> .test-marker\n",
            encoding="utf-8",
        )
        (root / "src").mkdir()
        (root / "src/example.txt").write_text("example\n", encoding="utf-8")
        (root / ".arccgz-harness/policy.txt").write_text("policy\n", encoding="utf-8")

        run_git(root, "init", "--quiet")
        run_git(root, "add", "src/example.txt")

        explained = run_guard(root, "--explain")
        assert explained.returncode == 0, explained.stderr
        assert "skip: full consistency" in explained.stdout
        assert not marker.exists()

        fast = run_guard(root)
        assert fast.returncode == 0, fast.stderr
        assert marker.read_text(encoding="utf-8") == "reminder\n"

        run_git(root, "add", ".arccgz-harness/policy.txt")
        explained = run_guard(root, "--explain")
        assert explained.returncode == 0, explained.stderr
        assert "run: staged consistency (child checks route by staged path)" in explained.stdout

        structural = run_guard(root)
        assert structural.returncode == 0, structural.stderr
        assert marker.read_text(encoding="utf-8") == "reminder\nconsistency:--staged\nreminder\n"

    print("PASS: pre-commit guard staged-path routing and explain mode")


if __name__ == "__main__":
    main()
