# 查询下推（Query Pushdown）

查询下推（query pushdown）是指尽量把筛选、排序、分页和可安全表达的计算转换为数据库查询，由数据库在数据源附近执行，而不是先把大量数据加载到应用层再过滤。

## Use When

Use this reference when a backend feature involves:

- search or filtering DSLs such as CEL, JSON filters, query parameters, or saved views;
- translating user expressions into SQL or another storage query language;
- combining user filters with authorization or tenant predicates;
- deciding between database filtering and in-memory filtering;
- cross-database SQL generation, pagination, indexes, or full-text search.

## Preferred Pipeline

Separate user-facing expression semantics from database syntax:

```text
user filter -> parser/type checker -> intermediate representation (IR) -> dialect renderer -> SQL + bound args
```

Treat the IR as a database-neutral condition tree. For example:

```text
AND
├── FieldPredicate(pinned)
└── Comparison(visibility, ==, "PUBLIC")
```

`FieldPredicate(pinned)` means that the boolean field `pinned` must be true. The renderer can emit the correct representation for each database, such as `memo.pinned IS TRUE`.

## Design Rules

1. **Validate against a schema.** Allow only declared fields, types, functions, and operators. Reject unknown identifiers, invalid operand types, unsupported operators, and non-boolean top-level expressions before execution.

2. **Use an IR for non-trivial translation.** Do not mix DSL parsing, authorization, field mapping, SQL construction, and dialect branching in one function. Keep parsing, semantic normalization, and rendering as separate responsibilities.

3. **Render dialect-specific SQL at the edge.** Keep the IR independent of SQLite, MySQL, or PostgreSQL. Isolate differences in JSON access, timestamps, booleans, regular expressions, `LIKE`/`ILIKE`, and placeholders in the renderer.

4. **Bind values; never interpolate user values into SQL.** The renderer should return a SQL fragment plus an argument list. Track placeholder offsets when appending to an existing query.

5. **Compose authorization with data filters.** Apply tenant, creator, visibility, or row-level permission predicates in the same database query. Preserve expression grouping: keep `OR` inside the user expression, parenthesize independently compiled filters, and combine independent filter sources with `AND`.

6. **Push down ordering and pagination.** Apply `ORDER BY`, `LIMIT`, and `OFFSET` or keyset predicates in the database. Add a deterministic tie-breaker, usually a unique ID, so pages do not shift when sort keys are equal.

7. **Keep structured filters explicit.** Simple identity, status, and ID-list constraints may remain typed repository fields. Use the DSL/IR for composable domain predicates, not as a reason to turn every query parameter into an opaque string.

8. **Test at the ownership boundary.** Test parser/type validation, IR semantics, and each dialect renderer separately. Add integration tests that execute representative generated queries against supported databases, especially for JSON, time, tags, nulls, boolean values, and permission combinations.

## Concrete SQL Builder Patterns

### Build Conditions Without Losing `WHERE`/`AND` Semantics

SQL uses `WHERE` before the first predicate and `AND` before subsequent predicates. A direct string builder therefore needs special handling for the first condition:

```go
query := "SELECT ... FROM memo"
first := true

if pinned {
    query += " WHERE memo.pinned IS TRUE"
    first = false
}
if publicOnly {
    if first {
        query += " WHERE memo.visibility = ?"
        first = false
    } else {
        query += " AND memo.visibility = ?"
    }
    args = append(args, "PUBLIC")
}
```

Prefer collecting predicates and joining them once when the query builder is small and local:

```go
where := []string{}
args := []any{}

if pinned {
    where = append(where, "memo.pinned IS TRUE")
}
if publicOnly {
    where = append(where, "memo.visibility = ?")
    args = append(args, "PUBLIC")
}

query := "SELECT ... FROM memo"
if len(where) > 0 {
    query += " WHERE " + strings.Join(where, " AND ")
}
```

### Use `1 = 1` for Uniform Append Logic

`1 = 1` is an always-true SQL predicate. It is not a business filter; it gives a builder a stable `WHERE` starting point so every later predicate can be appended uniformly with `AND`:

```go
where := []string{"1 = 1"}
args := []any{}

if pinned {
    where = append(where, "memo.pinned IS TRUE")
}
if publicOnly {
    where = append(where, "memo.visibility = ?")
    args = append(args, "PUBLIC")
}

query := "SELECT ... FROM memo WHERE " + strings.Join(where, " AND ")
```

The result is structurally simple:

```sql
WHERE 1 = 1
  AND memo.pinned IS TRUE
  AND memo.visibility = ?
```

Use this pattern when many repository branches append to the same predicate list. Do not add it when a condition list can be joined cleanly at the end; the latter avoids a redundant constant predicate.

### Append Rendered Filters With Parentheses and Bound Args

When a filter engine returns SQL plus arguments, append each independently compiled expression as a parenthesized predicate. Preserve placeholder offsets for dialects such as PostgreSQL:

```go
where := []string{"1 = 1"}
args := []any{}

for _, filterText := range find.Filters {
    stmt, err := engine.CompileToStatement(ctx, filterText, filter.RenderOptions{
        Dialect:           dialect,
        PlaceholderOffset: len(args),
    })
    if err != nil {
        return nil, err
    }
    if stmt.SQL == "" {
        continue
    }

    where = append(where, "("+stmt.SQL+")")
    args = append(args, stmt.Args...)
}
```

