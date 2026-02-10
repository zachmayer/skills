# Metaphorize Reference

Extended examples, quality dimensions, formula shelf, and advanced techniques for the metaphorize skill. See [SKILL.md](SKILL.md) for the core protocol.

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
Invariant: If lambda >= c*mu, queue grows without bound
Action: Must throttle intake or add capacity
```

**Priority Discipline:**
```
Source: Preemptive priority reduces W for high severity at cost to low
Target: P0 issues reduce cycle time for critical bugs at cost to P3 features
Invariant: W_high < W_low when priority enforced
```

**Handoff Protocol:**
```
Source: Patient reassignment requires explicit attending acknowledgment
Target: Issue reassignment requires explicit owner acceptance
Invariant: No orphaned work items
```

### Rule-Through (Numerical)

**Scenario:** Unstable queue

**Given parameters:**
- lambda = 5 issues/day (measured from last 30 days)
- mu = 2 issues/day/dev (historical average)
- c = 2 devs (current team)

**Calculation:**
```
rho = lambda/(c*mu) = 5/(2*2) = 1.25 > 1  ==>  UNSTABLE
```

**Interpretation:** Queue will grow without bound. Backlog accumulates faster than resolution.

**Options to restore stability (rho < 1):**

(a) **Raise c to 3 devs:**
```
rho = 5/(3*2) = 0.833 < 1  -- stable
Expected backlog reduction: ~40%
```

(b) **Reduce lambda via intake gate:**
```
Target: lambda = 3 issues/day
rho = 3/(2*2) = 0.75 < 1  -- stable
Method: Stricter triage, merge similar issues
```

(c) **Increase mu via process improvement:**
```
Target: mu = 2.5 issues/day/dev
rho = 5/(2*2.5) = 1.0  (marginal stability)
Method: Swarming, reduce non-work items, automation
```

**New SLA:** Set `P(W > 5 days) < 0.05` and monitor weekly

### Metrics

**Primary metrics:**
- Cycle time [days] - time from open to close
- Breach rate [%] - fraction exceeding SLA
- rho [dimensionless] - utilization factor
- Throughput [issues/day] - completion rate
- Age of WIP [days] - time issues spend in progress

**Secondary metrics:**
- Preemption count [count/week] - priority overrides
- Handoff latency [hours] - time for owner acceptance
- Reopen rate [%] - fraction reopened after close

**Counter-metrics (refuse to optimize):**
- Issue close rate if quality drops
- Dev velocity if measured narrowly

**Evaluation:**
- Weekly CFD (cumulative flow diagram)
- Alert when rho crosses 0.9
- Alert when P0 cycle time slope increases two weeks running

### Breakpoints (Explicit Exclusions)

**Does NOT port from ER to issues:**
- Mortality consequences (life/death stakes)
- Informed consent requirements
- Bedside manner / patient care ethics
- HIPAA compliance
- Physical resource constraints (ambulances, equipment)
- Triage under mass casualty protocols

**Why these matter:** Prevents overreach where high-stakes medical decision-making ethics get inappropriately mapped to software bug prioritization.

## Dimensionalization of Metaphorization Quality

Score mappings on these dimensions (0.0 to 1.0):

### 1. Pillar Integrity
Do exclusions avoid cutting the beams the map stands on?
- **0.0** = Nukes a core transform
- **0.5** = Some bleed between preserved/excluded
- **1.0** = Exclusions orthogonal to core structure

### 2. Counterpart Clarity
Unambiguous primitive mapping (1 to 1 or explicit 1 to n with adapters)?
- **0.0** = Mushy "this is roughly that"
- **0.5** = Mostly crisp
- **1.0** = Crisp with documented degeneracy

### 3. Invariant Set Quality
Preserved bits are operators/constraints (queues, budgets, feedback), not motifs
- **0.0** = Ornaments only
- **0.5** = Roles/flows align
- **1.0** = Core transforms that do computational work

### 4. Formal Leverage
Portable math/algorithms carried (Little's law, PID, Bayes, stock-flow, hazard)
- **0.0** = No formalism
- **0.5** = Heuristics + back-of-envelope
- **1.0** = Named equations with units + glossary

### 5. Adapter Load
How many/complex adapters to make types line up?
- **0.0** = Adapter spaghetti
- **0.5** = A few shims
- **1.0** = Minimal, typed, local adapters

### 6. Failure Localization
Do errors surface at the seam they're caused (good metaphors fail noisily)?
- **0.0** = Errors smear across domains
- **0.5** = Sometimes localized
- **1.0** = Seam-tight: breakpoints catch misuse

### 7. Scope & Edge Crispness
Bounded region where map holds + explicit edges
- **0.0** = Grand theory / toy slice
- **0.5** = Process-level scope
- **1.0** = Process-to-system slice with clear borders

### 8. Metric Rigor
Are we scoring what matters with baselines/thresholds?
- **0.0** = Vanity counts
- **0.5** = Mixed useful/vanity
- **1.0** = Decision-useful eval with counter-metrics

### 9. Unit Discipline
Explicit units + dimensional checks?
- **0.0** = Unitless vibes
- **0.5** = Partial unit tracking
- **1.0** = Unit-clean throughout with dimensional analysis

**Quality threshold:** Strong metaphors score >=0.7 on formal leverage, counterpart clarity, invariant set quality, and unit discipline.

## Formula Shelf (Starter Kit to Port)

### Queueing Theory
```
Little's Law: L = lambda*W
  L: average items in system [items]
  lambda: arrival rate [items/time]
  W: average time in system [time]

