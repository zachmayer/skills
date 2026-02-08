---
name: ask-questions
description: >
  Structure your approach by asking clarifying questions before acting.
  Use when requirements are ambiguous, the task has multiple valid approaches,
  or when making assumptions could waste effort. Do NOT use when the task
  is clear and specific with no ambiguity.
---

Before starting work, systematically identify and resolve ambiguity:

## Question Framework

### 1. Scope Questions
- What exactly is in scope? What is explicitly out of scope?
- Is this a minimal fix, a proper solution, or a comprehensive overhaul?
- Are there related issues I should or should NOT address?

### 2. Constraint Questions
- Are there performance requirements (latency, throughput, memory)?
- Are there compatibility requirements (browsers, OS versions, APIs)?
- What can I assume about the environment?

### 3. Preference Questions
- Is there an existing pattern I should follow?
- Are there libraries/tools already in use that I should prefer?
- What's the testing expectation (unit tests, integration tests, none)?

### 4. Priority Questions
- If I can't do everything, what matters most?
- Is correctness or speed more important right now?
- Ship fast and iterate, or get it right the first time?

## How to Ask

- **Batch questions** - Ask 2-4 focused questions at once, not one at a time
- **Offer options** - "Should I do A (simpler, less flexible) or B (more work, handles edge cases)?"
- **State your assumption** - "I'm assuming X. Should I proceed, or is that wrong?"
- **Ask only what matters** - Don't ask questions you can answer by reading the code

## When to Skip Questions

- The task is a clear bug fix with an obvious cause
- The user gave detailed, specific instructions
- The answer is findable in the codebase (read first, ask second)
- You're blocked on understanding, not on preferences
