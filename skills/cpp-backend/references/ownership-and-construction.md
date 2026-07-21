# Ownership and Construction

Use when reshaping constructors, placing **Options** on owners, writing factories from
**Config**, choosing smart pointers, or declaring CMake module sources.

## Options vs Config (construction view)

- **Config** enters at the process / SDK / factory boundary.  
- **Options** are owned by the type that implements the policy; defaulted on that type.  
- Constructors take **collaborators** (and only rarely true caller overrides). They do not
  take Options solely to re-apply product defaults the type already has.

## Construction Rules

1. **Inject collaborators, not default ferries.**  
   Pass services, loggers, and interfaces the callee cannot invent. Do not pass an Options
   value that is always the product default and never set by the parent.

2. **Member defaults for fixed Options policy.**  
   In-class initializers for allowlists, intervals, sizes, thresholds. Constructor body moves
   dependencies and may log auditable construction state.

3. **Exclusive vs shared ownership.**  
   - `std::unique_ptr<T>`: sole owner (subcomponents of a root).  
   - `std::shared_ptr` / `shared_ptr<const T>`: shared long-lived collaborators.  
   - Prefer `make_unique` / `make_shared`. No owning raw pointers.

4. **`final` and interfaces.**  
   Non-extension points: concrete `final` types.  
   Replaceable backends: abstract interface + factory returning `unique_ptr` to the interface.

5. **Factories own Config parsing.**  
   `CreateX(Config, …)` (or Config JSON) performs overlay, derivation, validation. Callers of
   higher layers receive ready collaborators, not raw product Options to re-parse.

6. **Headers stay thin.**  
   Normalize/derive/RAII helpers stay in the `.cpp` anonymous namespace unless multiple TUs
   share a clear owner header.

## When a Separate Options Type Is Justified

Keep a dedicated Options struct/class only if at least one holds:

- Multiple fields of internal policy that are still co-owned by one type.
- Shared Options shape across a few internal constructors (still **not** public Config).
- Tests or internal tools legitimately vary Options *inside* the product (not integrators).

If Options are a single fixed list/scalar and never injected, prefer **direct member
initializers** on the owning class and omit a separate Options type.

**Config** remains the external contract type (or JSON schema) regardless of whether Options
is a struct or in-class members.

## When Not to Keep Options on the Parent

Drop a field on a parent/root/SDK context when:

- It is only assigned from defaults and assigned into a child constructor.
- No public API sets it.
- The child can default the same Options itself.

## CMake / Module Ownership

- Each submodule lists its own sources and attaches them to the library target.
- Parent targets list only their own root sources; do not re-list submodule translation units.
- Moving a type moves header, source, and CMake ownership together.

## Abstract Anti-Patterns

**Anti-pattern — Options as constructor noise**

- `Child(ChildOptions options, Collaborator c)` where every caller passes `ChildOptions{}`
  or a parent-stored default identical to `Child`’s own defaults.

**Preferred**

- `Child(Collaborator c)`; Options policy defaulted on `Child`.

**Anti-pattern — Config and Options conflated**

- One “settings” struct mixes deployment identity and product TTL/allowlists, then is both
  documented as external and used as internal member defaults.

**Preferred**

- Config at the boundary; Options on the owner; factory maps Config → object with Options
  defaults applied.

## Cancellation and Long I/O

- Long remote/local work accepts cancel predicates or stop flags.
- Map cancel to a clear stopped/error path; RAII still releases resources.

## ✓Check

- [ ] Constructor parameters are collaborators or genuine overrides, not default-only Options.
- [ ] Product-fixed policy is Options (member defaults) on the owner.
- [ ] Config is only parsed/validated at the factory or process root.
- [ ] New sources live in the correct submodule CMakeLists.
- [ ] No parent field exists only to copy Options one layer down.
