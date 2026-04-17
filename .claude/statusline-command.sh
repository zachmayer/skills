#!/bin/bash
# Claude Code status line.
#
# Left:  ~/path  branch
# Right: Model · ctx-mode · EFFORT · ctx:NN%
#
# Palette uses ColorBrewer qualitative + sequential scales mapped to the
# 256-color terminal palette. Green = good, gold = warn, red = bad, blue =
# info; gray for identity/low-priority. Context % uses a YlOrRd sequential
# gradient — never green, since context always trends one way.
#
# Semantic color map:
#   model:  Opus  = green (71)    | Sonnet = gold (178)    | Haiku = red (160)
#   ctx:    1M    = green (71)    | other  = gold (178)
#   effort: MAX   = green (71)    | xhigh  = sky blue (117) | high/medium = gold (178) | low = red (160)
#   ctx %:  <20   = gray (244)    | 20-69  = gold (221)     | 70-89 = orange (208) | >=90 = dark red (124) bold
#
# Schema: https://code.claude.com/docs/en/statusline.md

set -u

# ─── ANSI palette (ColorBrewer-derived 256-color) ───────────────────────────
reset=$'\033[0m'
bold=$'\033[1m'
path_blue=$'\033[38;5;67m'      # Set1 #377EB8
gray=$'\033[38;5;244m'          # Greys mid
good=$'\033[38;5;71m'           # Set1 green #4DAF4A
warn=$'\033[38;5;178m'          # Dark2 #E6AB02
bad=$'\033[38;5;160m'           # Set1 red #E41A1C
info=$'\033[38;5;117m'          # Paired light blue #A6CEE3
ctx_mid=$'\033[38;5;221m'       # YlOrRd mid
ctx_high=$'\033[38;5;208m'      # YlOrRd orange
ctx_crit=$'\033[38;5;124m'      # YlOrRd dark red

# ─── Parse payload ──────────────────────────────────────────────────────────
input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
model_id=$(echo "$input" | jq -r '.model.id // ""')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Strip " (1M context)" or similar parentheticals — we show 1M as its own segment.
model="${model% (*}"

short_cwd="${cwd/#$HOME/~}"

# ─── Git branch ─────────────────────────────────────────────────────────────
branch=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null)
fi

# ─── Semantic colors ────────────────────────────────────────────────────────
case "$model_id" in
    *opus*)   model_color="${good}${bold}"   ;;
    *sonnet*) model_color="${warn}${bold}"   ;;
    *haiku*)  model_color="${bad}${bold}"    ;;
    *)        model_color="${warn}${bold}"   ;;
esac

if [ -n "$ctx_size" ] && [ "$ctx_size" -ge 1000000 ] 2>/dev/null; then
    ctx_mode="1M"
    ctx_mode_color="$good"
else
    case "${ctx_size:-}" in
        "")     ctx_mode="?" ;;
        200000) ctx_mode="200K" ;;
        *)      ctx_mode="$((ctx_size / 1000))K" ;;
    esac
    ctx_mode_color="$warn"
fi

effort="${CLAUDE_CODE_EFFORT_LEVEL:-}"
case "$effort" in
    max)           effort_display="MAX";    effort_color="$good" ;;
    xhigh)         effort_display="XHIGH";  effort_color="$info" ;;
    high|medium)   effort_display=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]'); effort_color="$warn" ;;
    low)           effort_display="LOW";    effort_color="$bad"  ;;
    "")            effort_display="";       effort_color=""      ;;
    *)             effort_display=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]'); effort_color="$warn" ;;
esac

ctx_pct_part=""
if [ -n "$used_pct" ]; then
    used_int=$(printf '%.0f' "$used_pct")
    if [ "$used_int" -ge 90 ]; then
        ctx_pct_part="${ctx_crit}${bold}ctx:${used_int}%${reset}"
    elif [ "$used_int" -ge 70 ]; then
        ctx_pct_part="${ctx_high}ctx:${used_int}%${reset}"
    elif [ "$used_int" -ge 20 ]; then
        ctx_pct_part="${ctx_mid}ctx:${used_int}%${reset}"
    else
        ctx_pct_part="${gray}ctx:${used_int}%${reset}"
    fi
fi

# ─── Compose ────────────────────────────────────────────────────────────────
sep=" ${gray}·${reset} "

left=""
[ -n "$short_cwd" ] && left+="${path_blue}${bold}${short_cwd}${reset}"
[ -n "$branch" ]    && left+="  ${gray}${bold}${branch}${reset}"

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
# Claude Code invokes this script with stdin = JSON, so stdin is not a tty.
# $COLUMNS isn't always exported into the subprocess, and `tput cols` /
# `stty size` need a tty — so probe several sources and take the largest.
detect_width() {
    local w="${COLUMNS:-}"
    [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null && printf '%s\n' "$w"

    # exec 2>/dev/null in the subshell suppresses bash's own "Device not
    # configured" when /dev/tty isn't available (e.g. non-interactive tests).
    w=$(exec 2>/dev/null; stty size </dev/tty | awk '{print $2}')
    [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null && printf '%s\n' "$w"

    w=$(exec 2>/dev/null; tput cols </dev/tty)
    [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null && printf '%s\n' "$w"
}
width=$(detect_width | sort -n | tail -1)
[ -z "$width" ] && width=200

strip_ansi() {
    printf '%s' "$1" | sed $'s/\033\\[[0-9;]*m//g'
}
left_len=$(strip_ansi "$left"  | wc -c | tr -d ' ')
right_len=$(strip_ansi "$right" | wc -c | tr -d ' ')
# Reserve 6 cols: 2 for Claude Code's leading indent, 4 for a right-edge
# margin so the final ctx:N% segment isn't truncated to `ctx:…`.
pad=$(( width - left_len - right_len - 6 ))
[ "$pad" -lt 1 ] && pad=1
padding=$(printf '%*s' "$pad" '')

printf '%b' "${left}${padding}${right}"
