# Agent Skills

A shared, open-source collection of agent skills following the [Agent Skills](https://agentskills.io) open standard. Works with Claude Code, Cursor, Codex, Gemini CLI, and 30+ other AI coding agents.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| [ask_questions](skills/ask_questions/) | Prompt | Structured questioning framework: clarify before acting |
| [concise_writing](skills/concise_writing/) | Prompt | Writing principles for tight, scannable prose |
| [discussion_partners](skills/discussion_partners/) | Python | Query OpenAI, Anthropic, or Google models for second opinions |
| [heartbeat](skills/heartbeat/) | Shell | Cron-based autonomous task processing for Claude Code |
| [hierarchical_memory](skills/hierarchical_memory/) | Python | ISO-timestamped notes aggregated into daily/weekly/overall summaries |
| [mental_models](skills/mental_models/) | Prompt | Reasoning frameworks: inversion, second-order thinking, pre-mortems |
| [obsidian](skills/obsidian/) | Prompt | Read, write, search, and link notes in a git-backed Obsidian vault |
| [pdf_to_markdown](skills/pdf_to_markdown/) | Python | Convert PDFs to clean markdown using marker |
| [private_repo](skills/private_repo/) | Prompt | Create or connect private GitHub repos for sensitive data like memory or notes |
| [ralph_loop](skills/ralph_loop/) | Prompt | Autonomous development loop: decompose, implement, validate, repeat |
| [staff_engineer](skills/staff_engineer/) | Prompt | Performance-first engineering principles and coding standards |
| [skill_stealer](skills/skill_stealer/) | Prompt | Extract skills from URLs (repos, tweets, blog posts) into SKILL.md format |
| [ultra_think](skills/ultra_think/) | Prompt | Activate deep extended thinking for complex decisions |

## Install

### Via npx (recommended, works with all agents)

```bash
# Install all skills
npx skills add zachmayer/skills

# Install a specific skill
npx skills add zachmayer/skills -s pdf_to_markdown

# Install globally (available in all projects)
npx skills add zachmayer/skills -g
```

### Via Makefile (Claude Code, symlinks)

```bash
git clone https://github.com/zachmayer/skills.git
cd skills
make install        # Install Python deps
make install-local  # Symlink skills to ~/.claude/skills/
```

### Pull external skills (FUTURE_TOKENS)

```bash
make pull-external  # Clone and copy FUTURE_TOKENS skills
make install-local  # Link everything including external skills
```

## Development

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
make install   # Install Python + deps + pre-commit hooks
make lint      # Run ruff linting and formatting
make test      # Run pytest
make upgrade   # Upgrade all dependencies
```

## Creating a New Skill

Each skill is a directory under `skills/` with a `SKILL.md` file:

```
skills/my_skill/
├── SKILL.md           # Required: instructions + YAML frontmatter
└── scripts/           # Optional: bundled code
    └── my_script.py
```

The `SKILL.md` format:

```yaml
---
name: my_skill
description: >
  WHEN to use: <specific triggers>.
  WHEN NOT to use: <boundaries>.
---

Your instructions here. For skills with code, reference scripts:

uv run --directory SKILL_DIR python scripts/my_script.py $ARGUMENTS
```

Use the `/skill_stealer` skill to extract skills from URLs automatically.

## Python Skills

Skills that bundle Python code use [Click](https://click.palletsprojects.com/) for CLIs and [UV](https://docs.astral.sh/uv/) for execution. Dependencies are managed in the root `pyproject.toml`.

Required environment variables for specific skills:
- `discussion_partners`: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

## License

MIT
