---
name: knowledge-system
description: >
  Persistent knowledge management for the Obsidian vault, notes, memories,
  reminders, and vault maintenance. Use when the user wants to save, recall,
  search, or organize information in the knowledge base, vault, or memory.
  Triggers: "obsidian", "vault", "knowledge base", "knowledge graph",
  "remember", "remember this", "remember this for later", "save to vault",
  "save a note", "save this", "capture this", "inbox", "route this",
  "file this", "log this", "note this down", "create a note", "daily note",
  "monthly note", "overall memory", "what do you know about X from our notes",
  "what do you remember about X", "recall", "what did we discuss",
  "what do I have on", "aggregate", "aggregate memories", "aggregation",
  "check memory", "find my notes on", "search my vault", "search notes",
  "add to my knowledge base", "link notes", "organize knowledge", "MOC",
  "map of content", "wiki-links", "remind me", "set a reminder",
  "don't let me forget", "follow up on", "vault maintenance", "tidy up",
  "clean the vault", "prune branches", "run maintenance", "staleness",
  "stale notes", "orphan notes", "broken links". Also triggers on any
  mention of the obsidian vault path or knowledge_graph directory.
  Do NOT use for code-specific documentation (CLAUDE.md, AGENTS.md),
  codebase questions about how code works (use staff-engineer), live status
  questions, or session-wide briefings and wrap-ups like "remember this
  session" or "save what we did today" (use session-lifecycle for those).
allowed-tools: Bash(uv run *), Bash(git *), Bash(gh *), Bash(obsidian *), Read, Write, Glob, Grep
---

# Knowledge System

Unified entry point for all knowledge management. Route to the right sub-skill.

## Vault Location

**The Obsidian vault is at `/Users/zach/claude/obsidian/`** (also `$CLAUDE_OBSIDIAN_DIR`). Do not search for it -- use this path directly.

```
/Users/zach/claude/obsidian/
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
│   ├── Briefings/               # Research briefings
│   ├── March_Madness/           # March Madness analysis
│   └── Prompts.md               # Prompt engineering notes
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

## General rule

**Always commit and push `$CLAUDE_OBSIDIAN_DIR` after any write operation** -- note saves, aggregation updates, obsidian notes, reminders. Changes that aren't committed and pushed don't sync. See [hierarchical-memory.md](hierarchical-memory.md#git-integration) for the commands.

## Related skills (not managed here)

- **session-lifecycle** -- Session start/plan/wrap-up (daily-briefing, session-planner, remember-session). Uses this skill's memory scripts.
