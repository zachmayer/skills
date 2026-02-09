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
   - Handle errors explicitly (don't punt to Claude)
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

Apply the [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) throughout:

**Conciseness**: The context window is a public good. Claude is already very smart — only add what it doesn't know. Challenge every line: "Does Claude need this?"

**Degrees of freedom**: Default to high freedom. Only drop to medium/low when the task is fragile. Over-specifying heuristic tasks wastes tokens and constrains Claude from finding better approaches.

**Progressive disclosure**: SKILL.md is the overview (under 500 lines). Split reference material into separate files Claude reads on-demand. References one level deep only.

**Description drives discovery**: Write in third person with specific trigger terms. Claude uses descriptions to choose from 100+ skills. Include both what it does and when to use it.

**Workflows for complex tasks**: Break multi-step operations into clear sequential steps. Include feedback loops (validate → fix → repeat) for quality-critical operations.

**Provide defaults, not options**: Don't present multiple approaches unless necessary. Pick the best default, mention alternatives only as escape hatches.

**Checklist**:
- Description uses WHEN/WHEN NOT pattern
- Instructions are actionable, not philosophical
- Under 500 lines for SKILL.md (split into reference files if needed)
- Name is kebab-case, memorable, and descriptive
- No time-sensitive information

## Output

Report what you extracted, what you simplified, what freedom level you chose and why, and the path to the new skill files.
