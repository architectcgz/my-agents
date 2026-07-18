# Aggregation And Responsibility Inspection

Read this reference for complex aggregation, broad queries, dashboard/overview loaders, report builders, or repositories/services combining several use-case responsibilities.

## Candidate Signals

- One method queries multiple business domains.
- Optional filters come from unrelated features.
- SQL or ORM joins mix unrelated aggregates.
- A service returns several independently owned UI sections.
- A small feature requires editing a broad query or result object.
- Names are generic: `getDashboardData`, `getOverview`, `getSummary`, `getStats`, `getReport`, `queryAll`, `searchEverything`.
- A repository or service mixes commands, member management, read models, user lookup, uniqueness/existence checks, and policy checks.

## Confirmation Steps

1. Read the interface, implementation, callers, tests, queries, and result consumers.
2. Identify the coupled subdomains or use-case responsibilities.
3. Map each responsibility to its tables, models, services, routes, jobs, UI consumers, command flows, or query flows.
4. Check transaction, consistency, permission, ordering, pagination, cache, and performance assumptions.
5. Explain why the aggregation is risky or acceptable.
6. Propose smaller use-case-oriented ports or queries with explicit result ownership.
7. Preserve external behavior unless API change is requested; prefer incremental extraction over broad rewrites.

Prefer splitting when subparts differ in lifecycle, command/query direction, permission model, cache strategy, pagination, ordering, consistency needs, consumer, transaction boundary, or release cadence. Do not split mechanically by table when use-case ownership cuts across tables.
