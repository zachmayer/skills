---
name: synthesize
description: Compress conflicting positions into decision-sufficient generative frame with explicit distortion tracking. Produces tiered outputs (quick/medium/deep), tracks what was dropped, and validates via round-trip testing. Use when thesis + antithesis exist and you need portable framework that explains both while generating novel predictions.
---

# Synthesis

## Overview

Synthesis is decision-sufficient compression of conflicting positions. It takes thesis + antithesis and produces a generative frame that preserves explanatory scope, generates novel predictions, minimizes description length, and tracks distortion. Synthesis is NOT "both sides have a point"---it is a NEW structure that explains why both positions seemed true while making predictions neither makes alone.

For worked examples, patterns, validation protocols, and quality dimensions, see [REFERENCE.md](REFERENCE.md).

## When to Use

- Two positions seem incompatible but both have evidence
- Need unified framework explaining both perspectives
- Decision requires knowing when to apply which position
- Creating teaching material integrating views
- Building research program bridging competing theories
- Positions are at similar level of abstraction and address the same question

## When NOT to Use

- Positions are incommensurable (different values, not facts)
- One position is simply wrong (don't synthesize truth with falsehood)
- Positions talk past each other (different questions, not contradictions)
- Simple answer exists (synthesis would overcomplicate)
- Evidence clearly favors one position (synthesis would hedge wrongly)
- Positions are early/incomplete (premature synthesis)
- Synthesis would lose critical nuance needed for the decision

## Minimal Usage

```
synthesize:
  thesis: [statement]
  antithesis: [statement]
```

Claude infers and states explicitly:
- **decision_question**: What the user needs to decide/understand
- **audience**: novice / general / expert
- **distortion_budget**: 0.0--0.5 (default 0.2)
- **output_tier**: quick (50w) / medium (150w) / deep (300w+)

## Process

### 1. Infer Context
Derive decision_question type (comparative, causal, normative, empirical), audience level, and distortion budget from context.

### 2. Extract Cruxes
Identify thesis cruxes, antithesis cruxes, shared assumptions, and points of conflict.

### 3. Identify Regime Boundaries
Determine when each position applies. Ask: what hidden variable(s) were they conditioning on differently?

### 4. Build Generative Mechanism
Construct minimal structure that explains why each position seemed true and makes predictions neither makes alone. Use fewest gears sufficient for coverage.

### 5. Generate Tiered Outputs
- **Quick (50w):** Core insight, key prediction, when to use.
- **Medium (150w):** Mechanism overview, why both partly right, novel predictions, regime boundaries.
- **Deep (300w+):** Full mechanism with gears, complete regime map, multiple predictions, edge cases, worked examples.

### 6. Compile Drop-Log
Track what was simplified, omitted, assumed, and deferred---with risk for each.

### 7. Self-Test
Validate: can the decision question be answered from each tier? Identify minimum sufficient tier.

### 8. Assess Distortion
Estimate information loss. Verify predicted distortion is within budget.

## Output Format

```
### Context (inferred)
**Decision question:** [what user needs to decide]
**Audience:** [novice/general/expert]
**Distortion budget:** [0.0-0.5]

### Synthesis: Quick (50w)
[Elevator pitch: core insight + key prediction]

### Synthesis: Medium (150w)
[Mechanism overview + why both partly right + novel predictions + regime boundaries]

### Synthesis: Deep (300w+)
[Full structure with gears, complete regime map, multiple predictions, edge cases]

### Structure

**Cruxes:**
- Thesis hinges on: [claims]
- Antithesis hinges on: [claims]
- Shared assumptions: [what both take as given]

**Regime Boundaries:**
- Use thesis when: [conditions]
- Use antithesis when: [conditions]
- Synthesis needed when: [conditions]

**Novel Predictions:**
1. [Prediction neither input makes]
2. [Prediction neither input makes]

**Drop-Log:**
- Simplified: [what] -> Risk: [consequence]
- Omitted: [what] -> Risk: [consequence]
- Assumed: [what] -> Risk: [consequence]
- Deferred: [what] -> Risk: [consequence]

**Predicted Distortion:** [0.0-0.5]
```

### Quality Check

- [ ] Round-trip Q&A succeeds (can answer decision question)
- [ ] Cruxes preserved (key dependencies intact)
- [ ] Regime boundaries specified (when to use what)
- [ ] Novel predictions present (>=2)
- [ ] Drop-log complete (risks flagged)
- [ ] Distortion within budget
- [ ] Coherent (no contradictions)
