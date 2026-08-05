---
name: harness-engineering
description: "Use when initializing or refactoring a repository into an AI-agent harness: AGENTS.md navigation, repo-as-source-of-truth docs, feedback/improvement loops, mechanical consistency checks, git hook or CI guardrails, and project-specific harness onboarding."
---

# Harness Engineering

Use this skill to turn a repository into a navigable, enforceable harness for coding agents.

Keep `deusyu/harness-engineering` as an important upstream reference, especially for repo-as-source-of-truth, progressive navigation, feedback capture, mechanical enforcement, and agent readability. Use strict top-level reference directories only when the user explicitly asks to follow the upstream structure.

For brand-new project initialization, `harness-engineering` owns the harness subsystem itself. It should expose mechanical commands that a higher-level workflow or operator can call, but it does not own reusable frontend/backend code templates.

## Workflow

1. Read the target repo first: `AGENTS.md`, README, docs indexes, existing hooks, CI, scripts, plan/review/improvement folders, and current `git status`.
2. Classify existing harness assets:
   - navigation: root and nested `AGENTS.md`
   - source of truth: architecture, requirements, contracts, plans, reviews
   - feedback loop: improvements, incidents, review findings, prompts
   - enforcement: scripts, hooks, CI, tests, linters
3. Use the current local harness shape by default while preserving the upstream `deusyu/harness-engineering` principles.
4. Initialize or repair the harness with `~/.agents/harness/harness-initializer.py`, or for the normal harness bootstrap path use `bash ~/.agents/harness/init-project.sh "$PWD"`.
5. Ensure the repository root keeps `CLAUDE.md -> AGENTS.md`; create the symlink when missing, but do not overwrite an existing non-symlink file silently.
6. If `--with-checks` is enabled, ensure the generated scaffold includes `scripts/checks/check-agent-entrypoints.sh` and that the repo's main consistency/governance check actually executes it.
7. If the local workspace provides `~/workspace/projects/scripts/check-agent-entrypoints.sh`, run it against the target repo after initialization.
8. If `--with-checks` is enabled, ensure the generated scaffold includes `scripts/checks/check-test-workflow.sh` and that `scripts/checks/check-harness-consistency.sh`, hooks, or CI actually invoke it.
9. If `--with-checks` is enabled, ensure the generated scaffold includes a minimal `scripts/checks/check-architecture.sh` guard plus seed policy files, and that the consistency check invokes it.
10. If `--with-checks` is enabled, ensure the generated scaffold includes `scripts/checks/check-script-guard.sh` plus `harness/policies/script-guard.json`, and that the consistency check invokes the script guard.
11. Run generated harness checks only when `--with-checks` is enabled and the check is explicitly requested or relevant to the change. Normal `init-project.sh` bootstrap does not install or run them.
12. Report changed files, validation evidence, and any residual gaps.
13. When the repository should adopt the shared non-trivial task workflow, explicitly install it with `bash ~/.agents/harness/workflow-installer.sh "$PWD" code-workflow`, or use `bash ~/.agents/harness/init-project.sh "$PWD" --workflow code-workflow`.
14. Treat `code-workflow` as the owner of non-trivial task workflow semantics. `harness-engineering` should only install or repair that shared workflow entry, not redefine its rules here.

When the repo uses project todos and checks are explicitly enabled, initialize a non-blocking reminder flow on the canonical path `docs/todo/`:

- add `scripts/checks/check-open-todos.sh`
- wire root `AGENTS.md` to read it at task start
- surface its output from `scripts/checks/check-harness-consistency.sh`

When the repo has automated tests or an obvious test surface and checks are explicitly enabled, initialize a mechanical test-workflow guard:

- add `scripts/checks/check-test-workflow.sh`
- have it verify `AGENTS.md` documents the narrowest-relevant-test-first workflow and follow-up script checks
- have `scripts/checks/check-harness-consistency.sh` execute it
- rely on existing pre-commit or CI entry points to enforce it transitively

When the repo has architecture docs or any structural code surface and checks are explicitly enabled, initialize a minimal architecture guard:

- add `scripts/checks/check-architecture.sh`
- seed `harness/policies/architecture-guard-paths.txt`
- seed `harness/policies/architecture-guard-commands.txt`
- have `scripts/checks/check-harness-consistency.sh` execute it
- treat the command list as the project-local extension point for backend/frontend/module boundary checks

