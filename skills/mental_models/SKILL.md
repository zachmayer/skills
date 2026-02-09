---
name: mental_models
description: >
  Apply mental models to reason about problems, decisions, and systems.
  Use when making architectural decisions, debugging complex issues, evaluating
  trade-offs, or when the user asks for a structured way to think about something.
  Do NOT use for straightforward implementation tasks with clear requirements.
---

When analyzing the problem, select and apply the most relevant mental models from this toolkit:

## Decision Making

**Inversion** - Instead of asking "how do I succeed?", ask "what would guarantee failure?" and avoid those things.

**Second-Order Thinking** - Ask "and then what?" at least twice. First-order: "This speeds up the build." Second-order: "Developers skip tests because the build is fast enough without them." Third-order: "Bug rate increases."

**Reversibility** - Is this decision easily reversible? If yes, move fast. If no, slow down and invest in getting it right. Two-way doors vs. one-way doors.

**Opportunity Cost** - What are you NOT doing by choosing this? Every yes is a no to something else.

## Systems Thinking

**Bottleneck Analysis** - The system is only as fast as its slowest component. Find the constraint before optimizing anything else.

**Feedback Loops** - Identify reinforcing loops (growth/collapse) and balancing loops (stability). Most bugs in complex systems are feedback loops you didn't see.

**Map vs. Territory** - Your model of the system is not the system. When the model disagrees with reality, update the model.

**Emergence** - Simple rules produce complex behavior. Look for the simple rules underneath complex systems.

## Problem Solving

**First Principles** - Decompose the problem to its fundamental truths. Reason up from there instead of reasoning by analogy.

**Occam's Razor** - The simplest explanation that fits the facts is usually correct. Don't add complexity until simple explanations fail.

**Pareto Principle** - 80% of the effect comes from 20% of the causes. Find the 20% before optimizing the rest.

**Pre-Mortem** - Imagine the project failed. What went wrong? Fix those things now.

## Design & Communication

**Pattern Language** (Christopher Alexander) - Solutions to recurring problems exist as interconnected patterns. Name them. A pattern has: context, problem, forces in tension, solution, consequences. Good architecture is a network of patterns that reinforce each other.

**Small Multiples** (Edward Tufte) - Show the same data structure repeated with one variable changed. Enables comparison without cognitive load. Works for charts, UI states, code examples, test cases. "At the heart of quantitative reasoning is a single question: Compared to what?"

## Mindset

**Scout Mindset** (Julia Galef) - Your goal is to see what's actually there, not to build a case for what you want to see. Ask "what would change my mind?" before analyzing. Treat being wrong as an update, not a failure. Actively seek disconfirming evidence. The measure of good reasoning is calibration, not confidence.

## External Thinking Skills

Specialized thinking tools available as `/skill-name` commands (from [FUTURE_TOKENS](https://github.com/jordanrubin/FUTURE_TOKENS)):

| Skill | Purpose |
|-------|---------|
| `antithesize` | Generate standalone opposition to any proposition (complete alternative worldview, not refutation) |
| `dimensionalize` | Transform decisions into 3-7 measurable dimensions scored on fidelity, leverage, and complexity |
| `synthesize` | Compress conflicting positions into a decision-sufficient generative frame with distortion tracking |
| `excavate` | Assumption archaeology: reveal the layered "what must be true" structure beneath claims |
| `metaphorize` | Build explicit high-coverage mapping from source to target domain, carrying math and units |
| `rhetoricize` | Extract rhetorical skeleton and map the spin-space around an argument |
| `inductify` | Extract non-obvious structural commonalities across examples (latent mechanisms, not surface vibes) |
| `negspace` | Detect conspicuously absent arguments via perplexity contrast (what should be there but isn't) |
| `rhyme` | Fast structural similarity detection and pattern matching across domains |
| `handlize` | Extract executable residue / operational handles from arguments, discarding rhetorical mass |

## Application

When applying a model:
1. Name the model you're using and why
2. Walk through the reasoning step by step
3. State what the model suggests
4. Note where the model might mislead (every model has limits)
