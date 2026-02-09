---
name: heartbeat
description: >
  Set up or run a cron-based heartbeat that periodically invokes Claude Code
  to check for and process pending tasks. Use when the user wants autonomous
  periodic task processing or asks about running Claude on a schedule.
  Do NOT use for one-time tasks or interactive work.
allowed-tools: Bash(*)
---

Set up or manage a heartbeat for autonomous Claude Code task processing.

Also apply `hierarchical_memory` and `obsidian` for reading context and persisting results.

## Setup

### 1. Create the task file

Tasks live in the obsidian vault at `~/claude/obsidian/heartbeat/tasks.md`:

```bash
mkdir -p ~/claude/obsidian/heartbeat
cat > ~/claude/obsidian/heartbeat/tasks.md << 'EOF'
# Heartbeat Tasks

Tasks for Claude to process on each heartbeat cycle. Before processing, read today's memory notes and decide the highest-value activity.

## Pending

- [ ] Example: Check for new GitHub issues in myrepo

## Completed

EOF
```

### 2. Add a cron entry

```bash
# Add heartbeat cron (runs every 4 hours)
(crontab -l 2>/dev/null; echo "0 */4 * * * SKILL_DIR/scripts/heartbeat.sh >> ~/claude/obsidian/heartbeat/heartbeat.log 2>&1") | crontab -
```

Verify with `crontab -l`.

## Heartbeat Behavior

On each cycle, the heartbeat agent should:
1. Read today's memory notes (`~/claude/obsidian/memory/`) for context
2. Read the task queue for pending items
3. Decide: is there a high-value task, or should it save its powder and wait?
4. If it has a question for the user, write it to `~/claude/obsidian/heartbeat/questions.md`
5. Process at most ONE task per cycle, then commit to the obsidian repo

## Task Queue

Edit `~/claude/obsidian/heartbeat/tasks.md` — add tasks as `- [ ] description` under Pending, completed tasks get marked `- [x] timestamp: description` and moved to Completed.

## Managing

- **Check log**: `tail -20 ~/claude/obsidian/heartbeat/heartbeat.log`
- **Pause**: `crontab -l | sed '/heartbeat/s|^|#|' | crontab -`
- **Stop**: `crontab -l | grep -v heartbeat | crontab -`
