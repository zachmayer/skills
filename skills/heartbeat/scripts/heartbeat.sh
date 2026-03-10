#!/bin/bash
# Heartbeat: auth + watchdog wrapper for orchestrator.py.
# Designed for macOS launchd user agent execution.
#
# Handles: PATH for launchd, OAuth auth, timeout watchdog, status recording.
# Delegates: issue discovery, worktree/PR management, agent invocation → orchestrator.py.
set -euo pipefail

# --- Configuration ---
OBSIDIAN_DIR="${CLAUDE_OBSIDIAN_DIR:-$HOME/claude/obsidian}"
OBSIDIAN_DIR="${OBSIDIAN_DIR/#\~/$HOME}"
STATUS_FILE="$HOME/.claude/heartbeat.status"
TIMEOUT_SECONDS=14400  # 4 hour hard kill

# --- PATH for launchd (doesn't source shell profile) ---
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# --- Auth: Use subscription via OAuth token ---
unset ANTHROPIC_API_KEY 2>/dev/null || true

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

# --- Ensure status dir exists ---
mkdir -p "$(dirname "$STATUS_FILE")"

# --- Run orchestrator with watchdog ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting orchestrator..."
set +e
# setsid makes the orchestrator a process group leader so the watchdog
# can kill it AND all child processes (claude subprocesses) together
setsid uv run --directory "$REPO_DIR" python "$SCRIPT_DIR/orchestrator.py" &
orch_pid=$!

# Watchdog: kill orchestrator + all child processes after timeout
(
    sleep "$TIMEOUT_SECONDS"
    # Kill entire process group (orchestrator + claude subprocesses)
    kill -- -"$orch_pid" 2>/dev/null
    sleep 10
    kill -9 -- -"$orch_pid" 2>/dev/null
) &
watchdog_pid=$!

wait "$orch_pid" 2>/dev/null
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
    echo "[$timestamp] ERROR: Orchestrator killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Orchestrator exited with code $exit_code"
fi

exit 0
