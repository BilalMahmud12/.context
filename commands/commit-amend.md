---
description: Safely amend the last commit
---

Amends the last commit with staged changes.

Safety checks:
1. **Not pushed**: Verify commit not on remote (git log origin/branch..HEAD)
2. **Recent**: Last commit within current session
3. **Confirmation**: Always prompt user before amending

Usage: /commit:amend

Will abort if:
- Last commit already pushed to remote
- Last commit not created in current session
- Working directory has unstaged changes

Use with caution - only for fixing mistakes in the most recent commit.
