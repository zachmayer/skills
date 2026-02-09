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

**Dimensionalization** - For complex decisions, identify 3-7 dials that actually move the system. Score each on Fidelity (does it track something real and stable?), Leverage (can you control it, and does changing it matter?), and Complexity (can you hold it in working memory?). Drop anything vague, uncontrollable, or redundant. More than 7 dimensions means you're overfitting.

## Systems Thinking

**Bottleneck Analysis** - The system is only as fast as its slowest component. Find the constraint before optimizing anything else.

**Feedback Loops** - Identify reinforcing loops (growth/collapse) and balancing loops (stability). Most bugs in complex systems are feedback loops you didn't see.

**Map vs. Territory** - Your model of the system is not the system. When the model disagrees with reality, update the model.

**Emergence** - Simple rules produce complex behavior. Look for the simple rules underneath complex systems.

**Regime Partitioning** - When two positions seem contradictory, ask "what hidden variable are they conditioning on differently?" Both may be correct in different regimes. Build a regime map: "X dominates when A holds; Y dominates when B holds." The synthesis is a boundary, not a compromise. Test: does your unified framework make predictions neither original position makes?

## Problem Solving

**First Principles** - Decompose the problem to its fundamental truths. Reason up from there instead of reasoning by analogy.

**Occam's Razor** - The simplest explanation that fits the facts is usually correct. Don't add complexity until simple explanations fail.

**Pareto Principle** - 80% of the effect comes from 20% of the causes. Find the 20% before optimizing the rest.

**Pre-Mortem** - Imagine the project failed. What went wrong? Fix those things now.

**Five Whys** - When something breaks, ask "why?" five times. Each answer becomes the subject of the next question. Stops you from fixing symptoms instead of root causes. "The server crashed." Why? "Out of memory." Why? "A query returned 10M rows." Why? "No pagination." Why? "The spec didn't mention large datasets." Root cause: incomplete spec, not a memory issue.

## Critical Analysis

**Rival Thesis** - Don't just critique a position — build a complete alternative that accepts the same facts and reaches the opposite conclusion. It must be comprehensible without reading the original. Steel-man first, then oppose the strongest version. Generators: flip the objective, invert causality, swap quantifiers, push to limits.

**Assumption Archaeology** - For any claim or plan, recursively ask "what must be true for this to make sense?" Tag each assumption: empirical (testable fact), normative (value judgment), structural (incentive/institution), psychological (cognition/motivation), or definitional (what terms mean). The crux — where disagreement actually lives — is rarely at the surface. Most arguments about facts are really about values, or vice versa.

**Negative Space Analysis** - The most informative part of a message is often what's missing. Ask "given the context, what should logically appear but doesn't?" Classify each absence: vulnerability (protects ego), upside (too ambitious to say), bedrock (so assumed nobody states it), blind spot (invisible to author), or optionality (strategically withheld). The unsaid reveals more than the said.

**Handle Extraction** - When confronted with a dense argument, ask "what here could actually change what I do?" Test each concept for actionability (would it shift a decision?), operationalizability (can it be measured?), and novelty (is it new or just repackaged?). Terms with degraded referents ("alignment," "synergy") need concrete operationalization to survive. Null output is honest — not everything contains executable residue.

**Rhetorical Stress Test** - To separate substance from spin, extract the facts (what's actually asserted) and hold them constant. Vary the framing: swap connotations, shift active to passive voice, toggle "must" to "could." The fulcrum is the single word or grammatical move that most changes how the argument lands while facts stay fixed. If the argument collapses under synonym substitution, the work was rhetoric, not evidence.

## Design & Communication

**Pattern Language** (Christopher Alexander) - Solutions to recurring problems exist as interconnected patterns. Name them. A pattern has: context, problem, forces in tension, solution, consequences. Good architecture is a network of patterns that reinforce each other.

**Small Multiples** (Edward Tufte) - Show the same data structure repeated with one variable changed. Enables comparison without cognitive load. Works for charts, UI states, code examples, test cases. "At the heart of quantitative reasoning is a single question: Compared to what?"

## Mindset

**Scout Mindset** (Julia Galef) - Your goal is to see what's actually there, not to build a case for what you want to see. Ask "what would change my mind?" before analyzing. Treat being wrong as an update, not a failure. Actively seek disconfirming evidence. The measure of good reasoning is calibration, not confidence.

## External Thinking Skills

Core techniques from these skills are integrated above. The full-length versions offer deeper protocols and worked examples, available as `/skill-name` commands (from [FUTURE_TOKENS](https://github.com/jordanrubin/FUTURE_TOKENS)):

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
