# Global Claude Instructions

## Model Preferences

Default to **Sonnet or Opus** for all subagents and reasoning tasks. Use Haiku only for genuinely mechanical work (token counting, simple parsing, trivial transforms). When in doubt, use Sonnet. The `ANTHROPIC_DEFAULT_HAIKU_MODEL` env var enforces Sonnet as the floor — this preference explains the intent behind it.

## Shell Operators

A pre-tool-use hook blocks `&&`, `||`, backticks, and `$()` in Bash commands. This prevents shell injection via permission bypass. Run commands sequentially (separate tool calls) instead of chaining them. Use `git commit -F file` instead of `git commit -m "$(cat file)"`. Pipes (`|`) and semicolons (`;`) are allowed.

## Temporary Files

Use `~/claude/scratch/` for all temporary files (PR bodies, commit messages, scripts, intermediate data, etc.).
Do NOT write to `/tmp/` — on macOS, `/tmp` is a symlink and Claude Code cannot auto-approve writes there (upstream bug: anthropics/claude-code#29098).

## Git Workflow

- **Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR. The human merges.
- **Use worktrees** when the current branch is occupied: `git worktree add ~/claude/worktrees/project-<name> main` then branch from there.
- **Atomic PRs.** Each PR should be independently mergeable. Don't bundle unrelated changes.
