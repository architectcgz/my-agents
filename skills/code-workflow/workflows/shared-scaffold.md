# Shared Scaffold Workflow

Read this file when starting, installing, checking, syncing, archiving, or cleaning up the shared non-trivial task workflow.

## Shared entry

The preferred global entry is:

```bash
bash ~/workspace/projects/scripts/start-workflow.sh <topic-or-slug>
```

Behavior:

- If the current repository already has `scripts/start-implementation.sh`, delegate to it.
- If not, initialize the shared workflow scaffold first, then re-run the command.

## Shared scaffold

The shared repo-local assets live under:

```text
~/.agents/harness/workflows/code-workflow/
```

To install the shared non-trivial task workflow into a repository:

```bash
bash ~/.agents/harness/workflow-installer.sh <repo-root> code-workflow
```

To verify that a repository still matches the shared workflow baseline:

```bash
bash ~/.agents/harness/workflow-sync-check.sh <repo-root> code-workflow
```

To resync a repository after the shared package changes:

```bash
bash ~/.agents/harness/workflow-sync.sh <repo-root> code-workflow
```

The scaffold provides the generic common pieces:

- `scripts/check-task-intake.sh`
- `scripts/start-implementation.sh`
- `scripts/check-startup-gate.sh`
- `harness/workflow-plugins/code-workflow/run_workflow_stage.sh`
- `harness/workflow-plugins/code-workflow/archive_task_artifacts.sh`
- `harness/workflow-plugins/code-workflow/cleanup_task_worktree.sh`
- `harness/workflow-plugins/code-workflow/cleanup_task_worktree.py`
- `harness/checks/check_startup_gate.py`
- `harness/templates/implementation-plan-skeleton.md`
- `/.harness/session-gates/` ignore rule

The shared stage runner defines:

- `pre-commit-quick`
- `completion-full`
- `workflow-governance`

Repositories still own which local plugins are registered under each `<stage>.d/` directory.

Generated managed files carry a `Managed by code-workflow package` version header so shared upgrades and drift checks have a stable mechanical target.

Project-specific protected-surface checks and repo-specific review audits remain local.

## Archive completed task artifacts

Use:

```bash
bash harness/workflow-plugins/code-workflow/archive_task_artifacts.sh
```

Run it when a task slice is complete, its conclusions have already been absorbed into the owning docs or code comments, and the active implementation plan should leave `docs/plan/impl-plan/`.

The archive script should:

- move the completed implementation plan into `docs/plan/archive/impl-plan/<YYYY-MM>/`
- archive matching `docs/tasks/*<task-slug>*.md` files into `docs/tasks/archive/<YYYY-MM>/` when that directory exists
- move the local startup gate from `active` to `ready_to_merge` when the current worktree owns the gate
- keep `archived` reserved as the terminal closed state after final cleanup or a later explicit close action

## Cleanup task worktree

Use:

```bash
bash harness/workflow-plugins/code-workflow/cleanup_task_worktree.sh
```

Run it after the task head has already been merged and the startup gate is `ready_to_merge`.

The cleanup script should:

- require the startup gate to already be `ready_to_merge`
- require the task worktree to be clean before removal
- require the task HEAD to already be merged into the chosen target ref, defaulting to `HEAD`
- mark the startup gate `archived` as the terminal closed state
- remove dedicated task worktrees, but never delete the current main worktree root just to close a task that ran in place
- delete the merged `task/<slug>` branch by default after cleanup, unless the operator explicitly keeps that branch reference
