# Shared Scaffold Workflow

Read this file when starting, installing, checking, syncing, archiving, or cleaning up the shared non-trivial task workflow.

## Global entry

`code-workflow` has one global implementation:

```bash
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> <command>
```

Use it directly for runtime operations:

```bash
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> intake
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> start <topic-or-slug>
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> gate --staged
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> stage completion-full
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> archive
bash ~/.agents/harness/workflows/code-workflow/workflow.sh <repo-root> cleanup
```

No repo-local `scripts/workflows/` entrypoint, workflow plugin runner, shared template, or Python helper is installed for this package.

## Package operations

```bash
# Prepare project state only: /.harness/session-gates/ + gitignore entry
bash ~/.agents/harness/workflow-installer.sh <repo-root> code-workflow

# Remove legacy package-managed copies and use the global runtime
bash ~/.agents/harness/workflow-sync.sh <repo-root> code-workflow

# Verify the global runtime and absence of managed local copies
bash ~/.agents/harness/workflow-sync-check.sh <repo-root> code-workflow
```

The project still owns its local documentation, policies, checks and optional stage plugins under `.arccgz-harness/harness/workflow-plugins/code-workflow/<stage>.d/`. The initializer does not create those plugin directories or duplicate shared assets.

## Task lifecycle

1. `start` creates the task worktree, implementation-plan skeleton and startup gate.
2. Run the relevant analysis skill, then `grill-with-docs`, and complete the implementation plan before coding.
3. `completion-full` is implementation-context validation only.
4. An independent `code-reviewer` provides the actual completion gate.
5. `archive` moves task artifacts and changes the gate to `ready_to_merge`; after integration, `cleanup` marks it `archived` and closes the dedicated worktree when safe.
