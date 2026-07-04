---
name: code-workflow
description: Use when establishing or running the shared non-trivial task workflow across repositories, especially task intake, worktree-per-task, implementation-plan startup gates, commit task binding, and the split between agent orchestration and mechanical enforcement.
---

# Code Workflow

Use this skill when the task is about the engineering workflow itself, or when non-trivial implementation work should enter a disciplined path instead of ad hoc coding.

This skill is global and cross-project. It defines the mechanical workflow model. Project repositories still own protected surfaces, local scripts, hooks, and review checks. Use `development-pipeline` for staged execution of a real engineering task.

## Always Read

- `rules/core.md` for the layered model, non-trivial task binding, project/global boundary, skill interactions, and required behavior.

## Reference Map

| Task surface | Read |
|---|---|
| Shared entry command, installer, sync check, sync, managed files, archive, cleanup | `workflows/shared-scaffold.md` |
| Independent review gate after `completion-full` | `workflows/independent-review.md` |
| Real multi-stage task execution | `../development-pipeline/SKILL.md` |
| Writing implementation plans | `../superpowers/writing-plans/SKILL.md` |
| Task intake analysis | `../superpowers/brainstorming/SKILL.md` or `../superpowers/systematic-debugging/SKILL.md` |
| Challenging assumptions against docs | `../grill-with-docs/SKILL.md` |
| Installing or checking shared workflow packages | `../workflow-package-manager/SKILL.md` |
| Repository harness installation or repair | `../harness-engineering/SKILL.md` |

## Known Gotchas

- Do not collapse intake, startup, pre-commit, completion, independent review, and governance into one script.
- Non-trivial work must not start directly in implementation; run the analysis gate first, then finalize the implementation plan.
- `completion-full` is implementation-context self-check, not the final review gate.
- The independent review gate is orchestration above shell stages; it is not a package-owned shell stage.
- If the shared `code-workflow` package itself changed, run `bash ~/.agents/harness/workflow-sync.sh <repo-root> code-workflow` against each target repository before handoff.

## Check

- Did you classify trivial vs non-trivial and bind non-trivial work to workspace, slug, plan, and startup gate?
- Did you use an existing project-local startup workflow before installing or inventing anything?
- Did you keep agent orchestration separate from mechanical enforcement?
- Did non-trivial completion include independent review after `completion-full`?
