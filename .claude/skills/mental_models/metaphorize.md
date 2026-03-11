# Metaphorize

Build explicit, high-coverage mapping from familiar source domain **s** onto target domain **t** so that rules, heuristics, and formulas from **s** can be systematically ported into testable hypotheses for **t**. Heavier than rhyme, lighter than formal proof. When source has math, carry the math with units and dimensional analysis.

## Process

### 1. Select source (s)
Pick domain with mature formalism (equations, metrics, known failure modes) that structurally fits target (from rhyme analysis).

### 2. List primitives
Enumerate entities, relations, operations in **s** that drive behavior: objects/agents, resources, states, flows, control structures.

### 3. Mine formalism (MANDATORY when available)
Harvest from **s**: equations & constraints (Little's Law, Bayes, PID, stock-flow, hazard functions), objective/penalty functions (loss, regret, cost-of-delay), standard metrics (SLAs, scores, throughput, defect rates), units & dimensions (carry explicitly, check consistency).

### 4. Draft mapping m : s → t
Name counterparts in **t** for each primitive in **s**. Mark gaps. Attach adapters with typed signatures.

Format: `| Source (s) | Target (t) | Adapter | Units |`

### 5. Name invariants (make them checkable)
Specify transforms/constraints from **s** to preserve under **m**, with units. Write as testable assertions:
```
ASSERT: λ < c·μ  (stability condition)
ASSERT: sum(inflow) = sum(outflow) + Δstock  (conservation)
```

Categories: queue discipline, conservation laws, budget constraints, escalation semantics, feedback loops, stability conditions.

### 6. Metric plan
Define success/failure measurement: primary metrics (targets, ranges), secondary metrics (supporting indicators), counter-metrics (what you refuse to optimize), baselines, acceptance thresholds, evaluation cadence.

### 7. Estimation & calibration
Lay out how parameters will be fit: estimation method, data needed, sampling window, validation strategy, error decomposition (bias/variance, aleatoric/epistemic).

### 8. Package
Compress into shareable deliverables:
- Primitive mapping table
- Formula shelf with relabeled equations (source notation → target notation, with variable glossary and units)
- Invariant list with units
- Metric plan with baselines
- Explicit exclusion list (what does NOT port)

### 9. Probe
Run 3-5 representative rules from **s** through **m**: apply mapping, compute numerical predictions, compare to observed behavior in **t**, document where mapping breaks.

## Key Quality Dimensions (score 0.0-1.0)

- **Counterpart clarity** — unambiguous 1:1 or explicit 1:n with adapters
- **Invariant set quality** — preserved bits are operators/constraints, not motifs
- **Formal leverage** — portable math carried with units and glossary
- **Unit discipline** — explicit units + dimensional analysis throughout
- **Exclusion clarity** — explicit list of what doesn't port
- **Failure localization** — errors surface at the seam they're caused

**Quality threshold:** ≥0.7 on formal leverage, counterpart clarity, invariant quality, and unit discipline.
