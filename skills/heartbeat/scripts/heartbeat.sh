#!/bin/bash
# Heartbeat v2: GitHub Issues → worktree → Claude Code → branch + PR.
# Designed for macOS launchd user agent execution.
#
# PARALLEL BY DESIGN: Multiple heartbeat instances may run concurrently on the
# same machine. Each gets its own worktree. Coordination uses git branches as
# atomic claims — `git checkout -b heartbeat/issue-N` either succeeds (claimed)
# or fails (another agent got it first). No locking, no label-based claiming.
# The agent receives a randomized list of available issues and picks one.
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
# Space-separated list of owner/repo. Each cycle picks a random repo with issues.
REPOS="zachmayer/skills"

# --- Issue filters (hardcoded for security — agent never constructs these) ---
ISSUE_AUTHOR="zachmayer"
ISSUE_LABEL="agent-task"

# --- Repo clone location (owner/repo → ~/source/repo-name) ---
repo_dir() { echo "$HOME/source/$(basename "$1")"; }

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

# --- Discover available issues (random repo selection) ---
# Shuffle repos so parallel agents naturally diverge. For each repo, fetch up to
# 25 open agent-task issues and filter out ones with existing heartbeat branches
# on origin (already claimed). Stop at the first repo that has available issues.
REPO=""
REPO_DIR=""
AVAILABLE_ISSUES="[]"
ISSUE_COUNT=0

# Randomize repo order
SHUFFLED_REPOS=$(echo "$REPOS" | tr ' ' '\n' | python3 -c "
import sys, random
repos = [l.strip() for l in sys.stdin if l.strip()]
random.shuffle(repos)
print(' '.join(repos))
")

for candidate in $SHUFFLED_REPOS; do
    candidate_dir=$(repo_dir "$candidate")
    if [ ! -d "$candidate_dir/.git" ]; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Skipping $candidate — $candidate_dir not a git repo"
        continue
    fi

    git -C "$candidate_dir" fetch origin 2>/dev/null || continue

    ALL_ISSUES=$(gh issue list \
        --repo "$candidate" \
        --author "$ISSUE_AUTHOR" \
        --label "$ISSUE_LABEL" \
        --state open \
        --json number,title,body \
        --limit 25 2>/dev/null || echo "[]")

    if [ "$ALL_ISSUES" = "[]" ] || [ -z "$ALL_ISSUES" ]; then
        continue
    fi

    # Get existing heartbeat branches to filter out already-claimed issues
    EXISTING_BRANCHES=$(git -C "$candidate_dir" ls-remote --heads origin 'refs/heads/heartbeat/issue-*' 2>/dev/null \
        | awk '{print $2}' | sed 's|refs/heads/heartbeat/issue-||' || echo "")

    # Filter claimed issues and randomize order
    # EXISTING_BRANCHES passed via env var (not interpolated into source) to prevent injection
    AVAILABLE_ISSUES=$(echo "$ALL_ISSUES" | EXISTING="$EXISTING_BRANCHES" python3 -c "
import sys, json, random, os
issues = json.loads(sys.stdin.read())
existing = set(line.strip() for line in os.environ.get('EXISTING', '').strip().split('\n') if line.strip())
available = [i for i in issues if str(i['number']) not in existing]
random.shuffle(available)
print(json.dumps(available))
")

    ISSUE_COUNT=$(echo "$AVAILABLE_ISSUES" | python3 -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

    if [ "$ISSUE_COUNT" != "0" ]; then
        REPO="$candidate"
        REPO_DIR="$candidate_dir"
        break
    fi
done

if [ -z "$REPO" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No available agent-task issues in any repo"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) IDLE" > "$STATUS_FILE"
    exit 0
fi

# Format issue list for the agent prompt
ISSUE_LIST=$(echo "$AVAILABLE_ISSUES" | python3 -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(f'### Issue #{i[\"number\"]}: {i[\"title\"]}')
    body = (i.get('body') or '').strip()
    if body:
        print(body)
    print()
")

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $ISSUE_COUNT available issues in $REPO. Creating worktree..."

# --- Clean stale local heartbeat branches ---
# If a prior run was killed after creating a local branch but before pushing,
# the branch lingers locally. Prune stale worktrees first (so branch -D succeeds),
# then clean up any heartbeat branches that aren't checked out elsewhere.
git -C "$REPO_DIR" worktree prune 2>/dev/null || true
for branch in $(git -C "$REPO_DIR" branch --list 'heartbeat/issue-*' | tr -d ' *'); do
    git -C "$REPO_DIR" branch -D "$branch" 2>/dev/null || true
done

# --- Set up worktree (detached HEAD on origin/main) ---
# The agent will create its own branch via `git checkout -b heartbeat/issue-N`.
# Detached HEAD avoids conflicts with branches checked out in other worktrees.
WORKDIR="/tmp/heartbeat-$$"

cleanup() {
    if [ -d "$WORKDIR" ]; then
        git -C "$REPO_DIR" worktree remove "$WORKDIR" --force 2>/dev/null || true
    fi
    git -C "$REPO_DIR" worktree prune 2>/dev/null || true
}
trap cleanup EXIT

git -C "$REPO_DIR" worktree add --detach "$WORKDIR" origin/main

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Worktree at $WORKDIR. Invoking Claude Code with $ISSUE_COUNT issues..."

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

Pick ONE issue from the list below. Create branch heartbeat/issue-N and work on it.
If git checkout -b fails, the issue is claimed by another agent — pick a different one.
NEVER commit to main.

<available-issues>
$ISSUE_LIST
</available-issues>

Repo: $REPO. Obsidian dir: $OBSIDIAN_DIR. Time limit: $WORK_MINUTES minutes. Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)."
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
    echo "$timestamp OK repo=$REPO issues_available=$ISSUE_COUNT" > "$STATUS_FILE"
    echo "[$timestamp] Heartbeat cycle complete"
elif [ $exit_code -eq 137 ] || [ $exit_code -eq 143 ]; then
    echo "$timestamp TIMEOUT repo=$REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code repo=$REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude exited with code $exit_code"
fi

exit 0
