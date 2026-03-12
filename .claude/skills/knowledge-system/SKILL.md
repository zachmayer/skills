---
name: knowledge-system
description: >
  Persistent knowledge management for discrete notes, memories, reminders, and
  vault maintenance. Use when the user wants to save or recall a specific fact,
  decision, learning, note, or follow-up from memory, notes, or the vault.
  Triggers: "capture this", "save this", "inbox", "route this", "file this",
  "remember this", "remember this for later", "log this", "note this down",
  "save a note", "what do you know about X from our notes", "what do you
  remember about X", "recall", "what did we discuss", "what do I have on",
  "aggregate memories", "check memory", "find my notes on", "create a note",
  "search my vault", "add to my knowledge base", "link notes", "organize
  knowledge", "remind me", "set a reminder", "don't let me forget", "follow
  up on", "tidy up", "clean the vault", "prune branches", "run maintenance",
  or mentions vault, wiki-links, MOC, or Obsidian. Do NOT use for code-specific
  documentation (CLAUDE.md, AGENTS.md), codebase questions about how code works
  (use staff-engineer), live status questions, or session-wide briefings and
  wrap-ups like "remember this session" or "save what we did today" (use
  session-lifecycle for those).
allowed-tools: Bash(uv run *), Bash(git *), Bash(gh *), Bash(obsidian *), Read, Write, Glob, Grep
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
