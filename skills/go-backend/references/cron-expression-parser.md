# Cron Expression Parser

Use `D:\projects\memos\internal\scheduler\parser.go` as a concrete reference when implementing a small Go cron parser or reviewing scheduled-work code.

The implementation is a good model for keeping parsing code explicit, composable, and easy to audit: the public schedule owns the complete expression, parsing is split by field, and each field delegates value matching to a small concrete matcher.

## Implementation Shape

Prefer a shape similar to the reference:

```go
type Schedule struct {
    seconds  fieldMatcher
    minutes  fieldMatcher
    hours    fieldMatcher
    days     fieldMatcher
    months   fieldMatcher
    weekdays fieldMatcher
}

type fieldMatcher interface {
    matches(value int) bool
}
```

- Keep the schedule as the aggregate that coordinates field matchers; do not make callers understand parser internals.
- Use a narrow consumer-owned interface when several implementations share one behavior. The parser can then return `exactMatcher`, `wildcardMatcher`, `rangeMatcher`, `listMatcher`, or `stepMatcher` without a type switch in `Schedule.matches`.
- Keep matcher implementations immutable after construction. Validate constructor input in `parseField`, so `matches` only evaluates an already-valid value.
- Prefer small concrete types and ordinary control flow over reflection, generic maps, or a single matcher with many mode flags.

## Parse Flow

Make the top-level parser read like a field-by-field contract:

1. Reject an empty expression and validate the accepted field count.
2. Normalize the optional seconds field and calculate the index offset once.
3. Parse each field with its own inclusive bounds.
4. Wrap errors at the field boundary so the caller knows which part failed.

The reference uses `offset` to describe the input layout, not parser success:

```go
offset := 0
if hasSeconds {
    seconds, err = parseField(fields[0], 0, 59)
    if err != nil {
        return nil, errors.Wrap(err, "invalid seconds field")
    }
    offset = 1
} else {
    seconds = &exactMatcher{value: 0}
}
```

This avoids duplicating the minute, hour, day, month, and weekday parsing branches. Keep the explicit field-specific error labels even when the underlying parser is shared.

The reference's `parseField(field, min, max)` follows a simple, ordered decision tree: wildcard, step, list, range, then exact value. Each branch validates its own syntax and bounds before returning a matcher. Preserve that ordering when syntax forms overlap, and return an error instead of silently accepting a partial expression.

The reference uses `github.com/pkg/errors` for contextual wrapping because that is the Memos repository convention. In another repository, use that repository's established error package and wrapping convention; preserve the field context either way.

## Matcher Style

Keep matching methods deliberately boring and total over validated inputs:

```go
func (m *stepMatcher) matches(value int) bool {
    if value < m.min || value > m.max {
        return false
    }
    return (value-m.min)%m.step == 0
}
```

The range check makes the matcher robust even when called outside the parser's expected path. Use standard-library helpers such as `slices.Contains` for list membership rather than hand-written search loops when the repository's Go version supports them.

## Field Layout

Support the accepted layouts explicitly:

- 5 fields: `minute hour day-of-month month day-of-week`
- 6 fields: `second minute hour day-of-month month day-of-week`

Parse the optional seconds field first. Keep an index offset for the remaining fields: `0` for five-field expressions and `1` for six-field expressions. The offset describes the input layout, not whether parsing returned an error. When seconds are omitted, match second `0`.

## Matching

Parse each field into a small matcher with one responsibility. The Memos reference separates exact values, wildcards, ranges, lists, and step values such as `*/5`. Validate values against the field's range before constructing a matcher.

For a step matcher, validate that the step is positive and within the field range. A step expression should match values relative to the field minimum, for example `*/15` in minutes matches `0, 15, 30, 45`.

Make cron dialect choices explicit. In the reference implementation, day-of-month and day-of-week are combined with OR semantics, while seconds, minutes, hours, and month must all match.

## Next-Run Search

Start strictly after the supplied time and truncate to the schedule's precision. Search using one-second increments for six-field expressions and one-minute increments for five-field expressions. Always impose a finite upper bound, such as the four-year cap used by the reference, so malformed or unusually sparse expressions cannot create an infinite loop.

Keep `Next` as a predictable linear search with three visible phases: normalize the start time, establish the search cap, and advance at the schedule precision until `matches` succeeds. Do not hide time advancement in callbacks or introduce a second scheduling abstraction for a parser this small. Return the first matching instant and make the no-match sentinel explicit.

Return an explicit zero time or an error when no match is found within the bound. Callers must handle that result rather than treating it as a valid scheduled time.

Keep timezone selection outside the parser or make it an explicit scheduler configuration. Do not silently mix the process local timezone with persisted cron definitions.
