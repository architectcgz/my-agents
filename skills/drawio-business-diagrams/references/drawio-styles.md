# Draw.io Style Reference

Use these styles when generating diagrams.net / draw.io XML for business relationship diagrams. Prefer stable semantic shapes over decorative variety.

## Color System

| Meaning | Fill | Stroke | Use |
| --- | --- | --- | --- |
| Entry / UI / API | `#e0f2fe` | `#0284c7` | user actions, UI panels, HTTP APIs, CLI commands |
| Business owner | `#dcfce7` | `#16a34a` | domain module, application service, owner boundary |
| External facts / infrastructure | `#ffedd5` | `#ea580c` | runtime, third-party, resource facts, external systems |
| Consumer / downstream | `#ede9fe` | `#7c3aed` | jobs, downstream modules, runtime consumers |
| Data / migration | `#f1f5f9` | `#64748b` | DB tables, persisted records, migration snapshots |
| Blocker / forbidden | `#fee2e2` | `#dc2626` | errors, blockers, unsupported paths, removed legacy flow |
| Confirmation / risk | `#fef3c7` | `#d97706` | manual confirmation, approval, high-risk operation |

## Node Styles

### Decision / Choice / Guard

Use this for every `if / switch / 是否 / 选择 / guard / 条件分支` node.

```text
rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=8;
```

XML example:

```xml
<mxCell id="decision-capacity" value="容量是否足够？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=8;" vertex="1" parent="1">
  <mxGeometry x="760" y="260" width="180" height="120" as="geometry"/>
</mxCell>
```

Decision-node rules:

- The label should be a question or guard expression.
- Every outgoing edge must have a condition label.
- Use at least two outgoing edges.
- Do not place actions inside a diamond. Put actions in the next rectangle.
- Do not use ordinary rectangles for branch logic.

### Entry / UI / API Action

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#e0f2fe;strokeColor=#0284c7;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=10;
```

Use for user operations, frontend actions, API calls, command invocations, and handler entrypoints.

### Business Owner / Domain Module

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#16a34a;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;spacing=10;spacingLeft=14;
```

Use for the module or service that owns the decision, invariant, state transition, or write.

### External Facts / Infrastructure

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;spacing=10;spacingLeft=14;
```

Use for components that provide facts but do not own the business decision.

### Consumer / Downstream Flow

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#ede9fe;strokeColor=#7c3aed;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;spacing=10;spacingLeft=14;
```

Use for downstream consumers, jobs, runtime flows, or lifecycle operations that consume confirmed decisions.

### Data Table / Persistent Record

```text
shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#f1f5f9;strokeColor=#64748b;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=10;
```

Use for DB tables, durable records, snapshots, ledgers, or migration state.

### Blocker / Forbidden Path

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#dc2626;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=10;
```

Use for blocker results, guard failures, prohibited transitions, removed fallback paths, and unsupported behaviors.

### Confirmation / Manual Approval

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;spacing=10;
```

Use for explicit user confirmation, approval, expected-value confirmation, or high-risk action staging.

### Callout / Constraint Note

```text
shape=note;whiteSpace=wrap;html=1;fillColor=#fff7ed;strokeColor=#f97316;fontSize=13;align=left;verticalAlign=top;spacing=10;spacingLeft=12;
```

Use for non-goals, transaction rules, rollback limits, or important constraints that would overload a node.

### Swimlane

```text
swimlane;html=1;startSize=34;horizontal=0;fillColor=#f8fafc;strokeColor=#cbd5e1;fontSize=14;fontStyle=1;align=center;verticalAlign=top;
```

Use only when lanes clarify owner boundaries or sequence responsibility.

## Edge Styles

### Required Call / Write / State Transition

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;strokeColor=#334155;strokeWidth=2;
```

### Read-only Fact Query

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;dashed=1;strokeColor=#64748b;strokeWidth=2;
```

### Success Path

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;strokeColor=#16a34a;strokeWidth=2;
```

### Blocker / Failure Path

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;strokeColor=#dc2626;strokeWidth=2;
```

### Confirmation Path

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;strokeColor=#d97706;strokeWidth=2;
```

### Forbidden / Removed Legacy Path

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;dashed=1;strokeColor=#dc2626;strokeWidth=2;
```

## Edge Label Rules

- Decision outgoing edges must be labeled.
- Prefer short labels: `yes`, `no`, `pass`, `fail`, `same target`, `different target`, `capacity ok`, `insufficient`, `allowed`, `blocked`.
- Label read-only edges only when the read meaning is not obvious.
- Do not label every linear happy-path edge if it adds clutter.

## Page Defaults

Use a stable canvas so rendered PNGs are readable:

```xml
<mxGraphModel dx="1800" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1800" pageHeight="1200" math="0" shadow="0">
```

Recommended node dimensions:

- Decision diamond: width `170-220`, height `110-150`.
- Action / owner node: width `240-340`, height `100-180`.
- Data table: width `220-320`, height `120-220`.
- Callout: width `260-420`, height `100-180`.

## Layout Checks

- Main flow reads left-to-right or top-to-bottom.
- Side branches do not cross the happy path.
- No edge should pass through node text.
- Keep text to 1-4 lines per node.
- Use callouts for long constraints.
- If a diagram only contains boxes with paragraphs, redraw it as relationships and decisions.
