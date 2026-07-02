# Backend Design Pattern Selection

Use this reference when backend behavior grows around one discriminator: type, status, provider, mode, event, command, tenant policy, lifecycle state, or validation rule.

Core rule: choose the smallest pattern that makes the variant behavior owned, testable, and extensible. Strategy is only one option.

## Pattern Selector

| Symptom | Prefer | Why |
| --- | --- | --- |
| Each branch executes replaceable business behavior behind the same use-case contract | Strategy or policy object | Keeps behavior variants explicit without spreading conditionals |
| Status changes must obey legal transitions | State machine or transition table | Makes lifecycle rules auditable and testable |
| Events, jobs, commands, or webhooks route to independent handlers | Command/handler registry | Keeps routing separate from handler behavior |
| External providers expose different APIs or error shapes | Adapter | Keeps provider quirks outside domain/use-case code |
| Many rules decide whether an action is allowed | Specification or rule object | Gives each rule a name and test owner |
| Branches differ only by constants, labels, or simple mapping data | Lookup table | Avoids creating classes/functions for data |
| Branches are short guard clauses or validation failures | Inline branches | Direct code is clearer when there is no variant behavior |

## Ownership Rules

- Put the pattern at the boundary that owns the decision: use case for domain policy, worker for job dispatch, integration layer for provider behavior, repository for persistence-specific variation.
- Keep permission checks, input validation, and linear failure handling inline unless each branch owns distinct dependencies, state transitions, or side effects.
- Before adding the third branch for one discriminator, stop and choose from the selector.
- If a multi-branch discriminator stays inline, leave a short comment explaining why extraction would add more ownership cost than clarity.

## Examples

### Strategy / Policy Object

Use for replaceable business behavior:

```text
BillingPlan -> PricingPolicy.Calculate(...)
ChallengeType -> ScoringPolicy.Score(...)
ProviderKind -> ProvisioningStrategy.Provision(...)
```

### State Machine

Use for lifecycle rules:

```text
Draft -> Published -> Archived
Queued -> Running -> Succeeded | Failed
PendingPayment -> Paid -> Refunded
```

### Handler Registry

Use for commands and events:

```text
event.type -> EventHandler.Handle(ctx, event)
job.kind -> JobHandler.Run(ctx, payload)
command.name -> CommandHandler.Execute(ctx, command)
```

### Adapter

Use for provider differences:

```text
AwsImageClient implements ImageProvider
DockerHubClient implements ImageProvider
Provider-specific retries and error normalization stay inside the adapter.
```

### Specification / Rule Object

Use for named rule composition:

```text
CanReserveSubnet = HasQuota AND RegionEnabled AND NotOverlapping
CanPublishChallenge = HasValidImage AND HasVisibleCategory AND OwnerApproved
```
