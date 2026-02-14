---
name: prompt_report
description: >
  Analyze prompt effectiveness: token budget, clarity, coverage gaps. Use when
  reviewing SKILL.md files, system prompts, or any prompt text for quality and
  efficiency. Do NOT use for generating or editing prompts (use prompt_evolution).
---

Analyze one or more prompt files and produce a structured effectiveness report.

## Quick Start

```bash
# Analyze a single skill
uv run --directory SKILL_DIR python scripts/analyze_prompt.py skills/staff_engineer/SKILL.md

# Analyze multiple files
uv run --directory SKILL_DIR python scripts/analyze_prompt.py skills/*/SKILL.md

# JSON output for programmatic use
uv run --directory SKILL_DIR python scripts/analyze_prompt.py --format json skills/ultra_think/SKILL.md

# Set a custom context window (default: 200000 tokens)
uv run --directory SKILL_DIR python scripts/analyze_prompt.py --context-window 128000 skills/mental_models/SKILL.md
```

## What It Measures

### 1. Token Budget
- Approximate token count (chars/4 heuristic — close enough for analysis)
- Percentage of context window consumed
- Line count and word count

### 2. Structure & Clarity
- YAML frontmatter present with `name` and `description`
- Description uses WHEN/WHEN NOT pattern
- Under 500 lines (repo convention)
- Has section headers (##)
- Name matches directory name

### 3. Content Analysis
- **Signal lines**: Behavioral overrides, prohibitions, templates, procedures, scoring formulas
- **Filler lines**: Examples, meta-commentary, integration notes, references
- **Signal ratio**: signal lines / total non-blank lines
- **Coverage flags**: Missing frontmatter fields, no procedural steps, no output format

### 4. Recommendations
- Compression candidates (>150 lines with low signal ratio)
- Missing structural elements
- Token budget warnings (>5% of context window)

## Report Format

```
## Prompt Report: <filename>

### Budget
- Tokens: ~N (N.N% of context window)
- Lines: N | Words: N

### Structure
- [PASS/FAIL] YAML frontmatter
- [PASS/FAIL] WHEN/WHEN NOT description
- [PASS/FAIL] Under 500 lines
- [PASS/FAIL] Has section headers
- [PASS/SKIP] Name matches directory

### Content
- Signal lines: N (NN%)
- Filler lines: N (NN%)
- Blank/structural: N

### Recommendations
- [actionable items]
```

## Interpreting Results

- **Signal ratio >70%**: Tight, well-compressed prompt
- **Signal ratio 40-70%**: Room for compression — check filler lines
- **Signal ratio <40%**: Heavy candidate for compression (see skill_pruner)
- **>5% context window**: Large prompt — ensure value justifies cost
- **>10% context window**: Very large — strongly consider splitting or compressing
