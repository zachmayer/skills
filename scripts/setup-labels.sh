#!/bin/bash
# Create status:human, status:lead, status:dev labels across all heartbeat repos.
# Idempotent: --force overwrites existing labels with the same name.
set -euo pipefail

REPOS_FILE="${HOME}/.claude/heartbeat-repos.conf"
if [ -f "$REPOS_FILE" ]; then
    REPOS=$(grep -v '^\s*#' "$REPOS_FILE" | grep -v '^\s*$' | tr '\n' ' ')
fi
REPOS="${REPOS:-zachmayer/skills}"

LABELS=(
    "status:human|#0E8A16|Human action needed"
    "status:lead|#1D76DB|Lead agent: route, scope, review"
    "status:dev|#D93F0B|Dev agent: build"
)

for repo in $REPOS; do
    echo "=== $repo ==="
    for entry in "${LABELS[@]}"; do
        IFS='|' read -r name color description <<< "$entry"
        if gh label create "$name" --repo "$repo" --color "${color#\#}" --description "$description" --force 2>/dev/null; then
            echo "  $name OK"
        else
            echo "  $name FAILED"
        fi
    done
done

echo "Done."
