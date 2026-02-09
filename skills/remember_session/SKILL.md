---
name: remember_session
description: >
  Review the current session and persist what matters to memory and obsidian.
  Use at the end of a work session, when the user says "remember this session",
  "take notes", or "save what we did". Do NOT use mid-session.
allowed-tools: Bash(uv run *), Bash(git *), Read, Write, Glob, Grep
---

End-of-session ritual. Review what happened, persist what matters, aggregate.

## Steps

### 1. Review the session

Scan the full conversation. Identify:
- **What was done**: features built, bugs fixed, decisions made, files changed
- **What was learned**: new tools, patterns, preferences, corrections
- **What changed**: facts about the user, project, or environment that updated
- **What's pending**: TODOs, deferred work, open questions

### 2. Save daily notes

Use the `hierarchical_memory` skill to save timestamped notes to today's daily file:

```bash
uv run --directory MEMORY_SKILL_DIR python scripts/memory.py note "NOTE_TEXT"
```

Save one note per distinct topic. Include:
- Completed work (prefix with `DONE:`)
- Decisions and their rationale
- New preferences or corrections the user made
- Remaining TODOs (prefix with `TODO:`)
- Facts that changed (new job, new tool, moved repo, etc.)

Be specific. "Updated auth" is useless. "Replaced JWT middleware with session cookies because latency was too high on mobile" is useful.

### 3. Save big-picture items to obsidian

If the session produced anything worth finding later — a new project, an architectural decision, a research finding, a personal milestone — create or update a note in obsidian using the `obsidian` skill.

Daily work does NOT go to obsidian. Only durable knowledge: project descriptions, design decisions, reference material, personal facts.

### 4. Aggregate memory

Run the monthly and overall memory aggregation sub-agents from the `hierarchical_memory` skill. This compresses daily notes into monthly summaries and updates the overall working memory.

### 5. Commit and push

```bash
cd ~/claude/memory && git add -A && git commit -m "memory update" && git push 2>/dev/null; true
cd ~/claude/obsidian && git add -A && git commit -m "notes update" && git push 2>/dev/null; true
```
