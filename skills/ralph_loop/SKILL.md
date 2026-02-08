---
name: ralph_loop
description: >
  Execute an autonomous development loop: decompose a feature into right-sized
  tasks, implement one per iteration with fresh context, validate with tests,
  persist via git commits, and repeat until complete. Based on the Ralph pattern
  (snarktank/ralph). Use when building a complete feature, working through a
  PRD or spec, or tackling a multi-step implementation. Do NOT use for
  single-task fixes or quick edits.
---

Execute a Ralph-style autonomous development loop for: $ARGUMENTS

## The Loop

### 1. Decompose
If no task breakdown exists yet, decompose the feature into **right-sized tasks**:
- Each task must fit in a single context window
- Each task should be independently testable
- Good size: "add a database migration", "create a UI component", "write an API endpoint"
- Bad size: "build the entire dashboard", "add authentication"

Create a task manifest (tasks.md or prd.json) tracking:
- Task name and description
- Status: pending / in-progress / complete
- Acceptance criteria

### 2. Select
Pick the highest-priority incomplete task. Consider dependencies - a task that unblocks others comes first.

### 3. Implement
Focus on this single task:
- Read relevant existing code first
- Implement the minimum to satisfy acceptance criteria
- Follow existing patterns in the codebase
- Do not touch code outside the task's scope

### 4. Validate
Run the project's test and type-check suite:
- All existing tests must still pass
- New code should have tests if the project has a test suite
- Type checks must pass if the project uses them

If validation fails, fix the issues before proceeding.

### 5. Persist
- **Git commit** the working changes with a clear message
- **Update task status** to complete in the manifest
- **Record learnings** - Append to a progress.txt or AGENTS.md:
  - What patterns did you discover?
  - What gotchas should future iterations know about?
  - What conventions does this codebase follow?

### 6. Repeat
Return to step 2. Continue until:
- All tasks are marked complete, OR
- You've hit an iteration limit (default: 10), OR
- You're blocked and need human input

## Key Principles

**Fresh context per iteration**: Each task gets a clean mental slate. Don't carry assumptions from previous tasks. Re-read relevant code each time.

**Right-sized tasks**: If a task feels too big, split it. If you can't complete it in one pass, it's too big.

**AGENTS.md as institutional memory**: Update project documentation files with patterns and conventions you discover. Future iterations (and future developers) benefit from this accumulated knowledge.

**Validation is mandatory**: Never mark a task complete if tests fail. Broken code compounds across iterations.

**Git is your checkpoint**: Commit after each successful task. If something goes wrong, you can always roll back.

## Output

After each iteration, report:
- Which task was completed
- What was learned
- What task is next
- Overall progress (X of Y tasks complete)
