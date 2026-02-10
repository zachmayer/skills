# Dimensionalize: Reference

Worked examples, detailed scoring methodology, and edge cases for the dimensionalize skill.

## Meta-Dimension Details

### Fidelity
> *Does the dial carve reality at the joints?*

**Validity** = tracks an actual difference that exists
**Stability** = keeps tracking when zoom, time, or context shift

**High-Fidelity examples:**
- Factor exposure (finance)
- Latency (systems)
- Tempo (music)

**Low-Fidelity examples:**
- "Vibe"
- "Tech debt" (without specification)
- Generic "efficiency"

### Leverage
> *Twist -> consequence*

**Actionability** = you control the slider
**Impact** = slider moves the outcome

**Good Leverage examples:**
- Autonomy vs stimulation (parenting decisions)
- Modularity (software architecture)
- Remote vs on-site (work arrangements)

**Bad Leverage examples:**
- "Be more strategic" (no clear control)
- "Gym-playlist BPM" (minimal impact)
- "Market conditions" (external, uncontrollable)

### Complexity
> *Few enough dials to stay in head-RAM*

**Cognitive load** = how many sliders you must juggle
**Overfitting** = dials that add theoretical resolution but no practical gain

**Low-Complexity examples:**
- Strength / endurance / recovery (fitness)
- Price / quality / speed (product)

**High-Complexity examples:**
- 30 biometric streams for a workout plan
- 50+ OKRs for five people
- More than 9 dimensions for any decision

## Detailed Scoring Methodology

Rate each candidate dimension on a 1-5 scale across all six sub-dimensions:

**Fidelity:**
- Validity: 1 (vague) -> 5 (precisely measurable)
- Stability: 1 (context-dependent) -> 5 (holds across contexts)
- Combined F score: average of validity + stability

**Leverage:**
- Actionability: 1 (no control) -> 5 (direct control)
- Impact: 1 (negligible effect) -> 5 (major effect)
- Combined L score: average of actionability + impact

**Complexity:**
- Cognitive load: 1 (simple) -> 5 (hard to track)
- Overfitting: 1 (essential) -> 5 (theoretical polish)
- Combined C score: average of load + overfitting
- **Lower is better for complexity**

### LLM Quick-Cast Recipe

When dimensionalizing, follow this protocol:
```
[[dimensionalize]]
[[goal: <decision / system>]]
[[fidelity_floor: validity+stability]]
[[leverage_floor: action+impact]]
[[complexity_ceiling: 7 axes]]
[[remember: mark each axis (F,L,C) score]]
```

## Worked Example: Career Decision

**Goal:** Choose next career move

**Dimensions:**

1. **Value-Capture Efficiency** [F: 5.0, L: 4.5, C: 1.0]
   - What: Post-tax compensation per unit of effort+risk
   - Range: $50/hr -> $500/hr equivalent
   - Lever: Negotiation, equity %, role choice
   - Why: Direct impact on financial security

2. **Counterfactual Impact** [F: 4.0, L: 4.0, C: 2.0]
   - What: Good that happens because you showed up
   - Range: Maintenance -> transformative
   - Lever: Choose high-leverage vs support roles
   - Why: Long-term meaning and satisfaction

3. **Option Surface Area** [F: 4.5, L: 5.0, C: 1.0]
   - What: Future doors unlocked (network, brand, skills)
   - Range: Dead-end -> exponential
   - Lever: Prestige vs stealth, industry choice
   - Why: Compounds across career

4. **Personal Excitation** [F: 4.0, L: 4.0, C: 1.0]
   - What: Will you wake up energized for 18+ months?
   - Range: Dread -> flow state
   - Lever: Scope negotiation, problem domain fit
   - Why: Performance and sustainability

5. **Autonomy Bandwidth** [F: 5.0, L: 4.0, C: 1.0]
   - What: Decision-making freedom
   - Range: Micromanaged -> self-directed
   - Lever: Title, reporting structure, remote options
   - Why: Agency and execution speed

6. **Skill Compounding Rate** [F: 4.0, L: 4.0, C: 2.0]
   - What: How fast rare capabilities grow
   - Range: Plateau -> steep learning curve
   - Lever: Problem complexity, mentor density
   - Why: Long-term career capital

7. **Lifestyle Stability** [F: 5.0, L: 4.0, C: 1.0]
   - What: Stress, hours, location flexibility
   - Range: Burnout risk -> sustainable
   - Lever: Team size, sector, remote policy
   - Why: Everything else requires this foundation

## Edge Cases and Failure Mode Details

### Too Many Dimensions (>9)
- Solution: Merge correlated ones, drop low-leverage
- Ask: "If I had to pick just 5, which matter most?"

### Vague Dimensions
- Bad: "Strategic alignment", "Culture fit"
- Good: "% of roadmap you control", "Team turnover rate"
- Fix: Demand concrete measurement criteria

### No-Control Dimensions
- Bad: "Market timing", "Regulatory environment"
- Good: "Entry timing choice", "Sector selection"
- Fix: Reframe to controllable version or drop

### Overfitted Dimensions
- Bad: Separate dims for "email velocity" and "slack response time"
- Good: Single "communication cadence" dimension
- Fix: Collapse correlated dials

### Hidden Dependencies
- Check: If dimension X is high, does that force dimension Y?
- Fix: Keep only the upstream dimension or treat as constraint

## Constraint Handling

Some factors are binary gates, not dimensions:
- "Must be remote" -> constraint, not dimension
- "Salary > $X" -> threshold, not slider
- Apply constraints first, dimensionalize remaining space

## Weighting by Context

Context determines relative importance:
- New parent -> boost lifestyle stability weight
- Early career -> boost skill compounding weight
- Pre-exit -> boost value capture weight

## Dimension Discovery via Rhyme

Stuck on dimensions? Use the Rhyme skill:
- "What is this decision structurally similar to?"
- Import proven dimensions from analogous domain
- Example: Career choice <- Athletic training <- Research project
