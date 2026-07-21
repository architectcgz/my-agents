# Product Defaults and External Contracts

Use when designing or reviewing **Config** (external) vs **Options** (internal), loaders,
factories, examples, or any value that might leak into an integrator-facing surface.

## Terms

| Term | Definition |
|------|------------|
| **Config** | External configuration. Integrator- or process-supplied. Documented public contract (JSON, C API, flags, env at the root). |
| **Options** | Internal configuration. Product-owned policy on the type that implements the behavior, with in-class / in-struct defaults. |

Config answers: *where do we connect, with what credentials?*  
Options answers: *how does the product behave once connected?*

## Core Split

| Kind | Owner | Lives as | In external Config? |
|------|-------|----------|---------------------|
| Endpoint / deployment identity | Integrator | Config fields overlaid in factory | Yes |
| Product policy defaults (TTL, allowlists, sizes, routing) | Product | Options on the owning type (member initializers) | No (unless product documents override) |
| Derived internal fields | Product | Computed in factory from Config identity + rules | No — do not re-ask |

## Rules

1. **Options sit on the type that uses them.**  
   Policy for a component defaults on that component (or its dedicated Options value), not on
   a parent that only forwards the bag downward.

2. **Config stays thin.**  
   Integrators supply identity and deployment facts. Product policy is Options, not extra
   required Config keys.

3. **Factory / loader sequence.**  
   - Materialize Options defaults (member initializers / defaulted Options).  
   - Overlay **Config** identity fields only.  
   - **Derive** internal fields that follow from identity (related paths, sibling endpoints).  
   - Validate required Config and successful derivation; fail at the boundary with clear errors.

4. **No pass-through Options on parents.**  
   If a composition root or SDK context only stores Options to inject into a child that already
   owns those defaults, delete the field. The child owns Options; the root holds Config-built
   collaborators.

5. **Examples show Config only.**  
   Sample apps and smoke tests pass external Config shape. They do not dump product Options
   and do not add comments that lecture integrators about what they “only need to supply”.

## Abstract Anti-Patterns

**Anti-pattern A — product policy forced into Config**

- External document requires keys that only encode product policy (refresh intervals, format
  allowlists, internal path templates).
- Integrators must copy product constants to “configure” the library.

**Anti-pattern B — Options ferry**

- Parent aggregate holds `ChildOptions options` solely to pass into `Child`.
- Callers never set meaningful values; defaults always apply.
- SDK context mirrors the same Options for wiring convenience.

**Anti-pattern C — teaching via example comments**

- Example Config is already identity-only, but a comment restates the design rule.
- Prefer silent correct shape over redundant prose.

## Abstract Preferred Shape

- **Config**: only identity / credentials / deployment selectors.  
- **Owning type**: applies behavior; holds Options as member defaults (or a nested Options
  value default-constructed on the owner).  
- **Factory**: `CreateService(Config) → unique_ptr<Interface>`; inside: defaults → overlay
  Config → derive → validate → construct.  
- **Composition root**: stores shared collaborators built from Config; does not store
  product Options for children that own them.  
- **Examples**: Config objects or JSON with identity fields only.

## Override Policy

- Default: product Options are **not** part of Config and not overridable by integrators.
- Add override only when product requirements explicitly need it; then document it as Config
  (or a separate advanced surface), do not silently reopen every Options field.

## ✓Check

- [ ] Every external key is something an integrator must know for *their* deployment (Config).
- [ ] Every product policy default is Options on the owner, not required Config.
- [ ] Derived fields are not required inputs in examples or public Config docs.
- [ ] No parent field exists only to forward defaulted Options one layer down.
- [ ] Examples do not restate ownership rules that the Config shape already demonstrates.
