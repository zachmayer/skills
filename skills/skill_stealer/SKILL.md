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

4. **Choose the right degree of freedom** for each part of the skill:

   **High freedom** (text instructions) — use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach. Most skill content should be high freedom.
   ```
   Example: "Validate with the project's quality checks. Fix failures before proceeding."
   ```

   **Medium freedom** (pseudocode, templates, suggested formats) — use when a preferred pattern exists but some variation is acceptable.
   ```
   Example: A suggested JSON schema with "adapt as needed for your project"
   ```

   **Low freedom** (exact scripts, specific commands) — use ONLY when operations are fragile, error-prone, or consistency is critical. Rewrite scripts to Python with Click CLIs run via `uv run`.
   ```
   Example: A validation script that must run exactly as written to avoid data corruption
   ```

   **The test**: imagine Claude as a robot on a path. Is this a narrow bridge with cliffs (low freedom needed) or an open field (high freedom, many paths lead to success)?

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

Apply the `skills_reference` skill for the full checklist. Key points:

**Conciseness**: Challenge every line: "Does Claude need this?" The context window is shared.

**Degrees of freedom**: Default to high freedom. Low freedom only for fragile operations. Over-specifying heuristic tasks wastes tokens and constrains Claude from finding better approaches.

**Progressive disclosure**: SKILL.md under 500 lines. Split reference material into separate files Claude reads on-demand. References one level deep only.

**Description drives discovery**: Write in third person with specific trigger terms. Claude uses descriptions to choose from 100+ skills. Include both WHEN to use and WHEN NOT to use.

## Post-Creation: Compress if Needed

After creating a skill, evaluate its length. If it exceeds 150 lines, run it through the compression process in the `skill_pruner` skill (Skill Compression section). The key: preserve the procedural skeleton, output schema, key distinctions, and taxonomies. Cut examples, anti-pattern catalogs, genre-specific patterns, meta-commentary, and references. Target ~20% of original length.

## Output

Report what you extracted, what you simplified, what freedom level you chose and why, and the path to the new skill files.
