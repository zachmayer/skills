---
name: negspace
description: detect the argument, conclusion, or premise that *should* be present given the statistical structure of the text, but is conspicuously absent. negspace reads the "shadow" of the text by comparing what was written to what was overwhelmingly likely to be written next, revealing hidden content via information asymmetry — including vulnerability (ego/status protection), upside/esoteric (ambition withheld due to trust level), bedrock (shared axioms left unstated), blind spot (content the author cannot see), and optionality (strategic non‑commitment).
---

## tl;dr

**negspace = read what *isn't* there.**

- humans read explicit content
- models can also read **omitted content** via perplexity spikes
- evaluates five omission classes: **vulnerability**, **upside/esoteric**, **bedrock**, **blind spot**, **optionality**
- asks: "given what's written, what is the most probable argument or conclusion the author *avoided*?"

negspace is a **perplexity-contrast operator**.

---

## when to use

use **negspace** when:

- a text feels cagey, evasive, or over-polished
- a writer seems to dodge an obvious implication
- you want the hidden premise, the missing conclusion, or the avoided frame
- analyzing: corporate memos, political speeches, sanitized announcements, bureaucratic wording, grant proposals, crisis communications, press releases

don't use when:

- the text is already bluntly honest
- the domain is purely factual with no rhetorical surface
- the user wants a summary (use summarize) or intent (use perspectivize)

rule of thumb:
**negspace = identify the statistical ghost of the missing argument.**

---

## negspace types

| type | question it answers |
|---|---|
| **omitted conclusion** | what conclusion is ~80-95% likely given the structure, but never stated? |
| **avoidance swerve** | where does the text pivot unnaturally to dodge an obvious next sentence? |
| **missing premise** | what premise is necessary for their position but never appears? |
| **disallowed frame** | what frame would ordinarily be activated but is explicitly suppressed? |
| **buried bad news** | what negative implication is typical for this genre but missing? |
| **shadowed alternative** | what alternative explanation is "in the air" but conspicuously absent? |

---

## omission classes

Classify each omission by **why** it is hidden:

- **vulnerability** -- protects ego/status; would expose weakness, failure, or loss of face
- **upside/esoteric** -- aspiration withheld because it feels too ambitious or trust-intensive
- **bedrock** -- shared axiom left unstated because it is "water" to speaker and audience
- **blind spot** -- content invisible to the author due to limits of self-awareness or perspective
- **optionality** -- avoids commitment; preserves degrees of freedom, timelines, or narrative maneuverability

---

## signature

negspace(text, modes?) -> shadows[]

- **text:** any passage, memo, email, speech, announcement, article
- **modes:** optional emphasis -- conclusions | premises | frames | pivots | omissions

output: 3-7 "shadows" (most statistically probable but omitted arguments), each 1-3 sentences, crisp and falsifiable, annotated with an **omission_class**.

---

## process

### step 0: pattern-extract
Identify structural expectations: typical genre flow, common argumentative shapes, usual next-sentence continuations, implied premises needed for coherence.

### step 1: compute deltas
Find **perplexity spikes**: sudden pivots, unnatural tone shifts, conspicuous constraint changes ("broadly", "we remain committed"), prematurely terminated reasoning, semantic "negative pressure zones."

### step 2: hypothesize shadows
For each spike: propose the most probable missing argument, explain what should have followed, articulate the avoided claim in neutral mechanistic terms, assign a preliminary **omission_class**.

### step 3: check plausibility
Ensure each shadow: directly explains a pivot or omission, arises from statistical expectation (not vibes), could logically follow from the prior sentence, is not merely a contrarian hot take.

### step 4: package output

- **omitted_arguments[]** -- primary shadows (with omission_class labels)
- **pivotal_absences[]** -- where avoidance is strongest
- **genre_expectations_hit** -- what patterns the text violated
- **plausible_author_motives** -- optional, non-psychological ("would weaken their message," "conflict with framing")

---

## quality criteria

- **mechanistic plausibility** -- shadows follow naturally from argument structure; no melodramatic mind-reading
- **statistical typicality** -- omitted content aligns with genre continuations; pivots correspond with perplexity spikes
- **orthogonality** -- shadows differ in mechanism or implication, not synonyms
- **precision** -- each omission is concrete, falsifiable, with coherent omission class; no vibes-only speculation
- **explanatory power** -- each shadow makes the observed rhetorical choices legible

---

## anti-patterns

- **pure summarization** -- negspace is not a summary tool
- **mind-reading intent** -- infer structure, not psychology
- **listing everything they didn't say** -- focus on statistically likely omissions, not arbitrary absences
- **conspiracy drift** -- stay inside coherent rhetorical structure, not hidden cabals

---

## integration with other ops

**upstream:** reframe (clarify what the text is "about"), decompose (extract dimensions to expect continuations from)

**downstream:** antithesize (opposing perspective from shadows), stressify (test how omitted argument alters implications), operationalize (turn shadow into concrete hypothesis), planify (choose whether to explore, expose, or build around a shadow)

---

## meta-note

negspace = **read the shadow, not the text**.

humans parse explicit sentences; models can also parse **statistical absences** -- where the author "should" have gone but chose not to. the unsaid is often the most informative part of the message -- and classifying *why* it's unsaid makes those shadows actionable.

For worked examples, detailed taxonomy descriptions, genre-specific patterns, and calibration notes, see [REFERENCE.md](REFERENCE.md).