For example, independent filters become:

```sql
WHERE 1 = 1
  AND (content ILIKE $1 OR tag @> $2)
  AND (creator_id = $3 OR visibility IN ($4, $5))
```

The parentheses are important: they preserve the `OR` grouping inside each expression while the independent filters remain combined with `AND`.

## Example

For a memo query:

```cel
content.contains("roadmap") && tags.exists(t, t.startsWith("project/"))
```

Use this flow:

1. Parse and type-check the CEL expression against the memo schema.
2. Normalize it to an IR containing a text-match condition and a collection predicate.
3. Render those conditions for the selected database using bound parameters.
4. Append authorization predicates and typed repository constraints with explicit parentheses.
5. Execute one SQL query with ordering and pagination.

The application should not fetch every memo and evaluate the CEL program in memory merely because the input was expressed in CEL.

## Memos Implementation Map

Use the following files as a concrete reference for a CEL-to-SQL query pushdown implementation:

1. **CEL compilation entry point**

   `internal/filter/engine.go:47` shows the main pipeline:

   ```go
   ast, issues := e.env.Compile(filter)
   parsed, err := cel.AstToParsedExpr(ast)
   cond, err := buildCondition(parsed.GetExpr(), ...)
   ```

   This is the `CEL -> AST -> IR Condition` transition.

2. **IR condition definitions**

   `internal/filter/ir.go:1` defines the condition nodes. Pay particular attention to:

   - `LogicalCondition` for `AND` and `OR`;
   - `ComparisonCondition` for field comparisons;
   - `FieldPredicateCondition` for direct boolean-field checks;
   - `TextMatchCondition` for text matching;
   - `ListComprehensionCondition` for collection traversal such as `exists()` and `all()`.

   These nodes represent query semantics without committing to SQL syntax.

3. **CEL AST to IR conversion**

   `internal/filter/parser.go:20` converts parsed CEL nodes instead of inspecting raw strings:

   ```go
   case "_&&_":
       left, err := buildCondition(call.Args[0], pc)
       right, err := buildCondition(call.Args[1], pc)

       return &LogicalCondition{
           Operator: LogicalAnd,
           Left:     left,
           Right:    right,
       }, nil
   ```

   Do not detect `&&` or `||` with string operations; use the parsed AST so precedence, nesting, and operand validation remain correct.

4. **IR rendering to SQL**

   `internal/filter/engine.go:73` and `internal/filter/render.go:1` render an IR condition into a SQL fragment and bound values:

   ```go
   type Statement struct {
       SQL  string
       Args []any
   }
   ```

   Keep SQL text and values separate. Never interpolate user-provided values into the SQL string.

5. **Combining multiple filters**

   `internal/filter/helpers.go:8` compiles each independent filter, wraps it in parentheses, and appends its arguments:

   ```go
   for _, filterStr := range filters {
       stmt, err := engine.CompileToStatement(ctx, filterStr, opts)
       if err != nil {
           return err
       }
       if stmt.SQL == "" {
           continue
       }
       *where = append(*where, fmt.Sprintf("(%s)", stmt.SQL))
       *args = append(*args, stmt.Args...)
   }
   ```

   The resulting structure is `each filter separately compiled -> parenthesized -> joined in SQL with AND`.

6. **Database driver integration**

   `store/db/sqlite/memo.go:54` shows the SQLite integration:

   ```go
   where, args := []string{"1 = 1"}, []any{}

   engine, err := filter.DefaultEngine()
   if err != nil {
       return nil, err
   }

   if err := filter.AppendConditions(
       ctx,
       engine,
       find.Filters,
       filter.DialectSQLite,
       &where,
       &args,
   ); err != nil {
       return nil, err
   }
   ```

   `store/db/mysql/memo.go:62` and `store/db/postgres/memo.go:51` use the same integration boundary with their own dialect. Keep the driver responsible for final query assembly and execution, while the filter package owns expression translation.

7. **Service-layer authorization composition**

   `server/router/api/v1/memo_service.go:178` appends the user filter and the authorization predicate to the same `FindMemo.Filters` collection:

   ```go
   memoFind.Filters = append(memoFind.Filters, request.Filter)

   memoFind.Filters = append(
       memoFind.Filters,
       fmt.Sprintf(`creator_id == %d || visibility in ["PUBLIC", "PROTECTED"]`, currentUser.ID),
   )
   ```

   This is a useful pattern for keeping business filters and permission filters in one database query. The service owns the authorization decision; the store owns translating and executing the final query.

## Common Mistakes

- Treating the DSL as SQL or concatenating raw expressions into SQL.
- Validating one representation but executing another representation with different semantics.
- Applying authorization after pagination or after an in-memory filter, which can cause data leaks or short/inconsistent pages.
- Losing parentheses when combining `AND` and `OR` conditions from different sources.
- Assuming `contains` is full-text search. `LIKE`/`ILIKE` scans may need indexes, database full-text indexes, FTS, or a search service as data grows.
- Hiding every condition inside a string and losing typed repository constraints, query observability, or index-friendly plans.

## Decision Boundary

Prefer query pushdown when the predicate can be expressed correctly and efficiently by the database. Use application-side filtering only for logic that cannot be represented in the storage query, and make that boundary explicit. If the query is a user-facing search over large text, evaluate whether a dedicated full-text or search index is required instead of expanding a SQL predicate DSL indefinitely.
