---
description: Rename the current session
---

Renames an ongoing session to better reflect the current work.

Usage: /session:rename <new-name>

Updates `.state/session.json` with:
- New session name
- Rename timestamp
- Preserves original start time

Useful when:
- Session scope changed (e.g., "bugfix" → "bugfix-and-refactor")
- Original name was generic (e.g., "testing" → "api-migration-testing")
- Work evolved into something different

Example:
```bash
/session:rename api-payment-integration
```

**Note:** This does NOT rename already saved files (distillations, snapshots). Those remain with their original names for historical tracking. Only affects current session and future saves.

If no session exists yet, use `/session:init` instead.