# Dimensionalize

Transform complex decisions or systems into 3-7 measurable dimensions (dials) scored on three meta-dimensions: Fidelity, Leverage, and Complexity.

## The Three Meta-Dimensions

| Meta-Dim | Sub-Dims | Question |
|----------|----------|----------|
| **Fidelity** | validity + stability | Is it *real* and does it hold up across contexts? |
| **Leverage** | actionability + impact | Can you twist it, and does twisting matter? |
| **Complexity** | cognitive load + overfitting risk | Can you hold it in your head? (lower is better) |

## Process

### 1. Identify the system
What needs dimensionalizing? A decision, a system, or a concept.

### 2. Generate candidates
Brainstorm 10-20 possible dials, then filter.

### 3. Score each dimension (1-5 scale)

**Fidelity:**
- Validity: 1 (vague) → 5 (precisely measurable)
- Stability: 1 (context-dependent) → 5 (holds across contexts)

**Leverage:**
- Actionability: 1 (no control) → 5 (direct control)
- Impact: 1 (negligible) → 5 (major effect)

**Complexity:**
- Cognitive load: 1 (simple) → 5 (hard to track)
- Overfitting: 1 (essential) → 5 (theoretical polish)

### 4. Filter and refine
Keep dimensions with: **F ≥ 3.5, L ≥ 3.5, C ≤ 2.5**. Aim for 3-7 final dimensions. **7 axes maximum, ideally 3-5.**

### 5. Validate
- Can you measure/score real options on each dimension?
- Does changing it actually change outcomes?
- Can you hold all dimensions in working memory?
- Are dimensions relatively independent?

## Output Format

For each dimension:
```
**[Dimension Name]** ⟦F: X.X, L: X.X, C: X.X⟧
- What it measures: [one sentence]
- Range: [low end] → [high end]
- Control lever: [how to adjust it]
- Why it matters: [connection to outcome]
```

## Failure Mode Quick Fixes

- **Too many (>7):** merge correlated ones, drop low-leverage. "If I had to pick 5, which matter most?"
- **Vague:** demand concrete measurement criteria. Bad: "culture fit." Good: "team turnover rate."
- **No-control:** reframe to controllable version or drop. Bad: "market timing." Good: "entry timing choice."
- **Overfitted:** collapse correlated dials. Bad: separate "email velocity" and "slack response time." Good: single "communication cadence."
- **Hidden dependencies:** if X high forces Y, keep only upstream dimension

## Constraint Handling

Some factors are binary gates, not dimensions. "Must be remote" → constraint, not dimension. Apply constraints first, dimensionalize remaining space.
