# Git Configuration

Bilal's git rules and preferences.

---

## Commit Format

```
{type}-#{id}: {description}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructuring
- `test` - Adding/updating tests
- `docs` - Documentation changes
- `chore` - Maintenance tasks

**Examples:**
```
feat-#050: Add portfolio migrations
fix-#051: Resolve auth token expiration
refactor-#052: Extract validation logic to service
test-#053: Add unit tests for user service
docs-#054: Update API documentation
chore-#055: Update dependencies
```

---

## Branch Format

```
{type}/{id}-{short-name}
```

**Examples:**
```
feat/050-portfolio-migrations
fix/051-auth-token-fix
refactor/052-validation-service
```

---

## Base Branches

**Projects:**
- Cast Club: `main`
- Origin Stack: `main`
- AgentShell: `main`

**Never:**
- Force push to main/master
- Commit directly to main (use feature branches)
- Delete main branch

---

## Commit Rules

**Always:**
- ✅ Meaningful commit messages
- ✅ Co-authored by Claude when AI-generated
- ✅ Reference task ID in message
- ✅ Keep commits atomic (one logical change)

**Never:**
- ❌ Vague messages ("fix stuff", "updates")
- ❌ Skip task ID reference
- ❌ Combine unrelated changes
- ❌ Commit secrets or credentials

---

## Git Workflow

**For new features:**
```bash
git checkout main
git pull origin main
git checkout -b feat/050-feature-name
# ... work ...
git add {scope files}
git commit -m "feat-#050: Description"
git push origin feat/050-feature-name
# Create PR via GitHub
```

**For bug fixes:**
```bash
git checkout main
git pull origin main
git checkout -b fix/051-bug-name
# ... work ...
git add {scope files}
git commit -m "fix-#051: Description"
git push origin fix/051-bug-name
# Create PR via GitHub
```

---

## Pull Requests

**Title format:**
```
[#{id}] {Description}
```

**Body format:**
```markdown
## Summary
- {Main change}
- {Main change}

## Test Plan
- [ ] {Test case}
- [ ] {Test case}

## Screenshots (if UI changes)
{Screenshots}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Protected Operations

**Require explicit permission:**
- Push to remote (`git push`)
- Merge branches
- Rebase
- Force push (`git push --force`)
- Amend pushed commits (`git commit --amend`)
- Reset hard (`git reset --hard`)

**Agents must ask before:**
- Modifying git history
- Changing remote branches
- Deleting branches

---

## .gitignore Patterns

**Always ignore:**
```
# Environment
.env
.env.local
.env.*.local

# Dependencies
node_modules/
vendor/

# Build
dist/
build/
.next/
.nuxt/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# AgentShell
.state/

# Logs
*.log
npm-debug.log*
```

---

## Hooks

**Pre-commit:**
- Run linter
- Run tests
- Check for secrets

**Never skip hooks** unless explicitly requested.

---

## Summary

| Aspect | Rule |
|--------|------|
| Commit format | `{type}-#{id}: {description}` |
| Branch format | `{type}/{id}-{short-name}` |
| Base branch | `main` |
| Force push | Never to main |
| Hooks | Never skip |
| Secrets | Never commit |
