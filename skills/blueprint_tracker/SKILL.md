---
name: blueprint_tracker
description: >
  Structured markdown tracking project state, dependencies, and attempts.
  Use when working on a multi-step project that spans sessions, when you need
  to track what was tried and what worked, or when tasks have dependencies.
  Do NOT use for single-session work (use TodoWrite) or daily notes
  (use hierarchical_memory).
---

# Blueprint Tracker

Maintain a structured markdown file that tracks project state across sessions. A blueprint is a living document — read it at session start, update it as you work, commit it when done.

## When to Create a Blueprint

- A project has 3+ components or tasks with dependencies
- Work will span multiple sessions or agents
- You need to track what was attempted and why it succeeded or failed

## Blueprint Location

Store blueprints in the project repo at `.claude/blueprint.md`. For multi-project tracking, use `.claude/blueprint-<name>.md`.

If the project has no repo (e.g. research), store in `$CLAUDE_OBSIDIAN_DIR/blueprints/<project-name>.md`.

## Blueprint Format

```markdown
# Blueprint: <Project Name>

**Goal:** <one-sentence objective>
**Status:** <not-started | in-progress | blocked | done>
**Last updated:** <YYYY-MM-DD>

## Components

### <Component Name>
- **Status:** <not-started | in-progress | blocked | done>
- **Depends on:** <component names, or "none">
- **Owner:** <agent/human, optional>

#### Attempts
1. **<YYYY-MM-DD>** — <what was tried>
   - **Result:** <succeeded | failed | partial>
   - **Notes:** <what happened, what was learned>

2. **<YYYY-MM-DD>** — <what was tried>
   - **Result:** <failed>
   - **Notes:** <root cause, why it failed>

#### Current State
<brief description of where this component stands right now>

---

### <Next Component>
...

## Dependency Graph

<text diagram showing component dependencies>

```
A ──→ B ──→ D
      ↓
      C
```

Read as: B depends on A. C depends on B. D depends on B.

## Decision Log

| Date | Decision | Rationale | Revisit? |
|------|----------|-----------|----------|
| YYYY-MM-DD | <what was decided> | <why> | <yes/no> |

## Blockers

- [ ] <blocker description> — <what's needed to unblock>
```

## Procedures

### Starting a Session

1. Read the blueprint file
2. Check which components are `in-progress` or `blocked`
3. Review the dependency graph — only work on components whose dependencies are `done`
4. Pick the highest-priority unblocked component

### During Work

- Update component status as you make progress
- Log every significant attempt with date, action, and result
- When blocked, add to the Blockers section with what's needed
- Record decisions in the Decision Log — future sessions need the "why"

### Ending a Session

1. Update all component statuses to reflect current reality
2. Update the `Last updated` date
3. Add any new blockers discovered
4. Commit the blueprint with a descriptive message

### Marking Done

A component is `done` when:
- Its acceptance criteria are met (if defined)
- Tests pass (if applicable)
- No open blockers reference it

The project is `done` when all components are `done`.

## Rules

- **Attempts are append-only.** Never delete or rewrite history. Failed attempts are valuable — they prevent repeating mistakes.
- **Dependencies are directional.** "A depends on B" means A cannot start until B is done. Keep the graph acyclic.
- **Status is honest.** Don't mark `done` if it's partial. Don't mark `in-progress` if it's actually blocked. Accurate state prevents wasted effort.
- **One blueprint per project.** Don't fragment tracking across multiple files for the same project.
- **Keep it scannable.** The blueprint should be readable in 30 seconds. Use terse language. Details go in attempt notes, not component descriptions.
