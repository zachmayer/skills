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

**Behavioral overrides** — content that earns its place:
- Opinionated defaults the model wouldn't choose on its own
- Prohibitions ("never use X", "avoid Y")
- Specific templates and formats
- Non-obvious workflows
- Tool invocation patterns

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

## Principles

- **Not aggressive**: Surface candidates, don't auto-delete. The human decides.
- **Precise wording matters**: Some phrasings elicit better LLM behavior than others. Don't flatten effective prompts just because they're "wordy."
- **Activation vs. education**: Listing mental models the LLM already knows can still add value by priming it to reach for them. Judge by whether the skill changes behavior, not just whether the content is "new."
- **External skill compilation**: When reviewing external skills alongside native ones, ask: can the core technique be captured in 3-5 lines within an existing skill, or does it need the full standalone version?
