# Component Contracts and Inputs

Read this file when the task changes props, emits, `v-model`, forms, user input, or API-to-UI data boundaries.

## Component contracts

- Props, emits, and exposed methods form a contract. Change them deliberately.
- Do not mutate props directly.
- Avoid creating two sources of truth for the same value across parent prop, child local state, and store state.
- Use local draft state only when temporary divergence is intentional, such as form editing, staged filters, or inline edits.
- If a component supports `v-model`, keep the ownership obvious: parent owns the canonical value, child emits updates.

## Derived state vs duplicated state

- Prefer derived state over copied state when the value can be computed from existing sources.
- Avoid syncing props into local refs unless you are intentionally creating an editable buffer.
- If local state mirrors remote payload shape only for convenience, reconsider the boundary and normalize earlier.

## Input handling and forms

- Preserve user input on failed submit unless there is a clear product reason to discard it.
- Disable submit while the same mutation is in flight.
- Show field-level validation when the user can act on it.
- Map server validation errors back to the form instead of collapsing them into one generic failure when possible.
- Do not clear dirty state, close dialogs, or reset forms until the authoritative success path is confirmed.

## Data normalization

- Normalize external data at the boundary closest to the source instead of scattering ad hoc checks through templates.
- Convert nullable, optional, or enum-like backend values into a shape the UI can reason about consistently.
- Keep formatting separate from ownership. A display label should not become the actual state source.

## Mock data boundaries

- Keep fixtures and demo records outside route views, workflow composables, stores, and presentational components unless the project already has a colocated story/test fixture convention.
- Feed mock data through the same DTO, adapter, or view-model contract as live data. The component should not branch on "mock mode" just to render normal content.
- Do not let mock convenience define production shape. If a mock omits loading, empty, error, permission, or partial-data cases, add explicit fixtures for those states instead of hardcoding template fallbacks.
- Without mock data, keep the same separation: source/adapters normalize data, workflow owners derive state and actions, UI components render props and emit user intent.
