#!/bin/bash
# Claude Code status line.
#
# Left:   ~/path  branch
# Middle: 5h:NN% NhNm · 7d:NN% NdNh       (Claude.ai rate limits; each optional)
# Right:  Model · ctx-mode · EFFORT · ctx:NN%
#
# Dependencies: jq, git.
#
# Palette uses ColorBrewer qualitative + sequential scales mapped to the
# 256-color terminal palette. Green = good, gold = warn, red = bad, blue =
# info; gray for identity/low-priority. Usage % (ctx and rate-limit) share a
# YlOrRd sequential gradient — never green, since usage always trends one way.
# Time-left is always gray — a single color, no gradient.
#
# Semantic color map:
#   model:   Opus  = green (71)    | Sonnet = gold (178)    | Haiku = red (160)
#   ctx:     1M    = green (71)    | other  = gold (178)
#   effort:  MAX   = green (71)    | xhigh  = sky blue (117) | high/medium = gold (178) | low = red (160)
#   usage %: <20   = gray (244)    | 20-69  = gold (221)     | 70-89 = orange (208) | >=90 = dark red (124) bold
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
pct_mid=$'\033[38;5;221m'       # YlOrRd mid
pct_high=$'\033[38;5;208m'      # YlOrRd orange
pct_crit=$'\033[38;5;124m'      # YlOrRd dark red

# ─── Parse payload (single jq pass → unit-separated fields → read) ──────────
# Unit-separator (0x1F) delimiter so bash doesn't collapse adjacent empty
# fields like it does with tab/space IFS. Process substitution (not a pipe
# into read) keeps the variables in this shell.
input=$(cat)
IFS=$'\x1F' read -r cwd model model_id ctx_size used_pct five_pct five_at week_pct week_at < <(
    jq -r '[(.workspace.current_dir // .cwd // ""),
            (.model.display_name // ""),
            (.model.id // ""),
            (.context_window.context_window_size // ""),
            (.context_window.used_percentage // ""),
            (.rate_limits.five_hour.used_percentage // ""),
            (.rate_limits.five_hour.resets_at // ""),
            (.rate_limits.seven_day.used_percentage // ""),
            (.rate_limits.seven_day.resets_at // "")]
           | map(tostring) | join("\u001F")' <<< "$input"
)

# Strip " (1M context)" or similar parentheticals — we show 1M as its own segment.
model="${model% (*}"
short_cwd="${cwd/#$HOME/~}"

# ─── Git branch (short SHA fallback for detached HEAD) ──────────────────────
branch=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null \
             || git -C "$cwd" -c core.fsmonitor=false rev-parse --short HEAD 2>/dev/null)
fi

# ─── Semantic colors ────────────────────────────────────────────────────────
case "$model_id" in
    *opus*)   model_color="${good}${bold}"   ;;
    *sonnet*) model_color="${warn}${bold}"   ;;
    *haiku*)  model_color="${bad}${bold}"    ;;
    *)        model_color="${warn}${bold}"   ;;
esac

ctx_mode=""
ctx_mode_color="$warn"
if [ -n "$ctx_size" ]; then
    if [ "$ctx_size" -ge 1000000 ] 2>/dev/null; then
        ctx_mode="1M"
        ctx_mode_color="$good"
    elif [ "$ctx_size" = "200000" ]; then
        ctx_mode="200K"
    else
        ctx_mode="$((ctx_size / 1000))K"
    fi
fi

effort="${CLAUDE_CODE_EFFORT_LEVEL:-}"
case "$effort" in
    max)   effort_color="$good" ;;
    xhigh) effort_color="$info" ;;
    low)   effort_color="$bad"  ;;
    "")    effort_color=""      ;;
    *)     effort_color="$warn" ;;
esac
effort_display=""
[ -n "$effort" ] && effort_display=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]')

# YlOrRd gradient shared by ctx% and rate-limit %.
pct_color() {
    local p=$1
    if   [ "$p" -ge 90 ]; then printf '%s%s' "$pct_crit" "$bold"
    elif [ "$p" -ge 70 ]; then printf '%s' "$pct_high"
    elif [ "$p" -ge 20 ]; then printf '%s' "$pct_mid"
    else                       printf '%s' "$gray"
    fi
}

# Format seconds as NdNh / NhNm / Nm — whichever pair of units fits best.
fmt_dur() {
    local s=$1
    [ "$s" -le 0 ] && { printf '0m'; return; }
    local d=$((s / 86400))
    local h=$(((s % 86400) / 3600))
    local m=$(((s % 3600) / 60))
    if   [ "$d" -gt 0 ]; then printf '%dd%dh' "$d" "$h"
    elif [ "$h" -gt 0 ]; then printf '%dh%dm' "$h" "$m"
    else                      printf '%dm' "$m"
    fi
}

ctx_pct_part=""
if [ -n "$used_pct" ]; then
    used_int=$(LC_NUMERIC=C printf '%.0f' "$used_pct")
    ctx_pct_part="$(pct_color "$used_int")ctx:${used_int}%${reset}"
fi

# ─── Rate-limit segments (Claude.ai only; each window independently optional)
now_s=$(date +%s)
rate_segs=()

