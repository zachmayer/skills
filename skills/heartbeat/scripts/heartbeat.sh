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
TRIAGE_FILE="$HOME/.claude/heartbeat.triage"
TRIAGE_COOLDOWN=21600  # 6 hours between triage sessions

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

# --- Discover available issues (random repo selection) ---
REPO=""
REPO_DIR=""
AVAILABLE_ISSUES="[]"
ISSUE_COUNT=0

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

    EXISTING_BRANCHES=$(git -C "$candidate_dir" ls-remote --heads origin 'refs/heads/heartbeat/issue-*' 2>/dev/null \
        | awk '{print $2}' | sed 's|refs/heads/heartbeat/issue-||' || echo "")

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

# --- Determine mode: work, triage, or idle ---
MODE="idle"
WORK_REPO=""
WORK_DIR=""

if [ -n "$REPO" ]; then
    MODE="work"
    WORK_REPO="$REPO"
    WORK_DIR="$REPO_DIR"
else
    # Check triage cooldown
    should_triage=true
    if [ -f "$TRIAGE_FILE" ]; then
        last_triage=$(cat "$TRIAGE_FILE" 2>/dev/null || echo "0")
        now=$(date +%s)
        elapsed=$((now - last_triage))
        if [ "$elapsed" -lt "$TRIAGE_COOLDOWN" ]; then
            should_triage=false
            remaining=$(( (TRIAGE_COOLDOWN - elapsed) / 60 ))
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No issues. Triage cooldown: ${remaining}min remaining"
        fi
    fi

    if [ "$should_triage" = true ]; then
        MODE="triage"
        WORK_REPO="${REPOS%% *}"
        WORK_DIR=$(repo_dir "$WORK_REPO")
        date +%s > "$TRIAGE_FILE"
    fi
fi

if [ "$MODE" = "idle" ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) IDLE" > "$STATUS_FILE"
    exit 0
fi

# --- Mode-specific setup (prompt, tools, budget) ---
WORK_TOOLS=(Read Write Edit Glob Grep
    "Bash(git status)" "Bash(git log *)" "Bash(git -C *)"
    "Bash(gh issue list *)" "Bash(gh pr list *)"
    "Bash(ls *)" "Bash(date *)" "Bash(uv run python *)")

if [ "$MODE" = "work" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $ISSUE_COUNT available issues in $REPO"

    # Format issue list for prompt
    ISSUE_LIST=$(echo "$AVAILABLE_ISSUES" | python3 -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(f'### Issue #{i[\"number\"]}: {i[\"title\"]}')
    body = (i.get('body') or '').strip()
    if body:
        print(body)
    print()
")

    # Clean stale local heartbeat branches
    git -C "$REPO_DIR" worktree prune 2>/dev/null || true
    for branch in $(git -C "$REPO_DIR" branch --list 'heartbeat/issue-*' | tr -d ' *'); do
        git -C "$REPO_DIR" branch -D "$branch" 2>/dev/null || true
    done

    # Work mode gets full git + PR tools
    WORK_TOOLS+=(
        "Bash(git diff *)" "Bash(git add *)" "Bash(git commit *)"
        "Bash(git checkout *)" "Bash(git branch *)" "Bash(git push *)"
        "Bash(git pull *)" "Bash(git fetch *)" "Bash(git worktree *)"
        "Bash(gh pr create *)" "Bash(gh pr view *)"
        "Bash(mkdir *)")
    AGENT_TURNS=$MAX_TURNS
    AGENT_BUDGET=$MAX_BUDGET_USD
    AGENT_PROMPT="You are the heartbeat agent. You MUST read and follow your heartbeat skill before doing anything.

Pick ONE issue from the list below. Create branch heartbeat/issue-N and work on it.
If git checkout -b fails, the issue is claimed by another agent — pick a different one.
NEVER commit to main.

<available-issues>
$ISSUE_LIST
</available-issues>

Repo: $REPO. Obsidian dir: $OBSIDIAN_DIR. Time limit: $WORK_MINUTES minutes. Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)."

elif [ "$MODE" = "triage" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No issues. Entering triage mode..."

    # Triage mode gets issue creation but no code modification tools
    WORK_TOOLS+=("Bash(gh issue create *)")
    AGENT_TURNS=50
    AGENT_BUDGET=1
    AGENT_PROMPT="You are the heartbeat agent in TRIAGE mode. No issues are available.

Your job: review the agent goals and create 1-2 well-specified GitHub Issues.

Steps:
1. Read the Agent Goals note: $OBSIDIAN_DIR/knowledge_graph/Technical/Agent Goals.md
2. Check existing open issues across repos: gh issue list --repo $WORK_REPO --state open --json number,title
3. Check recently merged PRs for context: gh pr list --repo $WORK_REPO --state merged --limit 10 --json number,title,mergedAt
4. Create 1-2 NEW issues that advance an active goal:
   gh issue create --repo $WORK_REPO --title '...' --label agent-task --body '...'
5. Each issue MUST have: clear title, detailed body with numbered acceptance criteria, be completable in ~30 minutes
6. Log what you created to hierarchical_memory

Rules:
- Create at most 2 issues per triage session
- Only create issues for Active Goals (not 'Not Now')
- Do NOT create issues that duplicate existing open issues or open PRs
- Do NOT modify any code. Triage is planning only.
- Prefer concrete, scoped tasks over vague improvement requests

Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)."
fi

# --- Set up worktree (shared for both modes) ---
WORKDIR="/tmp/heartbeat-$$"

git -C "$WORK_DIR" fetch origin 2>/dev/null || true
git -C "$WORK_DIR" worktree prune 2>/dev/null || true

cleanup() {
    if [ -d "$WORKDIR" ]; then
        git -C "$WORK_DIR" worktree remove "$WORKDIR" --force 2>/dev/null || true
    fi
    git -C "$WORK_DIR" worktree prune 2>/dev/null || true
}
trap cleanup EXIT

git -C "$WORK_DIR" worktree add --detach "$WORKDIR" origin/main

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Worktree at $WORKDIR. Mode: $MODE."

# --- Invoke Claude Code with safety bounds ---
set +e
(
    cd "$WORKDIR"
    exec claude --print \
        --permission-mode dontAsk \
        --add-dir "$OBSIDIAN_DIR" \
        --allowedTools "${WORK_TOOLS[@]}" \
        --max-turns "$AGENT_TURNS" \
        --max-budget-usd "$AGENT_BUDGET" \
        --model opus \
        "$AGENT_PROMPT"
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

kill "$watchdog_pid" 2>/dev/null
wait "$watchdog_pid" 2>/dev/null
set -e

# --- Record outcome ---
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ $exit_code -eq 0 ]; then
    echo "$timestamp OK mode=$MODE repo=$WORK_REPO" > "$STATUS_FILE"
    echo "[$timestamp] Heartbeat cycle complete ($MODE)"
elif [ $exit_code -eq 137 ] || [ $exit_code -eq 143 ]; then
    echo "$timestamp TIMEOUT mode=$MODE repo=$WORK_REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude killed after ${TIMEOUT_SECONDS}s timeout"
else
    echo "$timestamp FAIL exit=$exit_code mode=$MODE repo=$WORK_REPO" > "$STATUS_FILE"
    echo "[$timestamp] ERROR: Claude exited with code $exit_code"
fi

exit 0
