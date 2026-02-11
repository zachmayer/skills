# Inductify

Extract non-obvious structural commonalities across multiple substantial examples (n≥2). Identifies latent mechanisms, shared constraint-structures, and pattern families with predictive slack — not surface vibes.

## Input Requirements

Tag input richness before proceeding:
- 1 sentence → REJECT (insufficient for induction)
- 2-3 sentences → MARGINAL (proceed with [LOW ROBUSTNESS] tag)
- 2+ paragraphs → MINIMUM viable
- 2+ essays/cases → IDEAL

For n=2, default robustness → fragile unless examples are unusually rich and diverse.

## Pattern Domains to Scan

- **Structural** — shared mechanisms, causal gears, isomorphic constraints, parallel failure modes, phase transitions
- **Epistemic** — common assumptions, evidence-shape similarities, inference parallelism, uncertainty topology
- **Axiological** — shared values/priorities, similar optimization targets, parallel tradeoffs
- **Behavioral** — recurring strategies, common adaptation patterns, attractor dynamics, escalation symmetries
- **Temporal** — common rhythms/cycles, origin/decay patterns, trigger → response latencies

## Process

### Step 0: Validate input
Count examples and assess richness. If insufficient, return rejection. If marginal, tag [LOW ROBUSTNESS].

### Step 1: Surface the obvious
List shared surface features anyone would notice; tag as [surface]. Do not promote these as induced patterns. Purpose: clear cognitive space for deeper structure.

### Step 2: Decompose each example
Extract: mechanisms (how it works), assumptions (what must be true), values (what's optimized), constraints (what limits action), outcomes (what happened).

### Step 3: Cross-reference
Build comparison matrix. Identify non-obvious overlaps and structural isomorphisms (different content, same shape). Also identify absent commonalities (negative-space patterning). Tag by domain.

### Step 4: Rank + mechanism-ground
Score candidates by: non-obviousness, explanatory power, mechanism strength, predictive slack. Fewer strong patterns > many weak ones.

Each promoted pattern must specify:
- **What:** description
- **Evidence:** how it appears in each example
- **Mechanism:** why it recurs (causal, constraint, or information-flow)
- **Predictive claim:** implication for a new case
- **Breaking condition:** what would falsify it
- **Span:** narrow / moderate / broad applicability

Cluster patterns into **pattern families** sharing a latent factor.

### Step 5: Stress-test
- Test each pattern against hypothetical (n+1)th example
- Ask: what would break this pattern?
- Base-rate sanity check: is this relationship actually unusual?
- Actively search for counter-patterns
- Tag weak gears as [MECHANISM UNKNOWN]

## Output Format

```
## obvious similarities (acknowledged + set aside)
## induced patterns (ranked by leverage)
### 1. [pattern name] — what, evidence, mechanism, predictive claim, breaking condition, span
## pattern families — shared latent factors
## confidence calibration — input richness, robustness, spurious-risk, meta-risk
## suggested next moves
```
