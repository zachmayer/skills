Given $ARGUMENTS (a URL or description of a skill idea), extract and create a new skill.

## Process

1. **Fetch the source** - Read the URL content. For GitHub repos: README, prompt files, system prompts, SKILL.md, and any scripts. For tweets/posts: extract the core idea.

2. **Identify the essence** - Strip away:
   - Framework-specific boilerplate (the model knows frameworks)
   - Verbose explanations of things the model already knows
   - Marketing language and scaffolding
   - Over-complicated orchestration that Claude Code handles natively (e.g., bash loops that spawn CLI instances — use the Task tool instead)

3. **Extract the core** - Before cutting anything, enumerate the source's major ideas, procedures, and distinctions. Then for each, decide keep or cut — and justify cuts. The goal is to capture all key ideas thoroughly, even if you convert code to prose or simplify orchestration. Only remove what Claude genuinely already knows. Err on the side of keeping too much; the pruner can compress later.

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

8. **Evaluate the stolen skill** — Before declaring done, validate completeness and quality:

   **a. Trigger testing** — Draft 5+ queries that SHOULD trigger the skill and 5+ that should NOT. Review the `description` field against these. Fix undertriggering (missing keywords) or overtriggering (scope too broad).

   **b. Functional testing** — Draft 3+ realistic test scenarios with expected behaviors. Mentally walk through the skill: would Claude produce the right output for each scenario? Fix gaps.

   **c. Completeness audit** — Spawn an Explore sub-agent to compare the stolen skill against the original source. The agent should flag any major ideas, procedures, or distinctions from the source that were lost or diluted. Fix genuine gaps (not verbose fluff).

   If the audit surfaces missing ideas, add them and re-check. Only proceed to compression after evaluation passes.

## Post-Creation: Compress if Needed

After evaluation passes, if the skill exceeds 150 lines, run it through the [skill-pruner.md](skill-pruner.md) (Skill Compression section) for compression.

## Output

Report what you extracted, what you simplified, what freedom level you chose and why, evaluation results (trigger coverage, functional scenarios, completeness audit findings), and the path to the new skill files.
