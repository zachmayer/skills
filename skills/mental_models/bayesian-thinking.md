# Bayesian Thinking

Update beliefs proportionally to the strength of new evidence. Start with priors, observe data, update.

## Core Formula (Intuitive)

`P(hypothesis | evidence) ∝ P(evidence | hypothesis) × P(hypothesis)`

In plain terms: your updated belief = how likely you'd see this evidence if the hypothesis were true × how likely you thought the hypothesis was before.

## Process

1. **State your prior** — what do you believe before new evidence? Be explicit about confidence level (50%? 80%? 99%?)
2. **Observe evidence** — what new information arrived?
3. **Assess likelihood ratio** — how much more likely is this evidence if your hypothesis is true vs false?
4. **Update** — shift your belief proportionally. Strong evidence → big shift. Weak evidence → small shift.
5. **Check calibration** — are your updates appropriate to evidence strength?

## Key Principles

- **Strong priors need strong evidence to move.** If you're 95% confident, a single anecdote shouldn't flip you to 50%.
- **Weak evidence shouldn't flip strong beliefs.** But it should nudge them slightly.
- **Multiple weak signals compound.** Ten independent weak signals can equal one strong signal.
- **Base rates matter.** Before evaluating specific evidence, ask "how common is this in general?"
- **Absence of evidence IS evidence** — when you expected to see something and didn't, update toward it being unlikely.

## Common Failure Modes

- **Base rate neglect:** ignoring how common something is in the population
- **Anchoring on prior:** refusing to update when evidence is strong
- **Overreaction:** updating too much from single data points
- **Narrative bias:** treating a compelling story as stronger evidence than it is
