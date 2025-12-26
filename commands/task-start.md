---
description: Start a specific task from the pending queue
---

Moves a specific task from `.state/queue/pending.json` to `.state/current.json`.

Usage: /task:start [task-id]

Example: /task:start 005

Allows non-linear execution when you need to prioritize a specific task over others in the queue.
