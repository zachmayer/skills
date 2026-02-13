---
name: heartbeat
description: >
  Set up or run a launchd-based heartbeat that periodically invokes Claude Code
  to check for and process pending tasks. Use when the user wants autonomous
  periodic task processing or asks about running Claude on a schedule.
  Do NOT use for one-time tasks or interactive work.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status), Bash(git diff *), Bash(git log *), Bash(git add *), Bash(git commit *), Bash(git checkout *), Bash(git branch *), Bash(git push *), Bash(gh pr create *), Bash(gh pr view *), Bash(ls *), Bash(mkdir *), Bash(date *), Bash(uv run *)
---

Set up or manage a heartbeat for autonomous Claude Code task processing.

Also apply `hierarchical_memory` and `obsidian` for reading context and persisting results.

## Setup

Run `make setup-heartbeat-token` first, then `make install-heartbeat`.

### 1. Generate an OAuth token (one-time, interactive)

```bash
claude setup-token
```

This opens a browser for OAuth. It produces a 1-year token that uses your Claude subscription (not API billing).

### 2. Save the token

```bash
echo "export CLAUDE_CODE_OAUTH_TOKEN=<paste-token>" > ~/.claude/heartbeat.env
chmod 600 ~/.claude/heartbeat.env
```

### 3. Install the launchd agent

```bash
make install-heartbeat
```

This installs a macOS launchd user agent that runs every hour. It replaces any old cron-based heartbeat automatically.

**Why launchd over cron:**
- Sleep/wake resilience — fires missed jobs on wake (cron silently drops them)
- Runs in user security session (Keychain access if needed)
- Apple-supported (cron is legacy, broken on Sonoma)
- Declarative environment, process priority, and logging

## Heartbeat Agent Instructions

You are the heartbeat agent. You wake up every hour to process tasks autonomously. The human reviews your PRs in the morning.

### Scheduling

- You are invoked every **1 hour** by launchd.
- Target **30 minutes** of work per cycle. Usually you'll finish in 30 min, sleep 30 min, then the next heartbeat fires.
- If a task takes longer, keep going — the lock file prevents the next heartbeat from overlapping.
- Hard kill at **4 hours**. If you're still running, the watchdog kills you.
- Work on **multiple tasks** per cycle using a Ralph loop. Read your `ralph_loop` skill for methodology.

### Before Starting

1. Read the task file at `$CLAUDE_OBSIDIAN_DIR/heartbeat/tasks.md` (the launcher passes this path).
2. Read `$CLAUDE_OBSIDIAN_DIR/heartbeat/heartbeat.log` (last 50 lines) for context from prior cycles.
3. Check obsidian vault for relevant context: hierarchical memory (`memory/` directory), knowledge graph notes, and any prior heartbeat questions.
4. If the previous cycle was killed or errored, check for in-progress tasks and pick up where it left off.

### Task Processing

The task file uses three sections:

```markdown
## Open

- [ ] RECURRING: Pick up unchecked roadmap items from README.md...
- [ ] One-time task description

## In Progress

- [~] Task being worked on
  - PR: https://github.com/owner/repo/pull/123
  - Branch: heartbeat/short-name
  - Status: implementing X, tests passing

## Completed

- [x] 2026-02-10T15:00:00Z: Task description
```

**Workflow:**
1. Move a task from Open to In Progress when you start it. Add sub-bullets for tracking.
2. Update sub-bullets as you work (branch name, PR link, current status).
3. Move to Completed with timestamp when done.
4. For `RECURRING` tasks, leave them in Open — they repeat every cycle.
5. If a task needs permissions you don't have, mark it as blocked with a note.

### Logging

Write good logs so the next heartbeat cycle can pick up your progress:
- Update task sub-bullets with what you're working on and links to PRs/branches.
- If you get killed mid-task, the next cycle reads In Progress and continues.
- Write questions to `$CLAUDE_OBSIDIAN_DIR/heartbeat/questions.md` if you need human input.

### PR Workflow (for README roadmap tasks)

1. Start from `main` branch: `git checkout main && git pull`
2. Create a feature branch: `git checkout -b heartbeat/<short-name>`
3. Implement the change, commit with descriptive message
4. Push: `git push -u origin heartbeat/<short-name>`
5. Create PR: `gh pr create --title "..." --body "..."`
6. Update the task sub-bullets with the PR link

## Permissions (dontAsk mode)

The heartbeat runs with **least-privilege permissions** — no `--dangerously-skip-permissions`. Uses `--permission-mode dontAsk` which auto-denies anything not explicitly allowed.

**Allowed tools:**
- File ops: Read, Write, Edit, Glob, Grep (cwd + `--add-dir` for obsidian vault)
- Git (full workflow): git status, diff, log, add, commit, checkout, branch, push
- GitHub: gh pr create
- Utilities: ls, mkdir, date, uv run

**Denied (silently):** curl, wget, rm, sudo, chmod, and everything else. If a task needs broader permissions, mark it as blocked with a note explaining what's needed.

The safer the agent, the more the human can let it rip. Add tasks freely — the worst case is a task gets marked "blocked: needs permissions."

## Managing

- **Check log**: `tail -50 ~/claude/obsidian/heartbeat/heartbeat.log`
- **Check status**: `cat ~/.claude/heartbeat.status`
- **Test manually**: `make test-heartbeat`
- **Uninstall**: `make uninstall-heartbeat`
- **Verify running**: `launchctl list | grep claude-heartbeat`
- **Kick (run now)**: `launchctl kickstart gui/$(id -u)/com.anthropic.claude-heartbeat`

## Token Renewal

The OAuth token from `claude setup-token` lasts 1 year. To renew:

```bash
claude setup-token
# paste new token into ~/.claude/heartbeat.env
make install-heartbeat  # reloads the agent
```

Check `~/.claude/heartbeat.status` periodically — a FAIL status may indicate token expiry.
