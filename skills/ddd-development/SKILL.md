---
name: ddd-development
description: Use when implementing or reviewing backend DDD boundaries, domain/application layering, aggregate rules, domain events, integration events, ports, repositories, outbox mapping, or when code feels service-centered instead of domain-centered.
---

# DDD Development

## Overview

Use this skill to keep DDD practical: domain expresses business language and invariants; application owns use-case orchestration, transactions, ports, and outward side effects. Pair it with `onion-clean-architecture` and language-specific backend skills when editing code.

## Core Rule

Do not make the domain layer speak infrastructure or integration contracts.

```text
api/http -> application -> domain
          -> ports
infrastructure -> ports/domain mapping
```

## Boundary Checklist

Before editing, classify each concept:

| Concept | Default owner |
| --- | --- |
| Business invariant, state transition, value object | `domain` |
| Domain event as a business fact | `domain` |
| Use case, permission, transaction, side-effect order | `application` |
| Domain event -> integration event / outbox mapping | `application` |
| Repository/cache/MQ/client interface consumed by a use case | `ports` |
| SQL, ORM, Redis, HTTP clients, MQ publisher implementation | `infrastructure` |
| HTTP request/response DTO and status/error envelope | `api/http` |

## Event Rule

Distinguish three event shapes:

1. **Domain event**: a fact in ubiquitous language, such as `UserFollowed{FollowerID, FollowingID}`.
2. **Integration event contract**: externally consumed name and payload, such as `user.followed`.
3. **Outbox row**: durability mechanism with event type, aggregate id, payload, retry status, and publish metadata.

Domain may produce 1. Application maps 1 -> 2 and writes 3 through a port.

## Review Flow

1. Read module docs and existing code before judging folders.
2. Name the aggregate/value objects and invariants.
3. Name the use cases that orchestrate persistence, transactions, and side effects.
4. Check exported domain types: can they compile without HTTP, SQL, Redis, MQ, JSON payload contracts, or SDKs?
5. Check ports: are interfaces consumer-side and use-case-shaped?
6. Test at the owner layer: domain rules in domain tests; event/outbox mapping in application tests; request contract in handler tests.

## Practical Pattern

Use domain to plan and validate pure business intent:

```text
PlanBlock(actor, target, reason)
-> validates self-block and ACTIVE status
-> returns BlockPlan{BlockerID, BlockedID, RemovedFollows}
```

Use application to persist the plan:

```text
transaction:
  insert block
  delete affected follows
  update stats
  publish mapped outbox events
```

Keep integration strings and JSON fields out of domain even when the domain event name is similar. See the case reference for code.

## Red Flags

- Domain imports `time` only to build outward payload timestamps.
- Domain has strings like `user.followed`, routing keys, exchange names, JSON field maps, outbox statuses, SQL column names, HTTP codes, or DTO tags.
- Application service contains business branches with no domain vocabulary, only repository calls.
- A repository port is named after the database table instead of the use-case capability.
- Tests assert external payload shape only in domain tests.
- "Minimal diff" keeps service-centered code because moving the rule to domain touches one more file.

## Case Notes

For the User relationship event boundary case that motivated this skill, read `references/cases.md`.

## Common Mistakes

- Treating "domain event" as synonymous with "message broker event".
- Moving every helper into domain because it is "business related"; orchestration and side effects still belong to application.
- Creating entity methods that call repositories, clocks, clients, or publishers.
- Hiding application decisions inside repository methods to make services look thin.
- Splitting every port into one-method interfaces without a use-case boundary.
