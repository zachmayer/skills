#!/bin/bash
# Heartbeat: Periodically invoke Claude Code to process pending tasks.
# Designed for macOS launchd user agent execution.
set -euo pipefail

# --- Configuration ---
OBSIDIAN_DIR="${CLAUDE_OBSIDIAN_DIR:-$HOME/claude/obsidian}"
OBSIDIAN_DIR="${OBSIDIAN_DIR/#\~/$HOME}"
SKILLS_REPO="${HEARTBEAT_REPO:-$HOME/source/skills}"
TASKS_FILE="$OBSIDIAN_DIR/heartbeat/tasks.md"
LOCK_FILE="$HOME/.claude/heartbeat.lock"
STATUS_FILE="$HOME/.claude/heartbeat.status"
LOG_DIR="$OBSIDIAN_DIR/heartbeat"
TIMEOUT_SECONDS=14400  # 4 hour hard kill
WORK_MINUTES=30        # target work time per cycle
MAX_TURNS=200
MAX_BUDGET_USD=5

# --- PATH for launchd (doesn't source shell profile) ---
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# --- Auth: Use subscription via OAuth token ---
# Explicitly unset API key so claude uses CLAUDE_CODE_OAUTH_TOKEN (subscription billing).
# Without this, ANTHROPIC_API_KEY from the env would take priority.
unset ANTHROPIC_API_KEY 2>/dev/null || true

# Source the heartbeat env file for CLAUDE_CODE_OAUTH_TOKEN
ENV_FILE="$HOME/.claude/heartbeat.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: Missing $ENV_FILE. Run: make setup-heartbeat-token"
    exit 1
fi

perms=$(stat -f '%Lp' "$ENV_FILE" 2>/dev/null || stat -c '%a' "$ENV_FILE" 2>/dev/null)
if [ "$perms" != "600" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: $ENV_FILE has mode $perms, expected 600"
    exit 1
fi
# shellcheck source=/dev/null
source "$ENV_FILE"

if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: CLAUDE_CODE_OAUTH_TOKEN not set in $ENV_FILE"
    exit 1
fi

# --- Pre-flight auth check ---
if ! claude auth status >/dev/null 2>&1; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: Auth check failed. Token may be expired. Run: make setup-heartbeat-token"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FAIL auth_expired" > "$STATUS_FILE"
    exit 1
fi

# --- Ensure directories exist ---
mkdir -p "$(dirname "$LOCK_FILE")" "$LOG_DIR"

# --- Prevent overlapping runs ---
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Skipping: previous run (PID $pid) still active"
        exit 0
    fi
    rm -f "$LOCK_FILE"
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# --- Check for pending tasks ---
if [ ! -f "$TASKS_FILE" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No task file at $TASKS_FILE"
    exit 0
fi

open=$(grep -c '^\s*- \[ \]' "$TASKS_FILE" 2>/dev/null || echo "0")
in_progress=$(grep -c '^\s*- \[~\]' "$TASKS_FILE" 2>/dev/null || echo "0")
if [ "$open" = "0" ] && [ "$in_progress" = "0" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No open or in-progress tasks"
    exit 0
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $open open + $in_progress in-progress task(s). Invoking Claude Code..."

# --- Invoke Claude Code with safety bounds ---
# Run in a subshell with a watchdog timer for portability (macOS lacks `timeout` by default).
# --max-turns and --max-budget-usd provide Claude-level bounds; the watchdog catches hangs.
set +e
(
    cd "$SKILLS_REPO"
    exec claude --print \
        --permission-mode dontAsk \
        --add-dir "$OBSIDIAN_DIR" \
        --allowedTools Read Write Edit Glob Grep \
            "Bash(git status)" "Bash(git diff *)" "Bash(git log *)" \
            "Bash(git add *)" "Bash(git commit *)" \
            "Bash(git checkout *)" "Bash(git branch *)" "Bash(git push *)" \
            "Bash(git pull *)" "Bash(git fetch *)" \
            "Bash(git -C *)" \
            "Bash(gh pr create *)" "Bash(gh pr view *)" \
            "Bash(ls *)" "Bash(mkdir *)" "Bash(date *)" \
            "Bash(uv run python *)" \
        --max-turns "$MAX_TURNS" \
        --max-budget-usd "$MAX_BUDGET_USD" \
        --model sonnet \
        "Use your heartbeat skill. Task file: $TASKS_FILE. Obsidian dir: $OBSIDIAN_DIR. Time limit: $WORK_MINUTES minutes. Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)."
) &
claude_pid=$!

# Watchdog: kill claude after timeout, then force-kill stragglers
(
    sleep "$TIMEOUT_SECONDS"
    kill "$claude_pid" 2>/dev/null
    sleep 10
    kill -9 "$claude_pid" 2>/dev/null
) &
watchdog_pid=$!

wait "$claude_pid" 2>/dev/null
exit_code=$?

# Cancel watchdog
kill "$watchdog_pid" 2>/dev/null
wait "$watchdog_pid" 2>/dev/null
set -e

# --- Record outcome ---
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ $exit_code -eq 0 ]; then
    echo "$timestamp OK" > "$STATUS_FILE"
    echo "[$timestamp] Heartbeat cycle complete"
elif [ $exit_code -eq 137 ] || [ $exit_code -eq 143 ]; then
    echo "$timestamp TIMEOUT" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude exited with code $exit_code"
fi

exit 0
