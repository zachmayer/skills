---
name: ultra_think
description: >
  Activate extended deep thinking before responding. Use when facing complex
  architectural decisions, subtle bugs, multi-step reasoning, or any task
  where getting it right matters more than speed. Do NOT use for simple
  questions, quick lookups, or trivial edits.
---

ultrathink

Also apply the `mental_models` skill to select and use relevant thinking frameworks.

Also apply the `ask_questions` skill to identify and resolve ambiguity before starting work.

## Thinking Protocol

Break down the solution into clear steps. Use a step budget (start with 25, request more for complex problems).

Assign a quality score (0.0-1.0) after each reflection to guide your approach:

- 0.8+: Continue current approach
- 0.5-0.7: Consider minor adjustments
- Below 0.5: Backtrack and try a different approach

Explore multiple solutions individually when possible. Compare approaches in reflections.

Use thinking as a scratchpad — write out all calculations and reasoning explicitly.

## Verification

After initial analysis, verify by approaching the problem from a different angle or using an alternative method.

Actively question initial results: "What if this is incorrect?" Attempt to disprove your first conclusion.

When appropriate, use alternative representations (diagrams, tables, rewriting the problem differently) to gain new insights.

## Code Standards

Complexity kills codebases. Find simple, elegant, robust solutions.

Generate full code, no placeholders. If unable, explain in comments.

Prefer the most popular, idiomatic packages. Prefer built-in libraries. Prefer functional style over OO unless the problem is object oriented.

Functions should be small, focused, and unit tested.

## Math

For mathematical problems, show all work using LaTeX. For counting or enumeration tasks, count elements individually and mark them as you proceed.
