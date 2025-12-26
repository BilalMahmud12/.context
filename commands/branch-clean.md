---
description: Clean up merged feature branches
---

Safely removes local branches that:
1. Have been merged to base branch (from config)
2. Are not the current branch
3. Are not the base branch itself

Process:
1. Run: git branch --merged [base_branch]
2. Filter out current and base branch
3. Show list and prompt for confirmation
4. Delete with: git branch -d [branch-name]

Usage: /branch:clean

Safety: Uses `-d` flag (safe delete, only merged branches)
