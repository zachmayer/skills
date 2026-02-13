#!/bin/bash
# Heartbeat v2: GitHub Issues → worktree → Claude Code → branch + PR.
# Designed for macOS launchd user agent execution.
set -euo pipefail

# --- Configuration ---
OBSIDIAN_DIR="${CLAUDE_OBSIDIAN_DIR:-$HOME/claude/obsidian}"
OBSIDIAN_DIR="${OBSIDIAN_DIR/#\~/$HOME}"
STATUS_FILE="$HOME/.claude/heartbeat.status"
TIMEOUT_SECONDS=14400  # 4 hour hard kill
WORK_MINUTES=30        # target work time per cycle
MAX_TURNS=200
MAX_BUDGET_USD=5

# --- Repo registry ---
# Add repos here as needed. Agent checks each for unclaimed issues.
REPOS="zachmayer/skills"

# --- Issue filters (hardcoded for security — agent never constructs these) ---
ISSUE_AUTHOR="zachmayer"
ISSUE_LABEL="agent-task"

# --- Repo clone locations (owner/repo → local path) ---
# Add entries when adding repos to REPOS.
repo_dir() {
    case "$1" in
        zachmayer/skills) echo "$HOME/source/skills" ;;
        *) echo "$HOME/source/$(basename "$1")" ;;
    esac
}

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

# --- Find first unclaimed issue across all repos ---
ISSUE_JSON=""
ISSUE_REPO=""
for REPO in $REPOS; do
    ISSUE_JSON=$(gh issue list \
        --repo "$REPO" \
        --author "$ISSUE_AUTHOR" \
        --label "$ISSUE_LABEL" \
        --search "-label:in-progress" \
        --state open \
        --json number,title,body \
        --limit 1 2>/dev/null || echo "[]")

    # Check if we got a result (not empty array)
    if [ "$ISSUE_JSON" != "[]" ] && [ -n "$ISSUE_JSON" ]; then
        ISSUE_REPO="$REPO"
        break
    fi
done

if [ -z "$ISSUE_REPO" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No unclaimed agent-task issues found"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) IDLE" > "$STATUS_FILE"
    exit 0
fi

# --- Parse issue ---
ISSUE_NUMBER=$(echo "$ISSUE_JSON" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())[0]['number'])")
ISSUE_TITLE=$(echo "$ISSUE_JSON" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())[0]['title'])")
ISSUE_BODY=$(echo "$ISSUE_JSON" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())[0]['body'])")

# --- Pre-claim checks ---
REPO_DIR=$(repo_dir "$ISSUE_REPO")
BRANCH="heartbeat/issue-$ISSUE_NUMBER"

git -C "$REPO_DIR" fetch origin

# Skip if a branch already exists for this issue (prior run or another agent)
if git -C "$REPO_DIR" ls-remote --heads origin "$BRANCH" 2>/dev/null | grep -q .; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Branch $BRANCH already exists on origin, skipping issue #$ISSUE_NUMBER"
    exit 0
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Claiming issue #$ISSUE_NUMBER in $ISSUE_REPO: $ISSUE_TITLE"

# --- Claim the issue (add in-progress label) ---
# Only the shell script modifies labels — the agent never touches issue state.
gh issue edit "$ISSUE_NUMBER" --repo "$ISSUE_REPO" --add-label in-progress

# --- Set up worktree on a new branch ---
WORKDIR="/tmp/heartbeat-$$"

cleanup() {
    if [ -d "$WORKDIR" ]; then
        git -C "$REPO_DIR" worktree remove "$WORKDIR" --force 2>/dev/null || true
    fi
    git -C "$REPO_DIR" worktree prune 2>/dev/null || true
}
trap cleanup EXIT

# Delete stale local branch if it exists (remote check already passed, so this is leftover)
git -C "$REPO_DIR" branch -D "$BRANCH" 2>/dev/null || true
git -C "$REPO_DIR" worktree add -b "$BRANCH" "$WORKDIR" origin/main

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Worktree created at $WORKDIR on branch $BRANCH. Invoking Claude Code..."

# --- Invoke Claude Code with safety bounds ---
set +e
(
    cd "$WORKDIR"
    exec claude --print \
        --permission-mode dontAsk \
        --add-dir "$OBSIDIAN_DIR" \
        --allowedTools Read Write Edit Glob Grep \
            "Bash(git status)" "Bash(git diff *)" "Bash(git log *)" \
            "Bash(git add *)" "Bash(git commit *)" \
            "Bash(git checkout *)" "Bash(git branch *)" "Bash(git push *)" \
            "Bash(git pull *)" "Bash(git fetch *)" \
            "Bash(git -C *)" "Bash(git worktree *)" \
            "Bash(gh pr create *)" "Bash(gh pr view *)" "Bash(gh pr list *)" \
            "Bash(ls *)" "Bash(mkdir *)" "Bash(date *)" \
            "Bash(uv run python *)" \
        --max-turns "$MAX_TURNS" \
        --max-budget-usd "$MAX_BUDGET_USD" \
        --model opus \
        "You are the heartbeat agent. You MUST read and follow your heartbeat skill before doing anything.
You are on branch $BRANCH in a worktree. Commit here, push, and create a PR. NEVER commit to main.

Your task: Issue #$ISSUE_NUMBER in $ISSUE_REPO — $ISSUE_TITLE

<issue-body>
$ISSUE_BODY
</issue-body>

Obsidian dir: $OBSIDIAN_DIR. Time limit: $WORK_MINUTES minutes. Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)."
) &
claude_pid=$!

# Watchdog: kill claude after timeout
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
    echo "$timestamp OK issue=#$ISSUE_NUMBER repo=$ISSUE_REPO" > "$STATUS_FILE"
    echo "[$timestamp] Heartbeat cycle complete (issue #$ISSUE_NUMBER)"
elif [ $exit_code -eq 137 ] || [ $exit_code -eq 143 ]; then
    echo "$timestamp TIMEOUT issue=#$ISSUE_NUMBER repo=$ISSUE_REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code issue=#$ISSUE_NUMBER repo=$ISSUE_REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude exited with code $exit_code"
fi

exit 0
