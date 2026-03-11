# Global Claude Instructions

## Model Preferences

Default to **Sonnet or Opus** for all subagents and reasoning tasks. Never request Haiku directly — the `ANTHROPIC_DEFAULT_HAIKU_MODEL` env var remaps all Haiku calls to Sonnet, so specifying Haiku just adds confusion with no cost savings. When choosing a model for a subagent, use Sonnet (the floor) or Opus (for complex reasoning).

## Shell Operators

A pre-tool-use hook blocks `&&`, `||`, backticks, and `$()` in Bash commands. This prevents shell injection via permission bypass. Run commands sequentially (separate tool calls) instead of chaining them. Use `git commit -F file` instead of `git commit -m "$(cat file)"`. Pipes (`|`) and semicolons (`;`) are allowed.

## Temporary Files

Use `~/claude/scratch/` for all temporary files (PR bodies, commit messages, scripts, intermediate data, etc.).
Do NOT write to `/tmp/` — on macOS, `/tmp` is a symlink and Claude Code cannot auto-approve writes there (upstream bug: anthropics/claude-code#29098).

## Git Workflow

- **Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR. The human merges.
- **Use worktrees** when the current branch is occupied: `git worktree add ~/claude/worktrees/project-<name> main` then branch from there.
- **Atomic PRs.** Each PR should be independently mergeable. Don't bundle unrelated changes.
- **Keep PR title and description current.** When the scope of a PR evolves, update the title and body to reflect what the PR actually does now — not what it started as.

## Code Quality

- **Never band-aid broken code with try/except.** If an API doesn't exist, a feature doesn't work, or a code path is dead — remove it. Don't wrap known-broken calls in error handlers to "keep the script running." That hides bugs and makes the codebase harder to reason about. The correct fix is always: remove the broken thing, or fix it properly.
- **Prefer deletion over suppression.** Dead code, unavailable APIs, and unfinished features should be removed until they're actually ready. An absent feature is honest; a silently-swallowed exception is a lie.
