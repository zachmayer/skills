# Rhetoricize

Extract rhetorical skeleton and fact ledger, then map the "spin-space" around an argument by applying controlled connotation and syntax transforms. Surfaces the hidden fulcrum words and grammatical moves that do the persuasive work. Diagnostic, not generative.

## Key Definitions

**Rhetorical skeleton:** epistemic posture (confident/cautious/conditional) + thesis (one-sentence core claim) + evidence (2-5 supporting claims).

**Fact ledger:** atomic facts (what is asserted) + non-claims (what is explicitly not asserted) + drift budget (tolerance for semantic drift: low/medium/high).

**Fulcrum:** the single word/phrase or syntactic choice that, when flipped, most changes how the argument lands while staying ledger-consistent.

## Passes

- **a** — same stance, opposite valence or axis framing
- **b1** — inverted evaluation, same facts (strict: no new predicates, ledger-only)
- **b2** — inverted evaluation + flagged implicatures (loose: explicitly mark what's not entailed)
- **c** — neutral register (de-spin baseline)
- **s** — satire bound (optional bracket; explicitly non-epistemic)

Default pass set: [a, b1, c]. b2 and s are opt-in.

**Critical distinction:** b1 must NEVER add predicates. b2 must explicitly flag every implicature as "plausible; not entailed."

## Transform Types

**Lexical:** synonym shifts along affect axes (euphemism ↔ dysphemism), scalar softening/hardening (some ↔ many).

**Syntactic (often the real fulcrums):** agency transfer (active ↔ passive), responsibility assignment, modality shifts (must/should/can), uncertainty framing (likely/possible), nominalization vs verbing.

**Affect axes for tagging charged language:** agency, competence, warmth/intent, purity/contamination, status, risk, novelty. Not a 1D valence slider.

## Surprise Scoring

For each pass: `surprise = affect_shift (0-5) × meaning_overlap (0-1) × fluency_register (0-1)`

Winner = highest surprise among ledger-compliant passes.

## Process

1. **Attribution discipline** — distinguish user vs author(s) vs model; outputs are possible framings, not claims about intent
2. **Extract rhetorical skeleton** — epistemic posture + thesis + 2-5 evidence claims
3. **Build fact ledger** — list atomic facts, non-claims, set drift budget
4. **Tag charged language** — for each charged phrase, tag axes (not 1D valence)
5. **Run passes** — a: flip connotation/axis; b1: invert using only ledger; b2: allow flagged implicatures; c: strip charge to neutral; s: satire bound (optional)
6. **Score surprise** — affect_shift × meaning_overlap × fluency for each pass
7. **Select winner + name gestalt shift** — one sentence: original emotional center → transformed emotional center; surface fulcrum_k (default 2) highest-leverage choices
8. **Null result allowed** — if text is approximately neutral, state "no rhetorical degrees of freedom detected"

## Output Schema

- Original skeleton (posture, thesis, evidence)
- Fact ledger (facts, non-claims, drift budget)
- Charged terms with vector tags and axes
- Each pass with transformed thesis/evidence, axis moves, and drift checks
- Surprise ranking table
- Gestalt shift (one sentence)
- Hidden fulcrum(s) (1-3)

## Critical Constraints

- No attribution leakage: outputs are model-generated framings, not author intent
- No fact smuggling: b1 adds no predicates; b2 flags all implicatures
- No forced inverses: if no clean inverse, do axis-swap or neutralize
- Register integrity: each pass keeps consistent voice
- Satire is labeled: for bounding, not for belief
