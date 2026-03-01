---
name: heartbeat
description: >
  Autonomous heartbeat agent infrastructure. Managed by scripts/orchestrator.py
  and invoked periodically by launchd. Use when the user asks about autonomous
  periodic task processing or running Claude on a schedule. Do NOT use for
  one-time tasks or interactive work.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Bash(gh *), Bash(uv run python *), Bash(make *), Bash(ls *), Bash(mkdir *), Bash(date *)
---

Infrastructure skill — not interactive. The orchestrator (`scripts/orchestrator.py`)
handles issue discovery, worktree/PR lifecycle, and agent invocation. The agent
receives a templated prompt (`scripts/worker_prompt.md`) with full context.

## Labels

| Label | Meaning | Set by |
|-------|---------|--------|
| `ai:queued` | Ready for agent | Human |
| `ai:coding` | Agent working | Orchestrator |
| `ai:human` | Needs human | Agent (or orchestrator safety net) |

## Branch Naming

`ai/issue-N` — canonical, one branch per issue.
