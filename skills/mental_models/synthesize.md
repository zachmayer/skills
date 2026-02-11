# Synthesize

Compress conflicting positions into a decision-sufficient generative frame with explicit distortion tracking. Not "both sides have a point" — a NEW structure that explains why both positions seemed true from their angles while making predictions neither position makes alone.

## Input

- **thesis** (required): position 1
- **antithesis** (required): position 2
- **decision_question** (inferred if not given): what user needs to decide/understand
- **audience** (default: general): novice / general / expert
- **distortion_budget** (default: 0.2): how much simplification is acceptable [0.0 = lossless, 0.5 = aggressive]

## Process

### 1. Infer context
Extract decision_question from thesis/antithesis structure. If comparative: "when to use X vs Y?" If causal: "what actually causes Z?" If normative: "what should we optimize?"

### 2. Extract cruxes
- Thesis cruxes: key claims/assumptions thesis depends on
- Antithesis cruxes: key claims/assumptions antithesis depends on
- Shared assumptions: what both take as given (factor out)
- Points of conflict: where positions make incompatible predictions

### 3. Identify regime boundaries
Ask: what hidden variable were they conditioning on differently?
- Thesis regime: conditions where thesis dominates
- Antithesis regime: conditions where antithesis dominates
- Synthesis: unified framework specifying when to use which

### 4. Build generative mechanism
Construct minimal structure that: explains why thesis seemed true, explains why antithesis seemed true, makes predictions neither makes alone, uses fewest gears sufficient for coverage.

### 5. Generate tiered outputs
- **Quick (50w):** core insight + key prediction + when to use
- **Medium (150w):** mechanism overview + why both partly right + novel predictions + regime boundaries
- **Deep (300w+):** full mechanism with gears + complete regime map + multiple predictions + edge cases

### 6. Compile drop-log
Track what was simplified and risks:
- simplified: [what was black-boxed] → risk: [consequence if detail matters]
- omitted: [what cases ignored] → risk: [fails in those cases]
- assumed: [what taken as given] → risk: [breaks if assumption false]

### 7. Self-test
Can decision_question be answered from each tier? Which tier is minimum sufficient?

### 8. Assess distortion
predicted_distortion = questions_unanswerable / total_questions. Must be ≤ distortion_budget.

## Common Synthesis Patterns

**Regime Partition** — both correct in different contexts. "When X holds → thesis; when Y holds → antithesis." The synthesis is a boundary, not a compromise.

**Causal Chain Extension** — positions describe different links of longer mechanism. X → Y → Z where thesis covers X→Y and antithesis covers Y→Z.

**Level Mismatch** — positions operate at different levels of analysis (individual vs system, short-term vs long-term). Cross-level interaction is the synthesis.

**Hidden Variable** — positions condition on different values of an implicit variable. Make the variable explicit.

## When NOT to Synthesize

- Positions are incommensurable (different values, not facts) — synthesis would be false consensus
- One position is simply wrong — don't synthesize truth with falsehood
- Positions talk past each other (different questions) — clarify, don't synthesize
- Evidence clearly favors one side — synthesis that "finds middle ground" is epistemically dishonest
- Positions are early/incomplete — premature synthesis locks in assumptions

## Quality Criteria

- Round-trip Q&A succeeds (can answer decision question from synthesis)
- Cruxes preserved (key dependencies intact)
- Regime boundaries specified (when to use what)
- Novel predictions present (≥2 that neither input makes)
- Drop-log complete (risks flagged)
- Distortion within budget
- Coherent (no contradictions)
- Parsimonious (fewer gears than thesis + antithesis combined)
