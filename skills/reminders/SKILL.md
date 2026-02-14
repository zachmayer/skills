---
name: reminders
description: >
  Time-aware reminder system. Set reminders for the user (or the agent itself).
  Heartbeat checks for due reminders on each cycle and surfaces them.
  Use when the user wants to be reminded of something at a future date/time,
  or when the agent needs to schedule follow-up tasks.
  Do NOT use for immediate tasks (use TodoWrite) or for persistent notes (use hierarchical_memory).
allowed-tools: Bash(uv run *), Read, Write, Glob
---

Manage time-aware reminders stored in `$CLAUDE_OBSIDIAN_DIR/memory/reminders.json` (default: `~/claude/obsidian/memory/`).

Set `CLAUDE_OBSIDIAN_DIR` to change the vault root. All paths derive from it.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `add "text" YYYY-MM-DD` | Create a reminder with a due date |
| `add "text" YYYY-MM-DDTHH:MM` | Create a reminder with due date and time |
| `list` | Show active reminders |
| `list --all` | Show all reminders including completed |
| `due` | Show reminders that are due or overdue right now |
| `complete ID` | Mark a reminder as done (8-char short ID) |
| `remove ID` | Delete a reminder permanently (8-char short ID) |

## Commands

All commands:
```bash
uv run --directory SKILL_DIR python scripts/reminders.py <command> [args]
```

Where `SKILL_DIR` is the directory containing this skill.

### Add a reminder
```bash
# Due on a specific date (midnight)
uv run --directory SKILL_DIR python scripts/reminders.py add "Review PR #42" 2026-02-20

# Due at a specific time
uv run --directory SKILL_DIR python scripts/reminders.py add "Team standup" 2026-02-15T09:00
```

### Check what's due
```bash
# Show overdue and currently-due reminders
uv run --directory SKILL_DIR python scripts/reminders.py due
```

### List reminders
```bash
# Active only (default)
uv run --directory SKILL_DIR python scripts/reminders.py list

# Include completed
uv run --directory SKILL_DIR python scripts/reminders.py list --all
```

### Complete a reminder
```bash
# Use the 8-character short ID shown in list/due output
uv run --directory SKILL_DIR python scripts/reminders.py complete a1b2c3d4
```

### Remove a reminder
```bash
uv run --directory SKILL_DIR python scripts/reminders.py remove a1b2c3d4
```

## Heartbeat Integration

On each heartbeat cycle, run the `due` command to check for reminders that need attention:

```bash
uv run --directory SKILL_DIR python scripts/reminders.py due
```

If reminders are due, surface them to the user or take action as appropriate. The heartbeat skill should call `due` early in its cycle so overdue items are visible.

## Storage Format

Reminders are stored as a JSON array in `reminders.json`:

```json
[
  {
    "id": "hex-uuid",
    "text": "Review PR #42",
    "due": "2026-02-20T00:00:00",
    "created": "2026-02-14T11:00:00",
    "completed": false
  }
]
```

## Git Integration

After modifying reminders, commit and push the obsidian vault:

```bash
git -C $CLAUDE_OBSIDIAN_DIR add -A && git -C $CLAUDE_OBSIDIAN_DIR commit -m "reminders update" && git -C $CLAUDE_OBSIDIAN_DIR push
```
