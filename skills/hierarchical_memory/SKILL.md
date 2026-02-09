---
name: hierarchical_memory
description: >
  Manage a simple hierarchical memory system stored as markdown files.
  Use when the user wants to save a note, recall past context, review
  what was discussed previously, or aggregate learnings over time.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(uv run *), Bash(git *), Read, Write, Glob
---

Manage notes in the hierarchical memory at `~/claude/memory/`.

## Commands

### Save a note
```bash
uv run --directory SKILL_DIR python scripts/memory.py note "Your note text here"
```
Appends an ISO-timestamped entry to today's daily file (`YYYY-MM-DD.md`).

### View today's notes
```bash
uv run --directory SKILL_DIR python scripts/memory.py today
```

### View notes for a specific date or month
```bash
uv run --directory SKILL_DIR python scripts/memory.py show YYYY-MM-DD
uv run --directory SKILL_DIR python scripts/memory.py show YYYY-MM
```

### Aggregate daily notes into monthly and overall summaries
```bash
uv run --directory SKILL_DIR python scripts/memory.py aggregate
```
Rolls up daily notes into monthly summaries (`YYYY-MM.md`) and an overall `memory.md`.

### Search notes
```bash
uv run --directory SKILL_DIR python scripts/memory.py search "query"
```

Where `SKILL_DIR` is the directory containing this skill.

## File Structure

```
~/claude/memory/
├── memory.md           # Overall summary (aggregated from monthly)
├── 2026-02.md          # Monthly summary (sortable YYYY-MM)
├── 2026-02-08.md       # Daily notes
└── ...
```

## Aggregation Strategy

Use sub-agents for aggregation to keep context windows clean:

1. **Daily → Monthly**: Run `aggregate` command to roll up daily notes into monthly summaries
2. **Monthly → Overall memory**: The `aggregate` command builds `memory.md` from monthly summaries
3. **Working memory review**: Periodically launch a sub-agent to read all notes and produce a concise working memory summary

## Git Integration

After saving notes or aggregating, commit and push:

```bash
cd ~/claude/memory && git add -A && git commit -m "memory update" && git push 2>/dev/null; true
```

### First-time setup
```bash
mkdir -p ~/claude/memory && cd ~/claude/memory && git init
```

### Remote sync

If no remote is configured, use the `private_repo` skill to create or connect a private GitHub repo for `~/claude/memory/`.

## When the User Asks

- "Remember this..." or "Save this..." -> Use the `note` command, then git commit
- "What did we discuss..." or "What do you know about..." -> Use `search` or `show`
- "Summarize recent work..." -> Use `aggregate` then read memory.md
