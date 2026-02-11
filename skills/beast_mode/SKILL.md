---
name: beast_mode
description: >
  Activate autonomous problem-solving mode with maximum persistence. Use when
  the user says "beast mode", "go autonomous", or gives a large open-ended task
  they want fully solved without hand-holding. Do NOT use for simple tasks,
  quick edits, or when the user wants to stay in the loop.
---

Keep going until the problem is fully solved. Do not stop early, do not ask the user for help unless truly blocked.

Your training data is stale. Verify all library usage, APIs, and syntax via web search before using them. When the user says "resume" or "continue", find the last incomplete step and pick up from there.

If tests fail, debug. If debugging fails, try a different approach. If all approaches fail, explain what you tried and why each failed.
