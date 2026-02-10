---
name: synthesize
description: Compress conflicting positions into decision-sufficient generative frame with explicit distortion tracking. Produces tiered outputs (quick/medium/deep), tracks what was dropped, and validates via round-trip testing. Use when thesis + antithesis exist and you need portable framework that explains both while generating novel predictions.
---

# Synthesis

## Overview

**Synthesis** is decision-sufficient compression of conflicting positions. It takes thesis + antithesis and produces a generative frame that:
- Preserves explanatory scope (answers questions both positions answered)
- Generates novel predictions (enables decisions beyond original scope)
- Minimizes description length (fewest gears sufficient for coverage)
- Tracks distortion (explicit drop-log of what was simplified and risks)

Synthesis is NOT "both sides have a point" or "split the difference"—it's a NEW structure that explains why both positions seemed true from their angles while making predictions neither position makes alone.

Claude should use this Skill when the user:
- Explicitly asks to "synthesize" positions
- Has thesis + antithesis that need integration
- Says "combine these views" or "what's the unified picture?"
- Needs framework that resolves apparent contradiction
- Wants portable model that works across contexts

## Minimal Usage

**Simplest invocation:**
```
synthesize:
  thesis: [statement]
  antithesis: [statement]
```

Claude will infer:
- **decision_question**: "How should one best understand the information presented?"
- **audience**: general intelligent reader (assume undergraduate-level background)
- **distortion_budget**: 0.2 (moderate compression—preserve cruxes, simplify details)
- **output_tier**: medium (150w) as primary, with quick (50w) and deep (300w+) available

Claude outputs these inferences explicitly so user can adjust.

## Full Specification

### Input Parameters

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| **thesis** | required | statement | Position 1 to integrate |
| **antithesis** | required | statement | Position 2 to integrate |
| **decision_question** | inferred | question | What user needs to decide/understand |
| **audience** | general | novice/general/expert | Background knowledge assumed |
| **distortion_budget** | 0.2 | [0.0-0.5] | How much simplification acceptable (0=lossless, 0.5=aggressive) |
| **output_tier** | medium | quick/medium/deep/all | Which compression level(s) to deliver |

### Process

#### 1. Infer Context (if not specified)
```
decision_question: Extract from thesis/antithesis structure
  - If comparative: "When to use X vs Y?"
  - If causal: "What actually causes Z?"
  - If normative: "What should we optimize for?"
  - If empirical: "What predicts outcome O?"

audience: Assess required background
  - novice: minimal jargon, concrete examples
  - general: moderate technical depth
  - expert: full technical detail, edge cases

distortion_budget: Infer from context
  - research/academic context: 0.1 (low distortion)
  - blog/popular context: 0.3 (moderate distortion)
  - teaching/introductory: 0.4 (high distortion for clarity)
```

#### 2. Extract Cruxes
Identify what each position hinges on:
```
thesis_cruxes: Key claims/assumptions thesis depends on
antithesis_cruxes: Key claims/assumptions antithesis depends on
shared_assumptions: What both positions assume (constant to factor out)
points_of_conflict: Where positions make incompatible predictions
```

#### 3. Identify Regime Boundaries
Determine when each position applies:
```
thesis_regime: Conditions under which thesis dominates
antithesis_regime: Conditions under which antithesis dominates
synthesis_regime: Unified framework specifying when to use which

Ask: What hidden variable(s) were they conditioning on differently?
```

#### 4. Build Generative Mechanism
Construct minimal structure that:
- Explains why thesis seemed true (from its angle)
- Explains why antithesis seemed true (from its angle)
- Makes predictions neither position makes alone
- Uses fewest gears sufficient for coverage

#### 5. Generate Tiered Outputs

**Quick (50w):** Core insight + key prediction + when to use

**Medium (150w):** Mechanism overview + why both partly right + novel predictions + regime boundaries

**Deep (300w+):** Full mechanism with gears, complete regime map, multiple predictions, edge cases, worked examples

#### 6. Compile Drop-Log
Track what was simplified and risks:
```
simplified: [what was black-boxed] → risk: [consequence if detail matters]
omitted: [what cases ignored] → risk: [fails in those cases]
assumed: [what taken as given] → risk: [breaks if assumption false]
deferred: [what questions left open] → risk: [incomplete coverage]
```

