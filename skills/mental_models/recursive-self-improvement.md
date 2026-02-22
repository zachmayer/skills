# Recursive Self-Improvement

When a system improves itself, the improvements compound — but the dynamics are counterintuitive. Use this model when evaluating meta-level work (improving tools, processes, or skills that affect future productivity).

## The Two Types of Progress

**Grind** (80% of work) — Systematic iteration within the current paradigm. Finding small efficiency gains that compound multiplicatively. Most improvement is grinding: tweaking prompts, refining workflows, eliminating friction. An army of automated workers excels here.

**Paradigm shift** (20% of work) — Exploring entirely new approaches. Not "faster car" but "flying car." Rarer, harder to automate, requires novel hypotheses that current models struggle to generate. Humans (or lucky accidents) tend to drive these.

**Balance both.** A portfolio of all grind and no paradigm exploration eventually hits diminishing returns. A portfolio of all paradigm exploration and no grind never compounds. The compounding comes from the grind; the step functions come from paradigm shifts.

## The Multiplier Effect

Small improvements compound multiplicatively, not additively. If ten small optimizations each save 5%, the combined effect is 1.05^10 = 63% improvement, not 50%. This means:

- **Prioritize improvements that affect future work.** A skill that makes all future skills better is worth more than a skill that solves one problem.
- **Infrastructure improvements have hidden leverage.** They multiply everything downstream.
- **The order matters.** Improving the improvement process first (meta-improvement) has the highest multiplier.

## Diminishing Returns ("Adding Nines")

Order-of-magnitude increases in input yield linear improvements in reliability: 10x effort takes you from 90% to 99%, the next 10x from 99% to 99.9%. Recognize when you're in this territory:

- If each improvement requires dramatically more effort than the last, you're adding nines
- Switch paradigms (grind → paradigm shift) when the grind stops paying off
- "Good enough" is a real answer — not every system needs 99.99%

## Agent Self-Awareness

Models excel at systematic iteration within existing paradigms. Models struggle at generating novel research hypotheses and paradigm-level insights. Design workflows accordingly:

- **Automate the grind.** Repetitive testing, parameter sweeps, style consistency, known patterns — let agents handle these at scale.
- **Elevate humans for paradigm decisions.** Which direction to explore, what to build next, when to abandon an approach — these need human judgment or at minimum, structured exploration (see prompt_evolution).
- **Don't pretend to have insights you don't.** When grinding, say you're grinding. When speculating, flag it as speculation.

## Process

1. **Classify** — Is this work grind (incremental improvement) or paradigm (new approach)?
2. **Estimate the multiplier** — Does this improvement affect future work? How many downstream tasks benefit?
3. **Check for diminishing returns** — Is each unit of effort producing less than the last?
4. **Decide** — Grind if multiplier is high and returns aren't diminishing. Shift paradigm if returns are diminishing. Elevate to human if the decision requires novel judgment.
