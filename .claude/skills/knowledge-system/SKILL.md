---
name: knowledge-system
description: >
  Unified knowledge management: memory, notes, capture, reminders, and maintenance.
  Use when the user says "capture this", "save this", "inbox", "route this",
  "file this", "remember this", "log this", "note this down", "save a note",
  "what do you know about me", "recall", "what did we discuss", "aggregate memories",
  "check memory", "find my notes on", "create a note", "search my vault",
  "add to my knowledge base", "what do I have on", "remind me", "set a reminder",
  "don't let me forget", "follow up on", "tidy up", "clean the vault",
  "prune branches", "run maintenance", or mentions vault, wiki-links, MOC,
  Obsidian, or wants to persist context across sessions. Also use when the user
  references past conversations or wants to review previous learnings.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(uv run *), Bash(git *), Bash(obsidian *), Read, Write, Glob, Grep
---

# Knowledge System

Unified entry point for all knowledge management. Route to the right sub-skill.

## Quick Lookup

| Need | Reference file | When |
|------|---------------|------|
| **Route input to the right place** | [capture.md](capture.md) | "capture this", "inbox", "file this", unknown destination |
| **Save/read/aggregate memory** | [hierarchical-memory.md](hierarchical-memory.md) | "remember this", "recall", "what did we discuss", "check memory" |
| **Obsidian vault notes** | [obsidian.md](obsidian.md) | "save a note", "find my notes on", "search my vault", wiki-links, MOC |
| **Time-based reminders** | [reminders.md](reminders.md) | "remind me", "set a reminder", "don't let me forget", "follow up on" |
| **Vault/repo maintenance** | [evergreen.md](evergreen.md) | "tidy up", "clean the vault", "prune branches", "run maintenance" |

## Sub-skills

- **capture** -- Smart inbox that classifies input by durability/scope/audience and routes to memory, obsidian, GitHub Issues, CLAUDE.md, or README.md.
- **hierarchical-memory** -- Daily/monthly/overall memory hierarchy with CLI. Scripts in `scripts/memory.py`.
- **obsidian** -- Read, write, search, and link notes in a git-backed Obsidian vault. Supports Obsidian CLI and direct file ops.
- **reminders** -- Time-aware reminders stored in the obsidian vault's memory directory.
- **evergreen** -- Periodic housekeeping: orphan notes, broken links, missing metadata, stale aggregations, merged branches.

## Related skills (not managed here)

- **session-lifecycle** -- Session start/plan/wrap-up (daily-briefing, session-planner, remember-session). Uses this skill's memory scripts.
