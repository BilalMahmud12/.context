---
name: pr
description: Pull request creation with commit analysis and GitHub CLI integration
---

# PR Skill

Multi-step pull request workflow for AgentShell v2.0.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Current branch ahead of base branch
- Repository has remote on GitHub

## Workflow

1. **Read repository config**
   - Load `.agentshell.config.json`
   - Extract `git.base_branch` (main/develop)
   - Extract repository info

2. **Verify prerequisites**
   - Check `gh` is installed: `which gh`
   - Check `gh` is authenticated: `gh auth status`
   - Get current branch: `git branch --show-current`
   - Verify branch is ahead: `git log {base_branch}..HEAD --oneline`

3. **Analyze commits**
   - Get all commits since base branch: `git log {base_branch}..HEAD`
   - Identify commit types (feat, fix, refactor, etc.)
   - Extract file changes: `git diff {base_branch}...HEAD --stat`
   - Read commit messages for context

4. **Generate PR title and body**

   **Title generation:**
   - **Jira mode**: Use ticket ID + summary (e.g., `FIAT-209: Add player limits update endpoint`)
   - **Simple mode**: Use first commit subject or summarize changes

   **Body generation:**
   ```markdown
   ## Summary
   - [Bullet point summary of changes]
   - [Based on commit messages]
   - [Grouped by type: features, fixes, refactors]

   ## Changes
   - {file count} files changed
   - {additions}+ insertions, {deletions}- deletions

   ## Testing
   - [ ] Unit tests pass
   - [ ] Build succeeds
   - [ ] Lint passes

   ## Related
   - Task: [link to task file or Jira ticket]

   ---
   Generated with AgentShell v2.0
   ```

5. **Present to user**
   - Show proposed title and body
   - Ask: "Create PR with this content? (y/n/edit)"
   - If edit: allow user to modify title and body

6. **Push branch** (if needed)
   - Check if branch exists on remote: `git ls-remote --heads origin {branch}`
   - If not: `git push -u origin {branch}`
   - If exists and ahead: `git push`

7. **Create PR**
   - Use GitHub CLI: `gh pr create --title "{title}" --body "{body}"`
   - Capture PR URL from output

8. **Display result**
   - Show PR URL
   - Show PR number
   - Optionally open in browser: `gh pr view --web`

## Mode-Specific Behavior

**Simple Mode:**
- PR title: First commit subject or "feat: {summary}"
- Body includes: commits, files, test checklist
- Link to task file in repository (if available)

**Jira Mode:**
- PR title: "{JIRA-ID}: {summary}"
- Body includes: Jira ticket link, commits, files, test checklist
- Extract Jira ID from `.state/current.json` or branch name

## Critical Rules

- **ALWAYS push before creating PR** (verify with `git log origin/{branch}..HEAD`)
- **Use gh CLI** (not raw API calls)
- **Follow repository's base branch** from config
- **Include test checklist** in PR body
- **Link to source** (task file or Jira ticket)

## Error Handling

- **gh not installed**: Show installation instructions
- **gh not authenticated**: Run `gh auth login`
- **No commits ahead**: Show error, cannot create PR
- **Push fails**: Show error, check permissions
- **PR creation fails**: Show gh error, likely duplicate PR exists
