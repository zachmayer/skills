# Reversibility

Classify decisions as two-way doors (reversible) or one-way doors (permanent). Match investment in decision quality to reversibility.

## Framework

**Two-way doors:** easily reversible. Move fast, decide with 70% information, iterate based on feedback. Most decisions are this type. Examples: feature flags, A/B tests, hiring contractors, trying a new tool.

**One-way doors:** hard or impossible to reverse. Slow down, invest in getting it right, seek more information. Examples: major architecture choices, public API contracts, legal commitments, deleting production data.

## Process

1. **Classify** — is this reversible? What's the cost of reversal?
2. **If two-way:** decide quickly, bias toward action, plan to learn from the outcome
3. **If one-way:** invest in analysis, seek diverse input, consider optionality
4. **If uncertain:** can you convert it to a two-way door? (feature flags, pilots, staged rollouts)

## Common Mistake

Treating two-way doors as one-way doors — analysis paralysis on easily reversible decisions. The cost of slow, cautious decision-making on reversible choices often exceeds the cost of being wrong and correcting course.
