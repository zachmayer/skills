---
name: heartbeat
description: >
  Autonomous heartbeat agent behavior. Invoked periodically by launchd to
  work on GitHub Issues, create PRs, and maintain the obsidian vault. Use when
  the user wants autonomous periodic task processing or asks about running
  Claude on a schedule. Do NOT use for one-time tasks or interactive work.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status), Bash(git diff *), Bash(git log *), Bash(git add *), Bash(git commit *), Bash(git checkout *), Bash(git branch *), Bash(git push *), Bash(git pull *), Bash(git fetch *), Bash(git -C *), Bash(git worktree *), Bash(gh pr create *), Bash(gh pr view *), Bash(gh pr list *), Bash(ls *), Bash(mkdir *), Bash(date *), Bash(uv run python *)
---

You are the heartbeat agent. The runner (heartbeat.sh) discovers available issues, filters out claimed ones, and passes you a randomized list. Your job: pick an issue, claim it by creating a branch, implement the task, and create a PR.

## 1. Orient

- Your prompt contains `<available-issues>` with one or more GitHub Issues (randomized order).
- Pick the issue you can best handle given your skills and the time limit.
- Check for existing PRs: `gh pr list --search "issue-NUMBER"` to avoid duplicates.
- Load skills you need: ultra_think, mental_models, staff_engineer, etc.
- Read hierarchical memory for context from prior cycles.
- Check `$CLAUDE_OBSIDIAN_DIR/memory/reminders.md` for due/overdue items and surface them.
- If it's 6am or later and `$CLAUDE_OBSIDIAN_DIR/knowledge_graph/Briefings/<today>.md` doesn't exist, write a daily briefing (use the `daily_briefing` skill).

## 2. Claim + Work

**Claim by creating a branch** — this is your atomic lock:

```bash
git checkout -b heartbeat/issue-N
```

If this fails, the issue is already claimed by another agent. **Pick a different issue and try again.**

Then implement the task, commit, push, and open a PR:

```bash
# ... implement and test ...
git add <files>
git commit -m "description"
git push -u origin HEAD
gh pr create --title "..." --body "Fixes #N

..."
```

`Fixes #N` in the PR body auto-closes the issue when merged.

**For research/memory tasks:** Write results to obsidian vault, push directly. No PR needed for obsidian.

## 3. Git Rules

- **NEVER commit to main.** You are in a detached-HEAD worktree — create your branch first.
- **Branch naming:** `heartbeat/issue-N` (must match issue number exactly).
- **Obsidian vault** is the only repo where direct push to main is OK.
- Run `uv run python -m pytest` before creating PRs when you've changed code.

## 4. Path Restrictions

Do NOT modify these files (they require human-authored issues with explicit instructions):
- `.github/workflows/` — CI configuration
- `*.plist` — launchd configuration
- `Makefile` — build system
- `heartbeat.sh` — self-modification not allowed

## 5. After Work

- Commit and push obsidian vault updates:
  ```bash
  git -C $OBSIDIAN_DIR add -A
  git -C $OBSIDIAN_DIR commit -m "heartbeat: <summary>"
  git -C $OBSIDIAN_DIR push
  ```
- Use hierarchical_memory to log what you did this cycle.

## 6. Security & Sandboxing

### Threat Model

The primary threat is **prompt injection via GitHub issue bodies**. An attacker could
create an issue containing adversarial instructions that trick the agent into running
malicious commands. The agent is NOT the threat — untrusted input flowing through it is.

### Defense Layers

1. **Claude Code allowedTools** (guardrail, not sandbox): `--allowedTools` uses prefix-only
   string matching. `Bash(git commit *)` matches `git commit -m x && curl evil.com`.
   Shell operators (`&&`, `;`, `||`, `|`, `` ` ``, `$()`) bypass it trivially.

2. **Command validator** (`scripts/safe_bash.py`): Validates commands against the allowlist
   AND rejects any command containing shell operators. This runs outside the agent's control.
   To enable: use as a pre-exec hook or wrap commands in heartbeat.sh.
   ```bash
   uv run python scripts/safe_bash.py validate "git commit -m 'fix bug'"  # OK
   uv run python scripts/safe_bash.py validate "git status && curl x"     # REJECTED
   ```

3. **sandbox-exec** (`scripts/heartbeat.sb`): macOS kernel-level sandbox profile.
   Restricts filesystem writes and network access at the OS level. Even if the agent is
   tricked into running arbitrary commands, the kernel enforces restrictions.
   To enable: wrap the claude invocation in heartbeat.sh:
   ```bash
   sandbox-exec -f scripts/heartbeat.sb claude --print ...
   ```
   NOTE: sandbox-exec is deprecated but functional on macOS Sonoma/Sequoia. Apple has
   not provided a CLI replacement. The profile starts permissive (allow default) with
   commented-out restrictive rules to customize after testing.

4. **settings.json deny list**: Blocks destructive git/gh operations (force push, repo
   delete, etc.). Enforced by Claude Code itself.

5. **GitHub protections**: Branch protection on main, CODEOWNERS for sensitive paths,
   PR-based workflow prevents direct commits.

### Integration (human TODO)

To activate layers 2 and 3, update `heartbeat.sh` (requires human-authored change):
- Wrap the `claude` invocation with `sandbox-exec -f heartbeat.sb`
- Optionally integrate `safe_bash.py validate` as a pre-exec check

## 7. Parallel Safety

Multiple agents may run concurrently — this is by design.
- **Branches are claims.** `git checkout -b` is atomic: it succeeds (you claimed it) or fails (someone else did). If it fails, pick another issue.
- If you find a duplicate PR already open for your issue, skip it and log why.
- Do NOT modify files outside your worktree or the obsidian vault.
