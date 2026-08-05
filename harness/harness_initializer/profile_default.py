#!/usr/bin/env python3
"""Default harness initializer profile."""

from __future__ import annotations

from pathlib import Path

from .consistency_content import current_check_script
from .docs_content import current_docs
from .profile_common import quick_routing_shell, write_common_scaffold
from .scaffold import HARNESS_CHECKS, HARNESS_HOOKS, HARNESS_ROOT, ensure_documentation_scaffold, harness_dir, insert_or_replace, write


def configure_current(
    repo: Path, project_name: str, profile: str, with_checks: bool = False
) -> tuple[str, str]:
    root = harness_dir(repo)
    ensure_documentation_scaffold(repo)
    for relative, content in current_docs(project_name, profile, with_checks).items():
        write(root / relative, content)
    write_common_scaffold(repo, profile, current_check_script(), with_checks)
    insert_or_replace(
        repo / "AGENTS.md",
        "root-navigation",
        f"""## Harness Engineering

当前采用通用的本地 harness 形态，并保留 `deusyu/harness-engineering` 的核心原则作为重要参考。

| 路径 | 内容 | 说明 |
|------|------|------|
| `{HARNESS_ROOT}/state/` | 当前任务状态 | 只保存短期执行证据和当前 reuse 决策 |
| `{HARNESS_ROOT}/state/reuse-index/` | 本地私有索引 | 用户自用的长期复用线索，默认 gitignore，`index.yaml` + 镜像 `README.md` |
| `{HARNESS_ROOT}/harness/policies/` | 项目策略 | 项目级复用和约束配置 |
| `{HARNESS_ROOT}/harness/templates/` | 模板 | 当前项目重复使用的决策或记录模板 |
| `{HARNESS_ROOT}/harness/prompts/` | Prompt 入口 | 仓库内稳定入口、局部补充，以及仍然项目专属的 prompt |
| `{HARNESS_ROOT}/feedback/` | 反馈记录 | 踩坑、修正和可复用流程经验 |
| `{HARNESS_ROOT}/docs/documentation-rules.md` | 文档规范 | 改文档前置读取与新增路径登记 |
| `{HARNESS_ROOT}/docs/README.md` | 文档索引 | 当前事实源地图和文档阅读顺序 |
| `{HARNESS_ROOT}/docs/architecture/` | 架构事实 | 当前系统设计、边界和长期技术约束 |

项目根保持 `CLAUDE.md -> AGENTS.md`，让 Claude / Codex 使用同一份入口规则。

共享 workflow 不默认安装；需要时显式运行 `bash ~/.agents/harness/init-project.sh <repo-root> --workflow code-workflow`。

开发过程中，如果某个模块第一次形成稳定复用模式，主动补 `{HARNESS_ROOT}/state/reuse-index/<source-path>/README.md`；如果模块内部也已经分出稳定层次，再继续补该子路径下的镜像 `README.md`。这是本地提醒，不作为 pre-commit 阻塞项。

如果用户明确要求严格参考 `deusyu/harness-engineering` 的目录形态，再使用 strict reference 模式。""",
    )
    insert_or_replace(
        repo / "AGENTS.md",
        "quick-routing",
        quick_routing_shell(),
    )
    insert_or_replace(
        repo / "AGENTS.md",
        "todo-reminder",
        f"""## Todo Reminder

开始新任务前，先读取 `{HARNESS_ROOT}/docs/todo/` 里的未完成事项；如果命中当前主题，先把它纳入任务范围。已完成但还没归档的 todo 也应顺手处理。""",
    )
    insert_or_replace(
        repo / "AGENTS.md",
        "test-workflow",
        f"""## Test Workflow

- After changing tests, run the smallest relevant test command that covers the touched surface.
- Follow any project-specific test, build, or lint checks documented by the repository; the harness does not install a generic follow-up check by default.""",
    )
    hook_docs = f"""## Harness 检查

- `pre-commit`：运行 `{HARNESS_HOOKS}/check-pre-commit.sh`，只对 staged harness 相关路径运行完整一致性检查；普通业务提交走快速路径。
- 完整一致性检查：显式运行 `{HARNESS_CHECKS}/check-harness-consistency.sh`，用于 CI 或 harness 变更后的完整校验。
- 共享 workflow：运行 `bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> <command>`；安装或同步不会再复制 workflow 脚本、模板或插件到项目中。
- Hook 生效检查：运行 `{HARNESS_HOOKS}/check-hooks.sh`；如果尚未接入，运行 `bash ~/.agents/harness/install-project-hooks.sh <repo-root>`。
- skill sync reminder 保持非阻塞，只提醒把跨项目规则上收全局 skill 或 shared harness。
- `commit-msg`：运行 `{HARNESS_HOOKS}/check-commit-message.sh`，由共享检查器读取 `{HARNESS_ROOT}/harness/policies/commit-message.json` 校验标题、正文和激活任务的 `Task:` 绑定。
- 原有项目 hook 逻辑继续保留。"""
    return "Initialized default harness", hook_docs
