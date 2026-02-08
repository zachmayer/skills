---
name: senior-engineer
description: >
  Write code like a senior engineer. Apply performance-first principles and
  rigorous engineering standards. Use when writing production code, reviewing
  architecture, or when quality and performance matter. Do NOT use for
  quick prototypes, throwaway scripts, or exploration.
---

## Performance Hierarchy

Apply these in order. Each level beats micro-optimization at the level below it:

1. **Eliminate > Optimize** - The fastest code is code that doesn't exist. Remove features, delete dead paths, simplify requirements before optimizing what remains.

2. **Static > Dynamic** - Parse, don't execute. Resolve at compile/build time what you can. Config files over runtime computation. Types over runtime checks.

3. **Strict > Permissive** - Reject bad input at the boundary. No fallback logic, no "best effort" parsing. Fail fast, fail loud.

4. **Narrow > Broad** - Tight specs enable fast paths. A function that handles one case well beats a function that handles ten cases poorly.

5. **First hit > Exhaustive** - Stop early. Return on first match. Short-circuit evaluation. Don't scan what you don't need.

6. **Upfront > Reactive** - Resolve before acting. Validate inputs before processing. Plan before executing. Prefetch before needing.

7. **Share > Copy** - One cache, not many. Hardlinks over copies. References over clones. Singleton over instance.

8. **Parallel > Serial** - When there are no dependencies, run concurrently. I/O-bound work should never block.

9. **Architecture > Language** - Dropping a feature beats rewriting in a faster language. Design changes beat micro-optimization.

10. **Backward compatibility is a performance tax** - Every compatibility shim costs. Be deliberate about what you maintain.

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
