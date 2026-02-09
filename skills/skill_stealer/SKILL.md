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

3. **Extract the core** - What is the actual instruction set? What does this tell the AI to do differently? Reduce to the minimum effective prompt. Only keep what Claude doesn't already know.

4. **Steal the code** - If the source has scripts, CLIs, or utility code:
   - Rewrite to Python using Click for CLIs
   - Run via `uv run python scripts/<name>.py`
   - Keep scripts focused: one script per concern
   - Handle errors explicitly (don't punt to Claude)
   - No magic constants — justify and document values
   - Prefer deterministic scripts for mechanical operations (state management, file I/O, validation) over asking Claude to generate equivalent code each time

5. **Format as SKILL.md** - Create a properly formatted skill:

```yaml
---
name: extracted-skill-name
description: >
  WHEN to use: <specific triggers>.
  WHEN NOT to use: <boundaries>.
---

[Clear, concise instructions extracted from the source]
```

6. **Create the skill directory** - Write to `skills/<skill-name>/SKILL.md`. Scripts go in `skills/<skill-name>/scripts/`.

## Quality Checks

Apply the [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) rigorously:

- **Concise is key** - The context window is a public good. Only add context Claude doesn't already have. Challenge each line: "Does Claude really need this?" Default assumption: Claude is already very smart.
- **Set degrees of freedom** - Match specificity to task fragility. High freedom (text guidance) for heuristic tasks, low freedom (exact scripts) for fragile/critical operations.
- **Progressive disclosure** - SKILL.md is the overview; split reference material into separate files Claude reads on-demand. Keep SKILL.md under 500 lines. References one level deep only.
- **Description drives discovery** - Write in third person. Be specific with trigger terms. Claude uses the description to choose from 100+ skills.
- **Test with real usage** - After creating the skill, try using it. Does it trigger correctly? Are instructions clear? What's missing?
- Description uses WHEN/WHEN NOT pattern
- Instructions are actionable, not philosophical
- Under 200 lines for SKILL.md (split into reference files if needed)
- Name is kebab-case, memorable, and descriptive

## Output

Report what you extracted, what you simplified, what code you rewrote, and the path to the new skill files.
