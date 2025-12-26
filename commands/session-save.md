---
description: Save a snapshot of the current session state
---

Creates a timestamped snapshot in `.state/sessions/` with:
- Current task state
- Pending queue snapshot
- Git branch and status
- Timestamp

Usage: /session:save [snapshot-name]

Useful for:
- Before major refactors
- End of day checkpoints
- Experiment branching points

Example: /session:save pre-refactor
