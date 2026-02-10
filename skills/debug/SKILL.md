---
name: debug
description: >
  WHEN: User says "debug", code isn't working as expected, tests are failing,
  or behavior is wrong and the cause is unclear.
  WHEN NOT: Writing new code, refactoring working code, or performance optimization.
---

# Debug

Now debug: FULL, COMPREHENSIVE, GRANULAR code audit line by line — verify all intended functionality.

Loop until the end product would satisfy a skeptical Claude Code user who thinks it's impossible to debug with prompting.

## Process

1. **Read every line** of the code under investigation. Do not skim. Do not assume.
2. **State what each section does** in plain language. If you can't, that's a bug candidate.
3. **Trace the actual data flow** — inputs, transforms, outputs. Follow the values, not the names.
4. **Compare intended vs actual behavior** for every branch, edge case, and error path.
5. **Check the boundaries**: off-by-one, null/empty, type coercion, encoding, concurrency.
6. **Verify assumptions**: does that API actually return what you think? Does that config actually load? Does that variable actually have scope here?
7. **Run it** — if you can execute tests or the code itself, do so. Read the actual output. Don't guess.
8. **Fix and verify** — after each fix, re-run to confirm. One fix at a time.
9. **Loop** — go back to step 1 on the changed code. Repeat until clean.

## Rules

- Never say "this looks correct" without tracing the actual values.
- Never assume a function works because its name sounds right.
- If you're not sure, add a print/log and run it.
- If tests exist, run them. If they don't, write one for the bug.
- When you find the bug, explain WHY it happened, not just what to change.
