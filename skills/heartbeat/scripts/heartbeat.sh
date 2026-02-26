#!/bin/bash
# Heartbeat: Two-agent FSM (lead + dev) driven by status labels.
# Step 1: Lead agent processes all status:lead issues (route, scope, review).
# Step 2: Dev agent processes all status:dev issues (build, push, hand back).
# Designed for macOS launchd user agent execution.
set -euo pipefail

# --- Configuration ---
OBSIDIAN_DIR="${CLAUDE_OBSIDIAN_DIR:-$HOME/claude/obsidian}"
OBSIDIAN_DIR="${OBSIDIAN_DIR/#\~/$HOME}"
STATUS_FILE="$HOME/.claude/heartbeat.status"
TIMEOUT_SECONDS=14400  # 4 hour hard kill
LEAD_BUDGET=1          # $/issue for lead
DEV_BUDGET=4           # $/issue for dev
MAX_TURNS=200

# --- Repo registry ---
REPOS_FILE="${HOME}/.claude/heartbeat-repos.conf"
if [ -f "$REPOS_FILE" ]; then
    REPOS=$(grep -v '^\s*#' "$REPOS_FILE" | grep -v '^\s*$' | tr '\n' ' ')
fi
REPOS="${REPOS:-zachmayer/skills}"

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

# --- Run an agent on a single issue ---
# Usage: run_agent <agent_name> <repo> <issue_number> <issue_json> <budget>
run_agent() {
    local agent="$1"
    local repo="$2"
    local issue_number="$3"
    local issue_json="$4"
    local budget="$5"
    local repo_dir
    repo_dir=$(repo_dir "$repo")

    local owner
    owner=$(echo "$repo" | cut -d/ -f1)

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running $agent on $repo#$issue_number (budget: \$$budget)"

    local workdir=""
    local cleanup_workdir=""
    local run_dir="$repo_dir"

    if [ "$agent" = "dev" ]; then
        # Dev gets a worktree for isolation
        workdir="/tmp/heartbeat-$$-${issue_number}"
        cleanup_workdir="$workdir"
        git -C "$repo_dir" worktree prune 2>/dev/null || true
        git -C "$repo_dir" worktree add --detach "$workdir" origin/main 2>/dev/null || {
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Failed to create worktree for $repo#$issue_number"
            return 1
        }
        run_dir="$workdir"
    fi

    local issue_title
    issue_title=$(echo "$issue_json" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read()).get('title',''))")
    local issue_body
    issue_body=$(echo "$issue_json" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read()).get('body',''))")

    set +e
    (
        cd "$run_dir"
        exec claude --print \
            --agent "$agent" \
            --add-dir "$OBSIDIAN_DIR" \
            --max-turns "$MAX_TURNS" \
            --max-budget-usd "$budget" \
            "<issue>
Repo: $repo
Issue: #$issue_number
Title: $issue_title
Authorized user: $owner
Obsidian dir: $OBSIDIAN_DIR
Current time: $(date -u +%Y-%m-%dT%H:%M:%SZ)

$issue_body
</issue>"
    )
    local exit_code=$?
    set -e

    # Clean up worktree if dev
    if [ -n "$cleanup_workdir" ] && [ -d "$cleanup_workdir" ]; then
        git -C "$repo_dir" worktree remove "$cleanup_workdir" --force 2>/dev/null || true
        git -C "$repo_dir" worktree prune 2>/dev/null || true
    fi

    if [ $exit_code -ne 0 ]; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $agent on $repo#$issue_number exited with code $exit_code"
    fi

    return $exit_code
}

