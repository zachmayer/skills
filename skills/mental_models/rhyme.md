# Rhyme

Fast structural similarity detection. Maps a novel input onto known patterns by echo, not deduction. The match may be visual, narrative, functional, or systemic — it *feels* alike. Not true, not proven — just salient. Upstream of metaphor.

## How It Runs

1. **Register** — snapshot the input pattern or system
2. **Scan** — passive recall of matching structures from memory
3. **Note shared features** — form, role, sequence, function
4. **Tag candidates** — save as active candidates for further analysis

This is pre-analytical pattern matching, not rigorous mapping.

## Rhyme Tropes (pattern categories)

- **Visual motifs:** spirals, cascades, symmetries, recursions, fractals, waves
- **Narrative arcs:** fall-from-grace, double agent, forbidden loop, hero's journey, tragedy of commons
- **Role dynamics:** scapegoat, saboteur, empty throne, gatekeeper, bottleneck
- **Formal patterns:** ABBA, edge→core→edge, nested loops, call-and-response
- **Process analogs:** bottlenecked pipeline, open-loop feedback, stochastic search, filtering cascade
- **Systemic frames:** immune response ↔ infosec, market panic ↔ stampede, evolutionary adaptation ↔ A/B testing

## Key Quality Dimensions (score 0.0-1.0)

1. **Parallel density** — how many concrete overlaps? (≥2 structural + ≥1 functional for 0.5+)
2. **Source maturity** — is the source domain well-mapped with codified heuristics and known traps?
3. **Transfer leverage** — how much working know-how could port if the rhyme holds?
4. **Invariants salience** — are shared bits causal/transformational, not ornamental?
5. **Exclusion clarity** — can you crisply list what doesn't port?
6. **Novelty** — fresh enough to cut new affordances, not "business is war" tier?

**Quality threshold:** strong rhymes score ≥0.6 on parallel density, source maturity, transfer leverage, and invariants salience.

## Output Format

For each rhyme candidate:
```
**[Source Domain] ↔ [Target Domain]**
Shared structures: [structural + functional parallels]
Why it rhymes: [one sentence on core similarity]
Quality scores: [parallel density, source maturity, transfer leverage, invariants salience]
What doesn't port: [2-3 key exclusions]
```

Generate 3-5 candidates. Score on quality dimensions. Select highest-scoring for downstream use.

## Downstream

- **Metaphorize:** build complete structural mapping from best rhyme candidate
- **Dimensionalize:** extract source domain's proven dimensions, test which transfer
