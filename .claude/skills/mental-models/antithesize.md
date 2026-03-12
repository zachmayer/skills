# Antithesize

Generate standalone opposition to any proposition. Antithesis must be comprehensible without reading thesis — it's an alternative complete worldview, not refutation.

## Antithesis Types (pick by purpose)

| Purpose | Types |
|---------|-------|
| **Falsify** (is this true?) | refutation, counterexample, selection critique |
| **Replace** (better story?) | rival thesis, causal inversion, reparameterization |
| **Robustify** (will it break?) | adversarial example, boundary case, objective flip |
| **Clarify values** (what to optimize?) | axiological inversion, performative mirror |
| **Reframe** (right question?) | axis shift, phenomenological counter, foil |

### Type reference

- **Refutation** — show ¬p, contradiction, counterexample, or reductio
- **Rival thesis** — full counter-model with different primitives/priors that fits data better. Hardest to do well; most useful for synthesis
- **Objective flip** — optimize different loss (recall not precision; CVaR not mean; latency not throughput)
- **Axis shift** — change the question, hold the answer fixed; challenge relevance, not truth
- **Causal inversion** — reverse arrows or condition on different node
- **Role/quantifier swap** — swap ∀/∃, min/max, buyer/seller
- **Boundary/limit case** — test at extremes (n→∞, liquidity→0, adversary→adaptive)
- **Adversarial example** — craft worst-case inputs that satisfy constraints yet violate intent
- **Duality/reparameterization** — express same system in dual space
- **Selection/measurement critique** — attack the pipeline (sampling, survivorship, goodharting, leakage)
- **Axiological inversion** — reorder values, see if policy survives
- **Phenomenological counter** — lived-experience report that map misses
- **Performative/strategic mirror** — "if we make your claim common knowledge, equilibrium shifts"
- **Null model / ablation** — "a dumb baseline does as well; your gears add no marginal evidence"

## Generators (how to mint antithesis)

- Flip the sign (benefit ↔ harm), timeframe (short ↔ long), or unit of analysis (individual ↔ system)
- Swap the objective (mean → tail; accuracy → calibration; growth → resilience)
- Invert causality (B causes A), roles (principal ↔ agent), or quantifiers (∀ → ∃)
- Push to limits (resource → 0/∞; noise → 0/∞; adversary → adaptive)
- Ablate one gear; if predictions don't move, that gear was cosplay

## Process

### Step 1: Identify purpose
What are you trying to accomplish? Pick type(s) from the table above.

### Step 2: Choose axis + operator
Pick TWO axes — one mechanistic + one normative. Quick triage:
- Claim optimizes wrong thing → pragmatic axis
- Data feels shaky → epistemic/statistical axis
- Story feels post-hoc → causal axis
- Incentives misaligned → incentive axis
- Works in-sample, dies OOD → distributional axis
- Values conflict, not facts → axiological axis

### Step 3: Set intensity
- lvl 1: contrast (gentle) → lvl 3: stress-test → lvl 5: core challenge
- Increase levels only after logging a crux

### Step 4: Generate antithesis
1. Restate thesis in strongest form (steel-man)
2. Identify core claims to oppose
3. Accept shared reality (facts, observations, constraints)
4. Reinterpret valence (good → bad, feature → bug)
5. Propose opposite mechanism (if causal claim)
6. Reach opposite conclusion
7. Verify standalone (makes sense without reading thesis?)

### Step 5: Extract outputs
- **Antithesis** — the constructed opposite case
- **Failure modes** — specific ways thesis breaks (brittle assumptions, bad priors, incentive leaks, boundary violations)
- **Cruxes** — minimal belief changes that flip conclusion (empirical + axiological)
- **Evidence hooks** — what to measure next to resolve

## Critical Requirements

**Standalone test (non-negotiable):** Can someone understand this without reading the original? Does it make positive claims? Could it have been written first?

**Steel-man first:** Before opposing, state the STRONGEST version. Oppose the steel-man, not the weak version.

**Context-appropriate:** Understand actual constraints, not hypothetical ones. Who bears costs? What are real failure modes?
