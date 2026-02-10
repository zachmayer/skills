---
name: rhetoricize
description: extract rhetorical skeleton + fact ledger, then map the "spin-space" around an argument by applying controlled connotation and syntax transforms across multiple passes. ranks variants by rhetorical surprise and surfaces the hidden fulcrum words and grammatical moves that do the persuasive work. diagnostic, not generative.
---
## tl;dr

rhetoricize answers: "how much of this argument lands because of framing and word-choice, not facts?"

it (1) extracts thesis + evidence, (2) writes a fact ledger (invariants + non-claims), (3) perturbs connotation and agency grammar across several passes, then (4) reports the highest-surprise transformation and the single (or few) choices that pivot persuasion.

it's basically local robustness testing for rhetoric: "same facts, different drip."

---

## definition

a **rhetorical skeleton** is: epistemic posture (confident / cautious / conditional / mixed) + thesis (one-sentence core claim) + evidence (2-5 supporting claims).

a **fact ledger** is: atomic facts asserted + non-claims explicitly not asserted + drift budget (tolerance for meaning shift).

a phrase has **connotative load** if near-synonyms exist with similar denotation but different affect, agency, or moral valence.

a **fulcrum** is the single word/phrase or syntactic choice that, when flipped, most changes how the argument lands while staying ledger-consistent.

---

## the six dials

### dial 1: pass set
available passes:
- **a** same stance, opposite valence or axis framing
- **b1** inverted evaluation, same facts (strict)
- **b2** inverted evaluation + flagged implicatures (loose)
- **c** neutral register (de-spin baseline)
- **s** satire bound (optional bracket; explicitly non-epistemic)

default: [a, b1, c]. b2 and s are opt-in.

### dial 2: intensity
range: subtle (nearest defensible synonym) to maximal (furthest defensible inverse). subtle: visionary -> ambitious. maximal: visionary -> reckless.

### dial 3: drift budget
tolerance for meaning drift relative to the fact ledger. range: low -> high. default: low.

### dial 4: transform scope
range: lexical-only -> lexical+syntactic. lexical = synonym shifts, scalar softening/hardening. syntactic = agency transfer, responsibility assignment, modality shifts, uncertainty framing, nominalization.

### dial 5: opposition style
voice constraints for oppositional passes. range: steelman -> charitable-skeptic -> prosecutorial. default: charitable-skeptic.

### dial 6: output policy
- output: winner-only / full
- fulcrum_k: 1-3 (default 2)

**implicit parameter: context** -- domain, audience, stakes, norms are inferred, not dialed. rhetorical charge is context-relative.

---

## core operation

given input (text, argument, map, conversation):

1. **attribution discipline** -- distinguish user vs author(s) vs model. outputs are possible framings, not claims about intent.
2. **extract rhetorical skeleton** -- epistemic posture + thesis + 2-5 evidence claims. discard scaffolding unless load-bearing.
3. **build fact ledger** -- list atomic facts (f1, f2, ...), non-claims (n1, n2, ...), set drift budget.
4. **tag charged language** (vector, not scalar) -- for each charged phrase, tag axes: agency, competence, warmth/intent, purity/contamination, status, risk, novelty. do not pretend it's 1d "valence."
5. **run passes** -- a/b1/b2/c/s per dial 1 settings.
6. **score rhetorical surprise** -- per pass: affect_shift (0-5) x meaning_overlap (0-1) x fluency_register (0-1) = surprise.
7. **select winner + name gestalt shift** -- highest surprise among ledger-compliant passes. one-sentence gestalt shift. surface fulcrum_k highest-leverage choices.
8. **optional: satire bound** -- s+ booster caricature, s- hatchet-job. not included in surprise ranking by default.

---

## output schema (required)

- **original skeleton**: epistemic posture, thesis, evidence list
- **fact ledger**: facts (f1...), non-claims (n1...), drift budget
- **charged terms**: phrase, axes, role (thesis | evidence-#)
- **passes**: for each included pass -- thesis, evidence transforms, axis_move, drift checks
- **surprise ranking**: table of pass | affect_shift | overlap | fluency | surprise | notes
- **gestalt shift (winner)**: one sentence: original emotional center -> transformed emotional center
- **hidden fulcrum(s)**: up to fulcrum_k
- **null result**: if text is approximately neutral, state so and why

For worked examples and transform catalog, see [REFERENCE.md](REFERENCE.md).

---

## critical constraints
- no attribution leakage: outputs are model-generated framings, not author intent
- no fact smuggling: b1 must not add predicates; b2 must flag implicatures
- no forced inverses: if no clean inverse, say so; do axis-swap or neutralize
- register integrity: each pass keeps a consistent voice
- satire is labeled: satire is for bounding + fun, not for belief

---

## relationship to other moves

**upstream**: filterize (pre-select charged phrases), excavate (surface assumptions), deframe (map the frame before perturbing)

**downstream**: antithesize (use b1/b2 as seed), synthesize (merge spin-robust framings), handlize (extract executable residue)

**parallel**: rhyme (structure detection), deframe (logic constraints; rhetoricize is diction + grammar constraints)

---

## meta-note

most persuasion is just gradient descent on "what vibe makes this feel inevitable." rhetoricize is you peeking at the gradients.

satire exists bc sometimes the cleanest way to see the boundary is to tap it with a clown hammer.
