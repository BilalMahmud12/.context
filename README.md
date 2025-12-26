# .context

Global context for AgentsShell AI-augmented development across all machines.

---

## What is This?

This is your **global context folder** that syncs across all your Macs via GitHub.

It contains universal rules, agent configurations, and active repository registry that ALL your projects use.

---

## Structure

```
~/.context/
├── README.md                    # This file
│
├── meta/
│   ├── VERSION                  # Context version (1.0.0)
│   └── SYNC_STATUS.json         # Multi-machine sync status
│
├── core/                        # Universal philosophy (token-optimized)
│   ├── PHILOSOPHY.md            # Core principles (~500 words)
│   ├── WORKFLOW.md              # Daily operations (~400 words)
│   └── RULES.md                 # Hard rules (~600 words)
│
├── agents/                      # Agent initialization files
│   ├── AANG.md                  # Planning agent (Opus 4.5)
│   ├── MO.md                    # Execution agent (Sonnet 4.5)
│   └── ZUKO.md                  # Visual/consulting (optional)
│
├── bilal/                       # Your preferences
│   ├── GIT_CONFIG.md            # Git rules, commit format
│   ├── CODING_STYLE.md          # Language-specific style
│   └── PATTERNS.md              # Architectural patterns
│
└── repository.json              # Active repos registry
```

---

## How It Works

### On Each Machine

1. **Clone this repo:**
   ```bash
   cd ~
   git clone git@github.com:BilalMahmud12/.context.git
   ```

2. **Agents load context automatically:**
   - Aang reads: `PHILOSOPHY.md`, `WORKFLOW.md`, `RULES.md`, `AANG.md`, `PATTERNS.md`
   - M-O reads: `PHILOSOPHY.md`, `WORKFLOW.md`, `RULES.md`, `MO.md`, `PATTERNS.md`

3. **Work on any project:**
   ```bash
   cd ~/Repository/castclub
   # Aang/M-O load BOTH global context AND repo-specific context
   ```

### Syncing Between Machines

**Mac 1 updates context:**
```bash
cd ~/.context
# ... make changes ...
git add .
git commit -m "Update coding patterns"
git push origin main
```

**Mac 2 syncs:**
```bash
cd ~/.context
git pull origin main
# Now has latest context
```

---

## Token Optimization

**Total global context load: ~3,200 tokens**

- PHILOSOPHY.md: ~670 tokens
- WORKFLOW.md: ~540 tokens
- RULES.md: ~800 tokens
- AANG.md or MO.md: ~800 tokens
- PATTERNS.md: ~400 tokens

**Compare:** MCP-based approach = 15,000+ tokens

---

## Repository Registry

The `repository.json` file tracks all active repositories:

```json
{
  "castclub": {
    "name": "Cast Club",
    "remote": "git@github.com:BilalMahmud12/castclub.git",
    "local_path": "~/Repository/castclub",
    "type": "laravel",
    "status": "active",
    "agents": {
      "aang": true,
      "mo": true,
      "zuko": false
    }
  }
}
```

Agents can query this to understand your active projects.

---

## Updating Context

**When to update:**
- New coding patterns emerge
- Rules need refinement
- Agent behavior needs adjustment
- New repository added

**How to update:**
```bash
cd ~/.context
# Edit files
git add .
git commit -m "docs: Update {what changed}"
git push origin main
```

**Important:** After updating, sync all machines.

---

## Do NOT Commit

Never commit to this repo:
- Project-specific files
- Secrets or credentials
- Temporary files
- Large binaries

This repo should stay <1MB (just markdown files).

---

## Multi-Machine Workflow

**Morning on Mac 1:**
```bash
cd ~/.context && git pull  # Sync latest
cd ~/Repository/castclub   # Work on project
```

**Evening on Mac 2:**
```bash
cd ~/.context && git pull  # Sync latest
cd ~/Repository/castclub   # Continue work (different machine, same context)
```

Git + `.context/` = Your work follows you across machines.

---

## Summary

| What | Where | Purpose |
|------|-------|---------|
| Global rules | `~/.context/core/` | Universal principles |
| Agent configs | `~/.context/agents/` | How agents behave |
| Your preferences | `~/.context/bilal/` | Your coding style |
| Repo registry | `~/.context/repository.json` | Active projects |
| Repo-specific | `~/Repository/{repo}/docs/` | Project knowledge |
| Execution state | `~/Repository/{repo}/.state/` | Machine-local cache |

**Philosophy:** Docs as state. Git as truth. Machines as ephemeral containers.