When the repo has harness/operator scripts and checks are explicitly enabled, initialize a mechanical script-growth guard:

- add `scripts/checks/check-script-guard.sh`
- seed `harness/policies/script-guard.json`
- have `scripts/checks/check-harness-consistency.sh` execute it
- keep the policy focused on harness/operator entrypoints, wrappers, and harness checks instead of unrelated domain build scripts

When the repo uses the local reuse index pattern, wire a non-blocking reminder into root `AGENTS.md`:

- when implementation first forms a stable reuse pattern in a module, remind the operator to add `.arccgz-harness/state/reuse-index/<source-path>/README.md`
- when reuse structure stabilizes inside a module, remind the operator to add a deeper mirrored `README.md` for that subpath
- keep this as an operator reminder only; do not make local private indexes a pre-commit blocker

## Initialization Command

From any target repository root:

```bash
bash /home/azhi/.agents/harness/init-project.sh "$PWD"
```

To add the shared non-trivial task workflow after the harness exists:

```bash
bash ~/.agents/harness/workflow-installer.sh "$PWD" code-workflow
```

For strict upstream-reference mode:

```bash
bash /home/azhi/.agents/harness/init-project.sh "$PWD" --mode strict-reference
```

`init-project.sh` is the preferred high-level bootstrap wrapper. It runs `harness-initializer.py` and creates only the basic project harness by default. `--with-checks` explicitly adds project checks and hooks, `--workflow <name>` explicitly activates a shared workflow package, and `--full-check` implies `--with-checks` before running the full consistency check. The lower-level Python initializer remains the repair/debugging entry for harness-only operations.

The initializer is idempotent. In both modes it ensures the repo root keeps `CLAUDE.md -> AGENTS.md`, unless an existing conflicting `CLAUDE.md` requires manual resolution. The default profile creates the project documentation, feedback, reuse policy, templates, prompts, and state skeleton; it does not create project checks, hooks, tests, or workflow state. `--with-checks` adds `.arccgz-harness/scripts/checks/`, `.arccgz-harness/scripts/hooks/`, `.arccgz-harness/scripts/tests/`, and their policy inputs. `code-workflow` implementation stays under `~/.agents/harness/workflows/code-workflow/`; it is never copied into the project. In strict reference mode it creates `.arccgz-harness/concepts/`, `.arccgz-harness/thinking/`, `.arccgz-harness/practice/`, `.arccgz-harness/feedback/`, `.arccgz-harness/works/`, `.arccgz-harness/prompts/`, and `.arccgz-harness/references/`; checks remain opt-in through `--with-checks`.

### Existing Agent Instruction Files

Keep the ownership boundary explicit during initialization:

- `~/.agents/AGENTS.md` is global user guidance and is never modified by a project initializer.
- The repository root `AGENTS.md` is a thin auto-discovery and navigation shell. Preserve existing project text; add or update only clearly marked harness blocks, and report the resulting diff.
- `.arccgz-harness/AGENTS.md` is the project owner's harness guidance. Do not overwrite it. Create it only when missing and use a write-if-missing policy for any nested harness `AGENTS.md`.
- Keep durable project-specific rules in `.arccgz-harness/AGENTS.md` or the owning project documentation; do not duplicate the full harness policy into the root entrypoint.
- `CLAUDE.md` must remain a symlink to the root `AGENTS.md`. If a regular file or a symlink to another target already exists, stop and require explicit manual migration; never replace it silently.

## Harness Shape

Keep the harness as a map, not a manual. In the current local standard:

