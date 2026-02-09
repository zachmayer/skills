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

## Memory Hierarchy

Each level serves a distinct purpose:

| Level | Purpose | Freedom |
|-------|---------|---------|
| **Lines** | Raw capture. Append-only, no judgment. | None |
| **Daily** (`YYYY-MM-DD.md`) | Container for a day's notes. | None |
| **Monthly** (`YYYY-MM.md`) | Compress: what mattered this month? | High |
| **Overall** (`memory.md`) | Synthesize: current state of the world. | Highest |

## Aggregation

The `aggregate` command does a mechanical rollup. For intelligent summarization, use a sub-agent.

### Monthly summary sub-agent

Launch a sub-agent to read all daily files for a month and write the monthly summary:

> Read all daily notes in `~/claude/memory/` for YYYY-MM. Write a monthly summary to `~/claude/memory/YYYY-MM.md`. Include: key decisions, important events, learnings, and any facts that changed (new job, new tools, new preferences). Drop noise (test notes, trivial observations, routine operations). Organize by theme, not by date. Keep it concise.

### Overall memory sub-agent

Launch a sub-agent to read all monthly summaries and write the overall memory:

> Read all monthly summaries in `~/claude/memory/` chronologically. Write `~/claude/memory/memory.md` as a current-state working memory. Rules: (1) Facts use last-write-wins — if the user changed jobs, reflect only the current employer. (2) Key learnings and preferences persist across time. (3) Events compress — keep milestones, drop details. (4) The result should read like a living profile: "here is what I know about this user and their world right now." Not a changelog.

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
