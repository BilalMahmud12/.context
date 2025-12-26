---
description: Convert current session to markdown summary
---

Creates a distilled markdown summary of the current session in `docs/sessions/` or `.docs/sessions/` depending on mode.

**Output format:**
- With session name: `docs/sessions/{session-name}/YYYY-MM-DD-HH-MM.md`
- Without session name: `docs/sessions/YYYY-MM-DD-{task-id}-{task-name}.md`

Usage: /distill

**How it works:**
1. Checks `.state/session.json` for session name
2. Creates session folder if session name exists
3. Generates timestamped markdown summary
4. Updates session metadata

The summary includes:
- Session name (if set)
- Task objective
- Work completed
- Key decisions
- Code changes
- Issues encountered
- Next steps

**Tip:** Use `/session:init` to name your session before distilling for better organization.
