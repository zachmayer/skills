---
name: skill_stealer
description: >
  Extract a reusable agent skill from a URL (GitHub repo, blog post, tweet,
  or any source describing an AI workflow or prompt). Distills the core idea
  into a clean SKILL.md following the Agent Skills standard. Use when the user
  shares a link to a repo, skill, prompt, or workflow and you want to capture
  its essence as a reusable skill. Also use when you encounter a useful
  pattern that should be preserved. Do NOT use for general web browsing.
---

Given $ARGUMENTS (a URL or description of a skill idea), extract and create a new skill:

## Process

1. **Fetch the source** - Read the URL content. If it's a GitHub repo, focus on README, prompt files, system prompts, and any SKILL.md or similar files. If it's a tweet/post, extract the core idea.

2. **Identify the essence** - Strip away:
   - Over-complicated scaffolding
   - Framework-specific boilerplate
   - Verbose explanations that don't add to the instructions
   - Marketing language

3. **Extract the core** - What is the actual instruction set? What does this tell the AI to do differently? Reduce it to the minimum effective prompt.

4. **Format as SKILL.md** - Create a properly formatted skill:

```yaml
---
name: extracted-skill-name
description: >
  WHEN to use: <specific triggers>.
  WHEN NOT to use: <boundaries>.
---

[Clear, concise instructions extracted from the source]
```

5. **Create the skill directory** - Write the SKILL.md to `skills/<skill-name>/SKILL.md` in this repository. If the skill needs scripts, create them in `skills/<skill-name>/scripts/`.

## Quality Checks (from [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))

- **Concise is key** - The context window is a public good. Only add context Claude doesn't already have. Challenge each line: "Does Claude really need this?" Default assumption: Claude is already very smart.
- **Set degrees of freedom** - Match specificity to task fragility. High freedom (text guidance) for heuristic tasks, low freedom (exact scripts) for fragile/critical operations.
- **Progressive disclosure** - SKILL.md is the overview; split reference material into separate files Claude reads on-demand. Keep SKILL.md under 500 lines. References one level deep only.
- **Description drives discovery** - Write in third person. Be specific with trigger terms. Claude uses the description to choose from 100+ skills.
- Description uses WHEN/WHEN NOT pattern
- Instructions are actionable, not philosophical
- No unnecessary complexity
- Under 200 lines for the SKILL.md (split into reference files if needed)
- Name is kebab-case, memorable, and descriptive

## Output

Report what you extracted, what you simplified, and the path to the new skill file.
