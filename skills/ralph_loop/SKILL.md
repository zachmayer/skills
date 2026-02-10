---
name: ralph_loop
description: >
  Execute an autonomous development loop: decompose a feature into right-sized
  stories, implement one per iteration with fresh context, validate with tests,
  and repeat until complete. Time-aware — scales ambition to available time.
  Use when building a complete feature, working through a PRD or spec, or
  tackling a multi-step implementation. Do NOT use for single-task fixes or
  quick edits.
---

Execute a Ralph-style autonomous development loop for: $ARGUMENTS

Also apply these skills throughout the loop:
- `ultra_think` for architectural decisions and complex debugging
- `beast_mode` for maximum persistence — don't stop until it's solved
- `staff_engineer` for engineering standards and anti-sycophancy
- `ask_questions` if requirements are unclear — clarify before building
- `hierarchical_memory` to read past context and save learnings
- `obsidian` to record durable knowledge and architectural decisions

## Phase 0: Bootstrap (do this fast)

The goal is to gather everything you need from the user and the environment **up front** so the loop runs without interruption.

**Ask the user immediately:**
- "How long do you have?" (e.g. "2 hours", "overnight", "30 minutes")

**In parallel, while waiting for the answer:**
- Check the current time: `date`
- Read working memory (`hierarchical_memory`) for project context
- Note which tool permissions are available — this determines what you can do without prompting the user mid-loop

Compute a **deadline** from the user's answer + current time. This drives pacing for the rest of the loop.

## Phase 1: Decompose

Break the feature into right-sized stories. Each must complete in one context window. Order by dependency (database first, backend, then UI).

- Good: "Add database column with migration", "Create API endpoint for X", "Add filter dropdown to list"
- Bad: "Build entire dashboard", "Add authentication"

If a story can't complete in one pass, split it.

Track stories in a `prd.json` or similar manifest with pass/fail status.

```json
{
  "project": "project-name",
  "branchName": "ralph/feature-name",
  "deadline": "2026-02-10T22:00:00",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add database migration",
      "size": "medium",
      "acceptanceCriteria": ["Migration adds status column", "Tests pass"],
      "priority": 1,
      "passes": false
    }
  ]
}
```

## Phase 2: The Loop

For each iteration: **select, implement, validate, commit.**

1. **Check the clock** — `date`. Compute time remaining until deadline.
2. **Select** the highest-priority incomplete story that fits the remaining time.
3. **Implement** with fresh context. Re-read relevant code. Follow existing patterns. Stay in scope.
4. **Validate** with the project's quality checks (typecheck, lint, test). Fix failures before proceeding.
5. **Mark complete**, save learnings to `hierarchical_memory`, and commit.
6. **Repeat** from step 1.

### Time-aware pacing

| Time remaining | Story size | Ambition |
|---------------|------------|----------|
| > 50% of budget | Large | Tackle hard stories, architectural changes, new features |
| 25–50% | Medium | Solid implementation work, tests, integrations |
| 10–25% | Small | Quick wins, polish, documentation, cleanup |
| < 10% | Wrap up | Stop starting new stories. Finish current work. |

### At the deadline

You can keep working past the deadline — the user may or may not interrupt. But as you approach it:

1. **Finish** the current story if close to done, otherwise leave it clearly marked incomplete
2. **Commit and push** all work
3. **Write a status report** — output to the user:
   - What you completed
   - What's in progress or remaining
   - What you'd tackle next
   - Any decisions or blockers that need the user's input
4. **Save learnings** to `hierarchical_memory`
5. **Aggregate memory** if enough notes accumulated — run `status` to check

The user will read this report and decide what to do next.

## Key Principles

**Fresh context per iteration**: Each story gets a clean mental slate. Re-read relevant code. Use the Task tool for sub-agents when stories are independent.

**Validation is mandatory**: Never mark a story complete if tests fail. Broken code compounds across iterations.

**Front-load risk**: Do the hardest, most uncertain stories first while you have the most time to recover.
