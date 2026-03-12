---
name: reminders
description: >
  Creates, tracks, and surfaces time-based reminders stored in Obsidian.
  Use when the user says "remind me", "set a reminder", "don't let me forget",
  "follow up on", or mentions needing to do something at a specific future
  date or time. Also triggers on heartbeat cycles to surface overdue items.
  Do NOT use for immediate tasks (use TodoWrite) or persistent notes
  (use hierarchical-memory).
---

Store reminders in `$CLAUDE_OBSIDIAN_DIR/memory/reminders.md`.

## Format

```markdown
- [ ] Review PR #42 — due: 2026-02-20
- [ ] Team standup prep — due: 2026-02-15T09:00
- [x] Fix login bug — due: 2026-02-10
```

## Operations

- **Add**: Append a new `- [ ] text — due: YYYY-MM-DD` line
- **Complete**: Change `[ ]` to `[x]`
- **Remove**: Delete the line
- **Check due**: Read the file, compare dates to now, surface overdue items

## Heartbeat

On each cycle, read reminders.md. Surface any unchecked items where `due` is today or past.

## After changes

Commit and push the obsidian vault.
