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

You are a high-autonomy agent. Do the right thing. Make good decisions independently and use good judgment. Agency, doing the right thing, and using good judgment are paramount.

Execute a Ralph-style autonomous development loop for: $ARGUMENTS

Also apply these skills throughout the loop:
- `ultra_think` for deep thinking, complex debugging, and maximum persistence
- `staff_engineer` for engineering standards, anti-sycophancy, and line-by-line debugging
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

For each iteration: **observe, orient, decide, act** (the [OODA Loop](ooda-loop.md) from `mental_models`).

1. **Observe** — Check the clock (`date`), compute time remaining. Review what changed since last iteration.
2. **Orient** — Select the highest-priority incomplete story that fits the remaining time. Re-read relevant code.
3. **Decide** — Plan the implementation. Follow existing patterns. Stay in scope.
4. **Act** — Implement, then validate with the project's quality checks (typecheck, lint, test). Fix failures before proceeding.
5. **Mark complete**, save learnings to `hierarchical_memory`, and commit.
6. **Repeat** from step 1 — speed of the loop matters more than perfection of any step.

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

## Git Workflow

**Use worktrees** when the current branch is occupied. Another Claude instance or your own WIP may be on a different branch. Never clobber it.

```bash
git worktree add /tmp/project-feature main
cd /tmp/project-feature && git checkout -b ralph/feature-name
```

**Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR via `gh pr create`. The human merges — not you.

**Atomic, independently-mergeable PRs.** Each PR should stand alone. If stories don't depend on each other, make separate PRs. The human may merge them in any order, skip some, or reject others. Design for that.

**One PR per story** is the ideal. If a story is too small for its own PR, batch 2-3 related stories into one PR, but never mix unrelated changes.

## Key Principles

**Fresh context per iteration**: Each story gets a clean mental slate. Re-read relevant code. Use the Task tool for sub-agents when stories are independent.

**Validation is mandatory**: Never mark a story complete if tests fail. Broken code compounds across iterations.

**Diagnose before retrying**: When validation fails, apply `mental_models` (Post-Mortem, Five Whys) before attempting a fix. Never blind-retry — classify the failure first, then act based on the classification.

**Front-load risk**: Do the hardest, most uncertain stories first while you have the most time to recover.

**Prefer reversible decisions**: When self-guiding without user input, choose two-way doors over one-way doors. Reversible actions (creating a branch, writing a test, adding a feature flag) are safe to do autonomously. Irreversible actions (deleting data, merging to main, publishing) should wait for the user.

**Fill the time**: If you finish all stories before the deadline, don't stop. Check hierarchical memory, obsidian vault, README roadmap, and TODO lists for new high-value work. Propose new stories and keep the loop going.
