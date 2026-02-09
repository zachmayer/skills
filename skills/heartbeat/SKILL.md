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

Edit `~/claude/heartbeat/tasks.md`:

```markdown
## Pending

- [ ] Check for new issues in zachmayer/myrepo and triage them
- [ ] Review open PRs that have been waiting more than 24 hours

## Completed

- [x] 2026-02-08T10:15: Updated dependencies in project-alpha
```

## Managing

- **Check log**: `tail -20 ~/claude/heartbeat/heartbeat.log`
- **Check tasks**: `cat ~/claude/heartbeat/tasks.md`
- **Pause**: `crontab -l | sed 's|^|#|' | crontab -`
- **Stop**: `crontab -l | grep -v heartbeat | crontab -`

## Git Integration

After the heartbeat processes tasks, commit and push:

```bash
cd ~/claude/heartbeat && git add -A && git commit -m "heartbeat update" && git push 2>/dev/null; true
```

### Remote sync

If no remote is configured, use the `private_repo` skill to create or connect a private GitHub repo for `~/claude/heartbeat/`.
