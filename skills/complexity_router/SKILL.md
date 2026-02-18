---
name: complexity_router
description: >
  Assess task complexity (simple/medium/complex) and route to appropriate effort
  level. Use when receiving a new task and unsure how much planning, thinking, or
  tooling to apply. Do NOT use when the user has already specified the approach
  or loaded a specific skill like ultra_think or staff_engineer.
---

Before starting work on a task, assess its complexity and match your effort to the challenge. Over-engineering simple tasks wastes time; under-thinking complex ones causes rework.

## Assessment

Evaluate the task against these signals:

### Simple (do it now)
- Single file, <20 lines changed
- Clear requirements, no ambiguity
- No architectural decisions
- Examples: fix a typo, add a log line, rename a variable, answer a factual question

### Medium (plan then do)
- 2-5 files, moderate scope
- Some design choices but conventional solutions exist
- Follows existing patterns in the codebase
- Examples: add a CLI flag, write unit tests for an existing module, implement a well-defined feature

### Complex (think hard then plan then do)
- 5+ files or cross-cutting concerns
- Architectural decisions with trade-offs
- Novel problem without clear precedent in the codebase
- Ambiguous requirements needing clarification
- Performance, security, or correctness constraints
- Examples: design a new subsystem, refactor a core abstraction, debug a subtle concurrency issue

## Routing

State your assessment explicitly, then apply the matching effort level:

### Simple → Direct execution
- No planning overhead. Just do the work.
- Verify with a quick test or review.

### Medium → Lightweight plan
- Apply `ask_questions` if any requirements are unclear.
- State a 3-5 step plan before executing.
- Run tests after implementation.

### Complex → Full rigor
- Apply `ultra_think` for deep reasoning.
- Apply `ask_questions` to resolve ambiguity before committing to a direction.
- Apply `staff_engineer` for production-quality implementation.
- Surface assumptions explicitly. Get confirmation before large changes.

## Output Format

State your assessment at the start of work:

```
COMPLEXITY: [simple|medium|complex]
REASON: [one sentence explaining why]
APPROACH: [what you'll do]
```

Then proceed with the matched effort level. If complexity changes during work (e.g., a "simple" bug turns out to have deep roots), reassess and escalate.

## Anti-patterns

- Don't apply ultra_think to rename a variable.
- Don't skip planning on a multi-file refactor because it "looks straightforward."
- Don't gold-plate simple tasks with extra abstractions, tests, or docs beyond what's needed.
- Don't freeze on medium tasks — they don't need architectural review, just a quick plan.