#### 7. Self-Test
Validate via round-trip Q&A:
```
Can decision_question be answered from:
- Quick tier? (if not, what's missing?)
- Medium tier? (if not, what's missing?)
- Deep tier? (should succeed)

Which tier is minimum sufficient for decision?
```

#### 8. Assess Distortion
Estimate information loss:
```
predicted_distortion = (questions_unanswerable / total_questions)
actual_distortion ≤ distortion_budget (check)
```

## Output Format
```
### Context (inferred)
**Decision question:** [what user needs to decide]
**Audience:** [novice/general/expert]
**Distortion budget:** [0.0-0.5]

### Synthesis: Quick (50w)
[Elevator pitch: core insight + key prediction]

### Synthesis: Medium (150w)
[Mechanism overview + why both positions partly right + novel predictions + regime boundaries]

### Synthesis: Deep (300w+)
[Full structure with gears, complete regime map, multiple predictions, edge cases, worked examples]

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
3. [...]

**Drop-Log (what was simplified):**
- Simplified: [what] → Risk: [consequence]
- Omitted: [what] → Risk: [consequence]
- Assumed: [what] → Risk: [consequence]
- Deferred: [what] → Risk: [consequence]

**Predicted Distortion:** [0.0-0.5]

### Quality Check
- [ ] Round-trip Q&A succeeds (can answer decision question)
- [ ] Cruxes preserved (key dependencies intact)
- [ ] Regime boundaries specified (when to use what)
- [ ] Novel predictions present (≥2)
- [ ] Drop-log complete (risks flagged)
- [ ] Distortion within budget
- [ ] Coherent (no contradictions)
```

## Quality Dimensions

| # | Dimension | Type | Metric | Threshold |
|---|-----------|------|--------|-----------|
| 1 | Decision Sufficiency | PRIMARY | % of relevant questions answerable | ≥90% |
| 2 | Scope Preservation | CONSTRAINT | % of input cases still explained | ≥90% |
| 3 | Generativity | OPTIMIZE | Count of novel, testable predictions | ≥3 |
| 4 | Parsimony | OPTIMIZE | Gear count (fewer than thesis+antithesis combined) | < combined |
| 5 | Regime Clarity | STRUCTURE | Can classify novel cases into regimes | ≥70% |
| 6 | Robustness | OPTIMIZE | Survives steelman critiques | ≥70% |
| 7 | Communicability | OPTIMIZE | Time to understand (Quick <5m, Medium <15m, Deep <60m) | per tier |
| 8 | Distortion Tracking | HONESTY | Drop-log captures major risks | ≥80% |

## Synthesis Types

| Context | Optimize for | Distortion Budget | Default Tier |
|---------|-------------|-------------------|--------------|
| Research | Generativity, Scope | 0.05-0.1 | Deep |
| Teaching | Communicability, Parsimony | 0.3-0.4 | Medium + examples |
| Policy | Decision sufficiency, Regime clarity | 0.15-0.25 | Medium + bullets |
| Blog/Popular | Communicability, Generativity | 0.25-0.35 | Medium |
| Personal Decision | Decision sufficiency, Parsimony | 0.2-0.3 | Quick + Medium |

## Common Patterns

### Pattern 1: Regime Partition
Both positions correct in different contexts.
```
thesis: A causes B / antithesis: C causes B
synthesis: B = f(A, C, context) — A dominates in context X, C in context Y, interaction in Z
Example: Market efficiency = f(info_quality, coordination_cost, rationality)
```

### Pattern 2: Causal Chain Extension
Positions describe different parts of longer mechanism.
```
thesis: X → Y / antithesis: Y → Z
synthesis: X → Y → Z (positions describe different links)
Example: education → income (skills) AND income → education (resources) = reinforcing cycle
```

### Pattern 3: Level Mismatch
Positions operate at different levels of analysis.
```
thesis: individual-level mechanism / antithesis: system-level mechanism
synthesis: cross-level interaction with feedback
Example: individuals optimize given constraints; constraints emerge from system dynamics
```

### Pattern 4: Hidden Variable
Positions condition on different hidden variables.
```
thesis: X (assuming H=h1) / antithesis: ¬X (assuming H=h2)
synthesis: conclusion = f(H), making the implicit variable explicit
Example: remote work productivity = f(task_type, coordination_needs, preference)
```

