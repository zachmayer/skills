---
name: ralph_loop
description: >
  Execute an autonomous development loop: decompose a feature into right-sized
  stories, implement one per iteration with fresh context, validate with tests,
  and repeat until complete. Based on the Ralph pattern (snarktank/ralph).
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

## The Loop

0. **Bootstrap** — Read working memory (`hierarchical_memory`) for context on the project, user preferences, and past decisions. If the feature requirements are ambiguous, use `ask_questions` before decomposing.
1. **Decompose** the feature into right-sized stories. Each must complete in one context window. Track them in a `prd.json` or similar manifest with pass/fail status.
2. **Select** the highest-priority incomplete story. Respect dependencies.
3. **Implement** that single story. Read relevant code first. Follow existing patterns. Stay in scope.
4. **Validate** with the project's quality checks (typecheck, lint, test). Fix failures before proceeding.
5. **Mark complete** and save learnings to `hierarchical_memory`. Commit.
6. **Repeat** from step 2 until all stories pass.

## Story Sizing

Each story must fit in one context window. Order by dependency (database first, backend, then UI).

- Good: "Add database column with migration", "Create API endpoint for X", "Add filter dropdown to list"
- Bad: "Build entire dashboard", "Add authentication"

If a story can't complete in one pass, split it.

## Suggested prd.json format

```json
{
  "project": "project-name",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add database migration",
      "acceptanceCriteria": ["Migration adds status column", "Tests pass"],
      "priority": 1,
      "passes": false
    }
  ]
}
```

## Key Principles

**Fresh context per iteration**: Each story gets a clean mental slate. Re-read relevant code. Use the Task tool for sub-agents when stories are independent.

**Validation is mandatory**: Never mark a story complete if tests fail. Broken code compounds across iterations.
