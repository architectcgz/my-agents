# Harness Adaptation Notes

The reference project `deusyu/harness-engineering` remains an important upstream reference. It demonstrates these reusable patterns:

- repo-as-source-of-truth: knowledge lives in versioned files
- progressive navigation: root `AGENTS.md` points to smaller directory `AGENTS.md` files
- feedback capture: practical failures become durable records
- mechanical enforcement: scripts and hooks check claims that otherwise drift
- agent readability: directory shape and file names make next actions obvious

The current local default is an evolving harness shape. Use the upstream strict reference shape when the user explicitly asks to follow `deusyu/harness-engineering` structurally.

Current default mapping:

- root `AGENTS.md` -> repository entry map and project-specific overrides
- `.harness/` -> current-task scratch/state only
- `harness/policies/` -> project-local rules that can feed mechanical checks
- `harness/templates/` -> reusable project decision templates
- `harness/prompts/` -> validated project prompt assets
- `harness/checks/` -> deterministic guard scripts
- `.harness/reuse-index/` -> user-local durable reuse index, ignored by Git and mirrored from source paths with `README.md` secondary indexes
- `feedback/` -> workflow mistakes, corrections, and reusable lessons
- `scripts/check-consistency.sh` -> consistency guard for the chosen harness shape

Upstream strict reference mapping:

- concepts -> a project-local constraints index plus links to architecture and AGENTS rules
- thinking -> design/review rationale already present in architecture, plan, and review docs
- practice -> implementation plans and focused experiments
- actionable feedback and improvement items -> `docs/todo/`; review findings and incident notes remain in their owning records
- prompts -> project-local prompts or skills only when they are actually reused
- references -> links in the owning contract, architecture, plan, review, or todo document; do not create a standalone external-reference tree
- scripts/check-consistency.sh -> a project-tailored consistency script
