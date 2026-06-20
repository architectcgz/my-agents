# spec-coding-workflow package

This package owns the repo-local assets for a spec-first product development workflow.

It complements `code-workflow`; it does not replace it.

- `spec-coding-workflow` answers: what should be built, how it should look, what boundaries must hold, what tasks are allowed, and what must be checked before launch.
- `code-workflow` answers: how non-trivial code changes are isolated, planned, validated, reviewed, archived, and cleaned up.

Install into a repository:

```bash
bash ~/.agents/harness/workflow-installer.sh <repo-root> spec-coding-workflow
```

Sync a repository after the shared package changes:

```bash
bash ~/.agents/harness/workflow-sync.sh <repo-root> spec-coding-workflow
```

Check whether a repository still matches this package baseline:

```bash
bash ~/.agents/harness/workflow-sync-check.sh <repo-root> spec-coding-workflow
```

## Workflow

Use this workflow before starting substantial product or app work, especially when a request starts from an idea rather than a precise engineering task.

1. Product definition: produce `docs/spec/PRD.md`.
2. Visual design: produce `docs/spec/DESIGN.md`.
3. Development boundaries: produce `docs/spec/ARCHITECTURE.md`.
4. Execution slicing: produce `docs/spec/TODO.md`.
5. Implementation: enter `code-workflow` for non-trivial task slices.
6. Launch readiness: update `docs/spec/LAUNCH-READINESS.md` and reflect reality back into `ARCHITECTURE.md` and `README.md`.

## Installed Assets

The package installs these managed files:

- `scripts/start-spec-coding.sh`
- `scripts/check-spec-coding-docs.sh`
- `harness/templates/spec-coding-workflow/PRD.md`
- `harness/templates/spec-coding-workflow/DESIGN.md`
- `harness/templates/spec-coding-workflow/ARCHITECTURE.md`
- `harness/templates/spec-coding-workflow/TODO.md`
- `harness/templates/spec-coding-workflow/LAUNCH-READINESS.md`

Run the repo-local entrypoint:

```bash
bash scripts/start-spec-coding.sh <topic-or-slug>
```

Then validate the spec scaffold:

```bash
bash scripts/check-spec-coding-docs.sh
```

## Rules

- Do not ask a Coding Agent to start implementation before `PRD.md`, `DESIGN.md`, and `ARCHITECTURE.md` exist for non-trivial product work.
- Treat `TODO.md` as the implementation queue. One task slice should have one explicit goal, allowed edit scope, forbidden breakage, and acceptance criteria.
- Frontend work should include visual references, layout constraints, interaction states, loading states, empty states, and error states before coding.
- Architecture docs must state data models, service boundaries, AI/agent constraints, deployment assumptions, and non-negotiable invariants.
- Launch readiness must re-scan the actual code and deployment state, then update docs to match reality.
- When implementation starts, use the repository's `code-workflow` path for non-trivial slices.
