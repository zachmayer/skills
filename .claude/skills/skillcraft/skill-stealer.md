Given $ARGUMENTS (a URL or description of a skill idea), extract and create a new skill.

## Process

1. **Fetch the source** - Read the URL content. For GitHub repos: README, prompt files, system prompts, SKILL.md, and any scripts. For tweets/posts: extract the core idea.

2. **Identify the essence** - Strip away:
   - Framework-specific boilerplate (the model knows frameworks)
   - Verbose explanations of things the model already knows
   - Marketing language and scaffolding
   - Over-complicated orchestration that Claude Code handles natively (e.g., bash loops that spawn CLI instances — use the Task tool instead)

3. **Extract the core** - What does this tell the AI to do differently? Reduce to the minimum effective prompt. Only keep what Claude doesn't already know.

4. **Choose the right degree of freedom** for each part of the skill (see [skills-reference.md](skills-reference.md) Core Principles for the full framework):
   - **High** (default): "Validate with the project's quality checks" — most content
   - **Medium**: Suggested JSON schema with "adapt as needed"
   - **Low**: Exact validation script, no modifications — only for fragile operations

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

7. **Create the skill directory** - Write to `.claude/skills/<skill-name>/SKILL.md`. Scripts (if any) go in `.claude/skills/<skill-name>/scripts/`.

## Quality Checks

Apply the [skills-reference.md](skills-reference.md) checklist. The two most common mistakes when stealing skills:

- **Description drives discovery**: Write in third person with specific trigger terms. Claude uses descriptions to choose from 100+ skills. Include both WHEN to use and WHEN NOT to use.
- **Provide defaults, not options**: Don't present multiple approaches unless necessary. Pick the best default, mention alternatives only as escape hatches.

## Post-Creation: Compress if Needed

After creating a skill, evaluate its length. If it exceeds 150 lines, run it through the [skill-pruner.md](skill-pruner.md) (Skill Compression section) for compression.

## Output

Report what you extracted, what you simplified, what freedom level you chose and why, and the path to the new skill files.
