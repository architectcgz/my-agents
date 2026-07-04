# DDD Development Cases

## User Relationship Events

### Symptom

During `zhicore-go` User relationship work, the first implementation made `domain/relationship.go` own:

- integration event type strings such as `user.followed`, `user.blocked`
- a generic `RelationshipEvent` payload struct
- `Payload(occurredAt time.Time) map[string]any`
- JSON field names such as `followerId`, `followingId`, `occurredAt`

The user noticed the design still felt service-centered and asked whether those events belonged in domain.

### Diagnosis

The domain should know that a user followed, unfollowed, blocked, or unblocked another user. It should not know how that fact is published to other services.

Reasoning:

- `user.followed` is an integration contract / routing key shape.
- JSON payload fields are cross-service contract details.
- `occurredAt` in the outbox payload belongs to the publication/envelope mapping.
- Outbox is a durability and delivery mechanism, not a domain concept.

### Better Shape

Domain:

```go
type RelationshipEvent interface{ relationshipEvent() }

type UserFollowed struct {
    FollowerID  UserID
    FollowingID UserID
}

type UserUnfollowed struct {
    FollowerID  UserID
    FollowingID UserID
    Reason      UnfollowReason
}
```

Application:

```go
func publishRelationshipEvent(ctx context.Context, event domain.RelationshipEvent, occurredAt time.Time) error {
    switch e := event.(type) {
    case domain.UserFollowed:
        return publish(ctx, "user.followed", e.FollowerID, occurredAt, map[string]any{
            "followerId": e.FollowerID, "followingId": e.FollowingID, "occurredAt": occurredAt,
        })
    }
}
```

Tests:

- domain tests assert `PlanFollow(...).Event() == UserFollowed{...}`
- application tests assert outbox type `user.followed` and payload fields
- handler tests assert HTTP path, auth identity, cursor validation, and error code mapping

### Reusable Lesson

When a type name contains `Event`, ask:

```text
Is this a business fact, an integration contract, or an outbox storage record?
```

If it answers more than one, split it.

## "Domain-Centered" Does Not Mean "Everything In Domain"

The same case also showed a useful distinction:

- `PlanBlock` belongs in domain because it enforces self-block, active status, reason normalization, and mutual follow cleanup intent.
- Deleting rows, correcting stats, choosing event order, and writing outbox messages belong in application because they coordinate persistence and side effects.

Domain-centered code should make business language explicit. It should not make domain own infrastructure choreography.
