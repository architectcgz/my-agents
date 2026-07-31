---
name: executing-plans
description: Use when you have a written implementation plan and need to carry it through in the current session, including focused verification and handling of plan gaps or blockers
---

# Executing Plans

## Overview

Load the plan, turn it into working changes, verify the result, and report concrete evidence. Optimize for completed behavior rather than mechanically replaying every checkbox.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

Do not route to `subagent-driven-development`; this skill is the execution path for a single agent working inline.

## The Process

### Step 1: Load the plan

1. Read the plan, its referenced specification, and the repository instructions that apply to the touched files.
2. Identify the target behavior, task boundaries, expected verification, and any missing information that would make implementation unsafe or impossible.
3. Resolve ordinary ambiguities from repository evidence. Stop only for a genuine product, architecture, data-risk, or external-dependency decision that cannot be inferred safely.
4. Create a short working task list only when it improves coordination; do not reproduce the plan as a second checklist.

### Step 2: Execute Tasks

For each task:

1. Confirm the task's files, dependencies, acceptance criteria, and testing stance before editing.
2. Implement the smallest cohesive change that satisfies the task. Follow the plan's steps as implementation guidance, but combine purely mechanical substeps when they do not carry independent risk or evidence.
3. Run the narrowest useful verification for the changed behavior. Do not repeat an identical command merely because it appears under multiple steps; record one result against all applicable criteria.
4. Update the plan's task status and relevant checkboxes after the task reaches its acceptance point. Batch routine checkbox updates at task completion; preserve step-level updates only when the plan uses them as a real handoff or recovery point.
5. Continue to the next task when the current task's acceptance criteria and focused verification pass. Pause for user review only when the plan explicitly defines a review gate, the change is independently reviewable and high-risk, or an unresolved decision is exposed.
6. Do not auto-commit plan or code changes. A commit requires the user's explicit request and `@committing-changes`.

### Step 3: Complete Development

After all tasks complete:

- Run the plan's final verification, plus any broader check needed because tasks interact.
- Report changed files, commands and outcomes, remaining risks, and any plan deviations.
- Use `finishing-a-development-branch` only when the user asks to integrate, merge, clean up, or otherwise finish the branch. Do not turn ordinary plan execution into an integration workflow.

## When to Stop and Ask for Help

**Stop executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- The plan has a critical gap that prevents safe implementation
- An instruction conflicts with repository rules or the user's stated target
- Verification fails repeatedly

Explain the evidence, the exact blocking decision, and the smallest question needed. Do not ask for approval of reversible implementation details.

## When to Revisit the plan

**Return to the plan-loading step when:**
- The user changes the target or acceptance criteria
- Repository evidence invalidates a dependency, file boundary, or architectural assumption
- Verification shows the planned approach cannot satisfy the acceptance criteria

**Don't force through blockers** - stop and ask.

## Remember

- Keep the plan as the source of task intent; do not create a duplicate process log.
- Preserve the plan's acceptance criteria and run enough verification to prove them.
- Prefer one meaningful verification result over repeated ceremonial checks.
- Reference skills when the plan requires them.
- Never start implementation on `main` or `master` without explicit user consent.
- Do not hide deviations: record what changed in the approach and why.
- Never auto-commit; commit only on explicit user request via `@committing-changes`.

**Related skills:**
- **writing-plans** - Creates the plan this skill executes
- **verification-before-completion** - Required before claiming the work is complete
- **finishing-a-development-branch** - Use only when branch integration or cleanup is requested
