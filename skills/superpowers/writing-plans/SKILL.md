---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD where applicable. **Do not put git commit steps in the plan.** The user owns both independent review and quality review; plans must provide the evidence they need and must not schedule agent-run review loops.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** say that you are using the `writing-plans` skill to create the implementation plan, in the user's/project's conversation language.

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

## Project Style And Language Gate

Before writing or saving the plan, read the target repository's `AGENTS.md`, docs rules, and any user language preference that applies to durable Markdown. The plan's prose, headings, task labels, checkbox text, and handoff text MUST use the project's required documentation language.

English in the examples below is semantic scaffolding, not output text. Translate labels such as `Task`, `Files`, `Step`, `Run`, `Expected`, `Verification`, and `Risks` into the target project's documentation language when the project requires non-English Markdown. Keep code identifiers, paths, commands, package names, SQL, API fields, error constants, protocol names, and external proper nouns in their original form.

If project rules require Chinese Markdown, write the plan body in Chinese by default. Use mappings like `Task` -> `任务`, `Files` -> `文件`, `Step` -> `步骤`, `Run` -> `运行`, `Expected` -> `预期`, `Verification` -> `验证`, `Risks` -> `风险`, and `Architecture Fit Evaluation` -> `架构适配评估`. Before finalizing, run a quick residue scan for common template words such as `Task`, `Step`, `Files`, `Run:`, `Expected:`, `Risks`, and `Architecture Fit Evaluation`; revise any leftover template prose unless it is part of a command, code identifier, file path, test name, or quoted external text.

**Save plans to the appropriate directory based on plan type.**

Resolve the plan directory in this order:

1. **Default (exploratory plans)**: `docs/plan/exploratory/YYYY-MM-DD-<feature-name>.md`
   - Use this for quick drafts, technical exploration, prototyping, and temporary investigations
   - Does not require project to declare this location
   - Short lifecycle, can be deleted after completion

2. **Formal implementation plans**: Only use the project-defined formal plan location if ALL of these conditions are met:
   - The project explicitly defines a formal implementation plan location (e.g., via `<!-- FORMAL_IMPL_PLAN_DIR: docs/plan/impl-plan/ -->` marker in `AGENTS.md`, or explicit `formal_impl_plan_location` field)
   - The task is structural, cross-module, or requires formal review and task gate binding
   - The plan will be tracked through code-workflow with a task slug and startup gate
   - Create a dedicated plan package under that location: `YYYY-MM-DD-<feature-name>/README.md`
   - Do not add a new formal plan as a flat Markdown file directly under `docs/plan/impl-plan/`
   - A single executable plan may contain only `README.md`; a parent program keeps numbered child plans beside its `README.md` inside the same package directory

