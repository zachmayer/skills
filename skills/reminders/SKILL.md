---
name: reminders
description: >
  Time-aware reminders. Use when the user wants to be reminded of something
  at a future date/time. Do NOT use for immediate tasks (use TodoWrite) or
  persistent notes (use hierarchical_memory).
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
