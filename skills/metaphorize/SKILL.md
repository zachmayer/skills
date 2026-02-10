---
name: metaphorize
description: >
  Build explicit, high-coverage mapping from familiar source domain onto target
  domain to systematically port rules, heuristics, formulas, and metrics. Heavier
  than rhyme, lighter than formal proof. When source has math, carry the math with
  units and dimensional analysis. WHEN NOT: domains without rich formalism (use
  rhyme instead), precise formal proof needed, source domain poorly understood,
  target too different (poor rhyme scores), time-critical decisions, or when simple
  heuristics suffice.
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
Pick a domain with robust, worked rules that meaningfully fits **t**.

**Quality criteria:** mature formalism (equations, metrics, known failure modes), structural similarity to target, rich playbook of proven strategies, well-understood constraints and invariants.

### 2. List Primitives
Enumerate entities, relations, operations in **s** that drive behavior.

**Entity types:** objects/agents, resources (capacity, budget, attention), states (waiting, processing, complete), flows (arrival, departure, transformation), control structures (gates, priorities, feedback loops).

### 3. Mine Formalism & Metrics (MANDATORY when available)
Harvest **s**'s named formulas, laws, and scorekeeping:

- **Equations & Constraints:** Little's Law, Bayes' theorem, PID control, stock-flow equations, hazard functions, Markov chains, S-curves, conservation laws
- **Objective/Penalty Functions:** loss functions, regret, cost of delay, utility functions, risk premiums
- **Standard Metrics:** SLA/SLO definitions, Brier/log-loss/AUC, throughput, WIP, cycle time, defect rates
- **Units & Dimensions:** carry units explicitly, perform dimensional analysis, check unit consistency across mapping
- **Parameter Sets:** parameters needing estimation (theta), priors/bounds, data requirements, validation strategies

### 4. Draft Mapping `m : s -> t`
Name counterparts in **t** for each primitive in **s**. Mark gaps. Attach adapters with typed signatures.

**Adapter examples:**
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
Specify transforms/constraints from **s** to preserve under **m**, **with units**. Write as testable assertions.

**Categories:** queue discipline, conservation laws, budget constraints, escalation semantics, feedback loops (sign), stability conditions.

```
ASSERT: lambda < c*mu  (stability condition)
ASSERT: sum(inflow) = sum(outflow) + delta_stock  (conservation)
ASSERT: high_priority_wait < low_priority_wait  (priority discipline)
```

### 6. Metric Plan
Define how success/failure will be measured in **t**:

- **Primary metrics:** target values, acceptable ranges
- **Secondary metrics:** supporting indicators
- **Counter-metrics:** what you refuse to optimize
- **Baselines:** current state, historical average
- **Acceptance thresholds:** pass/fail criteria
- **Evaluation cadence:** how often to measure

### 7. Estimation & Calibration
Lay out how theta will be identified/fit:

- **Estimation method:** MLE, MAP, robust regression, Bayesian updating
- **Data needed:** sample size, time window, granularity
- **Validation strategy:** cross-validation, holdout, backtesting
- **Error decomposition:** bias/variance, aleatoric/epistemic

### 8. Package
Compress into a table/diagram/substitution kit + a **formula shelf** others can apply without you.

**Deliverables:** primitive mapping table, formula shelf with relabeled equations, invariant list with units, metric plan with baselines, worked examples (rule-throughs), explicit exclusion list.

**Quality gates before finalizing:**
- All carried formulas have explicit units and dimensional analysis passes
- Invariants listed as testable assertions
- Metric plan includes baselines, thresholds, and counter-metrics
- 3+ rule-throughs with numerical examples
- Exclusion list explicit and documented
- Scored >=0.7 on: formal leverage, counterpart clarity, invariant quality, unit discipline

### 9. Probe
Run representative rules from **s** through **m**; compute; compare to baselines; note failure modes at the seam.

**Test protocol:**
- Select 3-5 core rules from **s**
- Apply mapping to translate to **t**
- Compute numerical predictions
- Compare to observed behavior in **t**
- Document where mapping breaks

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
Worked examples `rule_s --> rule_t` with numbers.
```
Rule in s: [description]
Numerical example in s: [with units]
Mapped to t: [description]
Numerical example in t: [with units]
Prediction: [what should happen]
```

### Metric Sheet
Primary/secondary metrics, targets, and review cadence.

## Detailed Example: GitHub Issues <- ER Triage

**Target (t):** Backlog of GitHub issues
**Source (s):** Hospital emergency-room triage (queueing + priority scheduling)

### Primitive Mapping