3. **Fallback for projects without explicit structure**: 
   - If the project has neither `docs/plan/exploratory/` nor a formal plan marker, fall back to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` for backward compatibility
   - Otherwise, default to `docs/plan/exploratory/`

**Decision criteria:**

Ask yourself: "Is this a formal, structural change that will go through code-workflow with task gates and formal review?"
- **Yes** → Use a dedicated package under the project's formal plan location (typically `docs/plan/impl-plan/YYYY-MM-DD-<feature-name>/README.md`)
- **No** → Use `docs/plan/exploratory/`
- **Unsure** → Use `docs/plan/exploratory/` and mention that it can be promoted to formal plan if needed

Always report the actual entry path. For a formal plan, report its package `README.md`; for a parent program, also list its child-plan paths. When using `docs/plan/exploratory/`, briefly note: "This is an exploratory plan. If it evolves into a formal implementation, it should be promoted to its own package under the project's formal plan directory."

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Plan Shape Gate

Before writing detailed tasks, classify the artifact as either a single executable plan or a parent implementation program.

Every formal plan owns one package directory. Use `README.md` as the stable entry point and keep child plans, plan-local references, diagrams, or review inputs inside that directory. Do not encode ownership only through repeated filename prefixes in the shared `impl-plan/` root.

**Read `references/implementation-plan-structure.md` when any of these apply:**

- multiple services, deployable modules, or independently testable subsystems;
- a shared foundation followed by multiple adopters;
- a pilot whose review can change later APIs, constructors, files, or validation strategy;
- unresolved external branches, worktrees, contracts, or baselines;
- multiple independent review or rollback boundaries;
- a plan large enough that one executor would repeatedly reload unrelated context.

Do not write a program-sized migration as one checkbox document. Create a compact parent program that owns target state, dependencies, status, and final convergence, then create executable child plans that own exact files, acceptance, steps, validation, user quality-review checkpoints, and handoff state. Plans must not schedule automatic git commits.

Before finalizing the shape, build the reference's delivery-boundary, artifact-ownership, constraint-activation, and acceptance-ownership maps. Consolidate repeated file/document edits unless an explicit, testable intermediate state requires them. Enable mechanical guards before the first risky adopter, using migration mode plus a shrinking allowlist when strict mode cannot pass immediately.

## Research Before Boundary Questions

Before freezing plan scope or asking the user to choose an implementation direction:

1. Inspect the relevant repository code, config, tests, architecture docs, contracts, and recorded decisions.
2. For unknown framework recommendations, current versions, compatibility, migration mechanics, or external product behavior, consult official primary sources and use Web Search when needed.
3. Convert that evidence into a recommended approach plus viable alternatives and their target-state, risk, rollout, and maintenance impact.
4. Ask only about boundaries that evidence cannot decide, such as product intent, acceptable downtime, risk tolerance, budget, or whether delivery must be staged.

Do not ask the user researchable technical questions or present unexplained choices they may not understand. If a real decision blocks the plan, show the evidence and recommendation first, then ask one concrete boundary question. A plan based on an unresolved material boundary must mark it as pending instead of silently choosing or pretending the plan is executable.

When the user requests research but may not yet have a precise problem definition, produce and validate a research-question brief before writing the implementation plan. Include the core tension, subquestions across relevant ownership layers and runtime scenarios, candidate decision models, intended official sources, and expected research outputs. Do not begin with a premature implementation recommendation whose underlying question the user has not confirmed.

## Testing Workflow Classification

Before writing task steps, classify each implementation slice:

- `TDD`: behavior, state, data flow, validation, permissions, async flow, algorithm, API contract, persistence, or reproducible bug changes.
- `No TDD`: pure presentation work such as spacing, color, typography, static layout, copy-only edits, visual polish, or moving existing controls without changing event/state semantics.
- `Mixed`: split into a TDD logic slice and a direct UI slice when practical.

Do not add fake failing-test steps to simple UI tasks. For `No TDD` slices, require direct implementation plus the smallest sufficient visual/manual/component/type/build verification.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Acceptance Completeness Gate

Before writing slice steps, turn the repository facts into an explicit acceptance checklist. Do not leave requirements as broad phrases such as "validate config", "handle errors", "add runtime wiring", or "follow security rules".

For each slice:

1. Read the project `AGENTS.md` routing and every architecture, contract, runtime, security, configuration, testing, and review document named by the touched surface.
2. Extract concrete MUST / MUST NOT rules from those facts.
3. Expand each rule into observable acceptance bullets that name exact fields, states, errors, limits, commands, or API behavior.
4. Put those bullets in the slice before implementation steps.
5. Write tests or verification commands that cover each acceptance bullet, or explicitly mark why a bullet is verified by a later slice.

If a source document says "HTTP server must configure ReadHeaderTimeout, ReadTimeout, WriteTimeout, IdleTimeout, and shutdown timeout", the plan must list all five fields and their bounds. If a config document says "bool uses true/false, size uses explicit units, secrets are redacted", the plan must list strict bool parsing, unit requirement, non-positive/overflow rejection, and redaction checks. Do not rely on reviewers to rediscover these constraints after implementation starts.

A plan that only cites a broad document without expanding its applicable hard rules into per-slice acceptance criteria is incomplete; revise it before handing it to the user for independent review.

## Target-State Completeness Gate

For migrations, replacements, standardization, “use X everywhere”, or framework adoption, the plan MUST define:

1. The final production initialization and primary call path.
2. The final driver/provider and runtime/resource owner.
3. Legacy imports, constructors, drivers, adapters, wrappers, config, tests, and dependencies that must disappear.
4. Any retained legacy component and why it is a stable final-state boundary rather than a temporary compatibility seam.
5. A search, architecture check, or behavioral verification proving the old default path is gone.

The plan must include both positive acceptance (“the new path exists”) and negative acceptance (“the old default path no longer exists”). Reject plans that add a framework only at repository or call sites while production initialization, driver ownership, transactions, runtime wiring, or primary adapters remain on the legacy path without explicit user approval.

Do not introduce unstated scope-narrowing non-goals such as “driver migration is separate”, “keep the old runtime owner for safety”, or “only replace query calls”. Every excluded adoption layer must come from an explicit user decision, a hard external constraint, or a documented stable boundary.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**

For TDD-required slices:
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Record the verification evidence for user quality review" - step

For pure UI / presentation slices:
- "Inspect the current component and owner styles" - step
- "Apply the focused UI change" - step
- "Run type/build/component render or visual/manual check" - step
- "Record the verification evidence for user quality review" - step

Every executable step must be represented by a checkbox. The executor is required to flip each checkbox from `- [ ]` to `- [x]` immediately after the step's expected result is reached, before continuing to later steps. Plans should make this easy by keeping steps small and objectively verifiable.

## Executable Plan Document Header

**Every executable child plan MUST start with this semantic header, localized to the target project's documentation language. Parent programs use the parent template in `references/implementation-plan-structure.md`:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` according to the user-selected execution method. Steps use checkbox (`- [ ]`) syntax for tracking. Do not schedule git commits or automatic review loops in this plan; record verification evidence for any review the user requests. Commit only when the user later explicitly asks, via `@committing-changes`.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Behavior Or Logic Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Acceptance checklist from source docs:**
- [ ] [Specific observable rule from the relevant architecture/contract/runtime/security docs]
- [ ] [Specific edge case, limit, error, state transition, or redaction requirement]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Record verification evidence for user quality review**

