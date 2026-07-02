# Frontend Design Pattern Selection

Use this reference when frontend behavior grows around one discriminator: mode, status, provider, action type, tab, permission shape, lifecycle step, route state, or workflow state.

Core rule: choose the smallest pattern that keeps state ownership obvious. Strategy is only one option.

## Pattern Selector

| Symptom | Prefer | Why |
| --- | --- | --- |
| A mode or tab selects different user actions with the same contract | Strategy map | Keeps mode-specific behavior explicit without growing handlers |
| Toolbar, row, menu, or keyboard commands route to independent actions | Action registry | Gives each command an owner and disabled/loading/error policy |
| A multi-step flow has legal transitions and blocking states | State machine or transition table | Prevents impossible UI states and scattered step checks |
| API providers or backends return different shapes for one UI workflow | Adapter or mapper | Keeps provider quirks outside components |
| Permissions, feature gates, or visibility rules combine many predicates | Capability/rule object | Makes each rule named, testable, and reusable |
| Several components share one workflow capability | Capability composable | Keeps repeated async/state behavior in one owner |
| Branches only choose labels, icons, classes, or static copy | Lookup table | Data mapping is clearer than behavior abstractions |
| Branches are simple render guards or one-off validation | Inline branches | Extraction would obscure the template or state owner |

## Ownership Rules

- Put the pattern where the state is owned. Page-owned route/query behavior stays in the route view or page composable. Store-owned state stays in the store. Reusable component behavior stays behind props/emits contracts.
- Do not extract a pattern only to reduce line count. Extract when it reduces branch drift, duplicate async handling, contract ambiguity, or impossible states.
- Before adding the third branch for one UI/business discriminator, choose from the selector.
- If a repeated discriminator stays inline, leave a short comment explaining why extraction would make ownership less clear.

## Examples

### Strategy Map

Use for mode-specific behavior:

```text
viewMode -> loadRows(...)
editorMode -> buildSubmitPayload(...)
challengeType -> renderPreview(...)
```

### Action Registry

Use for commands:

```text
rowAction.key -> { visible, disabled, run }
toolbarAction.key -> { icon, label, run, inFlightKey }
keyboardShortcut -> action.run()
```

### State Machine

Use for multi-step workflows:

```text
Idle -> Loading -> Ready
Editing -> Saving -> Saved | SaveFailed
Draft -> Validating -> Submittable -> Submitted
```

### Adapter / Mapper

Use for external shape differences:

```text
ProviderA response -> UiChallengeSummary
ProviderB response -> UiChallengeSummary
Components render UiChallengeSummary only.
```

### Capability / Rule Object

Use for permission and visibility rules:

```text
canEdit = isOwner AND notArchived AND hasPermission
canRetry = failed AND notInFlight AND quotaAvailable
```
