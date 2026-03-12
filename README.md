# Agent Skills

A collection of 41 AI agent skills for Claude Code. Built on the [Agent Skills](https://agentskills.io) open standard.

## What's Here

Skills that make AI coding agents more capable: reasoning frameworks, multi-model review, code quality standards, autonomous development loops, prediction markets, theorem proving, forecasting, and more. Some are pure prompt instructions, some bundle Python/R scripts, some compose into larger workflows.

There's also an optional personal knowledge management layer built on Obsidian and hierarchical memory — capture information, organize it automatically over time, and process it with thinking tools. This is useful but not required; most skills work independently.

## Skills

### Thinking & Reasoning

| Skill | Description |
|-------|-------------|
| [mental_models](.claude/skills/mental_models/) | 33 reasoning frameworks: inversion, first principles, Occam's razor, plus critical analysis protocols (antithesize, excavate, negspace, rhetoricize, etc.) |
| [ultra_think](.claude/skills/ultra_think/) | Activate deep extended thinking for complex decisions |
| [ask_questions](.claude/skills/ask_questions/) | Structured questioning — clarify before acting |
| [rlm](.claude/skills/rlm/) | Phased reasoning for large context (100K+ tokens) |

### Code Quality & Development

| Skill | Description |
|-------|-------------|
| [staff_engineer](.claude/skills/staff_engineer/) | Performance-first engineering principles, coding standards, and debugging |
| [ralph_loop](.claude/skills/ralph_loop/) | Autonomous development loop: decompose, implement, validate, repeat |
| [pr_review](.claude/skills/pr_review/) | Multi-model PR review: subagent + external models |
| [prior_art_review](.claude/skills/prior_art_review/) | Search existing issues and PRs before acting |
| [orchestrate](.claude/skills/orchestrate/) | Decompose tasks into a dependency DAG, route to specialized sub-agents |
| [concise_writing](.claude/skills/concise_writing/) | Writing principles for tight, scannable prose |
| [constitution](.claude/skills/constitution/) | User values and principles for ambiguous tradeoffs |

### Multi-Model & Evaluation

| Skill | Description |
|-------|-------------|
| [discussion_partners](.claude/skills/discussion_partners/) | Query OpenAI, Anthropic, or Google models for second opinions |
| [llm_judge](.claude/skills/llm_judge/) | LLM-as-judge evaluation for comparing outputs |
| [prompt_evolution](.claude/skills/prompt_evolution/) | Evolve prompts through mutation and crossover |

### Forecasting & Analysis

| Skill | Description |
|-------|-------------|
| [superforecaster](.claude/skills/superforecaster/) | Calibrated probabilistic forecasts with multi-model aggregation |
| [check_odds](.claude/skills/check_odds/) | Check prediction market odds (Metaculus, Manifold, PredictIt, etc.) |
| [forecast](.claude/skills/forecast/) | Time series forecasting with R's auto.arima |
| [data_science](.claude/skills/data_science/) | Opinionated DS defaults: XGBoost, nested CV, no shap |
| [lean_prover](.claude/skills/lean_prover/) | Multi-agent Lean 4 theorem proving with search and repair |

### Knowledge Management

| Skill | Description |
|-------|-------------|
| [obsidian](.claude/skills/obsidian/) | Read, write, search, and link notes in a git-backed Obsidian vault (+ CLI) |
| [hierarchical_memory](.claude/skills/hierarchical_memory/) | Quick notes aggregated into daily/monthly/overall summaries |
| [capture](.claude/skills/capture/) | Smart routing: memory, GitHub Issues, obsidian, CLAUDE.md, or README |
| [web_grab](.claude/skills/web_grab/) | Fetch URL content and save to obsidian (Playwright for JS SPAs) |
| [pdf_to_markdown](.claude/skills/pdf_to_markdown/) | Convert PDFs to clean markdown |
| [skill_stealer](.claude/skills/skill_stealer/) | Extract reusable skills from URLs into SKILL.md |
| [remember_session](.claude/skills/remember_session/) | Save session learnings to memory and obsidian |
| [reminders](.claude/skills/reminders/) | Time-aware reminders stored in obsidian |

### Workflow & Session

| Skill | Description |
|-------|-------------|
| [session_planner](.claude/skills/session_planner/) | Plan a focused work session from memory, tasks, and context |
| [daily_briefing](.claude/skills/daily_briefing/) | Morning summary from memory, tasks, and vault |
| [evergreen](.claude/skills/evergreen/) | Periodic vault and repo housekeeping |
| [heartbeat](.claude/skills/heartbeat/) | Autonomous agent on a schedule: picks up `ai:queued` issues, codes, reviews, ships |
| [slack_bridge](.claude/skills/slack_bridge/) | Phone-to-Claude capture via Slack MCP |

### Tools & Reference

| Skill | Description |
|-------|-------------|
| [claude-code-config](.claude/skills/claude-code-config/) | Claude Code config reference: settings, permissions, hooks, env vars, MCP |
| [skills_reference](.claude/skills/skills_reference/) | Comprehensive reference for authoring SKILL.md files |
| [gh_cli](.claude/skills/gh_cli/) | GitHub CLI usage patterns and permissions |
| [gws_cli](.claude/skills/gws_cli/) | Google Workspace CLI for Drive, Gmail, Sheets, Calendar |
| [modal](.claude/skills/modal/) | Run GPU compute on Modal |
| [jina_grep](.claude/skills/jina_grep/) | Semantic grep using Jina embedding models on Apple Silicon |
| [api_key_checker](.claude/skills/api_key_checker/) | Verify AI provider API keys are configured and valid |
| [skill_pruner](.claude/skills/skill_pruner/) | Audit skills for overlap, bloat, and quality |
| [private_repo](.claude/skills/private_repo/) | Create or connect private GitHub repos for git-backed storage |

## Install

### Claude Code (full install)

```bash
git clone https://github.com/zachmayer/skills.git
cd skills
make install
```

This installs system deps (via Homebrew), Python deps (via UV), symlinks all skills into `~/.claude/skills/`, sets up global config (`settings.json`, `CLAUDE.md`, security hooks), and runs auth for GitHub and Google Workspace.

### Claude.ai (web)

```bash
make build-web
```

Packages 17 web-compatible skills (no auth required) as `.zip` files in `build/claude-ai/`. Drag them into a Claude.ai Project to install.

### What install sets up

**Global config** (applies to all repos):
- `~/.claude/settings.json` — Permissions with targeted deny rules for destructive operations
- `~/.claude/hooks/reject-shell-operators.sh` — Blocks shell injection (`&&`, `||`, backticks, `$()`)
- `~/CLAUDE.md` — Global agent instructions: model preferences, git workflow, conventions

**Agent workspace**:
- `~/claude/scratch/` — Temp files (PR bodies, commit messages, downloads)
- `~/claude/worktrees/` — Git worktrees for parallel development
- `~/claude/obsidian/` — Obsidian vault for knowledge management (optional)

**Per-project config** (this repo only):
- `.claude/settings.json` — Adds `Edit(**)` and `Write(**)` for full file access. Other permissions inherit from global config.
- `CLAUDE.md` — Repo-specific conventions, anti-patterns, and build commands.

## Development

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
make help           # Show all available targets
make ci             # CI checks: lint + typecheck + unit tests
make test           # All checks: CI + integration tests
make upgrade        # Upgrade all dependencies
make build-web      # Package skills for Claude.ai
```

### Heartbeat (opt-in)

Runs Claude Code on a schedule via launchd, picking up `ai:queued` issues automatically.

```bash
make setup-heartbeat-token   # Get OAuth token (lasts ~1 year)
make setup-heartbeat-labels  # Create ai:* labels on monitored repos
make install-heartbeat       # Install launchd daemon (every 15 min)
```

## Creating a New Skill

Each skill is a directory under `.claude/skills/` with a `SKILL.md` file:

```
.claude/skills/my_skill/
├── SKILL.md           # Required: instructions + YAML frontmatter
└── scripts/           # Optional: bundled code
    └── my_script.py
```

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

Python skills use [Click](https://click.palletsprojects.com/) for CLIs and [UV](https://docs.astral.sh/uv/) for execution. Use `/skill_stealer` to extract skills from URLs automatically.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_OBSIDIAN_DIR` | Vault root (default: `~/claude/obsidian`) |
| `OPENAI_API_KEY` | For `discussion_partners` (OpenAI models) |
| `ANTHROPIC_API_KEY` | For `discussion_partners` (Anthropic models) |
| `GOOGLE_API_KEY` | For `discussion_partners` (Google models) |

Add keys to `~/.zshrc` or `~/.bashrc`. Claude Code sources your shell profile at startup.

## License

MIT
