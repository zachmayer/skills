#!/bin/bash
# Claude Code status line.
# Reads the session JSON payload from stdin and prints one line:
#   ~/path (branch) [Model 1M | effort] ctx:NN%
#
# Schema reference: https://code.claude.com/docs/en/statusline.md

set -u

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

short_cwd="${cwd/#$HOME/~}"

branch=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null)
fi

# Reasoning effort isn't surfaced in the statusline payload; Claude Code exports
# CLAUDE_CODE_EFFORT_LEVEL into the hook/command environment.
effort="${CLAUDE_CODE_EFFORT_LEVEL:-}"

# Model label — append "1M" suffix for extended-context model variants.
model_label="$model"
if [ "$ctx_size" = "1000000" ] && [ -n "$model_label" ]; then
    model_label="$model_label 1M"
fi

model_bracket=""
if [ -n "$model_label" ] && [ -n "$effort" ]; then
    model_bracket="[$model_label | $effort]"
elif [ -n "$model_label" ]; then
    model_bracket="[$model_label]"
elif [ -n "$effort" ]; then
    model_bracket="[$effort]"
fi

parts=()
[ -n "$short_cwd" ] && parts+=("$short_cwd")
[ -n "$branch" ] && parts+=("($branch)")
[ -n "$model_bracket" ] && parts+=("$model_bracket")
if [ -n "$used_pct" ]; then
    used_int=$(printf '%.0f' "$used_pct")
    parts+=("ctx:${used_int}%")
fi

printf '%s' "${parts[*]}"
