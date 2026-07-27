---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** `subagent-driven-development` is globally disabled. Execute the plan inline in the current session unless the user explicitly requests a different collaboration method.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. After each step's expected result is achieved, immediately update that step's checkbox in the plan from `- [ ]` to `- [x]`
5. After all steps in the task pass validation, mark the task as completed
6. Do not start the next task while completed steps in the current task are still unchecked

Plan checkbox updates are required execution state. Keep them in the working tree as execution status; do **not** auto-commit them. Never report a task as complete while its implementation-plan checklist still shows `- [ ]` for completed work.

After each independently reviewable task or child-plan slice:
1. Run the plan's focused verification.
2. Present changed files, verification evidence, and risks to the user.
3. **Stop** and wait for the user to inspect code quality.
4. Only continue to the next slice after the user accepts or requests fixes.
5. Do **not** `git commit` unless the user later explicitly asks; then use `@committing-changes` and the repository commit policy.

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent
- After each reviewable slice, stop for user code-quality review before continuing
- Never auto-commit; commit only on explicit user request via @committing-changes

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers:writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
