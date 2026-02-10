# Rhyme — Reference

Extended pattern library, scoring rubrics, worked examples, and advanced techniques for the Rhyme skill.

## Quality Dimension Scoring Rubrics

### 1. Parallel Density
How many concrete overlaps (not vibes) can you name?
- **0.0** = 1 cute overlap
- **0.5** = >=2 structural + >=1 functional
- **1.0** = >=3 structural + >=2 functional, independently checkable

### 2. Source Maturity
Is the source domain well-mapped (canon, playbooks, failure literature)?
- **0.0** = Folk wisdom only
- **0.5** = Partial standards, scattered case studies
- **1.0** = Codified heuristics + known traps + metrics

### 3. Operator Expertise (Error-Spotting)
Do you know the source deeply enough to catch leaks?
- **0.0** = Tourist
- **0.5** = Competent user
- **1.0** = Can name edge cases & anti-patterns on demand

### 4. Transfer Leverage
How much working know-how could port if the rhyme holds?
- **0.0** = Decorative frame
- **0.5** = A couple of useful rules
- **1.0** = A compact playbook you can run tomorrow

### 5. Invariants Salience
Are the shared bits causal/transformational, not ornaments?
- **0.0** = Motif only (spirals, masks)
- **0.5** = Roles/flows line up
- **1.0** = Core constraints & transforms align (queues, budgets, feedbacks)

### 6. Exclusion Clarity (Leak-Proofing)
Can you crisply list what doesn't port?
- **0.0** = Hand-wavy "obviously not everything"
- **0.5** = A few do-not-ports
- **1.0** = Explicit exclusion set that would catch most dumb misuses

### 7. Communicability
Can you explain the rhyme in 2-4 bullets to a smart outsider?
- **0.0** = Requires a TED talk
- **0.5** = Intelligible with a diagram
- **1.0** = Lands in 20 seconds, no table needed

### 8. Measurability
Are there observable proxies to test the rhyme quickly?
- **0.0** = Pure vibes
- **0.5** = Qualitative spot-checks
- **1.0** = Leading indicators/metrics exist or are easy to stub

### 9. Time-Scale Alignment
Do the dynamics rhyme on timescale (latency, cadence, decay)?
- **0.0** = Mismatch (days vs microseconds)
- **0.5** = Can be rescaled with care
- **1.0** = Native alignment or trivial rescaling

### 10. Composability
Does the rhyme play nicely with other rhymes/maps?
- **0.0** = Conflicts with your existing frames
- **0.5** = Orthogonal
- **1.0** = Plugs into a larger scaffold (becomes a module)

### 11. Novelty (Anti-Cliche)
Is it fresh enough to cut new affordances, not generic poster talk?
- **0.0** = "Business is war" tier
- **0.5** = Familiar but specific
- **1.0** = Crisp, surprising, and helpful

## Parameter Tuning Examples

- **Understanding new domain:** loose tightness, wide breadth, systemic scope
- **Validation checking:** strict tightness, narrow breadth, structural depth
- **Creative brainstorming:** loose tightness, wide breadth, surface-to-deep range

## Worked Example: Protocol Failure Rhyme

**Input:** "An emergent protocol failure where automated systems amplify small errors into cascading problems"

**Rhymes generated:**

1. **Sorcerer's Apprentice (Fantasia) <-> Protocol Failure**
   - Shared structures:
     - Automation exceeds operator's control
     - Positive feedback with no governor
     - Small action -> exponential consequences
     - Helper becomes threat
   - Why it rhymes: Delegated process lacks stop condition
   - Scores: [0.7, 0.9, 0.6, 0.8]
   - Doesn't port: Magic vs code, single actor vs distributed

2. **Cascading Grid Blackout <-> Protocol Failure**
   - Shared structures:
     - Load redistribution creates new stress
     - Failure propagates through connections
     - Recovery requires external intervention
     - Time-critical detection window
   - Why it rhymes: Network effect amplifies local failure
   - Scores: [0.9, 1.0, 0.9, 0.9]
   - Doesn't port: Physical infrastructure vs digital, slower timescale

