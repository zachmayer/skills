# The Grug Brained Developer

A developer philosophy by Carson Gross (creator of htmx) that embraces simplicity, humility, and practicality over cleverness and abstraction. Written in a distinctive "caveman" voice, it distills decades of hard-won programming wisdom into a single thesis: complexity is the eternal enemy, and fighting it requires constant vigilance.

**Full text:** [grugbrain.dev](https://grugbrain.dev/)

## Core Thesis

Complexity is the "spirit demon" that invades codebases through well-meaning developers. Every section of the essay returns to this: fight complexity above all else. "Complexity very, very bad."

## Key Principles by Topic

### Saying No / Saying Ok

The primary weapon against complexity is refusing unnecessary features and abstractions. "No" is the magic word. When you must concede, apply 80/20: deliver 80% of value with 20% of the code. Sometimes just build the simpler version without announcing it — project managers often forget requirements or move on.

### Factoring Code

Don't abstract too early. Early in a project, the shape of the system is unclear — wait for natural "cut points" to emerge. Good abstractions have narrow interfaces hiding internal complexity. When the complexity demon is "trapped properly in crystal" behind a clean interface, you've won. Prototype early, especially when many strong architects are involved.

### Testing

Integration tests are the sweet spot. Writing tests before understanding the domain is counterproductive. Unit tests break too often as implementation changes; end-to-end tests are hard to debug. Keep a small, religiously maintained end-to-end suite for critical paths. Avoid mocking whenever possible — use it only at coarse-grained system boundaries. **One exception:** always reproduce a bug with a regression test before fixing it.

### Agile

Not terrible, not good. Agile processes can help but become harmful when taken too seriously. When agile projects fail, practitioners blame improper implementation — a self-serving defense. Better levers: good tooling, good prototyping, good hiring. "No silver club fix all software problems."

### Refactoring

Keep refactors small and incremental. The system should remain functional throughout. Large refactors fail more often and tend to introduce worse abstractions than what they replaced (J2EE, OSGi cited as cautionary tales).

### Chesterton's Fence

Ugly, seemingly pointless code often encodes hard-learned lessons. Understand why code exists before removing it. Tests often reveal why certain fences exist.

### Microservices

Taking the already-difficult problem of system decomposition and adding network calls multiplies confusion rather than reducing it.

### Tools & Type Systems

Invest heavily in learning your tools — two weeks of deep tool learning can double productivity. A good debugger teaches more than many courses. Types are valuable mainly for autocomplete ("hit dot, see what grug can do"), not formal correctness. Generics are a temptation trap — best limited to container classes. Watch out for type theorists who build beautiful but impractical abstractions.

### Expression Complexity & DRY

Break complex booleans into named intermediate variables for easier debugging and review. Simple, obvious repeated code can be better than elaborate abstractions built to eliminate duplication. Concern over duplication naturally decreases with experience.

### Separation of Concerns

Prefer locality of behavior over separating concerns across files. Code should live on the thing that does the thing. The canonical web example (HTML/CSS/JS in separate files) forces developers to jump across many locations to understand one feature.

### Logging

Log generously, especially in cloud-deployed systems. Log all major logical branches. Include request IDs for correlation across distributed systems. Make log levels dynamically adjustable at runtime and configurable per individual user for targeted debugging. Schools underteach logging despite its outsized production value.

### Concurrency & Optimizing

Avoid concurrency complexity: prefer stateless request handlers and simple job queues with independent jobs. Never optimize without profiling first — CPU is not always the bottleneck, network latency can cost the equivalent of millions of CPU cycles.

### APIs

Design for the simple case first. Layer APIs: simple interface for common cases, advanced for complex ones. Think from the user's perspective, not the implementation. Place methods on the relevant object rather than in separate utility classes.

### Parsing

Recursive descent parsers beat parser generators. Parser generators produce unreadable generated code that's nearly impossible to debug. *Crafting Interpreters* by Bob Nystrom is highly recommended.

### The Visitor Pattern

One-word verdict: bad.

### Front End Development

Don't split front end and back end unnecessarily. SPAs create two complexity demon lairs where one existed. Even simple forms-to-database apps get over-engineered with heavy frameworks. htmx and hyperscript exist as lower-complexity alternatives.

### Fads

Treat revolutionary new approaches with skepticism. Backend is more stable because most bad ideas have already been tried. Frontend is still cycling through many of them. Most "new" ideas are recycled concepts.

### Fear Of Looking Dumb (FOLD)

When senior developers openly say "this is too complicated for me," it gives juniors permission to admit the same. FOLD is a major source of complexity demon power — people accept confusing systems rather than question them. Humor and a mental catalog of past failures by overconfident architects are useful defenses.

### Impostor Syndrome

Nearly everyone feels like an impostor — that's normal. Even experienced developers with successful open source projects feel this regularly. "Nobody imposter if everybody imposter."

### Recommended Reading

- *Worse is Better* — Richard Gabriel
- *A Philosophy of Software Design* — John Ousterhout

## When to Apply

- Debating whether to add an abstraction layer
- Choosing between clever and straightforward approaches
- Reviewing architecture that feels unnecessarily complex
- Deciding on a testing strategy
- Resisting pressure to adopt the latest framework or pattern
- When "big brain" solutions are being proposed over simpler alternatives
- During refactoring: is this actually simpler, or just different?
- When someone is afraid to admit they don't understand the system
- When a codebase has too many layers of indirection

## When NOT to Apply

- The problem has genuine irreducible complexity (distributed consensus, etc.)
- You're in a domain where formalism and abstraction genuinely pay off (compilers, type theory)
- Using "keep it simple" as an excuse to avoid necessary rigor or work
- Premature simplification — you must understand the full problem before finding the simple design within it

## Related Models

- [hoares-dictum.md](hoares-dictum.md) — the formal version: "so simple there are obviously no deficiencies"
- [occams-razor.md](occams-razor.md) — simplest explanation; grug brain is simplest construction
- [first-principles.md](first-principles.md) — decompose before abstracting
- [chestertons-fence.md](chestertons-fence.md) — cited directly in the essay
- [pareto-principle.md](pareto-principle.md) — the 80/20 approach grug advocates

## Source

Carson Gross, [grugbrain.dev](https://grugbrain.dev/).
