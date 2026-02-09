---
name: ask_questions
description: >
  Ask clarifying questions before acting. Use when requirements are ambiguous,
  the task has multiple valid approaches, or when making assumptions could
  waste effort. Do NOT use when the task is clear and specific.
---

# Ask Questions If Underspecified

Also apply `hierarchical_memory`: read working memory before formulating questions — past context often resolves ambiguity. After getting answers, save key decisions as memory notes.

## Goal

Ask the minimum set of clarifying questions needed to avoid wrong work; do not start implementing until the must-have questions are answered (or the user explicitly approves proceeding with stated assumptions).

## Workflow

### 1) Decide whether the request is underspecified

Treat a request as underspecified if after exploring how to perform the work, some or all of the following are not clear:
- Define the objective (what should change vs stay the same)
- Define "done" (acceptance criteria, examples, edge cases)
- Define scope (which files/components/users are in/out)
- Define constraints (compatibility, performance, style, deps, time)
- Identify environment (language/runtime versions, OS, build/test runner)
- Clarify safety/reversibility (data migration, rollout/rollback, risk)

If multiple plausible interpretations exist, assume it is underspecified.

### 2) Ask must-have questions first (keep it small)

Ask 1-5 questions in the first pass. Prefer questions that eliminate whole branches of work.

Make questions easy to answer:
- Offer multiple-choice with a marked default/recommended option
- Include a fast-path response (e.g., reply `defaults` to accept all defaults)
- Structure for compact replies (e.g., `1b 2a 3c`); restate chosen options to confirm

### 3) Pause before acting

Until must-have answers arrive:
- Do not run commands, edit files, or produce a detailed plan that depends on unknowns
- Do perform a clearly labeled, low-risk discovery step only if it does not commit you to a direction (e.g., inspect repo structure, read relevant config files)

If the user explicitly asks you to proceed without answers:
- State your assumptions as a short numbered list
- Ask for confirmation; proceed only after they confirm or correct them

### 4) Confirm interpretation, then proceed

Once you have answers, restate the requirements in 1-3 sentences (including key constraints and what success looks like), then start work.

## Anti-patterns

- Don't ask questions you can answer with a quick, low-risk discovery read (e.g., configs, existing patterns, docs).
- Don't ask open-ended questions if a tight multiple-choice or yes/no would eliminate ambiguity faster.
