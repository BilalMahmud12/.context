# Session Distillation System

How to extract and preserve Claude Code session context for future reference.

---

## The Problem

Claude Code sessions contain valuable context:
- Planning discussions
- Implementation decisions
- Problem-solving approaches
- Code changes and their reasoning

But this context is:
- ❌ Stored in large JSONL files (3-4MB each)
- ❌ Too big for git
- ❌ Lost when switching machines
- ❌ Not searchable across sessions

---

## The Solution

**Two-tier context system:**

### Tier 1: Full Sessions (Local Only)
- **Location**: `~/.claude/projects/{project}/*.jsonl`
- **Size**: 3-4MB per session
- **Content**: Complete conversation history
- **Purpose**: Deep search when needed (local machine only)

### Tier 2: Distilled Summaries (Git-Tracked)
- **Location**: `{project}/docs/sessions/YYYY-MM-DD-topic.md`
- **Size**: 15-25KB per session
- **Content**: AI-generated markdown summaries
- **Purpose**: Quick reference, syncs via git

---

## How It Works

```
┌─────────────────────────────────────┐
│  Full Session (3.5MB JSONL)         │
│  ~/.claude/projects/castclub/       │
└──────────────┬──────────────────────┘
               │
               ↓ distill-session.sh
               │
┌──────────────┴──────────────────────┐
│  Extraction                          │
│  - Parse JSONL                       │
│  - Extract messages, tool calls      │
│  - Track file changes, commands      │
└──────────────┬──────────────────────┘
               │
               ↓ AI Summarization
               │
┌──────────────┴──────────────────────┐
│  3-Stage Summarization               │
│  1. Pre-filter (Python, free)        │
│  2. Chunk summaries (Haiku, ~$0.04)  │
│  3. Synthesis (Sonnet, ~$0.04)       │
└──────────────┬──────────────────────┘
               │
               ↓ Template Rendering
               │
┌──────────────┴──────────────────────┐
│  Draft Markdown (15-25KB)            │
│  docs/sessions/*.draft.md            │
└──────────────┬──────────────────────┘
               │
               ↓ Human Review
               │
┌──────────────┴──────────────────────┐
│  Finalized Summary                   │
│  docs/sessions/2025-12-26-topic.md   │
│  (Committed to git)                  │
└──────────────────────────────────────┘
```

**Cost**: ~$0.05-0.12 per session

---

## Quick Start

### After Each Session

```bash
# 1. List recent sessions
distill-session.sh --list

# 2. Distill the latest session
distill-session.sh --latest

# 3. Review the draft
code docs/sessions/*.draft.md

# 4. Edit as needed (remove sensitive info, improve clarity)

# 5. Finalize
mv docs/sessions/2025-12-26-topic.draft.md docs/sessions/2025-12-26-topic.md

# 6. Update INDEX.md with new entry

# 7. Commit
git add docs/sessions/
git commit -m "docs: Add session summary for [topic]"
```

### Distill Specific Session

```bash
# Use session ID
distill-session.sh 359ddc91-b696-476e-8ad8-5c707647800a

# Or find the ID first
distill-session.sh --list
```

### Skip AI (Fast but Less Detailed)

```bash
# Generate template without AI summarization
distill-session.sh --no-ai --latest

# Useful for:
# - Quick structure with manual writing
# - Avoiding API costs
# - Sessions you'll write up yourself
```

---

## What Gets Extracted

### Summary Sections

1. **Header**: Date, duration, session ID, branch, agent
2. **Summary**: One-paragraph overview
3. **Context**: User requests, starting state
4. **Narrative**: Detailed chronological story
5. **Key Decisions**: Decision/reasoning/impact table
6. **Files Changed**: Created/modified/deleted with links
7. **Commands Run**: Bash commands with outputs
8. **Related Tasks**: Links to task files
9. **Blockers**: Problems encountered and resolutions
10. **Code Snippets**: Important code with explanations
11. **Search Keywords**: For future discovery
12. **Raw Session Reference**: Link to full JSONL

### Automatically Tracked

