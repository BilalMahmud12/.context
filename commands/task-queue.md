---
description: Add a new task to the pending queue
---

Adds a task to `.state/queue/pending.json` for later execution.

Usage: /task:queue [task-file-path]

Example: /task:queue docs/tasks/phase1-foundation/003-authentication.md

The task will be queued and can be started with `/mo:turbo` or `/task:start`.
