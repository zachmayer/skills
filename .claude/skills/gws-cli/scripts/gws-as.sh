#!/bin/sh
# Run gws as a named profile.
# Usage: gws-as.sh <profile> [gws args...]
#
# Reads ~/.claude/gws-accounts.json to resolve profile names to config dirs.
# Falls back to ~/.config/gws/profiles/<profile>/ if no config file exists.

set -eu

if [ $# -lt 1 ]; then
    echo "Usage: gws-as.sh <profile> [gws args...]" >&2
    echo "" >&2
    echo "Available profiles:" >&2
    if [ -f "$HOME/.claude/gws-accounts.json" ]; then
        jq -r 'to_entries[] | select(.key != "default") | "  \(.key): \(.value.description // .value.email // .value.path)"' "$HOME/.claude/gws-accounts.json"
    else
        echo "  (no ~/.claude/gws-accounts.json found)" >&2
    fi
    exit 1
fi

profile="$1"
if ! echo "$profile" | grep -Eq '^[a-zA-Z0-9_-]+$'; then
    echo "ERROR: Invalid profile name '$profile'. Use only letters, numbers, hyphens, underscores." >&2
    exit 1
fi
shift

# Resolve config dir from accounts.json, or fall back to convention
if [ -f "$HOME/.claude/gws-accounts.json" ]; then
    config_dir=$(jq -r --arg p "$profile" '.[$p].path // empty' "$HOME/.claude/gws-accounts.json")
    # Expand ~ in path
    config_dir=$(echo "$config_dir" | sed "s|^~|$HOME|")
fi

if [ -z "${config_dir:-}" ]; then
    config_dir="$HOME/.config/gws/profiles/$profile"
fi

if [ ! -d "$config_dir" ]; then
    echo "ERROR: Profile '$profile' config dir not found: $config_dir" >&2
    echo "Run: mkdir -p '$config_dir' && GOOGLE_WORKSPACE_CLI_CONFIG_DIR='$config_dir' gws auth setup" >&2
    exit 1
fi

GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$config_dir" exec gws "$@"
