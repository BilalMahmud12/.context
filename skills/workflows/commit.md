---
name: commit
description: Smart commit workflow with analysis, message generation, and git config integration
---

# Commit Skill

Multi-step commit workflow for AgentShell v2.0.

## Workflow

1. **Read repository config**
   - Load `.agentshell.config.json`
   - Extract git config (user.name, user.email, commit_format, claude_signature)

2. **Set git user config**
   ```bash
   git config user.name "$(jq -r '.git.user.name' .agentshell.config.json)"
   git config user.email "$(jq -r '.git.user.email' .agentshell.config.json)"
   ```

3. **Analyze changes**
   - Run `git status` to see staged files
   - Run `git diff --staged` to see exact changes
   - Identify type: feat, fix, refactor, docs, test, chore

4. **Read recent commits**
   - Run `git log -5 --oneline` to see commit style
   - Follow repository's commit message patterns

5. **Generate commit message**
   - **Simple mode**: Follow `git.commit_format` (usually `feat: {description}`)
   - **Jira mode**: Include ticket ID from current task (e.g., `FIAT-209 {description}`)
   - Extract current task ID from `.state/current.json` if available
   - Multi-line format:
     ```
     {type}: {short description}

     - {detail 1}
     - {detail 2}
     - {detail 3}
     ```

6. **Present to user**
   - Show proposed commit message
   - Ask: "Proceed with this commit? (y/n/edit)"
   - If edit: allow user to modify message

7. **Commit**
   - Run `git commit -m "{message}"`
   - **NEVER add Claude signature** (check `claude_signature: false`)
   - Display commit hash and summary

8. **Verify**
   - Run `git log -1` to show committed change
   - Update task notes if applicable

## Critical Rules

- **ALWAYS set git user config first** (step 2)
- **NEVER add Claude signature** (even if user modified message)
- **Follow config's commit_format pattern**
- **In Jira mode**: Include ticket ID from current task
- **In Simple mode**: Use conventional commit format

## Error Handling

- **No staged changes**: Prompt user to stage files first
- **Dirty working tree**: Ask if user wants to stage all or select files
- **Config missing**: Show error, cannot commit without config
