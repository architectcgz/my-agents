#!/usr/bin/env python3
"""Behavior checks for staged consistency child-check routing."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness_initializer.consistency_routing import staged_check_routing


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


def run_router(root: Path) -> str:
    result = subprocess.run(
        [bash_command(), "router.sh", "--staged"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-consistency-routing-") as temp_dir:
        root = Path(temp_dir)
        (root / "router.sh").write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f"{staged_check_routing()}\n"
            "if should_run_entrypoints; then echo entrypoints=run; else echo entrypoints=skip; fi\n"
            "if should_run_script_guard; then echo script_guard=run; else echo script_guard=skip; fi\n",
            encoding="utf-8",
        )
        (root / "once.sh").write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f"{staged_check_routing()}\n"
            "check_once() { printf 'called\\n' >> once.marker; }\n"
            "run_check_once duplicate check_once\n"
            "run_check_once duplicate check_once\n",
            encoding="utf-8",
        )
        (root / "src").mkdir()
        (root / "src/example.txt").write_text("example\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("agents\n", encoding="utf-8")
        (root / ".arccgz-harness/scripts/checks").mkdir(parents=True)
        (root / ".arccgz-harness/scripts/checks/check-example.sh").write_text("check\n", encoding="utf-8")

        run_git(root, "init", "--quiet")

        subprocess.run([bash_command(), "once.sh"], cwd=root, check=True, capture_output=True, text=True)
        assert (root / "once.marker").read_text(encoding="utf-8") == "called\n"

        run_git(root, "add", "src/example.txt")
        ordinary = run_router(root)
        assert "entrypoints=skip" in ordinary
        assert "script_guard=skip" in ordinary

        run_git(root, "reset", "--quiet")
        run_git(root, "add", "AGENTS.md")
        entrypoint = run_router(root)
        assert "entrypoints=run" in entrypoint
        assert "script_guard=skip" in entrypoint

        run_git(root, "reset", "--quiet")
        run_git(root, "add", ".arccgz-harness/scripts/checks/check-example.sh")
        script = run_router(root)
        assert "entrypoints=skip" in script
        assert "script_guard=run" in script

    print("PASS: staged consistency routing selects entrypoint and script checks")


if __name__ == "__main__":
    main()
