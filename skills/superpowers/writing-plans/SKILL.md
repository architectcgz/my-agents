---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write implementation plans that make the target behavior and implementation path obvious to a skilled engineer who lacks local domain context. Name the files, ownership boundaries, important decisions, acceptance criteria, and useful verification. Keep tasks cohesive and concrete; do not turn every mechanical action or check into a separate plan step. Use tests when behavior warrants them. Never schedule git commits in the plan.

Assume the implementer is technically capable but unfamiliar with this repository and its domain.

Announce that you are using `writing-plans` to create the plan, in the project's conversation language.

Use a dedicated worktree when the repository workflow requires isolation. Do not make worktree setup part of the plan body.

## Project Style And Language

Before writing or saving the plan, read the target repository's `AGENTS.md`, documentation rules, and language preference for durable Markdown. Use that language for the plan prose and headings.

Keep code identifiers, paths, commands, package names, SQL, API fields, protocol names, and external proper nouns unchanged. Do not leave English template labels in a project that requires Chinese Markdown.

## Plan Location

Resolve the plan directory in this order:

1. Use `docs/plan/exploratory/YYYY-MM-DD-<feature-name>.md` for drafts, exploration, prototypes, and ordinary implementation plans when the project has no stronger convention.
2. Use the project-defined formal plan location only when the project declares it, the task is structural or cross-module, and it will be tracked through the project's workflow. Create `YYYY-MM-DD-<feature-name>/README.md` rather than a flat file.
3. If the project has no explicit plan structure and still uses the historical convention, use `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`.

Always report the actual entry path. If an exploratory plan later becomes a formal implementation, promote it into the project's formal plan package.

## Scope And Shape

Split a plan only when candidate parts have different owners, dependencies, rollout boundaries, or review boundaries. Do not split a cohesive change merely to create more checklist sections.

For substantial work, choose one of these shapes before writing tasks:

- **Single executable plan:** one owner, one cohesive result, one meaningful verification boundary.
- **Parent program plus child plans:** several services, deployable modules, independently deliverable capabilities, pilots that may change later APIs, or multiple rollback/review boundaries.

Read `references/implementation-plan-structure.md` for parent/child plans when any of those conditions apply. The parent owns target state, dependencies, cross-cutting invariants, child-plan paths, and final convergence. Child plans own local files, implementation approach, acceptance, and verification. Keep routine execution state in the executor's workflow instead of duplicating it throughout the parent.

For a formal multi-boundary plan, resolve delivery ownership, repeated artifact edits, guard timing, and acceptance ownership before freezing the child plans. Use these maps only when the change actually has those boundaries.

## Research And Decisions

Before freezing scope or asking the user to choose an implementation direction:

1. Inspect relevant code, configuration, tests, architecture docs, contracts, and recorded decisions.
2. Consult official primary sources for unknown framework recommendations, versions, compatibility, migration mechanics, or external product behavior.
3. Record a recommended approach. Record alternatives only when they materially change target state, risk, rollout, or maintenance cost.
4. Ask only about boundaries evidence cannot decide, such as product intent, acceptable downtime, risk tolerance, budget, or staged delivery.

Resolve ordinary implementation ambiguity from repository evidence. If a material decision remains open, show the evidence and recommendation, mark the plan pending, and ask one concrete boundary question.

## Testing Stance

Classify each implementation slice:

- **Behavior:** behavior, state, data flow, validation, permissions, async flow, algorithms, API contracts, persistence, or reproducible bug fixes. Include focused tests when the repository supports them.
- **Presentation:** spacing, color, typography, static copy, markup placement, or visual polish without changing event/state semantics. Use the smallest sufficient component, type, build, visual, or manual verification.
- **Mixed:** separate behavior and presentation when doing so clarifies ownership and verification.

Do not add fake failing-test steps to presentation-only work. Do not prescribe TDD mechanically when existing tests, fixtures, or the repository's testing strategy make another focused approach more useful.

## Files And Acceptance

Before defining tasks, map the files to create, modify, or delete and state each file's responsibility. Follow existing boundaries and reuse points; do not invent a new abstraction only to make the plan look modular.

Turn requirements into observable acceptance criteria. For high-risk or contract surfaces, expand applicable MUST/MUST NOT rules into exact fields, states, errors, limits, ownership rules, removal rules, and verification commands. For routine changes, concise acceptance language is enough.

For migrations, replacements, standardization, or framework adoption, define:

1. Final production initialization and primary call path.
2. Final driver/provider and runtime/resource owner.
3. Legacy imports, constructors, drivers, adapters, wrappers, configuration, tests, and dependencies that must disappear.
4. Any retained legacy component and why it is a stable final boundary.
5. A search, architecture check, or behavior check proving the old default path is gone.

Migration plans need both positive acceptance (the new path exists) and negative acceptance (the old default path is gone). Do not silently narrow a requested migration to call-site changes.

## Task Granularity

Each task should describe one cohesive change that can be implemented and verified without unrelated context. A task normally contains:

- **Intent:** what changes and why.
- **Files:** exact create/modify/delete paths, with symbols or line areas when known.
- **Approach:** important implementation decisions, reuse points, and data/state flow.
- **Acceptance:** observable behavior, edge cases, or structural conditions.
- **Verification:** the narrowest useful command or manual check and expected result.

Use numbered steps only when order matters, a step has independent risk, or the executor needs a concrete handoff point. Do not create separate steps for routine inspection, writing an obvious test, running the same command twice, or stopping for review. Checkboxes are optional task tracking, not a requirement for every sentence.

## Compact Plan Template

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing the target result]

**Architecture:** [The relevant owner, call path, interfaces, and important tradeoffs]

**Testing stance:** Behavior | Presentation | Mixed

## Files

- Create: `exact/path`
- Modify: `exact/path`
- Delete: `exact/path`

## Tasks

### Task 1: [Cohesive change]

**Intent:** [What changes and why]

**Approach:** [Concrete implementation path, reuse points, and state/data flow]

**Acceptance:**
- [Observable behavior or structural rule]
- [Important edge case or negative-removal rule]

**Verification:**
- Run: `exact command`
- Expected: `PASS` or the concrete observable result
```

For formal parent programs, use the parent template in `references/implementation-plan-structure.md`. Do not copy parent invariants into every child unless the child needs that exact rule to implement or verify its work.

## Self-Review Before Handoff

Perform one focused self-review after writing the plan:

- Is the artifact correctly shaped as one executable plan or a parent program with child plans?
- Are target architecture boundaries, shared owners, reuse points, and abstraction landing zones explicit where they matter?
- Does every task identify concrete files, an implementation approach, acceptance, and verification?
- Are high-risk constraints expanded into observable criteria instead of broad references?
- For migrations, do positive and negative acceptance prove both adoption and removal of the old default path?
- Are repeated file/document/config edits owned by one task unless an intermediate state is genuinely required?
- Would following this plan predictably require an immediate redesign after completion?

Revise the plan if a material answer is unclear. Formal or explicitly requested review should use the repository's current review workflow; ordinary cohesive plans do not need a reviewer loop.

## Commit Policy

Never add `Commit`, `git commit`, or commit-message commands as execution tasks. Commits happen only after a separate explicit user request through `@committing-changes` and the repository policy.

Do not add a routine user-review stop to every task. The executor decides whether a pause is needed based on risk and explicit review gates.

## Handoff

After saving the plan, report its actual path and state that it can be executed with `@executing-plans`. Do not force an execution-mode choice or add execution checkpoints to the plan unless the task requires them.