- `AGENTS.md`: repository navigation entry.
- `CLAUDE.md -> AGENTS.md`: Claude/Codex auto-discovery entrypoint alias; keep it as a symlink, not a divergent copy.
- `.arccgz-harness/state/`: current-task state and short-lived execution evidence only.
- `.arccgz-harness/harness/policies/`: project-local mechanical policy inputs.
- `.arccgz-harness/harness/templates/`: project-local templates for repeated decisions.
- `.arccgz-harness/harness/prompts/`: stable in-repo prompt entrypoints, local parameters, and prompts that are still truly project-local. Shared prompt bodies can live under `~/.agents/harness/prompts/`. Do not keep one-off initialization prompts, historical migration prompts, or rules already moved into a global skill.
- `.arccgz-harness/harness/checks/`: optional deterministic guard helpers, only when checks are enabled.
- `.arccgz-harness/state/reuse-index/`: user-local, gitignored reuse index. Keep `index.yaml` as the top-level route map and mirrored `README.md` files as module/module-internal secondary indexes.
- `.arccgz-harness/feedback/`: mistakes, corrections, workflow lessons, and reusable learning that has not yet been fully absorbed elsewhere.
- Optional `scripts/checks/check-harness-consistency.sh`: deterministic base harness guard against drift.
- Optional `scripts/checks/check-agent-entrypoints.sh`: deterministic guard for `CLAUDE.md -> AGENTS.md` and project-local Claude skill bridges.
- Optional `scripts/checks/check-architecture.sh`, `check-test-workflow.sh`, and `check-script-guard.sh`: project policy guards enabled together with `--with-checks`.
- Optional `scripts/checks/check-open-todos.sh` and `check-skill-sync-reminder.sh`: non-blocking operator reminders enabled together with `--with-checks`.
- Shared non-trivial task workflow package: install and verify `~/.agents/harness/workflows/code-workflow/`, but keep its behavior definition in the `code-workflow` skill instead of duplicating it here.

When strict upstream reference mode is requested, use `concepts/`, `thinking/`, `practice/`, `feedback/`, `works/`, `prompts/`, and `references/` as demonstrated by `deusyu/harness-engineering`. In that mode, `concepts/` supplements the root `AGENTS.md` with long-lived concepts and principles rather than replacing the root navigation role.

## Guardrails

- Do not duplicate long architecture content into harness docs; link to the owning source.
- Do not overwrite existing user text outside managed marker blocks.
- When the user says to strictly follow `deusyu/harness-engineering`, create the top-level reference directories even if the repo already has docs elsewhere.
- Treat the current local harness shape as an evolving default, not a frozen universal law; preserve project-specific adaptation when the target repo has stronger existing conventions.
- When checks are explicitly enabled, treat missing mechanical enforcement as a real harness gap, not just a documentation issue.
- Treat missing or drifted `CLAUDE.md -> AGENTS.md` as a harness gap; fix it during initialization or fail loudly if an existing file conflicts.
- If a repo has dirty worktree changes, avoid touching those files unless the task requires it.
- Feedback records should include a sedimentation status section that names whether the lesson is already absorbed, project-only, awaiting skill sync, mechanized, archived, or obsolete. Once a lesson is fully captured by a global skill, global AGENTS rule, project policy, or mechanical check, switch the feedback file into an archived state so it no longer reads like active guidance.
- Add or preserve a non-blocking skill-sync reminder when feedback, reuse knowledge, prompts, policies, or templates change. The reminder should force a conscious decision: keep project-only knowledge local, or move cross-project methods and anti-patterns into the relevant global skill.
- Prefer the shared harness implementation at `~/.agents/harness/skill-sync/remind_skill_sync.py`; project repositories should usually keep only a thin wrapper script and local hook wiring.
- Reuse-first policies should cover both frontend and backend creation surfaces. Frontend surfaces usually include pages, components, hooks, stores, API wrappers, forms, tables, modals, layouts, and schemas. Backend surfaces usually include services, handlers, repositories, ports, jobs/workers, mappers, read models, runtime composition, schemas, and migrations.
- Reuse-index reminders should fire during active implementation, especially when a new module, feature slice, service cluster, or module-internal layer is becoming a reusable pattern for the first time.
- New harness/project initialization should include project documentation architecture by reusing `documentation-architecture` assets, normally `docs/documentation-rules.md` and `docs/README.md`. Project `AGENTS.md` should only route to those files, not duplicate the full documentation policy.

## References

Read `references/harness-adaptation.md` only when the user explicitly asks for an adapted, non-strict harness.

Read `references/thin-shell-and-hooks.md` when wiring entry files (`AGENTS.md` / `CODEX.md` / `.cursor`) and SessionStart / PreToolUse hooks so discipline survives long sessions, compaction, and `/clear` — thin-shell routing tables, three-layer anti-amnesia, and placeholder-shell bootstrapping for fresh projects.

Read `references/skill-validation.md` when adding mechanical validation for skills — smoke-test (SKILL.md as source of truth: routing integrity, line counts, placeholder/entry consistency) and test-trigger (description trigger-rate), wired into the consistency check / hooks / CI.