| s (ER) | t (Issues) | Adapter | Units |
|--------|------------|---------|-------|
| patient | ticket | 1:1 | [entities] |
| triage nurse | intake bot | 1:1 | [agent] |
| severity level | priority class | severity:int -> {p0,p1,p2,p3} | [class] |
| attending physician | ticket owner | 1:1 | [agent] |
| beds / staff | parallel servers (devs) | beds:int -> devs:int, capacity `c` | [workers] |
| arrival rate `lambda` | issue inflow | lambda:[patients/hr] -> lambda:[issues/day] | [1/time] |
| service rate `mu` | resolve rate per dev | mu:[patients/hr/doc] -> mu:[issues/day/dev] | [1/time/worker] |
| utilization `rho=lambda/(c*mu)` | load factor | direct port | [dimensionless] |
| wait-time SLA | breach threshold | direct port with adapted time units | [time] |

### Preserved Structure (with Math)

**Little's Law:**
```
Source: L = lambda*W  [patients = (patients/hr)*(hr)]
Target: Backlog = lambda*W  [issues = (issues/day)*(days)]
Invariant: Conservation of items in system
```

**Stability Condition:**
```
Source: rho = lambda/(c*mu) < 1  (stable queue)
Target: rho = lambda/(c*mu) < 1  (stable backlog)
Action: If lambda >= c*mu, queue grows without bound -- throttle intake or add capacity
```

**Priority Discipline:**
```
P0 issues reduce cycle time for critical bugs at cost to P3 features
Invariant: W_high < W_low when priority enforced
```

**Handoff Protocol:**
```
Issue reassignment requires explicit owner acceptance
Invariant: No orphaned work items
```

### Rule-Through (Numerical)

**Scenario:** Unstable queue

**Given:** lambda = 5 issues/day, mu = 2 issues/day/dev, c = 2 devs

```
rho = lambda/(c*mu) = 5/(2*2) = 1.25 > 1  ==>  UNSTABLE
```

Queue grows without bound. Options to restore stability (rho < 1):

**(a) Raise c to 3 devs:** rho = 5/(3*2) = 0.833 < 1 (stable)
**(b) Reduce lambda to 3/day via intake gate:** rho = 3/(2*2) = 0.75 < 1 (stable)
**(c) Increase mu to 2.5/day/dev:** rho = 5/(2*2.5) = 1.0 (marginal -- needs buffer)

**New SLA:** Set `P(W > 5 days) < 0.05` and monitor weekly.

### Metrics

| Type | Metrics |
|------|---------|
| **Primary** | Cycle time [days], breach rate [%], rho [dimensionless], throughput [issues/day], age of WIP [days] |
| **Secondary** | Preemption count [/week], handoff latency [hours], reopen rate [%] |
| **Counter-metrics** | Issue close rate if quality drops; dev velocity if measured narrowly |
| **Alerts** | Weekly CFD; alert when rho > 0.9; alert when P0 cycle time slope up 2 weeks running |

### Breakpoints (Explicit Exclusions)

**Does NOT port from ER to issues:** mortality consequences, informed consent, bedside manner / patient care ethics, HIPAA compliance, physical resource constraints, mass casualty protocols.

**Why:** Prevents overreach where high-stakes medical ethics get inappropriately mapped to software bug prioritization.

## Quality Dimensions

Score mappings on these dimensions (0.0 -> 1.0). Strong metaphors score >=0.7 on dimensions marked with *.

| Dimension | 0.0 | 0.5 | 1.0 |
|-----------|-----|-----|-----|
| Counterpart clarity* | Mushy "this ~ that" | Mostly crisp | Crisp with documented degeneracy |
| Invariant set quality* | Ornaments only | Roles/flows align | Core transforms doing computational work |
| Formal leverage* | No formalism | Heuristics + back-of-envelope | Named equations with units + glossary |
| Unit discipline* | Unitless vibes | Partial unit tracking | Unit-clean with dimensional analysis |
| Pillar integrity | Nukes a core transform | Some bleed | Exclusions orthogonal to core structure |
| Adapter load | Adapter spaghetti | A few shims | Minimal, typed, local adapters |
| Failure localization | Errors smear across domains | Sometimes localized | Seam-tight: breakpoints catch misuse |
| Scope crispness | Grand theory / toy slice | Process-level scope | Process<->system slice with clear borders |
| Metric rigor | Vanity counts | Mixed useful/vanity | Decision-useful eval with counter-metrics |

## Downstream Moves & Compounding

### Dimensionalize
Score the map's complexity, leverage, fidelity; pick the best among alternative mappings. Generate 2-3 candidate metaphors, score each on the 9 quality dimensions, select highest-scoring map.

## Integration Protocol

### Rhyme -> Metaphorize Pipeline
1. Use Rhyme to identify 3-5 candidate source domains
2. Score candidates on quality dimensions from Rhyme skill
3. Select best source (high on parallel density, source maturity, transfer leverage)
4. Run full Metaphorization protocol on selected source
5. Validate with rule-throughs and numerical examples

### Metaphorize -> Dimensionalize Pipeline
1. Complete metaphor mapping
2. Use Dimensionalize to evaluate mapping quality
3. Score on F*L*C criteria
4. Refine mapping based on dimension scores
