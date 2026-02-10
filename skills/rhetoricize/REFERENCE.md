# rhetoricize -- reference

Extended transform catalog, failure modes, and detailed output templates.

---

## dial failure modes

### dial 1: pass set
- too few passes -> miss the actual degrees of freedom
- too many passes -> output bloat; you stop reading (skill issue, but still)

### dial 2: intensity
- subtle -> low signal, everything looks the same
- maximal -> parody leak (unless opposition style is constrained)

### dial 3: drift budget
- low -> false negatives (you reject useful reframes bc language is leaky)
- high -> "conjugate" quietly becomes "invent"

### dial 4: transform scope
- lexical-only -> you miss the biggest persuasion pivots (grammar does crimes too)
- syntactic without controls -> register collision / incoherence

### dial 5: opposition style
- prosecutorial + maximal -> dunks; low epistemic value
- steelman everywhere -> you underbound how persuasion operates in the wild

### dial 6: output policy
- winner-only -> you lose the map, keep only the jump-scare
- full without restraint -> text wall; you scroll, you forget, you cope

### implicit parameter: context
- unstated context -> category errors (you flip the wrong axis)
- "alignment" can be live in ml safety and burned in corp strategy
- "optimization" can be neutral in engineering and sinister in HR

---

## transform catalog

### lexical transforms
- axis-consistent synonym shifts (euphemism <-> dysphemism)
- scalar softening/hardening (some <-> many; friction <-> failure)

### syntactic transforms (often the real boss fight)
- agency transfer (active <-> passive; agent suppression; patient foregrounding)
- responsibility assignment (who did what to whom)
- modality shifts (must/should/can; inevitable/optional)
- uncertainty framing (likely/possible; typical/worst-case)
- nominalization vs verbing (process-as-thing vs action)

---

## detailed output schema

### original skeleton
- epistemic posture: ...
- thesis: ...
- evidence:
  1. ...
  2. ...

### fact ledger
- facts:
  - f1. ...
  - f2. ...
- non-claims:
  - n1. ...
- drift budget: low | medium | high

### charged terms (vector tags)

for each:
- phrase: "..."
- axes: [ ... ]
- role: thesis | evidence-#

### pass a: same stance, opposite valence or axis framing
- thesis: ...
- evidence:
  1. original: "..."
     transformed: "..."
     axis_move: ...
     transforms: lexical | syntactic: ...
- notes: drift checks

### pass b1: inverted evaluation, same facts (strict)
- thesis: ...
- evidence: ...
- constraints: no new predicates; ledger-only
- notes: drift checks

### pass b2: inverted evaluation + flagged implicatures (loose)
- thesis: ...
- evidence: ...
- flagged implicatures:
  - i1. ... (plausible; not entailed)
- notes: drift checks

### pass c: neutral register
- thesis: ...
- evidence: ...
- notes: what was stripped

### pass s: satire bound (optional)
- s+ booster caricature (clearly labeled satire)
- s- hatchet-job caricature (clearly labeled satire)
- notes: any labeled drift (if allowed)

### surprise ranking

| pass | affect_shift | overlap | fluency | surprise | notes |
|------|--------------|---------|---------|----------|-------|
| ...  | ...          | ...     | ...     | ...      | ...   |

### gestalt shift (winner)

one sentence: original emotional center -> transformed emotional center

### hidden fulcrum(s)
1. ...
2. ...
(... up to fulcrum_k)

### null result (allowed)

if text is approximately neutral:
- explicitly state: no rhetorical degrees of freedom detected
- why: low charge, high ledger redundancy, or already technical register

---

## satire bound details

satire is not epistemic output; it's a bracket.
- produce s+ boosterish caricature and s- hatchet-job caricature
- must remain ledger-consistent unless drift budget is high and every drift is labeled
- not included in surprise ranking by default (it's a safety rail, not the road)

---

## common failure modes

- **denotation drift**: flips add/remove facts.
  fix: tighten ledger; lower drift budget; prefer b1.
- **implicature smuggling**: b2 behavior leaks into b1/a.
  fix: enforce b1 strictness; require explicit "flagged implicatures" section.
- **axis collapse**: treating rhetoric as a 1d valence slider.
  fix: tag axes; report axis_move explicitly.
- **passive-voice laundering**: responsibility disappears ("mistakes were made").
  fix: include syntactic transforms; flag agency suppression as a fulcrum candidate.
- **parody leak**: outputs become dunks.
  fix: opposition style = charitable-skeptic; reduce intensity; keep b2 optional.
- **trivial output**: neutral sources yield near-identical passes.
  fix: declare low signal and stop.
