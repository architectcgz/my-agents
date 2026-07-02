# Design Pattern Selection

Use this reference when code grows repeated branching around one discriminator: type, status, mode, provider, event, command, lifecycle state, permission shape, or rule category.

Core rule: do not default to "multi-if means strategy." Choose the smallest pattern that matches the reason branches vary.

## Pattern Selector

| Branch reason | Candidate pattern |
| --- | --- |
| Replaceable behavior behind one contract | Strategy / policy object |
| Legal lifecycle transitions matter | State machine / transition table |
| Commands, jobs, events, or actions route to handlers | Command pattern / handler registry |
| External systems differ behind one internal contract | Adapter |
| Object creation varies by type and wiring is non-trivial | Factory / provider function |
| Many named predicates compose into a decision | Specification / rule object |
| Branches are simple data mapping | Lookup table / table-driven dispatch |
| Branches are validation, guard clauses, or local errors | Inline branches |

## Decision Rules

- Before adding the third branch for one discriminator, pick from the selector.
- Keep the pattern at the owner of the behavior, not in an unrelated helper.
- Prefer the language's natural shape: functions and maps may be enough in Go or TypeScript; classes may be appropriate only when the codebase already uses them.
- Do not introduce a pattern when the branch is a short guard clause, validation failure, or simple data lookup.
- If repeated branching stays inline, add a short comment explaining why extraction would be heavier than the branch.

## Examples

```text
Strategy: paymentMethod -> PaymentProcessor.Process(...)
State machine: Draft -> Published -> Archived
Handler registry: event.type -> handler.handle(event)
Adapter: ProviderAClient -> InternalImagePort
Factory: report.kind -> buildReportGenerator(...)
Specification: canPublish = hasOwner AND hasValidImage AND categoryVisible
Lookup table: status -> label/color/icon
Inline: if missing required field, return validation error
```
