---
name: superpowers
description: Use when explicitly inspecting, maintaining, or explaining the Superpowers skill collection, or when choosing among Superpowers sub-skills
---

# Superpowers

Core development practices for effective AI-assisted software development. These skills form the foundation of disciplined, high-quality development workflows.

## Getting Oriented

Use this overview only when the Superpowers collection itself is relevant. For ordinary work, match the task directly against specific skill descriptions instead of treating this container as a default entrypoint.

## 📚 Core Skills

### Development Cycle & Quality

- ~~**test-driven-development**~~ - 暂时禁用（已移到 `~/.agents/skills-disabled/test-driven-development/`，见该目录 `DISABLED.md`）
- **verification-before-completion** - Always verify changes work before claiming completion
- **systematic-debugging** - Root-cause analysis approach for bugs and failures

### Planning & Design

- **brainstorming** - Explore solution space and stress-test requirements before coding
- **writing-plans** - Structure implementation plans for multi-step tasks
- **executing-plans** - Execute plans in separate sessions with review checkpoints

### Code Review & Collaboration

- **requesting-code-review** - How to request effective code reviews
- **receiving-code-review** - How to handle review feedback with technical rigor

### Git & Workflow

- **using-git-worktrees** - Create isolated development environments for feature work
- **finishing-a-development-branch** - Clean branch completion with merge/PR/cleanup options

### Multi-Agent Coordination

- ~~**subagent-driven-development**~~ - 已禁用（已移到 `~/.agents/skills-disabled/subagent-driven-development/`，见该目录 `DISABLED.md`）
- **dispatching-parallel-agents** - Coordinate multiple agents for parallel work

### Meta-Skills

- ~~**writing-skills**~~ - 已禁用（已移到 `~/.agents/skills-disabled/writing-skills/`，见该目录 `DISABLED.md`）
- **writing-plans** - Structure implementation plans

## Usage

1. **Skill routing questions**: Use `using-superpowers` when the task is about skill discovery or invocation discipline.
2. **Creative or implementation design**: Consider `brainstorming` when the task actually involves shaping new behavior.
3. **Feature or bugfix implementation**: `test-driven-development` 当前暂时禁用。行为/逻辑改动按项目测试策略与最小充分验证执行，不要自动加载 TDD skill。
4. **Completion claims**: Apply `verification-before-completion` before claiming changes are complete or passing.
5. **Failures and bugs**: Follow `systematic-debugging` when investigating unexpected behavior.
6. **Skill authoring**: `writing-skills` 当前已禁用。通用 skill 创建、更新与校验使用 `skill-creator`（`quick_validate.py` + `references/validation-checklist.md`）；项目级 skill 路由结构使用 `authoring-project-skills`；仓库级机械校验使用 `harness-engineering`。
7. **Multi-agent plan execution**: `subagent-driven-development` 当前已禁用。不要在实施计划时自动采用该 skill 的多 agent 开发和 review 流程；仅在用户明确要求时，按当前协作能力单独调度。

## 📖 Philosophy

These skills enforce discipline through:
- **Explicit rules** (not suggestions)
- **Verification requirements** (evidence over assertions)
- **Test-first mindset** (RED-GREEN-REFACTOR for behavior-bearing code and docs)
- **Systematic approaches** (root-cause over quick fixes)

All superpowers skills are designed to resist rationalization under pressure. They include explicit counters to common excuses and enforce the letter of the rules, not just the spirit.
