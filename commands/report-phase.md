---
description: Generate phase progress report
---

Analyzes a specific phase folder and creates progress report:

1. **Task Breakdown**
   - Total tasks in phase
   - Completed (from git history)
   - In progress (current_task)
   - Pending (queue)

2. **Code Changes**
   - Files created
   - Files modified
   - Lines of code added

3. **Quality Metrics**
   - Tests written
   - Documentation coverage
   - Linting status

4. **Timeline**
   - Start date (first commit)
   - Last activity
   - Estimated completion

Usage: /report:phase [phase-name]

Example: /report:phase phase1-foundation

Output: docs/sessions/reports/[phase-name]-progress.md
