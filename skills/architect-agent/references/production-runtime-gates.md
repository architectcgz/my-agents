# Production Runtime And Delivery Gates

Read this reference when architecture analysis or an implementation plan touches service startup, external dependencies, health checks, shutdown, workers, queues, consumers, outbox delivery, observability, or deployment topology.

## Core Rule

Treat runtime safety and event delivery as architecture, not wiring detail. Trace each owner, state transition, failure path, recovery path, and proof point before approving implementation.

## Required Gate Matrix

| Gate | Inspect | Required architecture or plan evidence |
| --- | --- | --- |
| Secret-safe startup | Config parsing, dependency factories, wrapped driver/SDK errors, final fatal logging | Structural DSN/URL validation; generic safe outward errors at config and dependency-open boundaries; sentinel tests proving logs and returned errors exclude DSN, URL, username, password, userinfo, and sensitive host values |
| Database production policy | Pool creation, initial ping, repository contexts, transactions, readiness queries | Named and bounded max-open/max-idle/lifetime/idle-time settings; startup timeout; query/transaction timeout; child deadlines never extend a shorter parent; row iteration and transaction lifetime retain valid contexts |
| Dependency lifecycle | Startup dial, runtime connection/channel/client ownership, close notifications, reconnect/exit policy | One durable owner; explicit startup fail-fast versus runtime recovery semantics; bounded backoff and jitter; cancellation and shutdown behavior; atomic replacement or a tested process-exit strategy; no worker retaining a permanently closed client |
| Health semantics | Liveness, readiness, degraded details, backlog/capacity gates | Liveness means process health; readiness reflects whether traffic remains safe; optional dependencies do not automatically remove unrelated HTTP capacity; persistent backlog or unsafe capacity has explicit thresholds and backpressure behavior |
| Worker failure visibility | Loop/Supervisor owner, observer wiring, early exits, panic/error handling | Critical workers are supervised; abnormal exit reaches the process owner; transient errors do not silently kill the loop; observer is not nil on critical production paths; observation cannot alter control flow |
| Producer-owned outbox | Transaction writer, dispatcher, repository claim/fencing, broker publisher | Producer writes and dispatches its own private outbox; downstream services never connect to or claim the producer database; connection owner and dispatcher responsibilities remain separate |
| Failure taxonomy | Publish errors, dependency outage, poison payload, confirm timeout, mark failure | Dependency/topology failure is distinct from message-level permanent failure; broker outage does not consume poison-message attempts or mass-move valid events to DEAD; stored errors and labels use stable sanitized classifications |
| Backlog recovery | Eligible states, stale claims, ordering, concurrency, rate, replay controls | Define which PENDING/FAILED/CLAIMING rows recover; PUBLISHED is not automatically replayed; DEAD requires explicit replay; drain is bounded and cancelable; new messages do not silently bypass required ordering; oldest age and drain rate are observable |
| Delivery guarantee | Publisher confirm, uncertain outcomes, event identity, consumer idempotency | State at-least-once or other guarantee explicitly; confirm loss or mark failure may duplicate; retries preserve event ID; consumers own idempotency and tolerate declared ordering/late-arrival semantics |
| Broker topology | Exchange, consumer-owned queue, binding pattern, DLQ/retry, routing validation | Queue and binding have an actual consumer owner; one queue is not shared as broadcast state across unrelated consumers; routing wildcard matches real key segment depth; versioned deployment assets and tests prove the topology |
| Routed versus accepted | Publish flags, returned messages, confirms, alternate exchange | Publisher confirm alone does not prove routing. Required-delivery events use mandatory/return handling or an equivalent proven topology guarantee; zero-route publish cannot be marked delivered |
| Prometheus-ready observability | Counter/gauge/histogram ports, no-op behavior, labels, dependency state owner | Runtime depends on neutral narrow recorders, not a vendor SDK; no-op is safe; recorder panic/blocking is isolated; labels are low-cardinality and secret-safe; future exporter and alerting do not require business-control-flow changes |
| Lifecycle completion | Signal, parent cancellation, HTTP Serve failure, worker Start/Wait failure, cleanup errors | All terminal branches enter one bounded shutdown path; readiness drops before teardown; workers stop before their dependencies close; listener and goroutines are reclaimed; multiple cleanup failures remain visible |
| Real dependency proof | Migration, actual database/broker, HTTP, timeout, disconnect/recovery, unroutable publish | Unit tests are insufficient for production wiring. Require environment-gated smoke using disposable dependencies, with no production endpoints, and prove normal flow plus the highest-risk failure/recovery paths |
| Delivery surface completeness | Gateway/proxy route, deployment config, migrations, queue definitions, docs | A service is not production-complete if required ingress routes, migrations, topology, configuration, ownership docs, or system tests are absent, even when the service binary itself starts |

## Outbox And Broker Ownership

Use this default ownership model unless the project explicitly documents another proven architecture:

```text
producer transaction -> producer outbox
producer dispatcher -> broker exchange
consumer-owned queue -> downstream consumer
```

Do not recommend a downstream business service reading or claiming an upstream service's outbox. A CDC connector may replace an in-process dispatcher, but it remains producer-side infrastructure and still publishes through the broker contract.

Keep these owners separate:

- Connection owner: connection/channel/client generations, close notifications, reconnect, shutdown.
- Dispatcher: claim/fencing, publish attempt, status transition, backlog recovery.
- Consumer: queue, ack/retry/DLQ, idempotency, downstream side effects.
- Deployment/Ops: versioned broker topology, scrape configuration, alert routing.

## Plan Acceptance Rules

When producing or reviewing an implementation plan, expand every applicable gate into observable acceptance criteria:

- exact configuration fields, defaults, bounds, and secret-redaction behavior;
- exact state transitions and owners;
- exact stable error classes and retry-budget effects;
- exact health behavior during transient and prolonged dependency failure;
- exact unit, race, integration, migration, and real-dependency smoke scenarios;
- exact deployment/topology/doc files that complete the delivery surface;
- rollback behavior that does not recreate the original unsafe state.

Reject broad placeholders such as "add reconnect", "add metrics", "handle errors", or "test RabbitMQ". Name the failure event, owner, state transition, limit, observable output, and proof command.

## Severity Guidance

Treat these as blockers unless project facts prove otherwise:

- credentials or connection strings can reach logs or outward startup errors;
- event delivery can be acknowledged with no consumer route when delivery is required;
- ownership requires one service to read another service's private database;
- runtime can remain live forever while a critical worker holds a permanently closed dependency and no recovery/exit path exists.

Treat these as major findings:

- missing database pool limits or service-owned deadlines;
- infrastructure outages consume poison-message retry budgets;
- critical worker errors have no logs/metrics/observer;
- lifecycle branches or real dependency smoke are absent;
- ingress, migration, broker topology, or deployment assets are required but omitted from the plan.

Do not downgrade a touched-surface blocker or major finding into future debt solely to keep the current slice small. Split the plan before implementation if the safe closure genuinely requires a separate independently deliverable slice.
