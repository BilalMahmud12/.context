---
description: Show history of completed tasks
---

Reads `.state/current.json` (last_completed) and displays:
- Task ID and name
- Completion date
- Phase/folder
- Git branch used
- Number of commits
- Key changes

Derived from:
1. `.state/current.json` (last_completed field)
2. Task files in docs/tasks/
3. Git commit history

Usage: /history

Shows your progress and what's been accomplished.