Do **not** `git commit` in this step. Record the changed files, focused verification evidence, and any open risks in the handoff. The user decides whether to perform quality review and whether further work should continue; do not dispatch an agent reviewer.
````

## Simple UI Task Structure

Use this shape only when the task is pure presentation or markup placement and does not change event/state semantics.

```markdown
### Task N: [UI Surface]

**Testing stance:** No TDD - pure UI / presentation-only change.

**Files:**
- Modify: `exact/path/to/component.vue:123-145`

- [ ] **Step 1: Inspect the current component structure and style owner**

- [ ] **Step 2: Apply the focused UI change**

- [ ] **Step 3: Run the smallest sufficient verification**

Run: `pnpm typecheck` or targeted component/render/screenshot/manual check
Expected: PASS / visually confirms the requested layout

- [ ] **Step 4: Record verification evidence for user quality review**

Do **not** `git commit` in this step. Record the changed files and verification evidence in the handoff. The user owns any quality review decision; do not dispatch an agent reviewer.
```

## Remember
- Exact file paths always
- Complete acceptance checklist derived from source docs, not broad references
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD where applicable; no plan-scheduled commits; record evidence for user quality review at each reviewable slice
- Project documentation language always overrides this skill's English examples
- Parent programs track phase status; child plans own executable checkboxes
- Guards activate before the work they constrain, not only during final verification
- Repeated file or document edits have one owner unless an explicit intermediate state requires otherwise

## Plan Review Loop

After writing the complete plan:

1. Run an explicit architecture-fit evaluation on the written plan before any implementation handoff. Check:
   - whether the artifact is correctly classified as a single executable plan or parent program with child plans
   - whether the plan follows the target project's documentation language and does not leak English template labels into prose
   - whether the target architecture boundary is explicit
   - whether shared layers, owners, reuse points, and abstraction landing zones are named
   - whether the plan is only aligning output behavior while quietly deferring structural convergence
   - whether following the plan would predictably cause an immediate second-round redesign after "completion"
   - if structural convergence is intentionally deferred, whether it is captured as its own tracked task with completion criteria
   - whether the plan reaches the user-selected target state instead of preserving legacy initialization, drivers, wrappers, or owners merely to minimize the diff
   - whether positive and negative acceptance checks prove both adoption of the new path and removal of the old default path
   - whether mechanical guards become effective before the first task that can violate them
   - whether the same file, document, config owner, or active plan is modified by separated tasks without a necessary intermediate state
   - whether pilot-dependent late tasks are refreshed after the pilot instead of freezing stale file-level assumptions
   If any answer is unclear, revise the plan first.
2. Record the architecture-fit result, changed plan paths, and open assumptions in the plan handoff.
3. Present that evidence to the user for independent review when the user requests it or the plan declares a user review gate. Do not automatically dispatch an agent reviewer.
4. Apply only the feedback the user provides, then update the same handoff record.

**Review ownership:**
- The user controls whether and how independent review and quality review happen.
- The plan author performs the architecture-fit evaluation and prepares evidence; it does not substitute for review the user explicitly requests.
- Do not create an automatic review loop or treat a separate agent as an approval authority.

## Commit Policy In Plans

- **Never** write plan steps such as `Commit`, `git commit`, or example commit-message commands as required execution checkboxes.
- Commit is outside the plan's default delivery loop. It is authorized only by the user's explicit request at execution time, and then only through `@committing-changes` plus the target repository commit policy.
- Plans may still mention existing base commits, dependency commit evidence, or optional handoff fields for *already-made* commits. That is baseline tracking, not an instruction to create new commits.
- At each independently reviewable slice (task or child plan exit), record the diff scope and verification evidence for the user's quality review. A plan may name a user quality-review gate when the user requires it, but must not create an automatic agent review loop or treat a user review as agent-owned work.

## Execution Handoff

After saving the plan, offer the execution choice without scheduling an automatic review loop:

**"Plan complete and saved to `<actual-plan-path>`. Two execution options:

**1. Subagent-Driven** - Dispatch a fresh subagent per task and record verification evidence after each task; run review only when I explicitly request it

**2. Inline Execution** - Execute tasks in this session using `executing-plans`, with proportionate evidence checkpoints

**Which approach?**

The plan will not auto-commit or auto-review; commits and reviews happen only when I explicitly request them."**

If Subagent-Driven is chosen, use `superpowers:subagent-driven-development`. If Inline Execution is chosen, use `superpowers:executing-plans`.
