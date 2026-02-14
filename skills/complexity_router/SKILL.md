---
name: complexity_router
description: >
  Assess task complexity (simple/medium/complex) and route to appropriate
  effort level. Use at the start of any task to calibrate approach — especially
  when unsure how much planning, thinking, or tooling a request needs.
  Do NOT use when the user has explicitly requested a specific approach
  (e.g., "use ultra_think" or "just do it quickly").
---

# Complexity Router

Assess the complexity of the current task, then route to the right effort level. This prevents over-engineering simple tasks and under-investing in hard ones.

## Step 1: Assess Complexity

Evaluate the task against these signals. Count how many apply in each tier.

### Simple signals
- Single file change
- Clear, unambiguous requirements
- No architectural decisions needed
- Obvious implementation (e.g., rename, fix typo, add log, small bug fix)
- No tests to write or update
- Reversible with a single undo

### Medium signals
- 2-5 files affected
- Some ambiguity in requirements, but resolvable by reading code
- One or two design choices to make
- Tests need updating or writing
- Existing patterns to follow
- Moderate risk if wrong (but recoverable)

### Complex signals
- 5+ files affected or cross-cutting concern
- Ambiguous requirements needing user clarification
- Multiple valid architectural approaches
- New patterns or abstractions required
- High risk if wrong (data loss, security, breaking changes)
- Multi-step implementation with dependencies between steps
- Performance, concurrency, or compatibility constraints

### Classification

Count the signals that match. The tier with the most matches wins. When tied, round **up** — it's cheaper to over-prepare than to redo work.

## Step 2: Route to Effort Level

### Simple — Just do it

**Profile:** Fast, direct, minimal ceremony.

- Skip planning. Implement directly.
- No need for `ultra_think` or `ask_questions` — the task is clear.
- Make the change, verify it works, done.
- Commit message is sufficient documentation.

**Example tasks:** Fix a typo. Rename a variable. Add a missing import. Update a config value.

### Medium — Think, then do

**Profile:** Moderate investment. Understand before acting.

- Read the relevant code first. Understand existing patterns.
- Apply `ask_questions` if any requirements are ambiguous — but keep it to 1-2 questions max.
- Plan mentally (no formal plan document needed).
- Write or update tests.
- Apply `staff_engineer` principles: naive-then-optimize, test-first.

**Example tasks:** Add a new API endpoint following existing patterns. Fix a bug that spans multiple files. Implement a small feature with clear acceptance criteria.

### Complex — Plan, align, then do

**Profile:** Full investment. Plan explicitly. Get alignment before writing code.

- Apply `ultra_think` for deep reasoning about the approach.
- Apply `ask_questions` to clarify ambiguous requirements before starting.
- Use `EnterPlanMode` or write an explicit plan for user approval.
- Apply `staff_engineer` for engineering rigor and assumption surfacing.
- Consider using `ralph_loop` if the task decomposes into multiple stories.
- Apply `mental_models` for architectural decisions (especially Reversibility, Second-Order Thinking, Dimensionalize).
- Front-load risk: tackle the hardest, most uncertain part first.

**Example tasks:** Add authentication to an app. Refactor a core subsystem. Implement a feature with multiple valid architectures. Performance optimization with unknown bottleneck.

## Step 3: Announce and Proceed

After classifying, state the assessment concisely:

```
Complexity: [simple/medium/complex]
Reason: [1 sentence — the dominant signal]
Approach: [1 sentence — what you'll do]
```

Then proceed with the routed effort level. Do not ask for confirmation on the classification — just state it and go. The user can redirect if they disagree.

## Recalibration

If mid-task you discover the complexity was misjudged (e.g., a "simple" fix reveals a deeper issue), stop and re-assess. State:

```
Recalibrating: [simple → medium/complex]
Reason: [what changed]
```

Then switch to the appropriate effort level. This is normal — initial assessment is a best guess, not a commitment.
