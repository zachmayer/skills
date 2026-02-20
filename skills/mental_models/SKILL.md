---
name: mental_models
description: >
  Apply mental models to reason about problems, decisions, and systems.
  Use when making architectural decisions, debugging complex issues, evaluating
  trade-offs, analyzing arguments, or when the user asks for a structured way
  to think about something. Do NOT use for straightforward implementation tasks
  with clear requirements.
---

Select and apply the most relevant mental models from this toolkit. For models with full protocols, read the linked file before applying.

## Decision Making

**Inversion** — Instead of asking "how do I succeed?", ask "what would guarantee failure?" and avoid those. Unblocks stuck thinking by reversing the question. See [inversion.md](inversion.md).

**Second-Order Thinking** — Ask "and then what?" at least three times. First-order effects are obvious; second and third-order effects are where plans fail. See [second-order-thinking.md](second-order-thinking.md).

**Reversibility** — Is this a two-way door (easily reversible) or a one-way door (permanent)? Two-way: move fast. One-way: invest in getting it right. Most decisions are two-way doors treated as one-way. See [reversibility.md](reversibility.md).

**Opportunity Cost** — Every yes is a no to something else. What are you NOT doing by choosing this? The hidden cost of any choice is the best alternative foregone. See [opportunity-cost.md](opportunity-cost.md).

**Pre-Mortem** — Before starting, imagine the project failed. What went wrong? Fix those things now. More useful than post-mortems because you can still act. See [pre-mortem.md](pre-mortem.md).

**Dimensionalize** — Transform complex decisions into 3-7 measurable dials scored on Fidelity (is it real?), Leverage (can you twist it, does twisting matter?), and Complexity (can you hold it in your head?). Drop anything vague, uncontrollable, or redundant. **Read [dimensionalize.md](dimensionalize.md) for full protocol** — this has a specific scoring process.

**Bayesian Thinking** — Update beliefs proportionally to evidence strength. Start with a prior, observe data, update. Strong priors need strong evidence to move. Weak evidence shouldn't flip strong beliefs. See [bayesian-thinking.md](bayesian-thinking.md).

## Systems Thinking

**Bottleneck Analysis** — The system is only as fast as its slowest component. Find the constraint before optimizing anything else. Optimizing non-bottlenecks is waste. See [bottleneck-analysis.md](bottleneck-analysis.md).

**Feedback Loops** — Identify reinforcing loops (growth/collapse spirals) and balancing loops (stability). Most bugs in complex systems are feedback loops you didn't see. See [feedback-loops.md](feedback-loops.md).

**Map vs. Territory** — Your model of the system is not the system. When model disagrees with reality, update the model, not your perception of reality. See [map-vs-territory.md](map-vs-territory.md).

**Emergence** — Simple rules produce complex behavior. Look for the simple rules underneath complex systems before adding complexity to your solution. See [emergence.md](emergence.md).

**Leverage Points** — Places in a system where small changes produce big effects. Meadows' hierarchy: parameters < buffers < feedback loops < information flows < rules < goals < paradigms. Intervene at the highest leverage point you can reach. See [leverage-points.md](leverage-points.md).

## Problem Solving

**First Principles** — Decompose to fundamental truths. Reason up from there instead of reasoning by analogy. Breaks through "we've always done it this way." See [first-principles.md](first-principles.md).

**Occam's Razor** — The simplest explanation that fits the facts is usually correct. Don't add complexity until simple explanations fail. In debugging: the boring explanation is almost always right. See [occams-razor.md](occams-razor.md).

**Pareto Principle** — 80% of the effect comes from 20% of the causes. Find the 20% before optimizing the rest. Applies to bugs, features, customers, and effort. See [pareto-principle.md](pareto-principle.md).

**Five Whys** — When something breaks, ask "why?" five times. Each answer becomes the subject of the next question. Stops you from fixing symptoms. See [five-whys.md](five-whys.md).

**Post-Mortem** — After a failure, structured diagnosis before retrying. State what happened, what you expected, trace root cause, classify the failure (wrong assumption, wrong approach, scope error, flaky), then plan a fix based on the classification. Prevents blind retry loops. See [post-mortem.md](post-mortem.md).

**OODA Loop** — Observe → Orient → Decide → Act, then repeat faster than the environment changes. Speed of the loop matters more than perfection of any step. See [ooda-loop.md](ooda-loop.md).

