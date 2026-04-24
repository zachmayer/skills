---
name: knowledge-system
description: >
  Persistent knowledge management for Obsidian vault, notes, memories,
  reminders, and vault maintenance. Use when the user wants to save, recall,
  search, aggregate, link, organize, or clean up knowledge base/vault/memory
  information. Triggers: obsidian, vault, knowledge base, knowledge graph,
  remember this, save to vault, save a note, save this, capture this, inbox,
  route/file/log/note this, note this down, create a note,
  daily/monthly/overall memory, what do you know/remember about X, recall,
  what did we discuss, what do I have on, aggregate memories, check memory,
  find/search my notes/vault, link notes, organize knowledge, MOC, map of
  content, wiki-links, remind me, set a reminder, don't let me forget,
  follow up on, vault maintenance, tidy up, clean the vault, run maintenance,
  staleness, stale/orphan notes, broken links. Do NOT use for code docs
  (CLAUDE.md, AGENTS.md), codebase behavior (use staff-engineer), live status,
  or session briefings/wrap-ups (use session-lifecycle).
allowed-tools: Bash(uv run *), Bash(git *), Bash(gh *), Bash(obsidian *), Read, Write, Glob, Grep
---

# Knowledge System

Unified entry point for all knowledge management. Route to the right sub-skill.

## Vault Location

The vault path comes from `$CLAUDE_OBSIDIAN_DIR`. **Do not search for it** -- use this env var directly. Do NOT fall back to `mdfind`, `find`, `Glob`, or any other discovery method.

**If `$CLAUDE_OBSIDIAN_DIR` is empty or unset, HARD FAIL.** Do not proceed with any vault operation. Tell the user verbatim:

> `CLAUDE_OBSIDIAN_DIR` is not set. Add this to your `~/.zshrc`:
>
> ```
> export CLAUDE_OBSIDIAN_DIR="$HOME/path/to/your/obsidian/vault"
> ```
>
> Then restart your shell and Claude Code.
>
> Note: `settings.json` env values do NOT expand `$HOME` or `~` (see anthropics/claude-code#21551, closed Not Planned). Use shell profile instead.

Then stop. Do not guess a path, do not search the filesystem, do not proceed.

### Vault structure

```
$CLAUDE_OBSIDIAN_DIR/
├── memory/                      # Hierarchical memory (daily/monthly/overall notes)
│   ├── overall_memory.md        # Synthesized working memory -- current state of the world
│   ├── YYYY-MM.md               # Monthly summaries (e.g. 2026-02.md)
│   └── YYYY-MM-DD.md            # Daily notes -- append-only raw capture
├── knowledge_graph/             # Durable topic notes organized as nested MOCs
│   ├── Home.md                  # Top-level MOC index
│   ├── AI.md                    # AI topics MOC
│   ├── Technical/               # Technical knowledge (tools, APIs, architecture)
│   ├── Personal/                # Personal notes and preferences
│   ├── Work/                    # Work and consulting notes
│   ├── Articles/                # Saved articles and web grabs
│   └── Briefings/               # Research briefings
├── heartbeat/                   # Heartbeat agent workspace
└── research/                    # Research outputs
```

## Quick Lookup

| Need | Reference file | When |
|------|---------------|------|
| **Route input to the right place** | [capture.md](capture.md) | "capture this", "inbox", "file this", unknown destination |
| **Save/read/aggregate memory** | [hierarchical-memory.md](hierarchical-memory.md) | "remember this", "recall", "what did we discuss", "check memory", "daily note", "monthly note", "aggregate" |
| **Obsidian vault notes** | [obsidian.md](obsidian.md) | "save a note", "find my notes on", "search my vault", "knowledge graph", wiki-links, MOC |
| **Time-based reminders** | [reminders.md](reminders.md) | "remind me", "set a reminder", "don't let me forget", "follow up on" |
| **Vault/repo maintenance** | [evergreen.md](evergreen.md) | "tidy up", "clean the vault", "prune branches", "run maintenance", "staleness", "orphan notes" |

## Sub-skills

- **capture** -- Smart inbox that classifies input by durability/scope/audience and routes to memory, obsidian, GitHub Issues, CLAUDE.md, or README.md.
- **hierarchical-memory** -- Daily/monthly/overall memory hierarchy with CLI. Scripts in `scripts/memory.py`.
- **obsidian** -- Read, write, search, and link notes in a git-backed Obsidian vault. Supports Obsidian CLI and direct file ops.
- **reminders** -- Time-aware reminders stored in the obsidian vault's memory directory.
- **evergreen** -- Periodic housekeeping: orphan notes, broken links, missing metadata, stale aggregations, merged branches.

## General rules

**Always commit and push `$CLAUDE_OBSIDIAN_DIR` after any write operation** -- note saves, aggregation updates, obsidian notes, reminders. Changes that aren't committed and pushed don't sync. See [hierarchical-memory.md](hierarchical-memory.md#git-integration) for the commands.

**To-do items go in the vault's `README.md`, not in individual notes.** The vault README has a `## Todo` section that is the single source of truth for action items. To-dos scattered across individual Obsidian notes get lost -- they're invisible unless you happen to open that specific note. Individual notes may have note-specific follow-ups (e.g. "after Sept 15, decide whether to sell"), but anything that needs to be tracked and acted on should be in the README todo list. When creating or updating notes, move any actionable to-dos to the README and link back to the note for context.

## Related skills (not managed here)

- **session-lifecycle** -- Session start/plan/wrap-up (daily-briefing, session-planner, remember-session). Uses this skill's memory scripts.
