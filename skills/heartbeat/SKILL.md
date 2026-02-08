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

### 1. Create a task queue file

```bash
mkdir -p ~/claude/heartbeat
cat > ~/claude/heartbeat/tasks.md << 'EOF'
# Heartbeat Tasks

Tasks for Claude to process on each heartbeat cycle.
Add tasks below. Mark completed tasks with [x].

## Pending

- [ ] Example: Check for new GitHub issues in myrepo

## Completed

EOF
```

### 2. Install the heartbeat script

```bash
chmod +x SKILL_DIR/scripts/heartbeat.sh
```

### 3. Add a cron entry

```bash
# Edit crontab
crontab -e

# Add this line (runs every 15 minutes):
*/15 * * * * SKILL_DIR/scripts/heartbeat.sh >> ~/claude/heartbeat/heartbeat.log 2>&1
```

Adjust the interval as needed. Common intervals:
- `*/5 * * * *` - Every 5 minutes (aggressive)
- `*/15 * * * *` - Every 15 minutes (balanced)
- `0 * * * *` - Every hour (conservative)
- `0 9,12,17 * * *` - 9am, noon, 5pm (business hours)

## Task Queue Format

Edit `~/claude/heartbeat/tasks.md`:

```markdown
## Pending

- [ ] Check for new issues in zachmayer/myrepo and triage them
- [ ] Review open PRs that have been waiting more than 24 hours
- [ ] Run the test suite and report any failures

## Completed

- [x] 2026-02-08T10:15: Updated dependencies in project-alpha
```

## Managing the Heartbeat

- **Check status**: `cat ~/claude/heartbeat/heartbeat.log | tail -20`
- **Check tasks**: `cat ~/claude/heartbeat/tasks.md`
- **Pause**: Comment out the cron entry with `#`
- **Stop**: Remove the cron entry entirely
