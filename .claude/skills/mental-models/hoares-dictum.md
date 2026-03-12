# Hoare's Dictum

> There are two ways of constructing software: one way is to make it so simple that there are obviously no deficiencies, and the other way is to make it so complicated that there are no obvious deficiencies. The first method is far more difficult. — C. A. R. Hoare

## Core Idea

Simplicity with obvious correctness beats complexity with hidden deficiencies. The hard part isn't making something complex — it's making something simple enough that you can see it's right.

Complements Occam's Razor (simplest *explanation*) — Hoare's Dictum is about simplest *construction*. Occam's asks "which theory fits?" Hoare's asks "can you prove this design correct by inspection?"

## Application

- **Architecture:** If you can't explain the system in one paragraph, it's too complicated to verify. Prefer designs where correctness is obvious over designs where bugs are merely non-obvious.
- **API design:** A good API has few methods with clear contracts. If users need a tutorial to avoid misuse, the API is wrong.
- **Code review:** "I can't find any bugs" is weaker than "I can see this is correct." Aim for the second.
- **Testing:** If you need elaborate test harnesses to verify behavior, the code under test may be too complex. Simple code needs simple tests.
- **Refactoring:** The goal isn't fewer lines — it's fewer concepts. Reduce the number of things a reader must hold in their head simultaneously.

## Common Misuse

- **Conflating simple with easy.** Simple designs are often harder to achieve than complex ones. "Just make it simpler" is not actionable advice — it requires deep understanding of the problem.
- **Using it to reject all complexity.** Some problems are inherently complex. The dictum says prefer simplicity where possible, not that complexity is always wrong. Distributed consensus, for example, has irreducible complexity.
- **Premature simplification.** Oversimplifying before understanding the problem creates designs that are simple but wrong. You must first understand the full problem space, then find the simple design within it.
