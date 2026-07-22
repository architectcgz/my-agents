# Structured Logging with `log/slog`

Use standard library `log/slog` for new Go backend code. Business code calls `Logger.Info` / `Log` / `*Context` methods; process startup assembles a `Handler` chain for format, correlation, and redaction. Do not invent a parallel logging API.

## Scope

| This reference owns | This reference does not own |
| --- | --- |
| `slog` Logger vs Handler split, construction order, field placement | Metrics / full OpenTelemetry SDK setup → project observability docs |
| Context correlation (`requestId` / `traceId`), redaction boundaries | Business audit logs as durable domain facts → service schema / use cases |
| Levels, message style, injection vs `slog.Default()` | Project-specific field name tables → project `observability` architecture |

If the current project defines observability contracts (field names, redaction allowlists, GORM logger wiring), follow the project docs and treat this file as the language-level baseline.

## Core Rules

- Prefer `log/slog` over introducing new Zap/Zerolog/Logrus dependencies unless the repository already owns another stack.
- All environments use JSON handler (`slog.NewJSONHandler`). Do not ship a parallel text log format for local/dev; field semantics stay one contract.
- Message is a short, stable event name (for example `outbox.published`), not a free-form sentence that embeds IDs or durations.
- Put queryable facts in attributes (`eventId`, `durationMs`, `errorCode`), not in `fmt.Sprintf` messages.
- Static process fields (`service`, `env`, `version`) bind once with `logger.With(...)` at construction.
- Request / task correlation fields live in `context.Context` and are attached by a thin context `Handler`, or by an explicit child logger created at the boundary. Prefer one approach per process and keep it consistent.
- Use `context.Value` only for infrastructure metadata (trace/request IDs, principal claims). Do not pass business command fields through context for logging convenience.
- Define context keys and accessors in one infrastructure-owned package; validate correlation ID format before storing.
- Never log secrets: tokens, passwords, DSN userinfo, private keys, full request bodies, signed URLs with credentials.
- Library / driver log paths that may emit secrets (SQL drivers, ORMs, HTTP clients) must be wrapped with a dedicated redaction `Handler` at the **library entry**, not necessarily on the whole process logger.
- Do not hang a library-specific redaction key blacklist on the project-wide logger when that blacklist would wipe legitimate business fields (for example substring match on `error` breaking `errorCode`, or `content` breaking `contentId`).
- Prefer explicit logger injection. Production paths must not fall back to `slog.Default()` unless the project explicitly allows it for a narrow helper.
- Libraries accept `*slog.Logger` or `slog.Handler`; they do not open their own stderr sinks in production.
- Logging must not change business control flow. Observers and loggers record outcomes; they do not own retries, fallbacks, or success/failure decisions.
- Keep field names stable across services. Prefer project conventions (`requestId`, `traceId`, `durationMs`, `operation`, `errorCode`) over inventing synonyms.

## Construction Chain

Assemble handlers at the process root (typically `cmd/server`). Runtime code only calls `logger.Log` / `Info` / `Error`.

Recommended shape:

```text
outputHandler = slog.NewJSONHandler(writer, options)  // JSON in all environments
rawHandler    = NewContextLogHandler(outputHandler)   // whitelist requestId/traceId from ctx
projectLogger = slog.New(rawHandler).With("service", name, "env", env)

// Optional: library-only outer redaction
gormHandler   = NewRedactingHandler(projectLogger.Handler())
// pass gormHandler only into the ORM/DB open path
```

Rules for order:

1. Output handler is innermost (format + destination).
2. Context enrichment wraps output and only injects validated whitelist fields.
3. Static safe fields (`service`, `env`) bind with `Logger.With` on the project logger.
4. Aggressive library redaction wraps **outside** the handler passed into that library, after project fields exist on the inner chain.
5. Attributes bound with `With` **inside** a redactor are not visible to the outer `Handle` path and will not be scrubbed. Never pre-bind DSN, password, token, or dependency URLs on any handler that later sits under redaction without being re-bound outside.

When implementing a wrapping `Handler`, always re-wrap in `WithAttrs` and `WithGroup` so child loggers keep enrichment and redaction behavior.

## Logger API Usage

