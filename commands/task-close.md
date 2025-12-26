---
description: Close current task and update state
---

Marks the current task as completed and clears it from `.state/current.json`.

Updates:
- Sets `current_task` to null
- Updates `last_completed` with current task ID
- Increments `next_number`

Usage: /task:close

This should be called after M-O finishes executing a task successfully.
