# Negspace

Detect the argument, conclusion, or premise that *should* be present given the statistical structure of the text, but is conspicuously absent. Reads the "shadow" of the text — what was overwhelmingly likely to be written next but wasn't.

## Omission Classes

Classify each absence by *why* it is hidden:

- **Vulnerability** — protects ego/status; would expose weakness, failure, or loss of face
- **Upside/Esoteric** — aspiration withheld because it feels too ambitious or trust-intensive
- **Bedrock** — shared axiom left unstated because it's "water" to speaker and audience
- **Blind spot** — content invisible to author due to limits of self-awareness or perspective
- **Optionality** — avoids commitment; preserves degrees of freedom or narrative maneuverability

## Negspace Types

- **Omitted conclusion** — ~80-95% likely given argument structure, but never stated
- **Avoidance swerve** — unnatural rhetorical pivot to dodge obvious next sentence
- **Missing premise** — necessary for stated position to make sense but never appears
- **Disallowed frame** — would ordinarily be activated here but explicitly suppressed
- **Buried bad news** — negative implication typical for genre but missing from this instance
- **Shadowed alternative** — alternative explanation "in the air" but conspicuously absent

## Process

### Step 0: Pattern-extract
Identify structural expectations: typical flow for this genre, common argumentative shapes, usual next-sentence continuations, implied premises needed for coherence.

### Step 1: Compute deltas
Find perplexity spikes: sudden pivots, unnatural tone shifts, conspicuous constraint changes ("broadly", "we remain committed"), prematurely terminated reasoning, semantic negative-pressure zones.

### Step 2: Hypothesize shadows
For each spike: propose the most probable missing argument, explain what *should* have followed, articulate the avoided claim in neutral mechanistic terms, assign preliminary omission class.

### Step 3: Check plausibility
Each shadow must: directly explain a pivot or omission, arise from statistical expectation not vibes, logically follow from prior sentence, not be merely a contrarian hot take.

### Step 4: Package output
- **omitted_arguments[]** — primary shadows with omission_class labels
- **pivotal_absences[]** — where avoidance is strongest
- **genre_expectations_hit** — what patterns the text violated
- **plausible_author_motives** — non-psychological ("would weaken their message", "conflicts with framing")

## Quality Criteria

- Shadows follow naturally from argument structure (no melodramatic mind-reading)
- Omitted content aligns with genre continuations
- Shadows differ in mechanism or implication, not synonyms
- Each omission is concrete and falsifiable
- Omission class is identifiable and coherent
