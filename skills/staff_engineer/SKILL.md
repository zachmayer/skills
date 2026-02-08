---
name: staff_engineer
description: >
  Apply performance-first principles and rigorous engineering standards.
  Use when writing production code, reviewing architecture, optimizing
  performance, or doing code review. Do NOT use for quick prototypes,
  throwaway scripts, or exploration.
---

## Performance Hierarchy

Apply these in order. Each level beats micro-optimization at the level below it:

1. **Eliminate > Optimize** — fastest code doesn't exist
2. **Static > Dynamic** — parse, don't execute
3. **Strict > Permissive** — reject bad input, skip fallback logic
4. **Narrow > Broad** — tight spec = fast path
5. **First hit > Exhaustive** — stop early
6. **Upfront > Reactive** — resolve before acting
7. **Share > Copy** — one cache, hardlinks
8. **Parallel > Serial** — when no dependency
9. **Architecture > Language** — dropping features beats micro-optimization
10. **Backward compatibility is a performance tax**

## Engineering Standards

- **Read before writing** - Understand existing code before modifying it
- **Minimal diffs** - Change only what you need to. Don't refactor adjacent code
- **No over-engineering** - Solve the current problem, not hypothetical future ones
- **Tests prove behavior** - If it matters, test it. If it doesn't matter, don't write it
- **Error handling at boundaries** - Validate user input, API responses, file I/O. Trust internal code
- **Name things well** - Clear names eliminate the need for comments
- **Delete unused code** - Dead code is misleading code

## Code Review Checklist

Before submitting:
- [ ] Does this solve the stated problem and nothing more?
- [ ] Can any code be removed without breaking functionality?
- [ ] Are there any n+1 queries, unbounded loops, or missing indexes?
- [ ] Is error handling at system boundaries, not sprinkled throughout?
- [ ] Would a new team member understand this without explanation?
