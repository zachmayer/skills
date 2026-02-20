---
name: skill_stealer
description: >
  Extract a reusable agent skill from a URL (GitHub repo, blog post, tweet,
  or any source describing an AI workflow or prompt). Distills the core idea
  into a clean SKILL.md following the Agent Skills standard. Can also steal
  code — rewriting scripts to Python with Click CLIs run via uv. Use when the
  user shares a link to a repo, skill, prompt, or workflow and you want to
  capture its essence as a reusable skill. Do NOT use for general web browsing.
---

Given $ARGUMENTS (a URL or description of a skill idea), extract and create a new skill.

## Process

1. **Fetch the source** - Read the URL content. For GitHub repos: README, prompt files, system prompts, SKILL.md, and any scripts. For tweets/posts: extract the core idea.

2. **Identify the essence** - Strip away:
   - Framework-specific boilerplate (the model knows frameworks)
   - Verbose explanations of things the model already knows
   - Marketing language and scaffolding
   - Over-complicated orchestration that Claude Code handles natively (e.g., bash loops that spawn CLI instances — use the Task tool instead)

3. **Extract the core** - What does this tell the AI to do differently? Reduce to the minimum effective prompt. Only keep what Claude doesn't already know.

4. **Choose the right degree of freedom** for each part of the skill (see `skills_reference` Core Principles for the full framework). Default to high freedom. Drop to medium/low only when the operation is fragile or a specific sequence is required.

5. **Steal the code** (only when low freedom is justified) - If the source has scripts for fragile/mechanical operations:
   - Rewrite to Python using Click for CLIs, run via `uv run python scripts/<name>.py`
   - Validate inputs up front, let errors bubble up with clear messages (don't silently swallow)
   - No magic constants — justify values
   - If Claude can do it natively (manage JSON, use git, call APIs), don't write a script for it

6. **Format as SKILL.md** with YAML frontmatter:

```yaml
---
name: extracted-skill-name
description: >
  WHEN to use: <specific triggers>.
  WHEN NOT to use: <boundaries>.
---
```

7. **Create the skill directory** - Write to `skills/<skill-name>/SKILL.md`. Scripts (if any) go in `skills/<skill-name>/scripts/`.

## Quality Checks

Apply the `skills_reference` checklist. The two most common mistakes when stealing skills:

- **Description drives discovery**: Write in third person with specific trigger terms. Claude uses descriptions to choose from 100+ skills. Include both WHEN to use and WHEN NOT to use.
- **Provide defaults, not options**: Don't present multiple approaches unless necessary. Pick the best default, mention alternatives only as escape hatches.

## Post-Creation: Compress if Needed

After creating a skill, evaluate its length. If it exceeds 150 lines, run it through the compression process in the `skill_pruner` skill (Skill Compression section). The key: preserve the procedural skeleton, output schema, key distinctions, and taxonomies. Cut examples, anti-pattern catalogs, genre-specific patterns, meta-commentary, and references. Target ~20% of original length.

## Output

Report what you extracted, what you simplified, what freedom level you chose and why, and the path to the new skill files.