# --- Collect issues with a given label across all repos ---
# Usage: collect_issues <label>
# Output: JSON array of {repo, number, title, body}
collect_issues() {
    local label="$1"
    local all_issues="[]"

    # Randomize repo order
    local shuffled
    shuffled=$(echo "$REPOS" | tr ' ' '\n' | uv run python -c "
import sys, random
repos = [l.strip() for l in sys.stdin if l.strip()]
random.shuffle(repos)
print(' '.join(repos))
")

    for repo in $shuffled; do
        local rdir
        rdir=$(repo_dir "$repo")
        if [ ! -d "$rdir/.git" ]; then
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Skipping $repo — $rdir not a git repo" >&2
            continue
        fi

        git -C "$rdir" fetch origin 2>/dev/null || continue

        local issues
        issues=$(gh issue list \
            --repo "$repo" \
            --label "$label" \
            --state open \
            --json number,title,body \
            --limit 25 2>/dev/null || echo "[]")

        if [ -z "$issues" ]; then
            issues="[]"
        fi

        # Annotate each issue with its repo
        all_issues=$(echo "$all_issues" | ISSUES="$issues" REPO="$repo" uv run python -c "
import sys, json, os
existing = json.loads(sys.stdin.read())
new = json.loads(os.environ['ISSUES'])
repo = os.environ['REPO']
for i in new:
    i['repo'] = repo
    existing.append(i)
print(json.dumps(existing))
")
    done

    echo "$all_issues"
}

# --- Watchdog: kill the entire round after timeout ---
(
    sleep "$TIMEOUT_SECONDS"
    kill $$ 2>/dev/null
    sleep 10
    kill -9 $$ 2>/dev/null
) &
watchdog_pid=$!
trap "kill $watchdog_pid 2>/dev/null; wait $watchdog_pid 2>/dev/null" EXIT

# --- Main: two-step FSM ---
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "[$timestamp] Heartbeat round starting"

lead_count=0
dev_count=0
lead_ok=0
dev_ok=0

# Step 1: Lead agent on all status:lead issues
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Step 1: Querying status:lead issues..."
LEAD_ISSUES=$(collect_issues "status:lead")
lead_count=$(echo "$LEAD_ISSUES" | uv run python -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

if [ "$lead_count" != "0" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $lead_count status:lead issues"
    echo "$LEAD_ISSUES" | uv run python -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(f'{i[\"repo\"]}#{i[\"number\"]} {i[\"title\"][:60]}')
"
    # Process each issue sequentially
    echo "$LEAD_ISSUES" | uv run python -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(json.dumps(i))
" | while IFS= read -r issue_line; do
        repo=$(echo "$issue_line" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read())['repo'])")
        number=$(echo "$issue_line" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read())['number'])")
        if run_agent "lead" "$repo" "$number" "$issue_line" "$LEAD_BUDGET"; then
            lead_ok=$((lead_ok + 1))
        fi
    done
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No status:lead issues found"
fi

# Step 2: Dev agent on all status:dev issues
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Step 2: Querying status:dev issues..."
DEV_ISSUES=$(collect_issues "status:dev")
dev_count=$(echo "$DEV_ISSUES" | uv run python -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

if [ "$dev_count" != "0" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $dev_count status:dev issues"
    echo "$DEV_ISSUES" | uv run python -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(f'{i[\"repo\"]}#{i[\"number\"]} {i[\"title\"][:60]}')
"
    # Process each issue sequentially
    echo "$DEV_ISSUES" | uv run python -c "
import sys, json
for i in json.loads(sys.stdin.read()):
    print(json.dumps(i))
" | while IFS= read -r issue_line; do
        repo=$(echo "$issue_line" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read())['repo'])")
        number=$(echo "$issue_line" | uv run python -c "import sys,json; print(json.loads(sys.stdin.read())['number'])")
        if run_agent "dev" "$repo" "$number" "$issue_line" "$DEV_BUDGET"; then
            dev_ok=$((dev_ok + 1))
        fi
    done
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No status:dev issues found"
fi

# --- Record outcome ---
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ "$lead_count" = "0" ] && [ "$dev_count" = "0" ]; then
    echo "$timestamp IDLE" > "$STATUS_FILE"
    echo "[$timestamp] No issues to process"
else
    echo "$timestamp OK lead=$lead_count dev=$dev_count" > "$STATUS_FILE"
    echo "[$timestamp] Round complete: lead=$lead_count dev=$dev_count"
fi

exit 0
