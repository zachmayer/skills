---
name: metaphorize
description: Build explicit, high-coverage mapping from familiar source domain onto target domain to systematically port rules, heuristics, formulas, and metrics. Heavier than rhyme, lighter than formal proof. When source has math, carry the math with units and dimensional analysis.
---

# Metaphorization

## Overview

**Metaphorization** builds an explicit, high-coverage mapping from a familiar source **s** onto a live target **t** so that rules, heuristics, and intuitions from **s** can be systematically **ported** into testable hypotheses or prompts for **t**.

Heavier than tier-2 **rhyme**; lighter than a fully formal mapping. Preserve as many invariants as are useful; fence off the rest. When **s** has math, **carry the math**: equations, units, objective functions, constraints, and standard metrics.

Claude should use this Skill when the user:
- Explicitly asks to "metaphorize" something
- Has identified a good rhyme and wants complete structural mapping
- Needs to transfer strategy/rules from one domain to another systematically
- Wants to port mathematical formalism across domains
- Says "build the full mapping" or "what transfers from X to Y?"
- Needs testable hypotheses from cross-domain analogy

## How It Runs

### 1. Select Source (s)
Pick a domain with robust, worked rules that meaningfully fits **t**. Prefer mature formalism (equations, metrics, known failure modes) and structural similarity from rhyme analysis.

### 2. List Primitives
Enumerate entities, relations, operations in **s** that drive behavior: objects/agents, resources, states, flows, and control structures.

### 3. Mine Formalism & Metrics (MANDATORY when available)
Harvest **s**'s named formulas, laws, and scorekeeping: equations & constraints, objective/penalty functions, standard metrics, units & dimensions, and parameter sets needing estimation (theta). Carry units explicitly and perform dimensional analysis.

### 4. Draft Mapping `m : s -> t`
Name counterparts in **t** for each primitive in **s**. Mark gaps. Attach adapters with typed signatures.

```
priority_s:int -> class_t:{p0,p1,p2,p3}
severity_s -> risk_t := p(event) x impact
rate_s [1/time] -> rate_t [items/day]
capacity_s [beds] -> capacity_t [parallel workers]
```

**Mapping table format:**
| Source (s) | Target (t) | Adapter | Units |
|------------|------------|---------|-------|
| Entity_s | Entity_t | Type signature | [units] |

### 5. Name Invariants (Make them checkable)
Specify transforms/constraints from **s** to preserve under **m**, **with units**. Write as testable assertions:
```
ASSERT: lambda < c*mu  (stability condition)
ASSERT: sum(inflow) = sum(outflow) + delta_stock  (conservation)
ASSERT: high_priority_wait < low_priority_wait  (priority discipline)
```

### 6. Metric Plan
Define how success/failure will be measured in **t**: primary metrics (target values, acceptable ranges), secondary metrics, counter-metrics (what you refuse to optimize), baselines, acceptance thresholds, and evaluation cadence.

### 7. Estimation & Calibration
Lay out how theta will be identified/fit: estimation method, data needed, sampling window, validation strategy, and error decomposition (bias/variance, aleatoric/epistemic).

### 8. Package
Compress into a table/diagram/substitution kit + a **formula shelf** others can apply without you. Deliverables: primitive mapping table, formula shelf with relabeled equations, invariant list with units, metric plan with baselines, worked examples (rule-throughs), and explicit exclusion list.

### 9. Probe
Run 3-5 representative rules from **s** through **m**; compute numerical predictions; compare to observed behavior in **t**; document where mapping breaks.

## Parameters (Knobs)

| Knob | Range / Values | Effect |
|------|----------------|--------|
| **tightness** | loose <-> strict | Similarity required to accept the map |
| **coverage** | sparse <-> broad | Fraction of **s** given counterparts in **t** |
| **invariant count** | few <-> many | How much disciplined behavior is demanded |
| **invariant strength** | soft hints <-> hard constraints | How binding the invariants are during transfer |
| **scope** | local element <-> process <-> system | Region of **t** the map is allowed to touch |
| **directionality** | s->t / t->s / bidirectional | Where rules originate vs interrogated |
| **claim strength** | framing <-> hypothesis <-> provisional policy | Rhetorical weight of the mapping |
| **medium** | words / diagram / table / code / equations | Packaging; affects reuse and error rate |
| **exclusion clarity** | informal notes <-> explicit exclusion set | Leak-prevention fidelity |
| **test budget** | quick spot-checks <-> adversarial stress tests | Confidence in transfer |
| **source maturity** | folk schema <-> codified playbook | Reliability of imported intuition |
| **math depth** | heuristics <-> relabeled, unitful equations | Extent of formal carryover |
| **unit fidelity** | implicit <-> explicit units + dim. analysis | Prevents type errors across the seam |
| **metric rigor** | vanity counts <-> decision-useful eval w/ baselines | Quality of scorekeeping |

## Output Format

A compact **translation guide** `m(s -> t)` -- shareable and reusable -- plus:

### Formula Shelf
Relabeled equations/constraints with units and variable glossary.
```
[Formula Name]
Source: [equation in s notation]
Target: [equation in t notation]
Variables: [glossary with units]
Constraints: [parameter bounds]
Estimation: [how to fit theta]
```

### Hypothesis Set
What should be true in **t** if the map holds (quantified).
```
H1: [quantified prediction with units]
H2: [quantified prediction with units]
Test protocol: [how to validate]
```

### Rule-Throughs
Worked examples `rule_s -> rule_t` with numbers.
```
Rule in s: [description]
Numerical example in s: [with units]
Mapped to t: [description]
Numerical example in t: [with units]
Prediction: [what should happen]
```

### Metric Sheet
Primary/secondary metrics, targets, and review cadence.

## When NOT to Use

Avoid metaphorization for:
- Domains without rich formalism (use rhyme instead)
- When precise formal proof required (use mathematical modeling)
- Source domain poorly understood (strengthen source knowledge first)
- Target domain too different (poor rhyme scores)
- Time-critical decisions (too heavyweight)
- When simple heuristics suffice

## References

Canonical definition:
https://github.com/jordanrubin/FUTURE_TOKENS/blob/main/metaphorize.md

Examples and workflows:
https://jordanmrubin.substack.com/p/conceptual-rhyme-and-metaphor

Related concepts:
- Structure mapping theory (Gentner)
- Analogical reasoning (Hofstadter)
- Dimensional analysis (Buckingham pi theorem)
- Queueing theory (Kendall notation)

For worked examples, dimensional analysis details, and advanced patterns, see [REFERENCE.md](REFERENCE.md).
