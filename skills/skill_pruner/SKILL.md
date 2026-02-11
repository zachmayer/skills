---
name: skill_pruner
description: >
  Review all installed skills for quality, redundancy, and overlap. Surfaces
  candidates for merging, trimming, or deletion. Use when the skill collection
  has grown and needs curation, after adding new skills, or periodically to
  maintain quality. Do NOT use for creating new skills (use skill_stealer).
---

Audit all installed skills and produce a quality report with actionable recommendations.

## Audit Process

### 1. Read all skills

Read every `SKILL.md` in the skills directory. For each, extract:
- Line count
- Frontmatter (name, description)
- Section structure
- Cross-skill references

### 2. Check each skill against quality criteria

For each skill, evaluate:

**Structure**:
- Has YAML frontmatter with `name` and `description`?
- Description uses WHEN/WHEN NOT pattern?
- Under 500 lines?
- Name matches directory name?

**Conciseness** — the key question: "Does Claude need this?"
- Flag lines that teach the model what it already knows (common algorithms, standard practices, basic syntax)
- Flag verbose reformulations of the same point
- Flag sections that explain concepts rather than override behavior
- The value of a skill line is: `(behavior change it causes) / (tokens it costs)`
- Flag skills >150 lines as compression candidates (see Skill Compression below)

**Behavioral overrides** — content that earns its place:
- Opinionated defaults the model wouldn't choose on its own
- Prohibitions ("never use X", "avoid Y")
- Specific templates and formats
- Non-obvious workflows and multi-step procedures
- Tool invocation patterns
- Key distinctions the model wouldn't invent (e.g., strict vs. loose inference passes)
- Scoring formulas and taxonomies

### 3. Compare skills pairwise for overlap

Check for:
- Two skills giving the same behavioral instruction
- Skills that would conflict if both loaded
- Skills where one is a strict subset of another
- Sections that belong in a different skill

### 4. Produce the report

```
## Skill Quality Report

### Per-Skill Findings
[For each skill with issues:]
- **skill_name** (N lines): [finding]. Recommendation: [action].

### Overlap Candidates
[Pairs of skills with significant overlap:]
- **skill_a** vs **skill_b**: [what overlaps]. Recommendation: [merge/deduplicate/clarify boundary].

### Summary Stats
- Total skills: N
- Total lines: N
- Skills with issues: N
- Recommended actions: N
```

## Skill Compression

When a skill is too long (>150 lines) or contains verbose upstream content, compress it while preserving value. The key insight: **procedure is signal; examples are noise**.

### What to preserve (high value per token)

- **Process steps** (numbered sequences that define what to DO)
- **Output schema/format** (structural requirements for the output)
- **Key distinctions** (e.g., b1=strict-facts-only vs b2=flagged-implicatures — these are the analytical innovations a model won't invent on its own)
- **Scoring formulas** (e.g., surprise = affect_shift × meaning_overlap × fluency)
- **Taxonomies/classification systems** (e.g., omission classes: vulnerability / upside / bedrock / blind spot / optionality)
- **Quality criteria** (1-2 lines each, not paragraphs)
- **Opinionated defaults and prohibitions** ("never add new predicates in b1", "allow null output")

### What to cut (low value per token)

- **Worked examples** — strong models generate their own; examples consume context better spent on the actual input
- **Anti-pattern catalogs** — a bullet list of "don't do X" is fine; 5-paragraph descriptions of each failure mode are not
- **Genre-specific pattern lists** — the model already knows genre conventions
- **Detailed dial/parameter tables** — keep the 2-3 most important dials; cut the rest
- **Integration notes** ("use with @rhyme before @metaphorize") — these are coordination hints, not behavioral overrides
- **"When to use / when not to use" sections** — the frontmatter description already covers this
- **Meta-commentary** ("this is prosocial disagreement", "the goal isn't to WIN") — doesn't change output quality
- **References and links** — nice for humans, invisible to models

### Compression process

1. **Identify the procedural skeleton**: Extract the numbered steps. These are the load-bearing structure.
2. **Extract the output schema**: What must the output contain? Keep this verbatim.
3. **Identify key distinctions**: What concepts does this skill introduce that the model wouldn't produce on its own? (e.g., "fact ledger with drift budget", "b1 strict vs b2 with flagged implicatures")
4. **Cut everything else**: Examples, anti-patterns, genre guides, integration notes, meta-commentary.
5. **Target ~20% of original length**: A 300-line skill should compress to ~60 lines. If it doesn't compress well, the procedure itself may be too complex.

### Why this works

Empirically tested (Feb 2026): GPT 5.2 with xhigh thinking was given the same analytical task under three conditions — full skill (~300 lines), compressed skill (~30 lines), and no skill. Evaluated by two independent LLM judges (GPT 5.2 + Opus 4.6):

- **Compressed matched or beat full-length** on 4 of 6 evaluations
- **Full-length ranked last** on 3 of 6 evaluations (verbose examples may consume context that could be used for deeper analysis)
- **No-skill FAILED** on procedural tasks (rhetorical analysis without the b1/b2 distinction blended facts with interpretation)

**Conclusion**: Procedural structure is the value. Prose documentation is filler. Strong models don't need examples — they need the procedure.

## Principles

- **Not aggressive**: Surface candidates, don't auto-delete. The human decides.
- **Precise wording matters**: Some phrasings elicit better LLM behavior than others. Don't flatten effective prompts just because they're "wordy."
- **Activation vs. education**: Listing mental models the LLM already knows can still add value by priming it to reach for them. Judge by whether the skill changes behavior, not just whether the content is "new."
- **External skill compilation**: When reviewing external skills alongside native ones, ask: can the core technique be captured in 3-5 lines within an existing skill, or does it need the full standalone version?
- **Procedure over prose**: The highest-value content in a skill is its procedural skeleton — the numbered steps, output schema, and key distinctions. Everything else (examples, anti-patterns, meta-commentary) should justify its token cost or be cut.
