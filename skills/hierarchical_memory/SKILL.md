---
name: hierarchical_memory
description: >
  Manage a simple hierarchical memory system stored as markdown files.
  Use when the user wants to save a note, recall past context, review
  what was discussed previously, or aggregate learnings over time.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(uv run *), Bash(git *), Read, Write, Glob
---

Manage notes in the hierarchical memory at `~/claude/obsidian/memory/`.

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

### Search notes
```bash
uv run --directory SKILL_DIR python scripts/memory.py search "query"
```

### Check aggregation status
```bash
uv run --directory SKILL_DIR python scripts/memory.py status
```
Shows which monthly summaries need creating or updating, overall memory staleness, and obsidian vault contents.

Where `SKILL_DIR` is the directory containing this skill.

## File Structure

```
~/claude/obsidian/memory/
├── memory.md           # Overall working memory (synthesized from monthly)
├── 2026-02.md          # Monthly summary (sortable YYYY-MM)
├── 2026-02-08.md       # Daily notes (append-only)
└── ...
```

## Memory Hierarchy

| Level | Purpose | Freedom |
|-------|---------|---------|
| **Lines** | Raw capture. Append-only, no judgment. | None |
| **Daily** (`YYYY-MM-DD.md`) | Container for a day's notes. | None |
| **Monthly** (`YYYY-MM.md`) | Compress: what mattered this month? | High |
| **Overall** (`memory.md`) | Synthesize: current state of the world. | Highest |

## Memory Search Guidance

| Need | Source | Why |
|------|--------|-----|
| Big picture facts, preferences, context | `memory.md` | Synthesized, compressed — current state of the world |
| Time period context | `YYYY-MM.md` | Themed detail for a specific month |
| Specific details | `YYYY-MM-DD.md` | Raw, unfiltered daily entries |
| Curated knowledge | `~/claude/obsidian/Zach/` | Durable topic notes, personal knowledge base |

## Aggregation

Always run `status` first to see what needs work. Then launch sub-agents only for months that need CREATE or UPDATE.

### Monthly summary

Launch a sub-agent for each month that needs CREATE or UPDATE:

> Read all daily notes in `~/claude/obsidian/memory/` for YYYY-MM. Write a monthly summary to `~/claude/obsidian/memory/YYYY-MM.md`. Include: key decisions, important events, learnings, and any facts that changed (new job, new tools, new preferences). Drop noise (test notes, trivial observations, routine operations). Organize by theme, not by date. More recent notes take priority over older ones. Tag each theme with `#topic` tags (e.g. `#skills`, `#architecture`, `#debugging`). Include `[[obsidian links]]` to related vault notes where appropriate. Keep it concise.

### Overall working memory

Launch a sub-agent only if `status` shows overall needs CREATE or UPDATE:

> Read all monthly summaries in `~/claude/obsidian/memory/` chronologically. Write `~/claude/obsidian/memory/memory.md` as a current-state working memory. Rules: (1) Facts use last-write-wins — if the user changed jobs, reflect only the current employer. (2) Key learnings and preferences persist across time. (3) Events compress — keep milestones, drop details. (4) The result should read like a living profile: big picture facts, preferences, context, and knowledge — "here is what I know about this user and their world right now." Not a changelog. Not granular details unless truly important. (5) Tag each section with `#topic` tags for obsidian graph discoverability. (6) Include `[[obsidian links]]` to related vault notes.

### When to aggregate

- After a significant session (many notes added)
- When the user asks to summarize recent work
- Periodically via the `heartbeat` skill

## Fact Freshness

Key facts in `memory.md` can go stale — jobs change, preferences evolve, projects wind down. When relying on a fact from memory that seems like it could have changed (employment, location, active projects, tool preferences), consider asking the user to confirm it's still current rather than assuming. This is especially true for facts that are months old. Don't be annoying about it — just be aware that memory is a snapshot, not a live feed.

## Git Integration

After saving notes or aggregating, commit and push. Use `git -C` to avoid `cd` (matches the `Bash(git *)` permission):

```bash
git -C ~/claude/obsidian add -A && git -C ~/claude/obsidian commit -m "memory update" && git -C ~/claude/obsidian push
```

If no remote is configured, use the `private_repo` skill to set one up.
