---
name: heartbeat
description: >
  Autonomous heartbeat agent that processes GitHub issues on a schedule via
  launchd. Three-phase pipeline: queue (scope issues), coding (write code +
  tests), review (approve or request changes). Use when the user says
  "heartbeat", "autonomous agent", "scheduled tasks", "run Claude on a cron",
  or asks how issues get auto-processed. Do NOT use for one-time tasks,
  interactive work, or manual issue triage.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Bash(gh *), Bash(uv run python *), Bash(make *), Bash(ls *), Bash(mkdir *), Bash(date *)
---

Infrastructure skill — not interactive. The orchestrator (`scripts/orchestrator.py`)
runs a three-phase pipeline per heartbeat cycle. Agent files live in `.claude/agents/`
and are symlinked to `~/.claude/agents/` via `make install`.

## Pipeline

```
Loop 1: Queue   (ai:queued → queue agent → ai:coding)
Loop 2: Coding  (ai:coding → coding agent → ai:review)
Loop 3: Review  (ai:review → review agent → human)
```

## Labels

| Label | Color | Meaning | Set by |
|-------|-------|---------|--------|
| `ai:queued` | blue | In the AI queue; heartbeat picks up next cycle | Human |
| `ai:coding` | yellow | AI agent is actively coding; do not modify | Orchestrator |
| `ai:review` | purple | PR needs review; AI or human can review | Orchestrator |
| *(no label)* | — | Human's turn (scoping questions, or PR assigned for merge) | Orchestrator |

## Agents

| File | Phase | Budget | Purpose |
|------|-------|--------|---------|
| `.claude/agents/queue.md` | Queue | $1 | Scope the issue, post plan or questions |
| `.claude/agents/coding.md` | Coding | $8 | Write code, run tests, self-review |
| `.claude/agents/review.md` | Review | $2 | Review PR, approve or request changes |

## Branch Naming

`ai/issue-N` — canonical, one branch per issue.
