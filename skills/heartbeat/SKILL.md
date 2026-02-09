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

## Setup

### 1. Create the heartbeat directory

```bash
mkdir -p ~/claude/heartbeat
cat > ~/claude/heartbeat/tasks.md << 'EOF'
# Heartbeat Tasks

Tasks for Claude to process on each heartbeat cycle.

## Pending

- [ ] Example: Check for new GitHub issues in myrepo

## Completed

EOF
```

### 2. Add a cron entry

```bash
# Add heartbeat cron (runs every 4 hours)
(crontab -l 2>/dev/null; echo "0 */4 * * * SKILL_DIR/scripts/heartbeat.sh >> ~/claude/heartbeat/heartbeat.log 2>&1") | crontab -
```

Verify with `crontab -l`.

## Task Queue

Edit `~/claude/heartbeat/tasks.md` — add tasks as `- [ ] description` under Pending, completed tasks get marked `- [x] timestamp: description` and moved to Completed.

## Managing

- **Check log**: `tail -20 ~/claude/heartbeat/heartbeat.log`
- **Pause**: `crontab -l | sed 's|^|#|' | crontab -`
- **Stop**: `crontab -l | grep -v heartbeat | crontab -`

If no remote is configured for `~/claude/heartbeat/`, use the `private_repo` skill to set one up.
