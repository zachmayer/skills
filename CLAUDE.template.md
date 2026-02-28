# Global Claude Instructions

## Temporary Files

Use `~/claude/scratch/` for all temporary files (PR bodies, commit messages, scripts, intermediate data, etc.).
Do NOT write to `/tmp/` — on macOS, `/tmp` is a symlink and Claude Code cannot auto-approve writes there (upstream bug: anthropics/claude-code#29098).

## Git Workflow

- **Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR. The human merges.
- **Use worktrees** when the current branch is occupied: `git worktree add /tmp/project-<name> main` then branch from there. (Worktree creation via Bash is fine — only Write/Edit tools are affected by the /tmp bug above.)
- **Atomic PRs.** Each PR should be independently mergeable.