```go
// Preferred: context-aware methods when correlation may be present.
logger.InfoContext(ctx, "community.create.succeeded",
    "operation", "community.create",
    "durationMs", elapsed.Milliseconds(),
    "resourceId", publicID,
)

// Errors: include operation, correlation-capable context, stable error class, safe summary.
logger.ErrorContext(ctx, "community.create.failed",
    "operation", "community.create",
    "errorCode", "DEPENDENCY_TIMEOUT",
    "error", safeSummary, // already redacted / classified; not raw driver text
)
```

Guidance:

- Prefer `InfoContext` / `ErrorContext` / `Log` with `ctx` at request and worker boundaries.
- Hot paths may use `LogAttrs` with prebuilt `slog.Attr` values to reduce allocations.
- Types that can leak secrets may implement `slog.LogValuer` to return redacted groups.
- Do not log-and-ignore: if an error is returned to the caller, either the caller logs at the ownership boundary or this layer logs with a clear owner rule—avoid double noisy ERROR on expected business rejects.

## Levels

| Level | Use | Examples |
| --- | --- | --- |
| DEBUG | Temporary or local detail; off or sampled in production | cache miss internals |
| INFO | Normal lifecycle and successful business milestones | startup, request completed, idempotent replay accepted |
| WARN | Recoverable degradation, retry, brief dependency blip | ready check flapping, retryable downstream timeout |
| ERROR | Failures that need investigation | write failure, commit failure, panic, HTTP 5xx path |

Do not default expected client mistakes (validation, not-found, auth deny) to ERROR unless the project error policy says otherwise.

## Cardinality and Storage Friendliness

Treat low-cardinality identity as stream-like dimensions (`service`, `env`, `operation` template). Keep high-cardinality values as attributes (`requestId`, `userId`, resource IDs), never as dynamic field **names**.

Bad: `sku_0001.clicks` as a key.  
Better: `"sku", "0001", "clicks", 1`.

Prefer extracting numbers, statuses, and IDs into fields rather than burying them in free-text messages.

## Redaction Patterns

| Surface | Owner | Pattern |
| --- | --- | --- |
| Process / application logs | Project logger | Discipline + optional mild `ReplaceAttr`; keep `errorCode` and safe `error` summaries |
| ORM / SQL driver traces | DB open wiring | Outer redacting handler; parameterized SQL only; scrub `error` / connection strings |
| Config dump / startup summary | Config helpers | Explicit allowlist redaction helpers |
| Auth headers / tokens | HTTP middleware | Never log raw values |

Key blacklist design:

- Prefer exact keys or path-aware rules (`dsn`, `password`, `authorization`) over broad `strings.Contains` on fragments like `error`, `data`, `content`.
- If a shared redactor must be aggressive for SQL libraries, keep it on the library path only.

## Anti-Patterns

- Building a second process-wide logger that writes SQL traces to raw stderr while the app uses another logger.
- Falling back to `slog.Default()` in production wiring when injection failed.
- Pre-binding secrets with `logger.With("dsn", dsn)` before redaction.
- Putting business filters, user IDs used for branching, or pagination into `context` solely so logs can read them.
- Using ERROR for every returned `error` including expected domain rejects.
- Coupling retry/backoff decisions to “whether the logger is non-nil”.
- Copying full request/response bodies or domain entities into shared logging helpers “for convenience”.

## Tests

When changing logger construction, context enrichment, or redaction:

- Unit-test context ID validation, rejection of illegal values, and `WithAttrs` / `WithGroup` preservation.
- Assert secret sentinels never appear in handler output for library paths.
- Assert business fields that must survive (`errorCode`, safe summaries, `resourceId`) still appear on the project logger path.
- Prefer injectable buffer/handler test doubles over depending on global default logger state.

## Source Basis

Distilled from:

- Go blog: Structured Logging with slog (`https://go.dev/blog/slog`)
- `log/slog` package design (Logger frontend / Handler backend, `With`, context methods)
- Structured log storage practice: stable message, explicit time, low-cardinality stream dimensions vs high-cardinality attributes
- Common production patterns: context-enriching handlers, library-entry redaction, explicit injection

Do not browse these sources during normal task execution. Refresh only when the user asks for updated official references or a rule appears stale.
