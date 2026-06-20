---
name: spec-coding-workflow
description: Use when starting product, app, website, tool, or feature work from an idea, PRD, UI direction, MVP scope, launch plan, or vague vibe-coding request before implementation begins.
---

# Spec Coding Workflow

## Overview

Use this before substantial product work turns into coding. It makes PRD, design, architecture, TODO, and launch readiness explicit before `code-workflow` handles implementation slices.

## When to Use

Use for:

- New products, apps, websites, tools, prototypes, or major features.
- Requests that start from an idea, market/user problem, UI direction, MVP, or launch goal.
- Work where a Coding Agent would otherwise guess product scope, visual style, architecture, or deployment constraints.

Do not use for tiny edits, narrow bug fixes, or tasks that already have precise specs and only need `code-workflow`.

## Boundary With code-workflow

- `spec-coding-workflow`: defines what to build, what not to build, visual/interaction constraints, architecture boundaries, task slices, and launch readiness.
- `code-workflow`: manages isolated implementation, startup gates, validation, review, archive, and cleanup for non-trivial code slices.

For non-trivial implementation, run this first, then enter `code-workflow`.

## Commands

Install into a repository:

```bash
bash ~/.agents/harness/workflow-installer.sh <repo-root> spec-coding-workflow
```

Start a project spec:

```bash
bash scripts/start-spec-coding.sh <topic-or-slug>
```

Check the scaffold:

```bash
bash scripts/check-spec-coding-docs.sh
```

Check shared-package drift:

```bash
bash ~/.agents/harness/workflow-sync-check.sh <repo-root> spec-coding-workflow
```

## Required Outputs

- `docs/spec/PRD.md`
- `docs/spec/DESIGN.md`
- `docs/spec/ARCHITECTURE.md`
- `docs/spec/TODO.md`
- `docs/spec/LAUNCH-READINESS.md`

## Core Rules

1. Do not start substantial coding until PRD, design, and architecture docs exist.
2. Put MVP scope and explicit non-goals in `PRD.md`.
3. Put visual references, layout, components, interaction states, loading, empty, and error states in `DESIGN.md`.
4. Put stack, data model, service boundaries, AI constraints, deployment assumptions, and invariants in `ARCHITECTURE.md`.
5. Convert the docs into small task slices in `TODO.md`; each slice needs goal, allowed scope, forbidden breakage, acceptance criteria, and validation.
6. Before launch, re-scan the actual code and deployment state, update `ARCHITECTURE.md` and `README.md`, then complete `LAUNCH-READINESS.md`.
