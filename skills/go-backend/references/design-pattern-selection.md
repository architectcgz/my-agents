# Go Backend Design Pattern Selection

Use this reference when Go backend behavior grows around one discriminator: provider, status, event type, mode, command, job kind, lifecycle state, or business rule.

Core rule: choose the smallest Go-shaped pattern that makes behavior testable by key. Strategy is only one option.

## Pattern Selector

| Symptom | Prefer | Why |
| --- | --- | --- |
| Each branch calls replaceable behavior with shared inputs | `map[Key]func(...)` or small consumer-owned interface | Keeps behavior dispatch explicit without Java-style hierarchy |
| Branches need stateful dependencies or multiple methods | Small consumer-owned interface | Lets the consumer define the contract it needs |
| Events, jobs, commands, or webhooks route to independent handlers | Handler registry | Separates dispatch from handler behavior |
| Lifecycle status changes must follow legal transitions | Transition table or explicit state machine | Makes allowed transitions testable |
| Provider APIs differ but the use case needs one port | Adapter | Keeps provider-specific API and error mapping outside use cases |
| Many business predicates decide eligibility | Rule function, specification-like struct, or policy object | Gives each rule a name and focused tests |
| Branches only map constants or simple fields | Table lookup | Data does not need an interface |
| Branches are validation guards or local error classification | Inline branches | Direct code is clearer when behavior does not vary |

## Ownership Rules

- Define interfaces at the consumer side by default. Provider packages should expose concrete implementations unless an existing boundary already owns an abstraction.
- Keep `map[Key]func(...)` or handler maps close to the package that owns the business rhythm. Avoid global registries unless plugin-style extension is an explicit requirement.
- Before adding the third case for one discriminator, choose from the selector.
- If a repeated discriminator stays inline, leave a short comment explaining why a pattern would add more cost than clarity.

## Examples

### Function Map

Use when variants are stateless or dependencies are already captured:

```go
handlers := map[JobKind]func(context.Context, Job) error{
    JobKindCleanup: runCleanup,
    JobKindReport:  runReport,
}
```

### Small Interface

Use when the consumer needs replaceable behavior with dependencies:

```go
type Provisioner interface {
    Provision(ctx context.Context, req ProvisionRequest) (*Instance, error)
}
```

### Handler Registry

Use for commands, events, and jobs:

```text
event.Type -> EventHandler.Handle(ctx, event)
command.Name -> CommandHandler.Execute(ctx, command)
job.Kind -> JobHandler.Run(ctx, payload)
```

### Transition Table

Use for lifecycle rules:

```text
Queued -> Running
Running -> Succeeded | Failed
Failed -> Retrying | Dead
```

### Adapter

Use for providers:

```text
DockerClient -> ImageProvider
RegistryClient -> ImageProvider
Provider-specific errors become package-local typed errors before leaving the adapter.
```

### Rule Function / Policy Object

Use for named predicates:

```text
CanStartInstance(ctx, actor, challenge)
CanReserveSubnet(ctx, tenant, cidr)
```
