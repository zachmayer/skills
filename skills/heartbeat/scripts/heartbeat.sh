#!/bin/bash
# Heartbeat: GitHub Issues → worktree → Claude Code → branch + PR.
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
# Read from config file if present, otherwise use default.
# Config file: one owner/repo per line, # comments allowed.
REPOS_FILE="${HOME}/.claude/heartbeat-repos.conf"
if [ -f "$REPOS_FILE" ]; then
    REPOS=$(grep -v '^\s*#' "$REPOS_FILE" | grep -v '^\s*$' | tr '\n' ' ')
fi
REPOS="${REPOS:-zachmayer/skills}"

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

# --- Discover available issues across ALL repos ---
# Iterate every repo, fetch up to 25 open agent-task issues each, filter out
# ones with existing heartbeat branches on origin (already claimed). Collect
# issues from all repos into a unified list tagged with repo metadata.
ALL_REPO_ISSUES="[]"  # Combined JSON array across all repos
REPOS_WITH_ISSUES=""  # Space-separated list of repos that have available issues

for candidate in $REPOS; do
    candidate_dir=$(repo_dir "$candidate")
    if [ ! -d "$candidate_dir/.git" ]; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Skipping $candidate — $candidate_dir not a git repo"
        continue
    fi

    git -C "$candidate_dir" fetch origin 2>/dev/null || continue

    CANDIDATE_ISSUES=$(gh issue list \
        --repo "$candidate" \
        --author "$ISSUE_AUTHOR" \
        --label "$ISSUE_LABEL" \
        --state open \
        --json number,title,body \
        --limit 25 2>/dev/null || echo "[]")

    if [ "$CANDIDATE_ISSUES" = "[]" ] || [ -z "$CANDIDATE_ISSUES" ]; then
        continue
    fi

    # Get existing heartbeat branches to filter out already-claimed issues
    EXISTING_BRANCHES=$(git -C "$candidate_dir" ls-remote --heads origin 'refs/heads/heartbeat/issue-*' 2>/dev/null \
        | awk '{print $2}' | sed 's|refs/heads/heartbeat/issue-||' || echo "")

    # Filter claimed issues and tag each with repo metadata
    # EXISTING_BRANCHES and REPO passed via env vars (not interpolated into source) to prevent injection
    FILTERED=$(echo "$CANDIDATE_ISSUES" | EXISTING="$EXISTING_BRANCHES" REPO_NAME="$candidate" python3 -c "
import sys, json, os
issues = json.loads(sys.stdin.read())
existing = set(line.strip() for line in os.environ.get('EXISTING', '').strip().split('\n') if line.strip())
repo = os.environ['REPO_NAME']
available = [dict(i, repo=repo) for i in issues if str(i['number']) not in existing]
print(json.dumps(available))
")

    FILTERED_COUNT=$(echo "$FILTERED" | python3 -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

    if [ "$FILTERED_COUNT" != "0" ]; then
        # Merge into combined list
        ALL_REPO_ISSUES=$(echo "$ALL_REPO_ISSUES" | ADDITIONS="$FILTERED" python3 -c "
import sys, json, os
existing = json.loads(sys.stdin.read())
additions = json.loads(os.environ['ADDITIONS'])
existing.extend(additions)
print(json.dumps(existing))
")
        REPOS_WITH_ISSUES="$REPOS_WITH_ISSUES $candidate"
    fi
done

# Shuffle the combined list so parallel agents naturally diverge
AVAILABLE_ISSUES=$(echo "$ALL_REPO_ISSUES" | python3 -c "
import sys, json, random
issues = json.loads(sys.stdin.read())
random.shuffle(issues)
print(json.dumps(issues))
")

ISSUE_COUNT=$(echo "$AVAILABLE_ISSUES" | python3 -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

if [ "$ISSUE_COUNT" = "0" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No available agent-task issues in any repo"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) IDLE" > "$STATUS_FILE"
    exit 0
fi

# Determine unique repos that have issues
REPOS_WITH_ISSUES=$(echo "$REPOS_WITH_ISSUES" | tr ' ' '\n' | sort -u | grep -v '^\s*$' | tr '\n' ' ' || true)
REPO_COUNT=$(echo "$REPOS_WITH_ISSUES" | wc -w | tr -d ' ')

# Format issue list for the agent prompt (includes repo labels)
ISSUE_LIST=$(echo "$AVAILABLE_ISSUES" | python3 -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    repo = i.get('repo', 'unknown')
    print(f'### Issue #{i[\"number\"]}: {i[\"title\"]}')
    print(f'**Repo:** {repo}')
    body = (i.get('body') or '').strip()
    if body:
        print(body)
    print()
")

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $ISSUE_COUNT available issues across $REPO_COUNT repo(s):$REPOS_WITH_ISSUES"

# --- Clean stale local heartbeat branches (all repos) ---
for repo_slug in $REPOS_WITH_ISSUES; do
    rd=$(repo_dir "$repo_slug")
    git -C "$rd" worktree prune 2>/dev/null || true
    for branch in $(git -C "$rd" branch --list 'heartbeat/issue-*' | tr -d ' *'); do
        git -C "$rd" branch -D "$branch" 2>/dev/null || true
    done
done

# --- Set up worktrees (one per repo with issues) ---
# Each repo gets a worktree at /tmp/heartbeat-PID-REPONAME.
# The agent will create its branch via `git checkout -b heartbeat/issue-N`
# in the appropriate worktree for the issue's repo.
WORKDIR_BASE="/tmp/heartbeat-$$"
PRIMARY_WORKDIR="" # First worktree (used as primary CWD for claude)
ADD_DIR_ARGS=""    # Extra --add-dir args for additional repos

# Build repo→worktree mapping for the agent prompt
REPO_WORKDIR_MAP=""

for repo_slug in $REPOS_WITH_ISSUES; do
    rd=$(repo_dir "$repo_slug")
    repo_basename=$(basename "$repo_slug")
    workdir="${WORKDIR_BASE}-${repo_basename}"

    git -C "$rd" worktree add --detach "$workdir" origin/main

    REPO_WORKDIR_MAP="${REPO_WORKDIR_MAP}
- ${repo_slug} → ${workdir}"

    if [ -z "$PRIMARY_WORKDIR" ]; then
        PRIMARY_WORKDIR="$workdir"
        PRIMARY_REPO="$repo_slug"
    else
        ADD_DIR_ARGS="$ADD_DIR_ARGS --add-dir $workdir"
    fi
done

cleanup() {
    for repo_slug in $REPOS_WITH_ISSUES; do
        rd=$(repo_dir "$repo_slug")
        repo_basename=$(basename "$repo_slug")
        workdir="${WORKDIR_BASE}-${repo_basename}"
        if [ -d "$workdir" ]; then
            git -C "$rd" worktree remove "$workdir" --force 2>/dev/null || true
        fi
        git -C "$rd" worktree prune 2>/dev/null || true
    done
}
trap cleanup EXIT

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Worktrees created. Invoking Claude Code with $ISSUE_COUNT issues across $REPO_COUNT repo(s)..."

# --- Invoke Claude Code with safety bounds ---
set +e
(
    cd "$PRIMARY_WORKDIR"
    # shellcheck disable=SC2086
    exec claude --print \
        --permission-mode dontAsk \
        --add-dir "$OBSIDIAN_DIR" \
        $ADD_DIR_ARGS \
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

<repo-worktree-map>
Each issue is tagged with its repo. Use the matching worktree directory:
$REPO_WORKDIR_MAP

Your primary working directory is $PRIMARY_WORKDIR (repo: $PRIMARY_REPO).
If you pick an issue from a different repo, cd to its worktree first.
</repo-worktree-map>

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
    echo "$timestamp OK repos=\"$REPOS_WITH_ISSUES\" issues_available=$ISSUE_COUNT" > "$STATUS_FILE"
    echo "[$timestamp] Heartbeat cycle complete"
elif [ $exit_code -eq 137 ] || [ $exit_code -eq 143 ]; then
    echo "$timestamp TIMEOUT repos=\"$REPOS_WITH_ISSUES\"" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code repos=\"$REPOS_WITH_ISSUES\"" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude exited with code $exit_code"
fi

exit 0
