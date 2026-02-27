#!/bin/bash
# Heartbeat wrapper: env setup, auth validation, watchdog, then Python.
set -euo pipefail

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

# --- Watchdog: kill the entire process group after 4 hours ---
TIMEOUT_SECONDS=14400
(
    trap '' TERM
    sleep "$TIMEOUT_SECONDS"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] TIMEOUT: killing process group after ${TIMEOUT_SECONDS}s" >&2
    kill -- -$$ 2>/dev/null
    sleep 10
    kill -9 -- -$$ 2>/dev/null
) &
watchdog_pid=$!
trap "kill -9 $watchdog_pid 2>/dev/null; wait $watchdog_pid 2>/dev/null" EXIT

# --- Run Python ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run python "$SCRIPT_DIR/heartbeat.py"
