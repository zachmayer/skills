---
name: skills_reference
description: >
  Comprehensive reference for authoring Agent Skills (SKILL.md files).
  Covers structure, frontmatter, naming, descriptions, progressive disclosure,
  patterns, anti-patterns, and evaluation. Use when creating new skills,
  reviewing skill quality, or needing best practices for SKILL.md authoring.
  Do NOT use for general Claude Code configuration (use config reference instead).
---

# Agent Skills Reference

Comprehensive reference for writing effective SKILL.md files following the [Agent Skills](https://agentskills.io) open standard. Source: [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Core Principles

### Concise is key

The context window is a public good. Your skill shares it with the system prompt, conversation history, other skills' metadata, and the actual request. Only add context Claude doesn't already have.

**Default assumption**: Claude is already very smart. Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

### Set appropriate degrees of freedom

Match specificity to task fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent decisions. Most skill content should be high freedom.
- **Medium freedom** (pseudocode/parameterized scripts): Preferred pattern exists, some variation OK.
- **Low freedom** (exact scripts, no params): Fragile operations, consistency critical, specific sequence required.

Think of Claude as a robot on a path: **narrow bridge with cliffs** (low freedom, one safe way forward) vs **open field** (high freedom, many paths lead to success).

### Test with target models

Skill effectiveness depends on the model. Haiku may need more guidance; Opus may need less. Test with all models you plan to use.

## Skill Structure

### Required File

Every skill needs `SKILL.md` with YAML frontmatter:

```yaml
---
name: your-skill-name
description: What this does and when to use it
---

# Instructions here
```

### Frontmatter Fields

**Standard fields** (Agent Skills standard):

| Field | Required | Constraints |
|:------|:---------|:------------|
| `name` | Yes | Max 64 chars, lowercase letters/numbers/hyphens only. No XML tags. No reserved words ("anthropic", "claude") |
| `description` | Yes | Max 1024 chars, non-empty, no XML tags. Include WHAT it does and WHEN to use it |

**Claude Code extensions**:

| Field | Default | Purpose |
|:------|:--------|:--------|
| `allowed-tools` | (none) | Tools Claude can use without permission when skill is active |
| `disable-model-invocation` | `false` | `true` = only user can invoke via `/name` |
| `user-invocable` | `true` | `false` = hidden from `/` menu, only Claude invokes |
| `context` | (inline) | `fork` = run in isolated subagent |
| `agent` | `general-purpose` | Subagent type when `context: fork` (`Explore`, `Plan`, etc.) |
| `model` | (inherited) | Override model for this skill |
| `argument-hint` | (none) | Shown during autocomplete, e.g. `[issue-number]` |
| `hooks` | (none) | Hooks scoped to skill lifecycle |

### Naming Conventions

Prefer **gerund form** (verb + -ing): `processing-pdfs`, `analyzing-spreadsheets`, `testing-code`.

Acceptable alternatives: noun phrases (`pdf-processing`), action-oriented (`process-pdfs`).

Avoid: vague names (`helper`, `utils`), overly generic (`documents`, `data`).

### Writing Descriptions

Descriptions enable skill discovery. Claude uses them to select the right skill from 100+ candidates.

Rules:
- **Third person only.** "Processes Excel files" not "I can help you" or "You can use this"
- **Include key terms** users would naturally say
- **Include WHEN/WHEN NOT** triggers for clear invocation boundaries

```yaml
# Good
description: >
  Extract text and tables from PDF files, fill forms, merge documents.
  Use when working with PDF files or when the user mentions PDFs, forms,
  or document extraction.

# Bad
description: Helps with documents
```

## Progressive Disclosure

Keep SKILL.md under 500 lines. Split into separate files when approaching this limit. Claude loads referenced files only when needed.

### Directory Structure

```
my-skill/
├── SKILL.md              # Main instructions (loaded when triggered)
├── reference.md          # Detailed docs (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    └── helper.py         # Utility script (executed, not loaded)
```

### Reference Rules

- **One level deep.** All reference files link directly from SKILL.md
- **No nesting.** Don't have `advanced.md` → `details.md` → actual content
- **TOC for long files.** Reference files over 100 lines should start with a table of contents

### Referencing Pattern

```markdown
## Advanced features
- Form filling: See [FORMS.md](FORMS.md) for complete guide
- API reference: See [REFERENCE.md](REFERENCE.md) for all methods
```

## Common Patterns

### Template Pattern

Provide output format templates. Match strictness to requirements:

```markdown
## Strict (API responses, data formats)
ALWAYS use this exact template structure:
[template]

## Flexible (reports, analysis)
Here is a sensible default format, but use your best judgment:
[template]
```

### Examples Pattern

Provide input/output pairs for output-quality-sensitive skills:

````markdown
**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication
```
````

### Workflow Pattern

Break complex operations into sequential steps with checklists:

```markdown
## Workflow
Copy this checklist and track progress:
- [ ] Step 1: Analyze inputs
- [ ] Step 2: Create plan
- [ ] Step 3: Validate plan
- [ ] Step 4: Execute
- [ ] Step 5: Verify output
```

### Conditional Workflow Pattern

Guide through decision points:

```markdown
**Creating new content?** → Follow "Creation workflow"
**Editing existing?** → Follow "Editing workflow"
```

### Feedback Loop Pattern

Run validator → fix errors → repeat. Greatly improves output quality:

```markdown
1. Make edits
2. Validate: `python scripts/validate.py`
3. If validation fails → fix → validate again
4. Only proceed when validation passes
```

For detailed patterns for skills with executable code, see [code-skills.md](code-skills.md).

## Claude Code Specifics

### Skill Locations

| Location | Path | Scope |
|:---------|:-----|:------|
| Enterprise | Managed settings | All org users |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin enabled |

Priority: enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace.

### String Substitutions

| Variable | Description |
|:---------|:------------|
| `$ARGUMENTS` | All arguments passed when invoking |
| `$ARGUMENTS[N]` or `$N` | Specific argument by 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |

### Dynamic Context Injection

The `` !`command` `` syntax runs shell commands before skill content is sent to Claude:

```yaml
## Context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`
```

### Invocation Control

| Frontmatter | User invokes | Claude invokes |
|:------------|:-------------|:---------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

## Anti-Patterns

- **Too verbose**: Don't explain what Claude already knows (what PDFs are, how libraries work)
- **Too many options**: Provide a default, not "you can use X, Y, or Z..."
- **Time-sensitive info**: Don't write "before August 2025, use old API." Use an "old patterns" section
- **Inconsistent terminology**: Pick one term and use it throughout
- **Windows paths**: Always use forward slashes, even on Windows
- **Deep nesting**: Don't chain `advanced.md` → `details.md` → actual content
- **Assuming tools installed**: Explicitly list required packages
- **Magic numbers**: Document why constants have specific values

## Evaluation

Build evaluations BEFORE writing docs. Evaluation-driven development:

1. Run Claude on tasks WITHOUT the skill. Document failures
2. Build 3 scenarios testing those gaps
3. Measure baseline performance
4. Write minimal instructions to address gaps
5. Iterate: run evals, compare baseline, refine

For detailed evaluation and iterative development guidance, see [evaluation.md](evaluation.md).

## Checklist

### Core quality
- [ ] Description is specific with key terms and WHEN/WHEN NOT
- [ ] SKILL.md body under 500 lines
- [ ] Details in separate files if needed
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Concrete examples
- [ ] File references one level deep
- [ ] Progressive disclosure used appropriately

### Code and scripts
- [ ] Scripts validate inputs and fail with clear messages (don't silently swallow errors)
- [ ] Let errors bubble up — the agent reasons about them better than pre-written handlers
- [ ] No magic numbers
- [ ] Required packages listed
- [ ] Validation/verification for critical operations
- [ ] Feedback loops for quality-critical tasks

### Testing
- [ ] At least 3 evaluations created
- [ ] Tested with target models
- [ ] Tested with real usage scenarios
