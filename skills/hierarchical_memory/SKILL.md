---
name: hierarchical_memory
description: >
  Manage a simple hierarchical memory system stored as markdown files.
  Use when the user wants to save a note, recall past context, review
  what was discussed previously, or aggregate learnings over time.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(uv run *), Bash(git *), Read, Write, Glob
---

Manage notes in hierarchical memory at `$CLAUDE_OBSIDIAN_DIR/memory/` (default: `~/claude/obsidian/memory/`).

Set `CLAUDE_OBSIDIAN_DIR` to change the vault root. All paths derive from it.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `note "text"` | Append timestamped line to today, report aggregation staleness |
| `list` | List all memory files with type and date |
| `read-day [YYYY-MM-DD]` | Output a day's content (default: today) |
| `read-days START [END]` | Output multiple days (range or `--last N`) |
| `read-month [YYYY-MM]` | Output a month's summary (default: current) |
| `read-months START [END]` | Output multiple months (range or `--last N`) |
| `read-overall` | Output overall_memory.md |
| `read-current` | Output overall + current month + today in one call |
| `status` | Show aggregation staleness |

## Commands

All commands:
```bash
uv run --directory SKILL_DIR python scripts/memory.py <command> [args]
```

Where `SKILL_DIR` is the directory containing this skill.

### Save a note
```bash
uv run --directory SKILL_DIR python scripts/memory.py note "Your note text here"
```
Appends: `- **TIMESTAMP** [hostname:reponame]: TEXT` to today's daily file. Prints a staleness one-liner after saving — e.g. `Aggregation stale: 2026-02 CREATE, overall UPDATE` or `Aggregation: up to date`.

### Readers

Three focused readers, two multi-readers, and one convenience shortcut:

```bash
# Read a specific day (default: today)
uv run --directory SKILL_DIR python scripts/memory.py read-day 2026-02-10

# Read multiple days (range)
uv run --directory SKILL_DIR python scripts/memory.py read-days 2026-02-10 2026-02-14

# Read last 7 days
uv run --directory SKILL_DIR python scripts/memory.py read-days --last 7

# Read a monthly summary (default: current month)
uv run --directory SKILL_DIR python scripts/memory.py read-month 2026-02

# Read multiple months (range)
uv run --directory SKILL_DIR python scripts/memory.py read-months 2026-01 2026-02

# Read last 3 months
uv run --directory SKILL_DIR python scripts/memory.py read-months --last 3

# Read overall memory
uv run --directory SKILL_DIR python scripts/memory.py read-overall

# Read everything current (overall + month + today) in one call
uv run --directory SKILL_DIR python scripts/memory.py read-current
```

### List files
```bash
uv run --directory SKILL_DIR python scripts/memory.py list
```
Shows all memory files with type (daily/monthly/overall/unknown) and modification date. Warns on unknown files.

### Check aggregation status
```bash
uv run --directory SKILL_DIR python scripts/memory.py status
```
Shows which monthly summaries need creating or updating, overall memory staleness, and knowledge graph contents.

## File Structure

```
$CLAUDE_OBSIDIAN_DIR/memory/
├── overall_memory.md    # Overall working memory (synthesized from monthly)
├── 2026-02.md           # Monthly summary (sortable YYYY-MM)
├── 2026-02-08.md        # Daily notes (append-only)
└── ...
```

## Memory Hierarchy

| Level | Purpose | Freedom |
|-------|---------|---------|
| **Lines** | Raw capture. Append-only, no judgment. | None |
| **Daily** (`YYYY-MM-DD.md`) | Container for a day's notes. | None |
| **Monthly** (`YYYY-MM.md`) | Compress: what mattered this month? | High |
| **Overall** (`overall_memory.md`) | Synthesize: current state of the world. | Highest |

## Memory Search Guidance

| Need | Source | Why |
|------|--------|-----|
| Big picture facts, preferences, context | `overall_memory.md` | Synthesized, compressed — current state of the world |
| Time period context | `YYYY-MM.md` | Themed detail for a specific month |
| Specific details | `YYYY-MM-DD.md` | Raw, unfiltered daily entries |
| Curated knowledge | `$CLAUDE_OBSIDIAN_DIR/knowledge_graph/` | Durable topic notes, personal knowledge base |

For keyword search, use Grep/Glob directly on the memory directory:

```bash
# Find memory files by name pattern
Glob("$CLAUDE_OBSIDIAN_DIR/memory/*.md")

# Search memory contents for a keyword
Grep(pattern="search term", path="$CLAUDE_OBSIDIAN_DIR/memory/")
```

## Aggregation

Always run `status` first to see what needs work. Then launch sub-agents only for months that need CREATE or UPDATE.

### Monthly summary

Launch a sub-agent for each month that needs CREATE or UPDATE:

> Read all daily notes in `$CLAUDE_OBSIDIAN_DIR/memory/` for YYYY-MM. Write a monthly summary to `$CLAUDE_OBSIDIAN_DIR/memory/YYYY-MM.md`. Include: key decisions, important events, learnings, and any facts that changed (new job, new tools, new preferences). Drop noise (test notes, trivial observations, routine operations). Organize by theme, not by date. More recent notes take priority over older ones. Tag each theme with `#topic` tags (e.g. `#skills`, `#architecture`, `#debugging`). Include `[[obsidian links]]` to related vault notes where appropriate. Keep it concise.

### Overall working memory

Launch a sub-agent only if `status` shows overall needs CREATE or UPDATE:

> Read all monthly summaries in `$CLAUDE_OBSIDIAN_DIR/memory/` chronologically. Write `$CLAUDE_OBSIDIAN_DIR/memory/overall_memory.md` as a current-state working memory. Rules: (1) Facts use last-write-wins — if the user changed jobs, reflect only the current employer. (2) Key learnings and preferences persist across time. (3) Events compress — keep milestones, drop details. (4) The result should read like a living profile: big picture facts, preferences, context, and knowledge — "here is what I know about this user and their world right now." Not a changelog. Not granular details unless truly important. (5) Tag each section with `#topic` tags for obsidian graph discoverability. (6) Include `[[obsidian links]]` to related vault notes.

### When to aggregate

The `note` command reports staleness after each save. Finish all your notes first, then aggregate any stale months/overall in one pass. The `status` command still exists for manual inspection with full detail.

## Fact Freshness

Memory is a snapshot, not a live feed. When relying on a fact, consider its **information velocity** — how fast that kind of fact typically changes:

- **Fast** (weeks): current project, active tasks, what someone is working on right now
- **Medium** (months): tool preferences, workflows, team structure
- **Slow** (years): employer, location, core skills, long-term preferences

If a fact's age exceeds its expected velocity, ask the user to confirm before relying on it. Don't be annoying — just be aware that a 6-month-old "current project" is almost certainly stale, while a 6-month-old employer is probably fine.

## Git Integration

After saving notes or aggregating, commit and push. Use `git -C` to avoid `cd` (matches the `Bash(git *)` permission):

```bash
git -C $CLAUDE_OBSIDIAN_DIR add -A && git -C $CLAUDE_OBSIDIAN_DIR commit -m "memory update" && git -C $CLAUDE_OBSIDIAN_DIR push
```

If no remote is configured, use the `private_repo` skill to set one up.
