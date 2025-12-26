# AgentsShell Workflow

Daily operation flow for AI-augmented development.

---

## Task Cycle

**Phase 1: Planning (Aang)**
```
Bilal describes → Aang analyzes → Creates 01-PLAN.md, 02-TASK.md
```

**Phase 2: Authorization (Bilal)**
```
Reviews task spec → Approves → "Execute"
```

**Phase 3: Execution (M-O)**
```
Reads 02-TASK.md → Implements → Runs tests → Creates 03-NOTES.md
```

**Phase 4: Quality Gate (Bilal + M-O)**
```
Review → "Commit" → "Push" → PR
```

---

## File Communication

Agents communicate through MD files, not each other:

```
docs/tasks/{id}/
├── 00-TICKET.md    # Original requirement
├── 01-PLAN.md      # Aang's analysis
├── 02-TASK.md      # Executable spec for M-O
└── 03-NOTES.md     # M-O's execution report

.state/
├── current.json    # Current task status
└── queue/
    └── pending.json # Queued tasks
```

---

## Bilal Commands

| Command | Agent | Action |
|---------|-------|--------|
| "Feature: {desc}" | Aang | Start planning |
| "Approved" | Aang | Create task spec |
| "Execute" / "go" | M-O | Execute task |
| "Commit" | M-O | Git commit |
| "Push" | M-O | Git push |

---

## Blocked Flow

When M-O is blocked:

```
1. Try 3+ approaches
2. Report: "Blocked on {issue}. Tried: A, B, C. Options: 1, 2, 3."
3. Bilal decides or escalates to Aang
4. M-O continues with guidance
```

**No XML protocol. Just clear prose.**

---

## State Management

**`.state/current.json`** (NOT git-tracked):
```json
{
  "current_task": {
    "id": "050",
    "status": "in_progress",
    "assigned_to": "mo"
  }
}
```

**`docs/progress/CURRENT_STATE.md`** (git-tracked):
```markdown
## In Progress
- Task 050: Portfolio migrations (M-O executing)

## Completed Recently
- Task 049: User system migrations ✅
```

---

## Minimal Bilal Involvement

Per task: ~5-7 messages
1. Describe (1 message)
2. Approve plan (1-2 messages)
3. Authorize execution (1 message)
4. Quality gate (2 messages)

Everything else is autonomous.

---

## Success Metrics

✅ Clear task specs - M-O rarely blocked
✅ Accurate scope - Changes confined to expected files
✅ Fast cycles - <30min for small tasks
✅ Low back-and-forth - <10 messages per task
✅ Good documentation - Future sessions load quickly
