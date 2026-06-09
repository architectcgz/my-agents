# Skill Sync Reminder

This directory contains the shared harness-level reminder for deciding when project-local harness knowledge should be synchronized into global skills or shared harness assets.

Scope:

- non-blocking reminder only
- does not mutate repositories
- does not decide ownership automatically

The shared non-blocking reminder entrypoint is:

```bash
bash ~/.agents/harness/check-skill-sync-reminder.sh --cwd <repo-root> --staged
```

The shared blocking archive-state check is:

```bash
bash ~/.agents/harness/check-feedback-archive-state.sh --cwd <repo-root>
```

This blocker is for state transition, not deletion:

- absorbed/mechanized feedback must switch to an `archived` / `归档` status
- project-local or pending-sync feedback may stay active

Typical project reminder wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cwd="$(cd "$script_dir/.." && pwd)"
bash ~/.agents/harness/check-skill-sync-reminder.sh --cwd "$cwd" "$@"
```
