# AgentsShell Philosophy

Core principles for AI-augmented development.

---

## Docs as State

**Documentation is not paperwork. Documentation is state management.**

Like Redux for projects. Any new session loads state from docs and continues. The document IS the memory that AI doesn't have.

```
Traditional:    Code → Documentation (afterthought)
AgentsShell:    Documentation → Code (state drives execution)
```

---

## The Problem

AI assistants are **stateless**. Every session resets. Context is lost.

**Solution:**
- Global `.context/` syncs across machines
- Repository `docs/` captures knowledge
- Ephemeral `.state/` tracks execution
- Git is source of truth, machines are containers

---

## Four Layers

**Layer 0:** `.context/` - Global, multi-machine synced via GitHub
**Layer 1:** `docs/` - Repository knowledge (git-tracked)
**Layer 2:** `.state/` - Execution state (ephemeral, NOT git)
**Layer 3:** Git - Source of truth

---

## Key Principles

**1. Human Writes Prose, AI Writes Code**

Bilal writes requirements in prose (MD).
Aang (planning) creates detailed task files (MD, not XML).
M-O (execution) implements precisely from task files.

```
Human (prose) → Aang (task.md) → M-O (executes) → Git (commits)
```

**2. Specification, Not Interpretation**

Traditional: "Fix the auth bug" → AI interprets → Maybe right, maybe wrong
AgentsShell: task.md specifies exactly what to do → No interpretation → Precise execution

**3. Scope is Sacred**

Task files define scope. Files outside scope are untouchable.
Violations are failures, not creativity.

**4. Permission Gates**

Nothing commits without explicit human permission.
Human is the authority. AI proposes, human disposes.

**5. Escalate, Don't Guess**

When blocked, AI escalates with:
- What was tried (minimum 3 attempts)
- Options identified
- Specific question

Never guess. Never assume. Ask.

---

## Token Optimization

**Global context:** ~3,200 tokens (concentrated)
**Repo context:** ~1,600 tokens (specific)
**Total:** ~4,800 tokens vs 15,000+ with MCPs

AI doesn't get everything. AI gets exactly what it needs.

---

## Self-Proof

AgentsShell validates itself by being used to build the projects that use it.

The methodology documents the methodology.
The system builds the system.
The framework powers the framework.

---

## Summary

| Principle | Meaning |
|-----------|---------|
| Docs as state | Documentation IS the memory |
| Git is truth | Machines are ephemeral, git is permanent |
| MD-native | No XML overhead, direct execution |
| Specification over interpretation | Precise execution, no guessing |
| Scope is sacred | Boundaries are law |
| Permission gates | Human authorizes everything |
| Escalate, don't guess | Ask, don't assume |
| Context layers | Global + repo + state |
| Self-proof | System validates itself |
