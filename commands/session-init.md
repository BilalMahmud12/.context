---
description: Initialize and name the current session
---

Names the current Claude Code session for better organization and tracking.

Usage: /session:init [session-name]

If no name provided, prompts for one.

Creates `.state/session.json` with:
- Session name
- Start timestamp
- Initial context (task, branch, etc.)

Session names should be descriptive:
- "task-010-user-auth"
- "bugfix-payment-flow"
- "refactor-api-layer"
- "migration-v1-to-v2"

The session name will be used:
- In distillation filenames
- In session save snapshots
- In history tracking
- In daily reports

Example:
```bash
/session:init migration-testing
```

Session is automatically saved to `docs/sessions/{session-name}/` or `.docs/sessions/{session-name}/` depending on mode.