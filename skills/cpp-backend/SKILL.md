---
name: cpp-backend
description: >
  Use when implementing, refactoring, or reviewing C++ code (especially modern C++17/20
  libraries, SDKs, providers, Options vs Config design, factories, RAII ownership,
  module boundaries, CMake target source ownership, example/integrator surfaces, and
  public vs product-owned defaults). Activate for phrases like "C++ 风格", "类内默认",
  "Options 怎么设计", "Config 怎么设计", "provider 配置", "不要透传默认值",
  "integrators 只传 endpoint", header/source layout, or C++ SDK-shaped changes.
---

# C++ Backend

This skill extends `backend-engineer` for C++ library/SDK work: **configuration ownership**,
construction, comments, and module boundaries. Prefer the **current repository's patterns**
when they conflict; this skill decides *who owns defaults* and *what is external*, not a new
framework style.

Read and apply `backend-engineer` first when the change is service-shaped. Use this file for
C++-specific Config/Options, ownership, and module rules.

Does **not** replace project `AGENTS.md` / architecture guards.

## Options vs Config

| Term | Meaning | Audience | Typical home |
|------|---------|----------|--------------|
| **Config** | External configuration: endpoint identity and other integrator-supplied settings | Integrators / process root / public JSON / C API | Factory input, documented contract |
| **Options** | Internal configuration: product-owned policy and knobs that shape behavior | Library / product code | Owning type: in-class or dedicated Options members with defaults |

- **Config** is what outsiders *must* provide (or may provide as part of the public contract).
- **Options** is what the implementation *owns* and defaults; it is **not** a second public
  surface unless the product explicitly documents override.
- Do not name or place a bag of product defaults as Config, and do not ferry Options through
  composition roots only to re-inject them into the owner.

## Product Defaults vs External Contract

- Split **identity from Config** (endpoints, credentials, model names, deployment hosts)
  from **policy in Options** (TTL, allowlists, sizes, routing thresholds, derived paths).
- Product policy defaults live as **member initializers** on the type that applies them
  (class members or an Options value owned by that type). Prefer defaults on the owner over
  a pass-through Options field on a parent.
- External Config (JSON / C API / flags) should only carry fields integrators must set.
  Do not require product Options through Config.
- Factory / loader: **start from Options/struct defaults** → overlay **Config** identity →
  **derive** related internal fields from identity + rules → validate.
- If a value is not part of the public Config contract, do not put it on examples, SDK
  context, or parent option bags solely for wiring.
- ✓Check: can an integrator set this via the documented external Config? If no, it is Options
  (or private), not Config, and must not appear as a required external field.

Read `references/product-defaults-and-external-contracts.md` when touching Config loaders,
Options placement, factories, examples, or “who owns this default”.

## Ownership and Construction

- Inject **collaborators** (services, loggers, interfaces), not pass-through Options that only
  carry product defaults the callee already owns.
- Prefer `std::unique_ptr` for exclusive ownership; `std::shared_ptr` for shared long-lived
  collaborators. Avoid owning raw pointers.
- Mark concrete types `final` when inheritance is not designed; use abstract interfaces only
  at replaceable boundaries.
- Factories map **Config → concrete type**, applying Options defaults and derivation inside.
- Keep headers thin; implementation helpers in `.cpp` anonymous namespaces unless shared.
- Module owns its sources: declare files in the submodule `CMakeLists.txt`; do not backfill
  submodule sources into a parent target list.
- ✓Check: constructor parameters are dependencies or true caller-variable knobs—not fixed
  product Options the type should default itself.

Read `references/ownership-and-construction.md` when reshaping constructors, Options
placement, factories, or CMake module boundaries.

## Comments and Example Surfaces

- Comments explain **invariants, ownership (Config vs Options), and non-obvious trade-offs**,
  not the next line of syntax.
- Examples and smoke tests pass **Config only**. Do not add marketing comments that restate
  “integrators only supply …”; the Config shape should make that obvious.
- Short ownership notes are fine on Options members that look configurable but are internal.
- Match repository comment language and density.
- ✓Check: deleting the comment would not cause a maintainer to promote Options into Config
  or reintroduce a pass-through Options field.

## Errors, Logging, and Cancellation

- Validate **Config** early in factories; name missing identity or failed derivation.
- Log construction and routing that depend on Options when auditability matters; avoid hot-path noise.
- Propagate cancel/stop into long I/O; prefer RAII for handles and buffers.

## Naming and API Shape

- **Config**-facing keys: stable, integrator-oriented, documented.
- **Options** / internal fields: ownership-clear names; defaults on the type.
- Avoid dual APIs (`Foo` / `FooWithOptions`) when Options must not be overridden from outside.
- Prefer value Options with member defaults for small policy; prefer smart pointers for heavy
  shared collaborators.
- Keep public headers free of implementation includes that force rebuild cascades.

## Verification

- Build/test the narrowest targets that include the touched headers.
- Do not claim green without a build when headers cross multiple TUs.
- Pure Options/Config ownership refactors: dependents compiling is the minimum bar.

## References

| Task involves | Read |
|---|---|
| Config vs Options, public surface, derivation, examples | `references/product-defaults-and-external-contracts.md` |
| Constructors, Options on owner, factories, ownership, CMake | `references/ownership-and-construction.md` |

## Source Basis

Distilled from library/SDK configuration-ownership refactors and modern C++ practice (RAII,
clear ownership, thin external contracts). Prefer repository facts when they differ.