## Worked Example: Market Efficiency Debate

**Input:**
- **Thesis:** "Markets are efficient because they aggregate distributed information through prices, enabling optimal resource allocation."
- **Antithesis:** "Markets fail systematically due to information asymmetries, externalities, and coordination problems that prices cannot solve."

**Inferred Context:** Decision question: When should we rely on markets vs other mechanisms? | Audience: General (policy) | Distortion budget: 0.2

**Quick (50w):**
Markets efficiently aggregate information when participants have symmetric knowledge and low coordination costs, but fail when information asymmetries or externalities dominate. Optimal mechanism depends on information structure and coordination requirements of specific domain.

**Medium (150w):**
Both positions capture real phenomena in different regimes. Markets excel when: information is distributed and privately held, transaction costs are low, externalities are minimal. They fail when: information asymmetries enable exploitation, coordination problems prevent efficient outcomes, externalities disconnect private and social costs.

Novel prediction: Market efficiency is continuous—it degrades smoothly as information asymmetry and coordination costs increase. Optimal design uses markets for high-info-quality, low-coordination domains (commodity trading) and alternatives for high-asymmetry, high-coordination domains (healthcare, climate).

Regime map: Markets when info quality > 0.7 and coordination cost < 0.3; regulation when reversed; hybrid in between.

**Structure:**
- **Cruxes:** Thesis hinges on information dispersal + price signals; Antithesis on systematic info gaps + externalities; Shared: outcomes matter, efficiency is goal
- **Regime Boundaries:** Markets when info symmetric + low transaction costs; Regulation when info asymmetric + high coordination; Hybrid when mixed
- **Novel Predictions:** (1) Efficiency is continuous function of (info quality, coordination cost); (2) Hybrids outperform pure approaches in middle range; (3) Optimal policy varies by domain's info structure, not ideology
- **Drop-Log:** Simplified behavioral biases → risk: interventions underweighted | Omitted political economy → risk: implementation failures | Assumed social welfare goal → risk: distributional concerns secondary | Deferred dynamic efficiency → risk: static analysis only
- **Predicted Distortion:** 0.18

## Good vs Bad Synthesis

**Good synthesis** (free will example): "Both positions confuse LEVELS of explanation. At psychological level, agency is real with causal power. At physical level, processes are deterministic. These don't conflict—they describe same events at different resolutions. Novel prediction: Interventions targeting 'conscious choice' affect outcomes even if underlying processes are deterministic." Why good: explains why both seemed true, preserves scope, generates predictions, specifies regimes, parsimonious.

**Anti-patterns to avoid:**
- **False balance** — "Both have points, truth is in between" without mechanism or regime boundaries
- **Picking sides** — Choosing one position and dismissing the other as naive
- **Subject change** — Introducing unrelated framework that doesn't address original question
- **Complexity explosion** — More gears than thesis+antithesis combined; too complex to use
- **Premature synthesis** — Synthesizing when evidence is thin or exploratory
- **Value conflicts as factual** — Treating preference differences as resolvable by evidence
- **Drop-log neglect** — No tracking of what was simplified or lost
- **Scope loss** — Synthesis can't answer questions either input could

## When NOT to Use Synthesis

- **Value conflicts:** Positions reflect different priorities (liberty vs welfare), not factual disagreements—synthesis would create false consensus
- **One side is wrong:** When evidence clearly refutes one position (e.g., flat earth), explain the error rather than synthesizing
- **Different questions:** Positions address different questions and aren't actually contradicting—clarify the distinction instead
- **Simple partition suffices:** A straightforward "depends on X" answers the question without elaborate framework
- **Premature evidence:** Positions are exploratory and evidence is thin—wait for more data before locking in a synthesis

## Self-Validation Checklist

When constructing a synthesis, verify:

- **Round-trip Q&A:** List 5-10 questions the decision requires. Can you answer them from the synthesis alone? If not, add to synthesis or flag in drop-log.
- **Scope regression:** List cases each input explained. Does synthesis explain all of them? Flag exceptions.
- **Novelty check:** For each prediction, could thesis or antithesis make it alone? If yes, not novel—refine.
- **Parsimony test:** For each gear, remove it. Does synthesis still work? If yes, cut it.
- **Coherence check:** No logical contradictions, no impossible regime conditions, no circular dependencies.
