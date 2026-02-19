---
name: heartbeat
description: >
  Autonomous heartbeat agent behavior. Invoked periodically by launchd to
  work on GitHub Issues, create PRs, and maintain the obsidian vault. Use when
  the user wants autonomous periodic task processing or asks about running
  Claude on a schedule. Do NOT use for one-time tasks or interactive work.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status), Bash(git diff *), Bash(git log *), Bash(git add *), Bash(git commit *), Bash(git checkout *), Bash(git branch *), Bash(git push *), Bash(git pull *), Bash(git fetch *), Bash(git -C *), Bash(git worktree *), Bash(gh pr create *), Bash(gh pr view *), Bash(gh pr list *), Bash(gh issue edit *), Bash(gh issue close *), Bash(gh issue comment *), Bash(ls *), Bash(mkdir *), Bash(date *), Bash(uv run python *)
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
gh issue edit N --repo OWNER/REPO --add-label in-progress
```

If `git checkout -b` fails, the issue is already claimed by another agent. **Pick a different issue and try again.** The `in-progress` label prevents other agents from picking up the same issue in future cycles (the runner filters it out).

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

**For research/memory tasks** (no code changes needed):
1. Write findings to obsidian vault
2. Comment a summary of findings on the issue: `gh issue comment N --repo OWNER/REPO --body "..."`
3. Close the issue: `gh issue close N --repo OWNER/REPO`
4. No PR needed — the issue comment is the deliverable

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

## 6. Parallel Safety

Multiple agents may run concurrently — this is by design.
- **Branches are claims.** `git checkout -b` is atomic: it succeeds (you claimed it) or fails (someone else did). If it fails, pick another issue.
- If you find a duplicate PR already open for your issue, skip it and log why.
- Do NOT modify files outside your worktree or the obsidian vault.