# Rate-limit fields only appear in Claude Code's JSON after the first API
# response in a session. Cache them so timers survive session starts and
# idle/sleep gaps (refreshInterval recomputes time-left from the stored
# resets_at epoch each tick).
cache_file="${HOME}/.claude/cache/statusline-rate-limits.json"
if [ -n "$five_pct" ] || [ -n "$week_pct" ]; then
    mkdir -p "${cache_file%/*}"
    jq -n --arg fp "$five_pct" --arg fa "$five_at" \
          --arg wp "$week_pct" --arg wa "$week_at" \
          '{five_pct:$fp, five_at:$fa, week_pct:$wp, week_at:$wa}' \
          > "$cache_file.tmp.$$" 2>/dev/null \
        && mv "$cache_file.tmp.$$" "$cache_file"
elif [ -r "$cache_file" ]; then
    IFS=$'\x1F' read -r five_pct five_at week_pct week_at < <(
        jq -r '[(.five_pct // ""), (.five_at // ""),
                (.week_pct // ""), (.week_at // "")]
               | map(tostring) | join("")' "$cache_file" 2>/dev/null
    )
fi

build_rate() {
    local label=$1 pct_raw=$2 at=$3
    [ -z "$pct_raw" ] && return
    local p seg
    p=$(LC_NUMERIC=C printf '%.0f' "$pct_raw")
    seg="$(pct_color "$p")${label}:${p}%${reset}"
    if [ -n "$at" ]; then
        # Strip any fractional part — jq preserves floats, but bash arithmetic doesn't.
        local secs_left=$(( ${at%.*} - now_s ))
        # Skip windows whose reset has already passed (stale cache from a previous day).
        [ "$secs_left" -le 0 ] && return
        seg="${seg} ${gray}$(fmt_dur "$secs_left")${reset}"
    fi
    rate_segs+=("$seg")
}

build_rate "5h" "$five_pct" "$five_at"
build_rate "7d" "$week_pct" "$week_at"

# ─── Compose ────────────────────────────────────────────────────────────────
sep=" ${gray}·${reset} "

join_segs() {
    local out=""
    for s in "$@"; do
        if [ -n "$out" ]; then out="$out$sep$s"; else out="$s"; fi
    done
    printf '%s' "$out"
}

left=""
[ -n "$short_cwd" ] && left+="${path_blue}${bold}${short_cwd}${reset}"
[ -n "$branch" ]    && left+="  ${gray}${bold}${branch}${reset}"

middle=""
[ "${#rate_segs[@]}" -gt 0 ] && middle=$(join_segs "${rate_segs[@]}")

right_segs=()
[ -n "$model" ]          && right_segs+=("${model_color}${model}${reset}")
[ -n "$ctx_mode" ]       && right_segs+=("${ctx_mode_color}${ctx_mode}${reset}")
[ -n "$effort_display" ] && right_segs+=("${effort_color}${effort_display}${reset}")
[ -n "$ctx_pct_part" ]   && right_segs+=("$ctx_pct_part")

right=""
[ "${#right_segs[@]}" -gt 0 ] && right=$(join_segs "${right_segs[@]}")

# ─── Pad apart ──────────────────────────────────────────────────────────────
# Claude Code invokes this script with stdin = JSON, so stdin is not a tty.
# Prefer $COLUMNS (Claude Code sets it correctly), then tty probes. Return on
# first valid source — the previous "take the largest" logic was wrong when a
# stale $COLUMNS overshot the actual terminal and pushed content off-screen.
detect_width() {
    local w="${COLUMNS:-}"
    if [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null; then printf '%s\n' "$w"; return; fi

    # exec 2>/dev/null in the subshell suppresses bash's own "Device not
    # configured" when /dev/tty isn't available (e.g. non-interactive tests).
    w=$(exec 2>/dev/null; stty size </dev/tty | awk '{print $2}')
    if [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null; then printf '%s\n' "$w"; return; fi

    w=$(exec 2>/dev/null; tput cols </dev/tty)
    if [ -n "$w" ] && [ "$w" -ge 40 ] 2>/dev/null; then printf '%s\n' "$w"; return; fi
}
width=$(detect_width)
[ -z "$width" ] && width=200

strip_ansi() {
    printf '%s' "$1" | sed $'s/\033\\[[0-9;]*m//g'
}
left_len=$(strip_ansi "$left"   | wc -m | tr -d ' ')
mid_len=$(strip_ansi "$middle"  | wc -m | tr -d ' ')
right_len=$(strip_ansi "$right" | wc -m | tr -d ' ')

# Reserve 6 cols: 2 for Claude Code's leading indent, 4 for a right-edge
# margin so the final ctx:N% segment isn't truncated to `ctx:…`.
# With middle present, center the middle cluster in the usable width — not
# the whitespace — so the cluster stays in the middle even when left and
# right clusters have different widths.
usable=$(( width - 6 ))
if [ "$mid_len" -eq 0 ]; then
    pad1=$(( usable - left_len - right_len ))
    [ "$pad1" -lt 1 ] && pad1=1
    pad2=0
else
    pad1=$(( (usable - mid_len) / 2 - left_len ))
    [ "$pad1" -lt 1 ] && pad1=1
    pad2=$(( usable - left_len - mid_len - right_len - pad1 ))
    [ "$pad2" -lt 1 ] && pad2=1
fi

pad1_s=$(printf '%*s' "$pad1" '')
pad2_s=""
[ "$pad2" -gt 0 ] && pad2_s=$(printf '%*s' "$pad2" '')

printf '%s' "${left}${pad1_s}${middle}${pad2_s}${right}"
