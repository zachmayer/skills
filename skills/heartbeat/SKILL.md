---
name: heartbeat
description: >
  Set up or run a cron-based heartbeat that periodically invokes Claude Code
  to check for and process pending tasks. Use when the user wants autonomous
  periodic task processing or asks about running Claude on a schedule.
  Do NOT use for one-time tasks or interactive work.
allowed-tools: Bash(*)
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

This installs a macOS launchd user agent that runs every 4 hours. It replaces any old cron-based heartbeat automatically.

**Why launchd over cron:**
- Sleep/wake resilience — fires missed jobs on wake (cron silently drops them)
- Runs in user security session (Keychain access if needed)
- Apple-supported (cron is legacy, broken on Sonoma)
- Declarative environment, process priority, and logging

## Heartbeat Behavior

On each cycle, the heartbeat agent:
1. Sources `~/.claude/heartbeat.env` for the OAuth token
2. Explicitly unsets `ANTHROPIC_API_KEY` to force subscription billing
3. Checks `$CLAUDE_OBSIDIAN_DIR/heartbeat/tasks.md` for pending items
4. Processes at most ONE task per cycle (with --max-turns 20, --max-budget-usd 1, 10min timeout)
5. Records outcome to `~/.claude/heartbeat.status` (OK, TIMEOUT, or FAIL)
6. If it has a question, writes to `$CLAUDE_OBSIDIAN_DIR/heartbeat/questions.md`

## Task Queue

Edit `$CLAUDE_OBSIDIAN_DIR/heartbeat/tasks.md`:

```markdown
## Pending

- [ ] Review obsidian notes for stale information

## Completed

- [x] 2026-02-10T15:00:00Z: Example completed task
```

## Managing

- **Check log**: `tail -20 ~/claude/obsidian/heartbeat/heartbeat.log`
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