## Critical Analysis

These are heavy analytical protocols. **Read the linked files before applying** — each has a specific multi-step process with output schemas that Claude should follow.

**Antithesize** — Generate standalone opposition to any proposition. Not refutation — a complete alternative worldview that stands on its own, accepts the same facts, and reaches opposite conclusions. Menu of 14 antithesis types (refutation, rival thesis, objective flip, axis shift, causal inversion, etc.) selected by purpose: falsify, replace, robustify, clarify values, or reframe. **Read [antithesize.md](antithesize.md) for full protocol.**

**Excavate** — Assumption archaeology. Recursively ask "what must be true for this to make sense?" and tag each assumption: empirical, normative, structural, psychological, or definitional. Surfaces the cruxes where disagreement actually lives. **Read [excavate.md](excavate.md) for full protocol.**

**Negspace** — Detect what's conspicuously absent. Given the statistical structure of a text, what argument *should* be there but isn't? Classify each omission: vulnerability (ego protection), upside (ambition withheld), bedrock (unstated axioms), blind spot (invisible to author), or optionality (strategic non-commitment). **Read [negspace.md](negspace.md) for full protocol.**

**Rhetoricize** — Separate substance from spin. Extract facts into a ledger, then perturb framing (swap connotations, shift voice, toggle modality) while holding facts constant. The fulcrum is the word or grammatical move that most changes how the argument lands. Surprise = affect_shift × meaning_overlap × fluency. **Read [rhetoricize.md](rhetoricize.md) for full protocol.**

**Handlize** — Extract executable residue from dense arguments. For each concept, test: would it change a decision (actionability)? Can it be measured (operationalizability)? Is it genuinely new (novelty)? Classify as live / burned / dead. Null output is honest — not everything contains handles. **Read [handlize.md](handlize.md) for full protocol.**

**Inductify** — Extract non-obvious structural commonalities across multiple examples (n≥2). Decompose each case into mechanisms, assumptions, values, constraints. Cross-reference for structural isomorphisms. Each pattern must specify mechanism, predictive claim, and breaking condition. **Read [inductify.md](inductify.md) for full protocol.**

## Synthesis & Mapping

These protocols integrate or transfer knowledge across domains. **Read the linked files** — each has specific processes.

**Synthesize** — Compress conflicting positions into a decision-sufficient framework. Not "both sides have a point" — a NEW structure that explains why both positions seemed true from their angles, makes novel predictions neither makes alone, and tracks what was simplified (drop-log). Produces tiered outputs: quick (50w), medium (150w), deep (300w+). **Read [synthesize.md](synthesize.md) for full protocol.**

**Rhyme** — Fast structural similarity detection. Maps novel inputs onto known patterns through echo recognition. The pre-analytical step before deep mapping. Generate 3-5 candidates, score on parallel density, source maturity, transfer leverage. Quality threshold: ≥0.6 on key dimensions. **Read [rhyme.md](rhyme.md) for full protocol.**

**Metaphorize** — Build explicit, high-coverage mapping from source domain to target domain. Heavier than rhyme, lighter than formal proof. When source has math, carry the math with units and dimensional analysis. Produces mapping table, formula shelf, invariant assertions, and metric plan. **Read [metaphorize.md](metaphorize.md) for full protocol.**

## Cognitive Biases & Traps

These require recognition, not protocol. Knowing the name is usually enough to catch yourself.

**Confirmation Bias** — Tendency to seek, interpret, and remember information confirming existing beliefs. Counter: actively seek disconfirming evidence. Ask "what would change my mind?" before analyzing. See [confirmation-bias.md](confirmation-bias.md).

**Sunk Cost Fallacy** — Continuing an endeavor because of past investment (time, money, effort) rather than future value. The money is already spent regardless. Decision: "knowing what I know now, would I start this?" See [sunk-cost-fallacy.md](sunk-cost-fallacy.md).

**Anchoring** — Over-relying on the first piece of information encountered. First numbers, first impressions, first estimates disproportionately influence subsequent judgments. Counter: generate your own estimate before looking at others'. See [anchoring.md](anchoring.md).

**Dunning-Kruger Effect** — Unskilled individuals overestimate their ability; skilled individuals underestimate theirs. The less you know, the less you know about how much you don't know. See [dunning-kruger.md](dunning-kruger.md).