- All file reads/writes/edits
- All bash commands and outputs
- Tool calls (Read, Edit, Grep, etc.)
- Errors and warnings
- Git operations
- Token usage

---

## Dependencies

### Required Packages

```bash
pip install jinja2 anthropic
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Without API key, use `--no-ai` flag.

---

## File Structure

### In .context/

```
~/.context/scripts/
├── distill-session.sh              # Main entry point
└── session-distiller/
    ├── distill.py                  # Core logic
    ├── extractors.py               # JSONL parsing
    ├── summarizers.py              # AI summarization
    └── templates/
        └── session-summary.md.j2   # Markdown template
```

### In Project/

```
{project}/docs/sessions/
├── INDEX.md                           # Searchable registry
├── 2025-12-26-agentshell-migration.md # Finalized
├── 2025-12-25-user-migrations.md      # Finalized
└── 2025-12-26-chat-system.draft.md    # Pending review
```

---

## Cost Considerations

### Per Session (~3MB JSONL)

| Stage | Model | Tokens | Cost |
|-------|-------|--------|------|
| Pre-filter | Python | 0 | $0.00 |
| Chunk summaries | Haiku | ~80K input | ~$0.04 |
| Final synthesis | Sonnet | ~15K input | ~$0.04 |
| **Total** | | ~95K | **~$0.08** |

### Monthly Estimate

- 20 sessions/month = ~$1.60
- 50 sessions/month = ~$4.00

Very affordable for valuable knowledge retention.

---

## Best Practices

### 1. Review Before Committing

**Always review drafts**:
- Remove sensitive data (API keys, passwords, private info)
- Verify decisions are accurately captured
- Add context AI might have missed
- Fix technical inaccuracies

### 2. Update INDEX.md

Keep the session index up to date:
```markdown
| Date | Session | Agent | Keywords |
|------|---------|-------|----------|
| 2025-12-26 | [AgentShell Migration](./2025-12-26-agentshell-migration.md) | M-O | agentshell, rename, bootstrap |
```

### 3. Link to Tasks

Reference related task files:
```markdown
## Related Tasks

- [Task 001](../tasks/001-user-migrations.md)
- [Task 050](../tasks/050-next-feature.md)
```

### 4. Search Keywords

Include varied keywords:
- Technologies (Laravel, Docker, React)
- Actions (migration, refactor, debug)
- Files (app.php, User.php)
- Concepts (authentication, permissions)

### 5. Distill Regularly

Don't let sessions pile up:
- Distill after each significant session
- Batch-distill weekly if needed
- Easier to remember context when fresh

---

## Troubleshooting

### "Session not found"

```bash
# Make sure you're in a git repository
cd ~/Repository/your-project

# List sessions to verify
distill-session.sh --list
```

### "anthropic package not installed"

```bash
pip install anthropic jinja2
```

### "ANTHROPIC_API_KEY not set"

```bash
# Add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-..."

# Or use --no-ai flag
distill-session.sh --no-ai --latest
```

### Draft looks incomplete

- Use `--no-ai` to see raw extraction
- Check if session JSONL is corrupted
- Manually write summary if needed

---

## Future Enhancements

- Auto-link to git commits
- Batch distillation for multiple sessions
- Search command across all sessions
- Integration with docs/progress/ tracking
- Periodic reminders to distill
- Auto-detect related tasks from file paths

---

## Aliases

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias distill='~/.context/scripts/distill-session.sh'
alias distill-latest='~/.context/scripts/distill-session.sh --latest'
alias distill-list='~/.context/scripts/distill-session.sh --list'
```

Then:
```bash
distill --latest
distill-list
```

---

## Philosophy

**Sessions are knowledge, not just history.**

Every Claude Code session contains:
- Problem-solving approaches that worked
- Decisions and their reasoning
- Blockers encountered and overcome
- Code patterns and conventions

By distilling sessions into git-tracked summaries, we:
- ✅ Preserve institutional knowledge
- ✅ Enable search across sessions
- ✅ Share context across machines
- ✅ Build a searchable decision log

**Small investment (~5 min review), huge long-term value.**

---

**AgentShell v1.0.0** | Session Distillation System
