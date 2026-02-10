---
name: rhyme
description: Fast structural similarity detection that maps novel inputs onto known patterns through echo recognition. Use for understanding unfamiliar domains, creative seeding, intuition framing, or finding parallel structures across different contexts. Upstream move before metaphor or detailed mapping.
---

# Rhyme

## Overview

**Rhyme** is fast structural similarity. It maps a novel input onto known patterns by echo, not deduction. The match may be visual, narrative, functional, or systemic—but it *feels* alike. Not true, not proven—just salient.

Rhyme is upstream of metaphor. It clusters, suggests, frames. Nothing more—but often the first real foothold.

Claude should use this Skill when the user:
- Explicitly asks to "rhyme" something
- Seeks structural parallels or analogies
- Wants to understand an unfamiliar domain through pattern matching
- Needs creative seeding across domains
- Says "what's this like?" or "remind me of..."
- Wants to bootstrap intuition about a new system

## How It Runs (~1-3s cognitive time)

1. **Register A** – Snapshot the input pattern or system
2. **Scan memory** – Passive recall of matching structures
3. **Note shared features** – Form, role, sequence, function
4. **Tag A ↔ B** – Save as active candidate for further analysis

This is pre-analytical pattern matching, not rigorous mapping.

## Rhyme Tropes

Common pattern categories that trigger rhyme:

- **Visual Motifs:** Spirals, cascades, symmetries, recursions, fractals, waves
- **Narrative Arcs:** Fall-from-grace, double agent, forbidden loop, hero's journey, tragedy of commons
- **Role Dynamics:** Scapegoat, saboteur, empty throne, gatekeeper, facilitator, bottleneck
- **Formal Patterns:** ABBA, edge→core→edge, nested loops, call-and-response
- **Process Analogs:** Bottlenecked pipeline, open-loop feedback, stochastic search, filtering cascade
- **Systemic Frames:** Immune response ↔ infosec, market panic ↔ stampede, evolutionary adaptation ↔ A/B testing, river delta ↔ org structure

## Parameters

| Knob | Range | Effect |
|------|-------|--------|
| **tightness** | loose → strict | Shared features needed to register a rhyme |
| **scope** | local → systemic | Within elements or across processes |
| **breadth** | narrow → wide | How many rhymes held in working memory |
| **depth** | surface → structural | How abstract the match can be |
| **agenda** | neutral / goal-tuned | Constrain activation by current objective |

## Quality Dimensions

Score each rhyme candidate (0.0 → 1.0) on 11 dimensions:

1. **Parallel Density** – How many concrete overlaps can you name?
2. **Source Maturity** – Is the source domain well-mapped (canon, playbooks, failure lit)?
3. **Operator Expertise** – Do you know the source deeply enough to catch leaks?
4. **Transfer Leverage** – How much working know-how ports if the rhyme holds?
5. **Invariants Salience** – Are the shared bits causal/transformational, not ornaments?
6. **Exclusion Clarity** – Can you crisply list what doesn't port?
7. **Communicability** – Can you explain the rhyme in 2-4 bullets?
8. **Measurability** – Are there observable proxies to test the rhyme?
9. **Time-Scale Alignment** – Do the dynamics rhyme on timescale?
10. **Composability** – Does the rhyme play nicely with other rhymes/maps?
11. **Novelty** – Fresh enough to cut new affordances, not generic poster talk?

**Quality threshold:** Strong rhymes score >=0.6 on parallel density, source maturity, transfer leverage, and invariants salience.

For full scoring rubrics and worked examples, see [REFERENCE.md](REFERENCE.md).

## Output Format

For each rhyme candidate, provide:
```
**[Source Domain] ↔ [Target Domain]**

Shared structures:
- [Structural parallel 1]
- [Structural parallel 2]
- [Functional parallel 1]

Why it rhymes: [One sentence on core similarity]

Quality scores: [Parallel density, Source maturity, Transfer leverage, Invariants salience]

What doesn't port: [2-3 key exclusions]
```

## When to Use

- **Understanding Unfamiliar Domains:** Bootstrap comprehension via structural echo
- **Creative Seeding:** Generate multiple reference-class hits before designing
- **Intuition Framing:** Snap a half-formed hunch to known shape
- **Debugging & Sensemaking:** Check for recurring structures in divergent settings

## When NOT to Use

- Rigorous proof or validation (use formal methods)
- When you need precision over intuition
- Highly technical domains where analogies mislead
- When existing formal models are adequate
- Time-critical decisions (too exploratory)

## Downstream Moves

**Dimensionalize:** Filter rhymes for utility, leverage, clarity using the 11 quality dimensions

**Metaphorize:** Build complete structural mapping from best rhyme candidate

## References

Canonical definition:
https://github.com/jordanrubin/FUTURE_TOKENS/blob/main/rhyme.md

Examples and workflows:
https://jordanmrubin.substack.com/p/conceptual-rhyme-and-metaphor

Related concepts:
- Analogical reasoning (Hofstadter)
- Pattern matching in expertise (Klein)
- Structural similarity (Gentner)
