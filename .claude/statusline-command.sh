#!/bin/bash
# Claude Code status line.
#
# Reads the session JSON payload from stdin and prints one line:
#   ~/path branch[#PR] · Model · ctx-mode · EFFORT · ctx:NN%
#
# Colors flag non-ideal state so you notice at a glance:
#   - model:  green bold if Opus family, bright-yellow otherwise
#   - ctx:    green "1M" if >=1M context, bright-yellow actual size (e.g. "200K") otherwise
#   - effort: green "MAX" if CLAUDE_CODE_EFFORT_LEVEL=max, bright-yellow actual level otherwise
#   - ctx %:  dim under 70%, yellow 70-89%, bright-red 90%+
#
# Also shows the open PR number for the current branch (cached, refreshed
# in the background every 30s — never blocks the statusline).
#
# Schema: https://code.claude.com/docs/en/statusline.md

set -u

# ─── ANSI palette ────────────────────────────────────────────────────────────
reset=$'\033[0m'
dim=$'\033[2m'
bold=$'\033[1m'
cyan=$'\033[36m'
yellow=$'\033[33m'
green=$'\033[32m'
bright_yellow=$'\033[93m'
bright_red=$'\033[91m'

# ─── Parse payload ──────────────────────────────────────────────────────────
input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
model_id=$(echo "$input" | jq -r '.model.id // ""')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

short_cwd="${cwd/#$HOME/~}"

# ─── Git branch ─────────────────────────────────────────────────────────────
branch=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null)
fi

# ─── PR number (cached, background refresh) ─────────────────────────────────
# Calling `gh pr view` on every render would block and hit the network; instead
# read a cached number and refresh in a detached background process every 30s.
pr_num=""
if [ -n "$branch" ] && command -v gh >/dev/null 2>&1; then
    cache_dir="$HOME/.claude/cache"
    mkdir -p "$cache_dir"
    key=$(printf '%s' "${cwd%/}:$branch" | shasum | cut -c1-12)
    cache_file="$cache_dir/statusline-pr-$key.txt"
    lock_dir="$cache_dir/statusline-pr-$key.lock"

    now=$(date +%s)

    # Drop stale locks (> 60s old — previous refresh likely crashed).
    if [ -d "$lock_dir" ]; then
        lock_mtime=$(stat -f %m "$lock_dir" 2>/dev/null || stat -c %Y "$lock_dir" 2>/dev/null || echo "$now")
        [ $((now - lock_mtime)) -gt 60 ] && rmdir "$lock_dir" 2>/dev/null
    fi

    refresh=0
    if [ -f "$cache_file" ]; then
        cache_mtime=$(stat -f %m "$cache_file" 2>/dev/null || stat -c %Y "$cache_file" 2>/dev/null || echo 0)
        [ $((now - cache_mtime)) -gt 30 ] && refresh=1
    else
        refresh=1
    fi

    if [ "$refresh" = 1 ] && mkdir "$lock_dir" 2>/dev/null; then
        (
            exec >/dev/null 2>&1
            trap 'rmdir "$lock_dir" 2>/dev/null' EXIT
            cd "$cwd" || exit 0
            pr=$(gh pr view --json number -q .number 2>/dev/null || true)
            printf '%s' "$pr" > "$cache_file.tmp"
            mv -f "$cache_file.tmp" "$cache_file"
        ) & disown
    fi

    [ -f "$cache_file" ] && pr_num=$(cat "$cache_file")
fi

# ─── Binary warnings ────────────────────────────────────────────────────────
# Model: Opus family = good, anything else = warning.
case "$model_id" in
    *opus*) model_color="$green$bold" ;;
    *)      model_color="$bright_yellow$bold" ;;
esac

# Context mode: >= 1M = good, smaller = warning showing actual size.
if [ -n "$ctx_size" ] && [ "$ctx_size" -ge 1000000 ] 2>/dev/null; then
    ctx_mode="1M"
    ctx_mode_color="$green"
else
    case "${ctx_size:-}" in
        "")     ctx_mode="?" ;;
        200000) ctx_mode="200K" ;;
        *)      ctx_mode="$((ctx_size / 1000))K" ;;
    esac
    ctx_mode_color="$bright_yellow"
fi

# Reasoning effort: max = good, anything else = warning showing actual level.
# CLAUDE_CODE_EFFORT_LEVEL isn't in the JSON payload — Claude Code exports it.
effort="${CLAUDE_CODE_EFFORT_LEVEL:-}"
if [ "$effort" = "max" ]; then
    effort_display="MAX"
    effort_color="$green"
elif [ -n "$effort" ]; then
    effort_display=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]')
    effort_color="$bright_yellow"
else
    effort_display=""
    effort_color=""
fi

# Context %: the one metric that trends up over a session — use thresholds.
ctx_pct_part=""
if [ -n "$used_pct" ]; then
    used_int=$(printf '%.0f' "$used_pct")
    if [ "$used_int" -ge 90 ]; then
        ctx_pct_part="${bright_red}ctx:${used_int}%${reset}"
    elif [ "$used_int" -ge 70 ]; then
        ctx_pct_part="${yellow}ctx:${used_int}%${reset}"
    else
        ctx_pct_part="${dim}ctx:${used_int}%${reset}"
    fi
fi

# ─── Compose ────────────────────────────────────────────────────────────────
sep=" ${dim}·${reset} "

# Left: path + branch[#PR]
left=""
[ -n "$short_cwd" ] && left+="${cyan}${bold}${short_cwd}${reset}"
if [ -n "$branch" ]; then
    left+=" ${yellow}${branch}${reset}"
    [ -n "$pr_num" ] && left+="${dim}#${reset}${yellow}${pr_num}${reset}"
fi

# Right: model, ctx mode, effort, ctx %
segments=()
[ -n "$model" ]          && segments+=("${model_color}${model}${reset}")
[ -n "$ctx_mode" ]       && segments+=("${ctx_mode_color}${ctx_mode}${reset}")
[ -n "$effort_display" ] && segments+=("${effort_color}${effort_display}${reset}")
[ -n "$ctx_pct_part" ]   && segments+=("$ctx_pct_part")

result="$left"
for s in "${segments[@]}"; do
    if [ -n "$result" ]; then
        result="$result$sep$s"
    else
        result="$s"
    fi
done

printf '%b' "$result"
