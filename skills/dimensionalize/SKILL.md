---
name: dimensionalize
description: Transform complex decisions or systems into 3-7 measurable dimensions that score high on fidelity (validity+stability), leverage (actionability+impact), and low on complexity (cognitive load+overfitting). Use when facing multi-factor choices, analyzing systems, or comparing non-obvious options.
---

# Dimensionalize

## Overview

Dimensionalization is naming the handful of dials that actually move a system. A good dial scores high on three meta-dimensions: **fidelity**, **leverage**, and low on **complexity**.

Claude should use this Skill when the user:
- Explicitly asks to "dimensionalize" something
- Faces a complex decision with competing factors
- Wants to understand what actually moves a system
- Needs to compare options across different attributes
- Asks "what dimensions matter here?" or similar

## Core Framework

### The Three Meta-Dimensions

| Meta-Dim | Sub-Dims | Mnemonic |
|----------|----------|----------|
| **Fidelity** | validity + stability | "is it *real* and does it hold up?" |
| **Leverage** | actionability + impact | "can i twist it, and does twisting matter?" |
| **Complexity** | cognitive load + overfitting risk | "can i juggle it, or does it drown me?" |

**Remember: F=valid+stable, L=action+impact, C=load+overfit**

**Dimension quality thresholds:** F >= 3.5, L >= 3.5, C <= 2.5

**Complexity ceiling: 7 axes maximum (ideally 3-5)**

## Process

### 1. Identify the System
What needs dimensionalizing? A decision, a system, or a concept.

### 2. Generate Candidate Dimensions
Brainstorm 10-20 possible dials, then filter using F/L/C criteria.

### 3. Score Each Dimension (1-5 scale)

- **Fidelity:** Validity (vague -> precise) + Stability (context-dependent -> holds across contexts). Average the two.
- **Leverage:** Actionability (no control -> direct control) + Impact (negligible -> major). Average the two.
- **Complexity:** Cognitive load (simple -> hard to track) + Overfitting (essential -> theoretical polish). Average the two. **Lower is better.**

### 4. Filter and Refine
Keep dimensions meeting the quality thresholds above. Aim for 3-7 final dimensions.

### 5. Validate
For each dimension: Can you measure real options on it? Does changing it change outcomes? Are dimensions relatively independent? Can you hold all of them in working memory?

## Output Format

For each dimension, provide:
```
**[Dimension Name]** [F: X.X, L: X.X, C: X.X]
- What it measures: [one sentence]
- Range: [low end] -> [high end]
- Control lever: [how to adjust it]
- Why it matters: [connection to outcome]
```

## Common Failure Modes

| Failure | Fix |
|---------|-----|
| Too many dimensions (>9) | Merge correlated ones, drop low-leverage. Ask: "If I had to pick just 5?" |
| Vague dimensions ("culture fit") | Demand concrete measurement criteria ("team turnover rate") |
| No-control dimensions ("market timing") | Reframe to controllable version ("entry timing choice") or drop |
| Overfitted dimensions | Collapse correlated dials into one ("communication cadence") |
| Hidden dependencies | Keep only the upstream dimension or treat as constraint |

## Advanced Techniques

- **Constraint handling:** Binary gates (must be remote, salary > $X) are constraints, not dimensions. Apply constraints first, then dimensionalize.
- **Weighting:** Context determines relative importance (new parent -> boost lifestyle stability; early career -> boost skill compounding).
- **Dimension discovery via Rhyme:** Find structurally similar decisions in other domains and import their proven dimensions.
- **Meta-dimensionalization:** Validate your framework by dimensionalizing the dimensions themselves using F/L/C.

## When NOT to Use

- Simple binary choices (overhead exceeds value)
- Pure gut decisions (some things resist analysis)
- Time-critical decisions (use faster heuristics)
- When an excellent framework already exists
- Emotionally fraught choices where analysis obscures values

## Quality Checklist

- [ ] 3-7 dimensions total
- [ ] Each dimension: F >= 3.5, L >= 3.5, C <= 2.5
- [ ] Can score 5+ real options on each dimension
- [ ] Dimensions are relatively independent
- [ ] Covers 80%+ of what matters
- [ ] Each dimension has clear measurement criteria and control lever

## Integration with Other Skills

**Rhyme:** Find analogous systems, borrow their dimensions
**Metaphorize:** Port complete dimension frameworks across domains

## References

For worked examples and scoring details, see [REFERENCE.md](REFERENCE.md).

- [Theoretical foundation](https://www.lesswrong.com/posts/LSFiKt4zGxXcX2oxi/dimensionalization)
- [Practical examples](https://jordanmrubin.substack.com/p/use-ai-to-dimensionalize)
- [Canonical definitions](https://github.com/jordanrubin/FUTURE_TOKENS/blob/main/dimensionalize.md)
