#!/bin/bash
# Claude Code status line.
#
# Left:  ~/path  branch
# Right: Model · ctx-mode · EFFORT · ctx:NN%
#
# The two halves are padded apart so identity stays on the left edge and
# state sits on the right edge.
#
# Color logic flags non-ideal state so you notice at a glance:
#   - model:  green bold if Opus family, bright-yellow otherwise
#   - ctx:    green "1M" if >=1M context, bright-yellow actual size (e.g. "200K") otherwise
#   - effort: green "MAX" if CLAUDE_CODE_EFFORT_LEVEL=max, bright-yellow actual level otherwise
#   - ctx %:  dim under 70%, yellow 70-89%, bright-red 90%+
#
# Schema: https://code.claude.com/docs/en/statusline.md

set -u

# ─── ANSI palette ────────────────────────────────────────────────────────────
# Identity uses neutral tones (cyan, bold default-fg) so it doesn't compete
# with the semantic colors (green/yellow/red) that actually mean something.
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

# ─── Binary warnings ────────────────────────────────────────────────────────
case "$model_id" in
    *opus*) model_color="$green$bold" ;;
    *)      model_color="$bright_yellow$bold" ;;
esac

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

# Left: path (cyan) + branch (bold, default fg — neutral, no hue bleed with
# the semantic colors on the right).
left=""
[ -n "$short_cwd" ] && left+="${cyan}${bold}${short_cwd}${reset}"
[ -n "$branch" ]    && left+="  ${bold}${branch}${reset}"

# Right: model · ctx_mode · effort · ctx%
segments=()
[ -n "$model" ]          && segments+=("${model_color}${model}${reset}")
[ -n "$ctx_mode" ]       && segments+=("${ctx_mode_color}${ctx_mode}${reset}")
[ -n "$effort_display" ] && segments+=("${effort_color}${effort_display}${reset}")
[ -n "$ctx_pct_part" ]   && segments+=("$ctx_pct_part")

right=""
for s in "${segments[@]}"; do
    if [ -n "$right" ]; then
        right="$right$sep$s"
    else
        right="$s"
    fi
done

# ─── Pad apart ──────────────────────────────────────────────────────────────
width="${COLUMNS:-}"
[ -z "$width" ] && width=$(tput cols 2>/dev/null || true)
[ -z "$width" ] && width=120

strip_ansi() {
    printf '%s' "$1" | sed $'s/\033\\[[0-9;]*m//g'
}
left_len=$(strip_ansi "$left"  | wc -c | tr -d ' ')
right_len=$(strip_ansi "$right" | wc -c | tr -d ' ')
pad=$(( width - left_len - right_len ))
[ "$pad" -lt 1 ] && pad=1
padding=$(printf '%*s' "$pad" '')

printf '%b' "${left}${padding}${right}"
