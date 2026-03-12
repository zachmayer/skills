---
name: skills-reference
description: >
  Comprehensive reference for authoring Agent Skills (SKILL.md files).
  Covers structure, frontmatter, naming, descriptions, progressive disclosure,
  patterns, anti-patterns, and evaluation. Use when creating new skills,
  reviewing skill quality, or needing best practices for SKILL.md authoring.
  Do NOT use for general Claude Code configuration (use config reference instead).
---

# Agent Skills Reference

Comprehensive reference for writing effective SKILL.md files following the [Agent Skills](https://agentskills.io) open standard.

**Sources**: [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (web docs) and [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (PDF guide). Fetch the latest versions when creating or reviewing skills.

### Reference files

This skill uses progressive disclosure. Detailed guidance lives in reference files:

- [code-skills.md](code-skills.md) — scripts, dependencies, runtime environments
- [patterns.md](patterns.md) — advanced multi-step workflow patterns
- [mcp-integration.md](mcp-integration.md) — Skills + MCP design and troubleshooting
- [evaluation.md](evaluation.md) — eval-driven development, iterative improvement
- [troubleshooting.md](troubleshooting.md) — debugging trigger/load/execution issues
- [distribution.md](distribution.md) — packaging, sharing, API deployment
- [resources.md](resources.md) — official docs, blog posts, example repos

## Core Principles

### Concise is key

The context window is a public good. At startup, only name and description from all skills are loaded. Claude reads SKILL.md only when relevant — but once loaded, every token competes with the system prompt, conversation history, other active skills, and the actual request. Only add context Claude doesn't already have.

**Default assumption**: Claude is already very smart. Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good** (~50 tokens):
````markdown
## Extract PDF text
Use pdfplumber for text extraction:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Bad** (~150 tokens): "PDF (Portable Document Format) files are a common file format that contains text, images, and other content. To extract text from a PDF, you'll need to use a library. There are many libraries available..."

The concise version assumes Claude knows what PDFs are and how libraries work.

### Set appropriate degrees of freedom

Match specificity to task fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent decisions. Most skill content should be high freedom.
- **Medium freedom** (pseudocode/parameterized scripts): Preferred pattern exists, some variation OK.
- **Low freedom** (exact scripts, no params): Fragile operations, consistency critical, specific sequence required.

Think of Claude as a robot on a path: **narrow bridge with cliffs** (low freedom, one safe way forward) vs **open field** (high freedom, many paths lead to success).

### Test with target models

Skill effectiveness depends on the model. Test with all models you plan to use:

- **Haiku** (fast, economical): Does the skill provide enough guidance?
- **Sonnet** (balanced): Is the skill clear and efficient?
- **Opus** (powerful reasoning): Does the skill avoid over-explaining?

What works for Opus may need more detail for Haiku.

### Composability

Claude loads multiple skills simultaneously. Your skill should work well alongside others — don't assume it's the only capability available. Avoid generic names or overly broad triggers that would conflict with other skills.

### Portability

Skills use the same packaging format across Claude.ai, Claude Code, and API — portable by default, subject to environment and tool availability. Runtime behavior depends on available tools, MCP servers, file system access, code execution support, and permissions. Note platform-specific requirements in the `compatibility` field.

### Skills undertrigger by default

Claude will skip your skill on simple tasks — it thinks "I got this." Your skill only fires when the task is hard enough that Claude needs help. `Read this file` will never trigger a skill no matter what you put in the description. To compensate, make descriptions "pushy": instead of "Helps deploy to cloud" write "Use whenever user mentions deploy, hosting, servers, scaling — even if they don't say cloud."

**Debug triggering**: Ask Claude "When would you use the [skill name] skill?" It will quote the description back. Whatever's missing in that answer is what you need to fix.

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

**Standard optional fields** (Agent Skills standard):

| Field | Purpose |
|:------|:--------|
| `license` | Open source license (MIT, Apache-2.0, etc.) |
| `compatibility` | Environment requirements (1-500 chars). E.g. intended product, required system packages, network access needs |
| `metadata` | Custom key-value pairs. Suggested: `author`, `version`, `mcp-server` |

**Security restrictions**: XML angle brackets (`<` `>`) are forbidden in frontmatter — it goes directly into Claude's system prompt. Code execution in YAML is blocked (safe parsing). Skills named with "claude" or "anthropic" prefix are reserved.

**No README.md inside skill folders.** All documentation goes in SKILL.md or reference files. When distributing via GitHub, use a repo-level README for human visitors.

### Naming Conventions

Prefer **gerund form** (verb + -ing): `processing-pdfs`, `analyzing-spreadsheets`, `testing-code`.

Acceptable alternatives: noun phrases (`pdf-processing`), action-oriented (`process-pdfs`).

Avoid: vague names (`helper`, `utils`), overly generic (`documents`, `data`).

### Writing Descriptions

The description is the **single most important field** in your skill. Each skill has exactly one description, and Claude uses it to choose the right skill from potentially 100+ available skills. Your description must provide enough detail for Claude to know **when to select** this skill, while the rest of SKILL.md provides the implementation details.

> "This metadata...provides just enough information for Claude to know when each skill should be used without loading all of it into context." — [Anthropic Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**Description formula**: `[What it does] + [When to use it] + [Key capabilities]`

**Rules**:

1. **Third person only.** The description is injected into the system prompt. Inconsistent point-of-view causes discovery problems.
   - Good: "Processes Excel files and generates reports"
   - Bad: "I can help you process Excel files"
   - Bad: "You can use this to process Excel files"

2. **Include key terms** users would naturally say — specific tasks, file types, domain terms, tool names.

3. **Include WHEN/WHEN NOT** triggers for clear invocation boundaries. Negative triggers (`Do NOT use for...`) prevent over-triggering.

4. **Be pushy.** Skills undertrigger by default (see above). Include explicit trigger phrases users would actually say. Instead of "Helps deploy to cloud" write "Use whenever user mentions deploy, hosting, servers, scaling — even if they don't say cloud."

5. **Be specific, not vague.** Include both what the skill does and specific triggers/contexts for when to use it.

6. **Mention file types** if your skill works with specific formats (.fig, .pdf, .xlsx, .csv, etc.).

**Good descriptions**:

```yaml
# Specific, includes trigger phrases and file types
description: >
  Analyzes Figma design files and generates developer handoff documentation.
  Use when user uploads .fig files, asks for "design specs", "component
  documentation", or "design-to-code handoff".

# Clear value proposition with WHEN NOT
description: >
  Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).

# Includes trigger phrases users would say (from PDF guide)
description: >
  Manages Linear project workflows including sprint planning, task creation,
  and status tracking. Use when user mentions "sprint", "Linear tasks",
  "project planning", or asks to "create tickets".

# End-to-end workflow with multiple trigger phrases
description: >
  End-to-end customer onboarding workflow for PayFlow. Handles account
  creation, payment setup, and subscription management. Use when user says
  "onboard new customer", "set up subscription", or "create PayFlow account".

# Extract and process with clear scope
description: >
  Extract text and tables from PDF files, fill forms, merge documents.
  Use when working with PDF files or when the user mentions PDFs, forms,
  or document extraction.
```

**Bad descriptions**:

```yaml
# Too vague — won't trigger on anything specific
description: Helps with documents

# Missing triggers — no "when to use" clause
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.

# Too generic — will either never trigger or trigger on everything
description: Processes data
```

**Debugging description quality**: Ask Claude "When would you use the [skill name] skill?" It will quote the description back. Whatever's missing in that answer is what you need to fix in the description.

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

### Domain-Specific Organization

For skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    └── product.md (API usage, features)
```

When a user asks about revenue, Claude reads only `reference/finance.md`. Other files stay on disk, consuming zero context.

### Conditional Details

Show basic content inline, link to advanced content:

```markdown
## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

Claude reads REDLINING.md only when the user needs that feature.

## Planning Your Skill

### Start with use cases

Before writing any code, identify 2-3 concrete use cases your skill should enable:

```
Use Case: Project Sprint Planning
Trigger: User says "help me plan this sprint" or "create sprint tasks"
Steps:
1. Fetch current project status from Linear (via MCP)
2. Analyze team capacity
3. Suggest task prioritization
4. Create tasks in Linear with proper labels and estimates
Result: Fully planned sprint with tasks created
```

Ask yourself: What does a user want to accomplish? What multi-step workflows does this require? Which tools are needed (built-in or MCP)? What domain knowledge or best practices should be embedded?

### Common use case categories

1. **Document & Asset Creation**: Consistent, high-quality output (documents, designs, code). Key techniques: embedded style guides, template structures, quality checklists. *Real examples*: [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design), [docx](https://github.com/anthropics/skills/tree/main/skills/docx), [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx), [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx)
2. **Workflow Automation**: Multi-step processes benefiting from consistent methodology. Key techniques: step-by-step workflows with validation gates, templates, iterative refinement loops. *Real example*: [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
3. **MCP Enhancement**: Workflow guidance on top of MCP tool access. Key techniques: coordinating multiple MCP calls, embedding domain expertise, providing context users would otherwise need to specify. *Real example*: [sentry-code-review](https://github.com/getsentry/sentry-for-claude/tree/main/skills)

For detailed MCP integration patterns, see [mcp-integration.md](mcp-integration.md).

### Problem-first vs tool-first

Think of it like a hardware store. You might walk in with a problem — "I need to fix a kitchen cabinet" — or with a tool — "I have Notion MCP connected."

- **Problem-first**: "I need to set up a project workspace" — your skill orchestrates the right tools in the right sequence. Users describe outcomes; the skill handles the tools
- **Tool-first**: "I have Notion MCP connected" — your skill teaches Claude optimal workflows and best practices. Users have access; the skill provides expertise

Most skills lean one direction. Knowing which framing fits your use case helps you choose the right patterns.

### Writing the Main Instructions

After the frontmatter, write the actual instructions in markdown. Recommended structure (adapt for your skill):

````markdown
---
name: your-skill
description: [...]
---
# Your Skill Name

## Prerequisites
- Required tools: [MCP servers, CLI tools, packages]
- Required access: [API keys, permissions, scopes]

## Instructions

### Step 1: [First Major Step]
Clear explanation of what happens.

```bash
python scripts/fetch_data.py --project-id PROJECT_ID
```
Expected output: [describe what success looks like]

### Step 2: [Validate Before Proceeding]
Run `python scripts/validate.py` to check results.
If validation fails → fix → re-validate before continuing.

### Step 3: [Destructive or External Action]
Before executing, summarize what will change and WAIT for user confirmation.
If user declines, skip to [fallback step].

## Expected Inputs and Outputs
- **Input**: [what the user provides or what the skill reads]
- **Output**: [what gets created, modified, or returned]
- **Success criteria**: [how to know it worked]

## Examples

### Example 1: [Common scenario]
User says: "Set up a new marketing campaign"
Actions:
1. Fetch existing campaigns via MCP
2. Create new campaign with provided parameters
Result: Campaign created with confirmation link

## Reference Files
- Detailed API docs: See [reference/api.md](reference/api.md)
- Additional examples: See [examples.md](examples.md)

## Troubleshooting
Error: [Common error message]
Cause: [Why it happens]
Solution: [How to fix]
````

Not every skill needs every section. Omit Prerequisites if none exist, omit Reference Files if everything fits in SKILL.md, omit the confirmation gate if no actions are destructive. The template is a menu, not a mandate.

## Common Patterns

For advanced workflow patterns (sequential orchestration, multi-MCP coordination, iterative refinement, context-aware tool selection, domain-specific intelligence), see [patterns.md](patterns.md).

### Be specific and actionable

Language is ambiguous, code isn't. For anything critical, bundle a script:

```markdown
# Bad - ambiguous
Validate the data before proceeding.

# Good - specific and actionable
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)
```

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

Provide 1-2 minimal input/output pairs for output-quality-sensitive skills. Examples are expensive — keep them short and only include when they lock in a strict format or demonstrate a non-obvious transformation. Move longer examples to `examples.md`:

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
2. Validate: `uv run python scripts/validate.py`
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
- **Time-sensitive info**: Don't write "before August 2025, use old API." Use a collapsible "old patterns" section:
  ```markdown
  ## Current method
  Use the v2 API endpoint: `api.example.com/v2/messages`

  <details>
  <summary>Legacy v1 API (deprecated 2025-08)</summary>
  The v1 API used: `api.example.com/v1/messages`
  </details>
  ```
- **Inconsistent terminology**: Pick one term and use it throughout
- **Windows paths**: Always use forward slashes, even on Windows
- **Deep nesting**: Don't chain `advanced.md` → `details.md` → actual content
- **Assuming tools installed**: Explicitly list required packages (see [code-skills.md](code-skills.md) Dependencies and Runtime)
- **Magic numbers**: Document why constants have specific values

## Troubleshooting

Common issues and fixes. For detailed troubleshooting with examples, see [troubleshooting.md](troubleshooting.md).

| Problem | Likely Cause | Fix |
|:--------|:-------------|:----|
| Skill won't upload | File not named exactly `SKILL.md` (case-sensitive) or invalid YAML | Verify filename with `ls -la`; use `---` delimiters |
| Skill doesn't trigger | Description too vague or missing trigger phrases | Add specific keywords users would say; add negative triggers |
| Skill triggers too often | Description too broad | Add `Do NOT use for...` clauses; be more specific about scope |
| Instructions not followed | Too verbose, buried, or ambiguous | Put critical instructions first; use bullet points; use scripts for critical validation |
| Large context / slow | SKILL.md too large or too many skills enabled | Move content to reference files; keep SKILL.md under 5,000 words |

## Evaluation

Build evaluations BEFORE writing docs. Evaluation-driven development:

1. Run Claude on tasks WITHOUT the skill. Document failures
2. Build 3 scenarios testing those gaps
3. Measure baseline performance
4. Write minimal instructions to address gaps
5. Iterate: run evals, compare baseline, refine

**Using the skill-creator skill**: The [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) skill (available in the [anthropics/skills](https://github.com/anthropics/skills) repository for use in Claude.ai or Claude Code) can generate skills from descriptions, review skills for common issues, and suggest test cases. Use: "Help me build a skill using skill-creator". Note: it helps design and refine skills but does not run automated test suites.

For detailed evaluation and iterative development guidance, see [evaluation.md](evaluation.md).

## Checklist

### Before you start
- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Planned folder structure

### Core quality
- [ ] Description follows formula: [What it does] + [When to use it] + [Key capabilities]
- [ ] Description includes trigger phrases users would actually say
- [ ] Description includes WHEN NOT for clear boundaries
- [ ] SKILL.md body under 500 lines
- [ ] Details in separate files if needed
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Instructions are specific and actionable (script commands > vague language)
- [ ] File references one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps
- [ ] No README.md inside skill folder

### Code and scripts
- [ ] Scripts validate inputs and fail with clear messages (don't silently swallow errors)
- [ ] Let errors bubble up — the agent reasons about them better than pre-written handlers
- [ ] No magic numbers
- [ ] Required packages listed and verified as available
- [ ] Scripts have clear documentation (interface, output format)
- [ ] No Windows-style paths (all forward slashes)
- [ ] Validation/verification for critical operations
- [ ] Feedback loops for quality-critical tasks

### Testing
- [ ] Tested triggering on obvious tasks (should fire)
- [ ] Tested triggering on paraphrased requests (should fire)
- [ ] Verified doesn't trigger on unrelated topics (should not fire)
- [ ] Functional tests pass (valid outputs, error handling)
- [ ] Tested with target models (Haiku, Sonnet, Opus)
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)

### After deployment
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions

## Distribution

For guidance on sharing skills (GitHub hosting, API usage, organization deployment, positioning), see [distribution.md](distribution.md).

## Resources

For official documentation, blog posts, and example skills, see [resources.md](resources.md).
