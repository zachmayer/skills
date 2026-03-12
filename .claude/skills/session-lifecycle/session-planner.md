# Session Planner

Read available context, then propose a focused work plan for this session.

## Inputs

Gather these (skip any that don't exist):

1. **Hierarchical memory** — `read-overall` for current priorities and context
2. **Task queue** — `gh issue list --label ai:queued,ai:coding --state open` (heartbeat pipeline items)
3. **Git state** — `git status`, recent commits, open PRs/branches
4. **TodoWrite** — any existing todo list from a prior session
5. **Time budget** — ask if not stated (15min / 1hr / half-day / open-ended)

## Output

Present a short session plan:

```
## Session Plan — <date>

**Time budget:** <duration>
**Context:** <1-sentence summary of current state from memory>

### Proposed tasks (in priority order)
1. <task> — <why now, estimated effort>
2. <task> — <why now, estimated effort>
3. <task> — <stretch goal if time permits>

### Not today
- <task> — <why deferred>

### Blockers / questions
- <anything that needs human input before starting>
```

## Rules

- **3 tasks max** for the main plan. A focused session beats a scattered one.
- **Prioritize:** unfinished in-progress work > blocked items with new info > highest-leverage open task > recurring maintenance.
- **Be concrete.** "Fix the flaky test in auth.py" not "work on testing."
- **Mention dependencies.** If task 2 depends on task 1, say so.
- **Adapt to time.** 15-minute session = 1 task. Half-day = 2-3 tasks with a stretch goal.
- **Don't execute.** This skill produces a plan. The user (or ralph-loop) executes it.
