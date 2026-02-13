---
name: deep_mode
description: >
  Activate deep thinking with maximum persistence. Use when facing complex
  architectural decisions, subtle bugs, large open-ended tasks, or multi-step
  reasoning where getting it right matters more than speed. Do NOT use for
  simple questions, quick edits, or trivial tasks.
---

ultrathink

Keep going until the problem is fully solved. Do not stop early, do not ask the user for help unless truly blocked.

Apply `mental_models` to select relevant thinking frameworks. Apply `ask_questions` to resolve ambiguity before starting.

## Thinking Protocol

Break solutions into clear steps. Use a step budget (start with 100, request more for complex problems).

Assign quality scores (0.0-1.0) after each reflection:
- 0.8+: Continue current approach
- 0.5-0.7: Consider minor adjustments
- Below 0.5: Backtrack and try a different approach

Explore multiple solutions individually. Compare approaches in reflections.

## Verification

Verify by approaching from different angles. Actively question initial results: "What if this is incorrect?"

Use alternative representations (diagrams, tables) to gain new insights.

## Persistence

Your training data is stale. Verify all library usage, APIs, and syntax via web search before using.

When the user says "resume" or "continue", find the last incomplete step and pick up from there.

If tests fail, debug. If debugging fails, try a different approach. If all approaches fail, explain what you tried and why each failed.

## Code Standards

Complexity kills codebases. Find simple, elegant, robust solutions.

Generate full code, no placeholders. Prefer popular, idiomatic packages. Prefer built-in libraries. Prefer functional style over OO unless the problem is object oriented.

Functions should be small, focused, and unit tested.

## Math

For mathematical problems, show all work using LaTeX. For counting tasks, count elements individually and mark them as you proceed.
