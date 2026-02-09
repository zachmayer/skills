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

## Setup

```bash
uv run python scripts/ralph.py init "feature description" --branch ralph/feature-name
```

### prd.json format

```json
{
  "project": "project-name",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add database migration",
      "description": "Create migration for new status column",
      "acceptanceCriteria": ["Migration adds status column", "Tests pass"],
      "priority": 1,
      "passes": false
    }
  ]
}
```

Each story must complete in one context window. Order by dependency (database first, backend, then UI).

## The Loop

### 1. Read state

```bash
uv run python scripts/ralph.py status
```

### 2. Select

Pick the highest-priority story with `passes: false`.

### 3. Implement

Focus on this single story. Read relevant code first. Follow existing patterns. Don't touch code outside the story's scope.

### 4. Validate

Run the project's quality checks (typecheck, lint, test). Fix failures before proceeding.

### 5. Complete

```bash
uv run python scripts/ralph.py complete US-001
```

Save learnings to `hierarchical_memory`. Commit.

### 6. Repeat

Return to step 2 until all stories pass.

## Key Principles

**Fresh context per iteration**: Each story gets a clean mental slate. Re-read relevant code. Use the Task tool for sub-agents when stories are independent.

**Right-sized stories**: If it can't complete in one pass, split it with `ralph.py split US-003 "subtask a" "subtask b"`.

**Validation is mandatory**: Never mark a story complete if tests fail.
