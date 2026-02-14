---
name: daily_briefing
description: >
  Morning orientation: what happened overnight, what's on your plate, what
  needs attention. Use at the start of the day, when the user says "brief me",
  "what happened", or "morning update". Do NOT use mid-session or for planning
  (use session_planner for that).
---

Gather context, then deliver a concise morning briefing.

## Gather (parallel where possible)

1. **Yesterday's memory** — `uv run --directory SKILL_DIR python skills/hierarchical_memory/scripts/memory.py read-day` (defaults to most recent day with notes)
2. **Heartbeat status** — `cat ~/.claude/heartbeat.status`
3. **Open PRs** — `gh pr list --repo zachmayer/skills --state open --json number,title,author,createdAt`
4. **Recently merged** — `gh pr list --repo zachmayer/skills --state merged --json number,title,mergedAt --limit 5`
5. **Open agent-task issues** — `gh issue list --repo zachmayer/skills --label agent-task --state open --json number,title --limit 10`
6. **Git state** — `git status`, current branch, any stale worktrees
7. **Overall memory** — scan for deadlines, TODOs, upcoming dates

## Deliver

Format as a briefing the user can scan in 30 seconds:

```
## Daily Briefing — <date>

### Overnight
- <what the heartbeat did: PRs created, issues completed, or "idle">

### Open PRs (need review)
- #N: title (by author, age)

### Active Issues (agent-task queue)
- N issues in queue. Top 3: #X title, #Y title, #Z title

### Deadlines & Reminders
- <anything time-sensitive from memory: tax deadlines, meetings, launches>

### Suggested Focus
- <1-2 sentence recommendation based on priorities and context>
```

## Rules

- **30 seconds to read.** If it's longer, cut it.
- **Flag what's new.** Bold or call out things that changed since yesterday.
- **Don't execute work.** This produces a briefing, not action. Use `session_planner` or `ralph_loop` to act.
- **Save the briefing** to the obsidian vault as `knowledge_graph/Briefings/<date>.md` so there's a record.
