# Troubleshooting Skills

Common problems and solutions when building and deploying skills.

## Contents
- Skill won't upload
- Skill doesn't trigger
- Skill triggers too often
- Instructions not followed
- MCP connection issues
- Large context issues

## Skill Won't Upload

### Error: "Could not find SKILL.md in uploaded folder"

**Cause**: File not named exactly `SKILL.md` (case-sensitive).

**Fix**:
- Rename to `SKILL.md` (not `skill.md`, `SKILL.MD`, etc.)
- Verify with: `ls -la` should show `SKILL.md`

### Error: "Invalid frontmatter"

**Cause**: YAML formatting issue.

Common mistakes:
```yaml
# Wrong - missing delimiters
name: my-skill
description: Does things

# Wrong - unclosed quotes
---
name: my-skill
description: "Does things
---

# Correct
---
name: my-skill
description: Does things
---
```

### Error: "Invalid skill name"

**Cause**: Name has spaces, capitals, or underscores.

```yaml
# Wrong
name: My Cool Skill

# Wrong
name: notion_project_setup

# Wrong
name: NotionProjectSetup

# Correct
name: my-cool-skill
```

Rules: kebab-case only, no spaces, no capitals, no underscores.

## Skill Doesn't Trigger

**Symptom**: Skill never loads automatically.

**Fix**: Revise your description field.

**Quick checklist**:
- Is it too generic? ("Helps with projects" won't work)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types if applicable?
- Is it too technical with no user-facing language?

**Debugging approach**: Ask Claude "When would you use the [skill name] skill?" Claude will quote the description back. Whatever's missing in that answer is what you need to fix.

**Key insight**: Skills undertrigger by default. Claude will skip your skill on simple tasks — it thinks "I got this." Your skill only fires when the task is hard enough that Claude actually needs help.

**Solution**: Make descriptions "pushy" with explicit trigger phrases:
```yaml
# Before - undertriggers
description: Manages Linear project workflows.

# After - includes trigger phrases
description: >
  Manages Linear project workflows including sprint planning, task creation,
  and status tracking. Use when user mentions "sprint", "Linear tasks",
  "project planning", or asks to "create tickets".
```

## Skill Triggers Too Often

**Symptom**: Skill loads for irrelevant queries.

**Solutions**:

1. **Add negative triggers**:
```yaml
description: >
  Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

2. **Be more specific**:
```yaml
# Too broad
description: Processes documents

# More specific
description: Processes PDF legal documents for contract review
```

3. **Clarify scope**:
```yaml
description: >
  PayFlow payment processing for e-commerce. Use specifically for
  online payment workflows, not for general financial queries.
```

## Instructions Not Followed

**Symptom**: Skill loads but Claude doesn't follow instructions.

**Common causes and fixes**:

### 1. Instructions too verbose

Claude may skim long instruction blocks. Fix:
- Keep instructions concise
- Use bullet points and numbered lists
- Move detailed reference to separate files

### 2. Instructions buried

Critical rules lost in the middle of a wall of text. Fix:
- Put critical instructions at the top
- Use `## Important` or `## Critical` headers
- Repeat key points if needed

### 3. Ambiguous language

```markdown
# Bad
Make sure to validate things properly

# Good
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

**Advanced technique**: For critical validations, bundle a script that performs the checks programmatically rather than relying on language instructions. Code is deterministic; language interpretation isn't. See [code-skills.md](code-skills.md).

### 4. Model "laziness"

Add explicit encouragement:
```markdown
## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```

Note: Adding this to user prompts is more effective than in SKILL.md. Same words, different location, different results. Placement matters more than phrasing.

## MCP Connection Issues

**Symptom**: Skill loads but MCP tool calls fail.

**Checklist**:

1. **Verify MCP server is connected**
   - Claude.ai: Settings > Extensions > [Your Service]
   - Should show "Connected" status

2. **Check authentication**
   - API keys valid and not expired
   - Proper permissions/scopes granted
   - OAuth tokens refreshed

3. **Test MCP independently**
   - Ask Claude to call MCP directly (without skill)
   - "Use [Service] MCP to fetch my projects"
   - If this fails, the issue is MCP not skill

4. **Verify tool names**
   - Skill references correct MCP tool names
   - Use fully qualified names: `ServerName:tool_name`
   - Tool names are case-sensitive
   - Check MCP server documentation

## Large Context Issues

**Symptom**: Skill seems slow or responses degraded.

**Causes**:
- Skill content too large
- Too many skills enabled simultaneously
- All content loaded instead of progressive disclosure

**Solutions**:

1. **Optimize SKILL.md size**
   - Move detailed docs to `references/`
   - Link to references instead of inline
   - Keep SKILL.md under 5,000 words

2. **Reduce enabled skills**
   - Evaluate if you have more than 20-50 skills enabled simultaneously
   - Recommend selective enablement
   - Consider skill "packs" for related capabilities
