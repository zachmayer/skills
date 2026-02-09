# Agent Skills

A shared, open-source collection of agent skills following the [Agent Skills](https://agentskills.io) open standard. Works with Claude Code, Cursor, Codex, Gemini CLI, and 30+ other AI coding agents.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| [ask_questions](skills/ask_questions/) | Prompt | Structured questioning framework: clarify before acting |
| [beast_mode](skills/beast_mode/) | Prompt | Maximum persistence mode: keep going until fully solved |
| [concise_writing](skills/concise_writing/) | Prompt | Writing principles for tight, scannable prose |
| [data_science](skills/data_science/) | Prompt | Opinionated DS defaults: XGBoost, nested CV, no shap |
| [discussion_partners](skills/discussion_partners/) | Python | Query OpenAI, Anthropic, or Google models via pydantic-ai |
| [forecast](skills/forecast/) | R | Time series forecasting with auto.arima |
| [gh_cli](skills/gh_cli/) | Prompt | GitHub CLI usage patterns and permissions |
| [heartbeat](skills/heartbeat/) | Shell | Cron-based autonomous task processing for Claude Code |
| [hierarchical_memory](skills/hierarchical_memory/) | Python | Notes aggregated into daily/weekly/monthly/overall summaries |
| [lean_prover](skills/lean_prover/) | Prompt | Multi-agent Lean 4 theorem proving with search and repair |
| [llm_judge](skills/llm_judge/) | Prompt | LLM-as-judge evaluation for comparing outputs with rubrics |
| [mental_models](skills/mental_models/) | Prompt | Reasoning frameworks: inversion, pattern language, pre-mortems |
| [obsidian](skills/obsidian/) | Prompt | Read, write, search, and link notes in a git-backed Obsidian vault |
| [pdf_to_markdown](skills/pdf_to_markdown/) | Python | Convert PDFs to clean markdown using marker |
| [private_repo](skills/private_repo/) | Prompt | Create or connect private GitHub repos for sensitive data |
| [prompt_evolution](skills/prompt_evolution/) | Prompt | Evolve prompts through mutation and crossover over generations |
| [ralph_loop](skills/ralph_loop/) | Prompt | Autonomous development loop: decompose, implement, validate, repeat |
| [remember_session](skills/remember_session/) | Prompt | Save session learnings to hierarchical memory and obsidian |
| [skill_stealer](skills/skill_stealer/) | Prompt | Extract skills from URLs into SKILL.md with degrees-of-freedom analysis |
| [staff_engineer](skills/staff_engineer/) | Prompt | Performance-first engineering principles and coding standards |
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
make help      # Show all available targets
make install   # Install Python + deps + pre-commit hooks
make lint      # Run ruff linting and formatting
make typecheck # Run ty type checker
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
- `discussion_partners`: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`

## Roadmap

Major improvements, curated by human and Claude together.

### Architecture

- [ ] **Consolidate memory repos into obsidian** — Daily notes, monthly summaries, overall memory, and heartbeat tasks all live in one obsidian vault. Single git repo. Time-series in `daily/`, curated knowledge in topic notes, TODO lists as standalone files. Eliminates managing 3 separate repos (memory, obsidian, heartbeat).
- [ ] **Smarter heartbeat** — Heartbeat should read the day's memory and obsidian notes, decide the highest-value activity (or sleep), and write questions to the user as obsidian notes instead of requiring interactive input.

### Skill Quality

- [ ] **Skill pruner/compactor** — A skill that reviews all installed skills, finds overlaps, and proposes merges or deletions. Not aggressive — just surfaces candidates. Compares each skill against the [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): is this teaching the model what it already knows?
- [ ] **Compile external skills into existing ones** — Instead of copying FUTURE_TOKENS skills wholesale, review each against our existing skills (e.g., external thinking tools vs mental_models), merge what's novel, discard what's redundant. Precise wording may matter for eliciting specific LLM behavior — evaluate case by case.

### Human TODOs

- [ ] Delete old `~/claude/heartbeat/` repo after heartbeat consolidation
- [ ] Delete old `~/claude/memory/` repo after memory consolidation
- [ ] Re-run crontab setup after heartbeat path changes

## License

MIT