M/M/1 Queue Wait: W_q = rho/(mu-lambda)
  rho: utilization = lambda/mu [dimensionless]
  mu: service rate [items/time]

M/M/c Stability: rho = lambda/(c*mu) < 1
  c: number of servers [count]
```

### Bayesian Inference
```
Bayes' Theorem: P(H|D) proportional to P(D|H)*P(H)
  H: hypothesis
  D: data

Calibration metrics:
  Brier score: (1/N) * sum(f_i - o_i)^2
  Log loss: -(1/N) * sum[o_i*log(f_i) + (1-o_i)*log(1-f_i)]
```

### Control Theory
```
PID Controller: u(t) = K_p*e(t) + K_i*integral(e(t)dt) + K_d*de/dt
  e(t): error = setpoint - measurement
  u(t): control signal
  K_p, K_i, K_d: tuning parameters

Map e to: gap vs target metric
```

### Stock-Flow Accounting
```
Stock Evolution: stock_{t+1} = stock_t + inflow - outflow
  All terms must have same units [items]
  Conservation: delta_stock = integral(inflow - outflow)dt
```

### Survival Analysis
```
Survival Function: S(t) = exp(-integral_0^t h(tau) d_tau)
  h(t): hazard rate [1/time]
  S(t): probability of surviving past time t

Applications: retention, time-to-defect, churn
```

### Learning Curves
```
Experience Curve: cost proportional to n^(-beta)
  n: cumulative production [units]
  beta: learning rate [dimensionless]

Map to: throughput/quality improvements over time
```

**Usage:** For each formula:
1. Relabel variables for target domain
2. Specify units explicitly
3. Document parameter estimation plan
4. List data requirements
5. Define validation tests

## Common Pitfalls & Patches

| Pitfall | Symptom | Patch |
|---------|---------|-------|
| **Underreach** | Vibes-only mapping; no formulas/units/metrics | Run steps 3-7; build formula shelf; add unit checks + metric sheet |
| **Leakage** | Irrelevant parts of **s** infect **t** | Expand exclusion set; make non-ports explicit |
| **Overreach** | Mapping treated as truth | Keep invariants listed; label as provisional scaffold |
| **Mushy primitives** | Ambiguous counterparts | Reduce coverage; redefine crisper primitives first |
| **Cliche drag** | Stale metaphors bias attention | Generate counter-maps; prefer cleaner, less-worn sources |
| **Untested transfer** | No friction checks | Run adversarial rule-throughs; hunt contradictions/edges |
| **Unit errors** | Dimensional mismatches | Add explicit unit tracking; run dimensional analysis |
| **Metric confusion** | Vanity metrics vs decision-useful | Add counter-metrics; demand baselines and thresholds |

## Downstream Moves & Compounding

### Dimensionalize
Score the map's complexity, leverage, fidelity; pick the best among alternative mappings.

**Process:**
1. Generate 2-3 candidate metaphors
2. Score each on the 9 quality dimensions
3. Select highest-scoring map (>=0.7 on key dimensions)

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

## Quality Checklist

Before finalizing metaphorization:

- [ ] Primitive mapping table complete with adapters
- [ ] All carried formulas have explicit units
- [ ] Dimensional analysis performed (units consistent)
- [ ] Invariants listed as testable assertions
- [ ] Metric plan includes baselines and thresholds
- [ ] Counter-metrics identified (what not to optimize)
- [ ] Exclusion list explicit and documented
- [ ] 3+ rule-throughs with numerical examples
- [ ] Estimation/calibration plan for parameters
- [ ] Scored >=0.7 on: formal leverage, counterpart clarity, invariant quality, unit discipline
- [ ] Probed for failure modes at domain seam
- [ ] Packaged for reuse (formula shelf, glossary, worked examples)

## Advanced Techniques

### Multi-Source Synthesis
Combine mappings from multiple source domains:
```
Domain A -> [process flow]
Domain B -> [resource allocation]
Domain C -> [failure modes]
Synthesized map: composite structure
```

### Bidirectional Mapping
Map s<->t instead of just s->t:
- Validates symmetry of structure
- Reveals hidden assumptions
- Tests for accidental complexity

### Adaptive Mapping
Evolve mapping over time as understanding deepens:
- Version mappings (v1.0, v1.1, etc.)
- Track which predictions held/failed
- Refine based on empirical validation

### Constraint-Based Mapping
Specify hard requirements on mapping:
- "Must preserve conservation laws"
- "Must carry at least 3 equations"
- "Exclusions must be orthogonal to core"
