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
runs a three-phase pipeline per heartbeat cycle. Agent files live in `agents/` and
are installed to `~/.claude/agents/` via `make install`.

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
| `agents/queue.md` | Queue | $1 | Scope the issue, post plan or questions |
| `agents/coding.md` | Coding | $8 | Write code, run tests, self-review |
| `agents/review.md` | Review | $2 | Review PR, approve or request changes |

## Branch Naming

`ai/issue-N` — canonical, one branch per issue.
