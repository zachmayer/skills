---
name: context_compiler
description: >
  Assemble structured context docs from git diffs, files, memory, and obsidian notes.
  WHEN: Preparing context for PR reviews, code discussions, or feeding structured
  input to external models. WHEN NOT: For direct PR review (use pr_review), or when
  you just need to read a single file.
allowed-tools: Bash(uv run *), Bash(git diff *), Bash(git log *), Bash(git show *), Bash(gh pr *), Bash(gh api *), Read, Glob, Grep
---

Compile structured context documents from multiple sources into a single XML document. Generalizes the context assembly pattern from `pr_review` into a reusable tool.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/compile_context.py [OPTIONS]
```

All sources are optional — include only what you need. Output goes to stdout.

## Options

### Git sources
- `--diff REF`: Include `git diff REF` output (e.g., `HEAD~3`, `main..HEAD`, a commit SHA)
- `--log REF`: Include `git log REF` output (e.g., `-5`, `main..HEAD`)
- `--pr NUMBER`: Include PR metadata and diff via `gh` (number, URL, or `owner/repo#N`)

### File sources
- `--file PATH`: Include a file's contents (repeatable)
- `--glob PATTERN`: Include files matching a glob pattern (repeatable)

### Memory / obsidian sources
- `--memory PATH`: Include a memory file from the obsidian vault (repeatable)
- `--obsidian-search QUERY`: Search obsidian vault and include matching notes (repeatable)
- `--obsidian-dir DIR`: Obsidian vault directory (default: `$CLAUDE_OBSIDIAN_DIR` or `~/claude/obsidian`)

### Output control
- `--max-chars N`: Truncate total output at N chars (default: 100000)
- `--format FORMAT`: Output format: `xml` (default) or `markdown`

## Examples

```bash
# Context for a PR review (equivalent to what pr_review builds internally)
uv run --directory SKILL_DIR python scripts/compile_context.py \
  --pr 33 --file CLAUDE.md

# Context from recent commits + architecture docs
uv run --directory SKILL_DIR python scripts/compile_context.py \
  --diff main..HEAD --log main..HEAD --file CLAUDE.md --file README.md

# Context from obsidian notes
uv run --directory SKILL_DIR python scripts/compile_context.py \
  --memory memory/session_log.md --obsidian-search "authentication"

# Combine everything for a thorough review
uv run --directory SKILL_DIR python scripts/compile_context.py \
  --pr 33 --file CLAUDE.md --memory memory/reminders.md --format xml
```

## Output Format

### XML (default)

```xml
<context>
  <source type="diff" ref="main..HEAD">
    ... diff content ...
  </source>
  <source type="log" ref="main..HEAD">
    ... log content ...
  </source>
  <source type="pr" ref="33">
    <metadata>...</metadata>
    <description>...</description>
    <files>...</files>
    <diff>...</diff>
  </source>
  <source type="file" path="CLAUDE.md">
    ... file content ...
  </source>
  <source type="memory" path="memory/session_log.md">
    ... note content ...
  </source>
  <source type="obsidian-search" query="authentication">
    <result path="notes/auth.md">... content ...</result>
  </source>
</context>
```

### Markdown

Sections are separated by headers with source metadata.
