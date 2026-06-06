# Skill Sync Reminder

This directory contains the shared harness-level reminder for deciding when project-local harness knowledge should be synchronized into global skills or shared harness assets.

Scope:

- non-blocking reminder only
- does not mutate repositories
- does not decide ownership automatically

The shared entrypoint is:

```bash
python3 ~/.agents/harness/skill-sync/remind_skill_sync.py --cwd <repo-root> --staged
```

Typical project wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cwd="$(cd "$script_dir/.." && pwd)"
python3 ~/.agents/harness/skill-sync/remind_skill_sync.py --cwd "$cwd" "$@"
```