**Goodhart's Law** — When a measure becomes a target, it ceases to be a good measure. People optimize the metric, not the underlying goal. Every KPI eventually gets gamed. Counter: use counter-metrics and measure what you refuse to sacrifice. See [goodharts-law.md](goodharts-law.md).

## Strategic Thinking

**Chesterton's Fence** — Before removing something, understand why it was put there. If you don't understand its purpose, you don't understand the consequences of removing it. Applies to code, processes, and institutions. See [chestertons-fence.md](chestertons-fence.md).

**Circle of Competence** — Know the boundary of what you actually understand vs. what you think you understand. Operating inside your circle: genuine knowledge. Outside: overconfidence. The skill is knowing where the edge is. See [circle-of-competence.md](circle-of-competence.md).

**Antifragility** — Some systems don't just survive stress — they get stronger from it. Fragile breaks under volatility; robust survives; antifragile improves. Design for antifragility: small reversible bets, option-rich positions, barbell strategy. See [antifragility.md](antifragility.md).

**Margin of Safety** — Build in buffer for the unknown. Engineers over-spec bridges; investors buy below intrinsic value. The margin between your estimate and disaster is your insurance against being wrong. See [margin-of-safety.md](margin-of-safety.md).

**Lindy Effect** — The longer a non-perishable thing has survived, the longer its expected remaining lifespan. A book in print for 50 years will likely be in print for 50 more. Prefer battle-tested over novel when the cost of failure is high. See [lindy-effect.md](lindy-effect.md).

## Coordination & Incentives

**Tragedy of the Commons** — Individual rational behavior depleting shared resources. Each actor takes more because the cost is distributed. Solutions: privatize, regulate, or create social norms that make defection costly. See [tragedy-of-the-commons.md](tragedy-of-the-commons.md).

**Principal-Agent Problem** — When one party (agent) acts on behalf of another (principal) but has different incentives. The agent optimizes for themselves, not the principal. Solutions: align incentives, monitor, or reduce information asymmetry. See [principal-agent.md](principal-agent.md).

**Hanlon's Razor** — Never attribute to malice what can be adequately explained by ignorance, incompetence, or misaligned incentives. Most failures are systemic, not conspiratorial. See [hanlons-razor.md](hanlons-razor.md).

**Forcing Function** — A constraint that forces confrontation with an issue. Deadlines, budgets, public commitments, and ship dates are forcing functions. Without them, decisions defer indefinitely. See [forcing-function.md](forcing-function.md).

## Design & Communication

**Pattern Language** (Christopher Alexander) — Solutions to recurring problems exist as interconnected patterns. A pattern has: context, problem, forces in tension, solution, consequences. Good architecture is a network of patterns that reinforce each other. See [pattern-language.md](pattern-language.md).

**Small Multiples** (Edward Tufte) — Show the same structure repeated with one variable changed. Enables comparison without cognitive load. Works for charts, UI states, code examples, test cases. See [small-multiples.md](small-multiples.md).

**Scout Mindset** (Julia Galef) — Your goal is to see what's actually there, not to build a case for what you want to see. Treat being wrong as an update, not a failure. The measure of good reasoning is calibration, not confidence. See [scout-mindset.md](scout-mindset.md).

## Application

Almost every non-trivial problem benefits from at least one mental model. When you encounter a decision, analysis, or debugging task, scan this index for a fit — there is usually one. Multiple models often apply simultaneously; use whichever combination illuminates the situation.

When applying a model:
1. Name the model you're using and why it fits
2. Read the linked .md file if the model has a protocol
3. Walk through the reasoning step by step
4. State what the model suggests
5. Note where the model might mislead — every model has limits

When uncertain which model to use, start with these high-hit-rate defaults:
- **Stuck?** → Inversion, First Principles
- **Debugging?** → Five Whys, Post-Mortem, Bottleneck Analysis
- **Something failed?** → Post-Mortem (diagnose before retrying)
- **Deciding?** → Second-Order Thinking, Reversibility, Opportunity Cost
- **Analyzing an argument?** → Excavate, Negspace, Rhetoricize
- **Comparing options?** → Dimensionalize
- **Conflicting views?** → Synthesize, Antithesize
- **New domain?** → Rhyme, Metaphorize
