---
description: Save a snapshot of the current session state
---

Creates a timestamped snapshot in `.state/sessions/` with:
- Current task state
- Pending queue snapshot
- Git branch and status
- Session name (if set)
- Timestamp

Usage: /session:save [snapshot-name]

**Output format:**
- With session name: `.state/sessions/{session-name}/{snapshot-name}-YYYY-MM-DD-HH-MM.json`
- Without session name: `.state/sessions/{snapshot-name}-YYYY-MM-DD-HH-MM.json`

Useful for:
- Before major refactors
- End of day checkpoints
- Experiment branching points
- Before risky operations

Example:
```bash
/session:save pre-refactor
/session:save end-of-day
/session:save before-merge
```

**Tip:** Sessions with names get organized into folders, making it easier to track snapshots across multiple sessions.
