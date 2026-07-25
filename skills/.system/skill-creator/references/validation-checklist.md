# Skill Validation Checklist

Read this file when finishing a new or updated skill, before declaring the skill ready.
This checklist was migrated from the disabled `writing-skills` skill: structural and
quality gates only. It does **not** reintroduce mandatory TDD-for-docs as a hard law.

Mechanical frontmatter checks live in `scripts/quick_validate.py`. This file covers the
judgment checks that the script cannot automate.

For project-level skill routing structure, also use `authoring-project-skills`.
For repo-wide smoke-test / trigger-rate harness checks, use `harness-engineering`.

## When validation is required

Run this checklist after:

- creating a new skill
- editing an existing skill's `SKILL.md`, frontmatter, scripts, or references
- renaming a skill or changing its folder layout

Do not move on to another skill, or claim the skill is ready, until Step 5 in `SKILL.md`
has completed for the current skill.

## 1. Mechanical checks (script)

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Must pass:

- `SKILL.md` exists with valid YAML frontmatter
- required fields: `name`, `description`
- only allowed frontmatter keys
- `name` is hyphen-case (`[a-z0-9-]+`), no leading/trailing/consecutive hyphens, ≤64 chars
- `description` is a string, no angle brackets, ≤1024 chars

Fix every reported issue and re-run until the script exits 0.

## 2. Frontmatter and discovery (CSO)

### Name

- [ ] Folder name equals skill `name`
- [ ] Name uses only lowercase letters, digits, hyphens
- [ ] Prefer verb-led / action-oriented names when possible
  - good: `condition-based-waiting`, `requesting-code-review`
  - weak: `helpers`, `utils`, `misc`

### Description = when to use, not how it works

`description` is the primary trigger. Future agents decide whether to load the skill from
this field alone.

- [ ] Written in third person
- [ ] Starts with or clearly centers on "Use when..." trigger conditions
- [ ] Includes concrete symptoms, situations, user phrasings, or contexts
- [ ] Covers multiple realistic ways a user might ask for the same help
- [ ] Does **not** summarize the skill's process, workflow, or step sequence
- [ ] Prefer ≤500 characters when possible; hard max 1024

```yaml
# ❌ BAD: workflow summary becomes a shortcut; agent may skip the body
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD: process detail instead of triggers
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ❌ BAD: too abstract / first person
description: For async testing
description: I can help you with async tests when they're flaky

# ✅ GOOD: triggers and symptoms only
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
description: Use when executing implementation plans with independent tasks in the current session
```

**Why no workflow in description:** if description narrates the process, agents often
follow the description and skip the skill body. Keep process instructions in the body.

### Keyword coverage

- [ ] Error messages / symptoms a future agent would search for
- [ ] Synonyms users actually say
- [ ] Tool, file type, or domain names when the skill is domain-specific

## 3. Structure and progressive disclosure

- [ ] `SKILL.md` stays a lean entry: overview, workflow, routing; prefer under 500 lines
- [ ] Heavy reference, long examples, selector tables live under `references/` or sibling files
- [ ] Scripts that are repeatedly rewritten live under `scripts/` and are actually runnable
- [ ] Assets used in outputs live under `assets/`
- [ ] No auxiliary clutter files (`README.md`, `CHANGELOG.md`, installation guides, etc.)
  unless the skill's purpose is specifically to produce that kind of user-facing doc
- [ ] References are one level deep from `SKILL.md` and linked with when-to-read guidance
- [ ] Broad judgment topics use thin `SKILL.md` routing plus detailed `references/`
- [ ] Supporting files exist only for tools, heavy reference, decision guides, or examples

## 4. Content quality

- [ ] Overview states the core principle in 1–2 sentences
- [ ] Instructions use imperative/infinitive form
- [ ] One excellent example beats many mediocre or multi-language clones
- [ ] Examples are complete enough to adapt, not fill-in-the-blank shells
- [ ] No narrative storytelling about a single past session as the rule
- [ ] Common mistakes / gotchas called out when agents repeatedly fail there
- [ ] Degrees of freedom match fragility: free text for judgment, scripts for fragile ops
- [ ] Each paragraph earns its tokens: default assumption is the model is already capable

## 5. Boundary and ownership

- [ ] This skill does one job; out-of-scope work routes to another skill
- [ ] Shared global skill body lives under `~/.agents/skills/` when cross-agent
- [ ] Project-only routing/structure concerns use `authoring-project-skills`
- [ ] Repo harness / smoke-test / trigger-rate gates use `harness-engineering`
- [ ] Before inventing helper scripts, check `~/.agents/skills/` and `~/.agents/scripts/`
  for an existing owner

## 6. Risk-based verification

Not every skill needs a full pressure campaign. Choose depth by risk:

| Skill type | Minimum verification |
|---|---|
| Pure reference / thin router | Script + checklist sections 1–5 |
| Technique / workflow | Script + checklist + walk one realistic prompt through the skill |
| Discipline / high-compliance cost | Above + forward-test with fresh subagent under pressure |
| Complex multi-resource skill | Above + run bundled scripts for real |

Forward-testing rules (from main `SKILL.md`):

- treat the subagent as a normal task agent, not a skill reviewer
- pass raw artifacts, not your intended answer or diagnosis
- prefer fresh threads; clean leftover artifacts between iterations
- if success depends on leaked context, the skill or the test setup is still wrong

Do **not** claim "validated" without running the script and completing the applicable
checklist rows. Do not invent pass results.

## 7. Completion gate

Before saying the skill is ready:

1. [ ] `quick_validate.py` exits 0
2. [ ] Sections 2–5 checked for this change
3. [ ] Section 6 verification done at the depth the change warrants
4. [ ] `agents/openai.yaml` still matches `SKILL.md` when that file exists; regenerate if stale
5. [ ] Only this skill is being finished; do not batch-create untested siblings

If any item fails, fix and re-validate. Partial checklist completion is not done.
