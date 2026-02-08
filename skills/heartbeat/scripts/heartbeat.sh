#!/bin/bash
# Heartbeat: Periodically invoke Claude Code to process pending tasks.
# Designed to be run via cron. See the heartbeat skill SKILL.md for setup.
set -euo pipefail

TASKS_FILE="${CLAUDE_HEARTBEAT_TASKS:-$HOME/.claude/heartbeat/tasks.md}"
LOCK_FILE="/tmp/claude-heartbeat.lock"
LOG_PREFIX="[$(date -u +%Y-%m-%dT%H:%M:%SZ)]"

# Prevent overlapping runs
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "$LOG_PREFIX Skipping: previous run (PID $pid) still active"
        exit 0
    fi
    # Stale lock file, remove it
    rm -f "$LOCK_FILE"
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# Check for task file
if [ ! -f "$TASKS_FILE" ]; then
    echo "$LOG_PREFIX No task file at $TASKS_FILE"
    exit 0
fi

# Check for pending tasks (unchecked checkboxes)
pending=$(grep -c '^\s*- \[ \]' "$TASKS_FILE" 2>/dev/null || echo "0")
if [ "$pending" = "0" ]; then
    echo "$LOG_PREFIX No pending tasks"
    exit 0
fi

echo "$LOG_PREFIX Found $pending pending task(s). Invoking Claude Code..."

# Invoke Claude Code in non-interactive mode
claude --print \
    "You are running as an autonomous heartbeat agent. Read the task file at $TASKS_FILE. Process the first unchecked task (marked with '- [ ]'). After completing a task, mark it as done by changing '- [ ]' to '- [x] TIMESTAMP:' with the current ISO timestamp, and move it to the Completed section. Only process ONE task per heartbeat cycle. If a task requires human input, skip it and note why." \
    2>&1

echo "$LOG_PREFIX Heartbeat cycle complete"
