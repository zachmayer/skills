# Five Whys

When something breaks, ask "why?" five times. Each answer becomes the subject of the next question. Stops you from fixing symptoms.

## Process

1. **State the problem** clearly and specifically
2. **Ask "why?"** — identify the immediate cause
3. **Ask "why?" again** — what caused that cause?
4. **Repeat** 3-5 times until you reach a root cause you can act on
5. **Verify** — does fixing the root cause prevent recurrence?

## Example

- "The server crashed." Why? → Out of memory
- "Why out of memory?" → A query returned 10M rows
- "Why 10M rows?" → No pagination on the endpoint
- "Why no pagination?" → The spec didn't mention large datasets
- **Root cause:** Incomplete spec process, not a memory issue

## Guidelines

- Stop when you reach something you can change (a process, a system, a decision)
- Avoid stopping at "human error" — ask why the system allowed the error
- Multiple branches are fine — a problem can have multiple root causes
- Don't use it for simple, obvious failures where the cause is apparent