3. **Bank Run <-> Protocol Failure**
   - Shared structures:
     - Rational individual action creates collective harm
     - Self-fulfilling prophecy dynamics
     - Trust threshold collapse
     - Circuit breakers as mitigation
   - Why it rhymes: Coordination failure under stress
   - Scores: [0.8, 0.9, 0.8, 0.9]
   - Doesn't port: Human psychology vs automated logic

**Best candidate:** Cascading grid blackout (highest scores across dimensions, mature source domain with known mitigations)

## Worked Example: Understanding TikTok Scrolling

**Input:** "Why do people spend so much time scrolling TikTok?"

**Rhymes generated:**

1. **Panning for Gold in River <-> TikTok Scrolling**
   - High-throughput flow, sparse jackpots
   - Hand motions that sift
   - Skill in "where/when to swirl," not producing gold
   - Move-on rules when patch depletes

2. **Patch Foraging (Ecology) <-> TikTok Scrolling**
   - Probe content patches, decide when to leave
   - Rewards deplete locally
   - Travel cost is time/attention
   - Marginal value theorem applies

3. **QC on Fast Assembly Line <-> TikTok Scrolling**
   - Rapid yes/no triage
   - Rare exceptions pulled for inspection
   - Fatigue increases misses
   - Throughput over precision

## Micro-Example

**Input:** An emergent protocol failure

**Rhyme stack (pre-mapping):**
- Enchanted broom in *Fantasia*
- Cascading blackout
- Sorcerer's apprentice archetype
- Positive feedback loop with no governor
- Runaway chemical reaction
- Flash crash in markets

No formal mapping yet—just a stack of echoes primed for model-building.

**Next move:** Score these candidates, select best, then metaphorize for detailed mapping.

## Common Pitfalls & Patches

| Pitfall | Symptom | Patch |
|---------|---------|-------|
| **False positives** | Superficial resemblances crowding signal | Increase tightness; require functional AND structural overlap |
| **Anchoring** | Early match blocks richer ones | Erase & re-query with shifted lens |
| **Overreach** | Treating rhyme as explanatory | Explicitly flag as pre-model heuristic |
| **Cliche trap** | Generic comparisons ("life is a journey") | Score novelty dimension, require >=0.6 |
| **Scope mismatch** | Comparing wrong abstraction levels | Clarify whether matching elements or systems |
| **Porting everything** | Assuming all features transfer | Demand explicit exclusion list |

## Integration Protocol

### Rhyme -> Metaphorize Pipeline
1. Generate 3-5 rhyme candidates
2. Score on quality dimensions
3. Select highest-scoring rhyme (>=0.6 on key dimensions)
4. Use as input for metaphorize move
5. Build complete domain mapping

### Rhyme -> Dimensionalize Pipeline
1. Rhyme target domain with mature source
2. Extract source domain's proven dimensions
3. Test which dimensions transfer
4. Adapt dimension definitions for target context

## Quality Checklist

Before finalizing rhyme candidates:

- [ ] Generated 3+ distinct rhyme candidates
- [ ] Each rhyme has >=2 structural parallels
- [ ] Each rhyme has >=1 functional parallel
- [ ] Scored top candidates on quality dimensions
- [ ] Identified what doesn't port for each rhyme
- [ ] Can explain each rhyme in <30 seconds
- [ ] Selected best candidate scores >=0.6 on: parallel density, source maturity, transfer leverage, invariants salience
- [ ] Explicitly flagged as pre-analytical pattern match, not proof

## Advanced Techniques

### Constraint-Based Rhyming
Specify what must rhyme:
- "Rhyme X, but constrain to systems with known failure modes"
- "Rhyme X, focusing on resource allocation patterns"

### Multi-Source Rhyming
Find multiple partial rhymes, synthesize:
- "X rhymes with A for process, B for roles, C for failure modes"
- Composite mapping from multiple sources

### Temporal Rhyming
Match on dynamic patterns across time:
- Growth curves (S-curves, exponential, logarithmic)
- Cycle patterns (boom-bust, seasonal, oscillation)
- Decay patterns (half-life, asymptotic, stepped)

### Anti-Rhyming
Find structural opposites to define boundaries:
- "What is the opposite structure?"
- Useful for exclusion lists and constraint mapping
