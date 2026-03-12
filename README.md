# Agent Skills

A collection of 32 AI agent skills for Claude Code. Built on the [Agent Skills](https://agentskills.io) open standard.

## What's Here

Skills that make AI coding agents more capable: reasoning frameworks, multi-model review, code quality standards, autonomous development loops, prediction markets, theorem proving, forecasting, and more. Some are pure prompt instructions, some bundle Python/R scripts, some compose into larger workflows.

There's also an optional personal knowledge management layer built on Obsidian and hierarchical memory — capture information, organize it automatically over time, and process it with thinking tools. This is useful but not required; most skills work independently.

## Skills

### Thinking & Reasoning

| Skill | Description |
|-------|-------------|
| [mental-models](.claude/skills/mental-models/) | 33 reasoning frameworks: inversion, first principles, Occam's razor, plus critical analysis protocols (antithesize, excavate, negspace, rhetoricize, etc.) |
| [ultra-think](.claude/skills/ultra-think/) | Activate deep extended thinking for complex decisions |
| [ask-questions](.claude/skills/ask-questions/) | Structured questioning — clarify before acting |
| [rlm](.claude/skills/rlm/) | Phased reasoning for large context (100K+ tokens) |

### Code Quality & Development

| Skill | Description |
|-------|-------------|
| [staff-engineer](.claude/skills/staff-engineer/) | Performance-first engineering principles, coding standards, and debugging |
| [ralph-loop](.claude/skills/ralph-loop/) | Autonomous development loop: decompose, implement, validate, repeat |
| [pr-review](.claude/skills/pr-review/) | Multi-model PR review: subagent + external models |
| [prior-art-review](.claude/skills/prior-art-review/) | Search existing issues and PRs before acting |
| [orchestrate](.claude/skills/orchestrate/) | Decompose tasks into a dependency DAG, route to specialized sub-agents |
| [concise-writing](.claude/skills/concise-writing/) | Writing principles for tight, scannable prose |
| [constitution](.claude/skills/constitution/) | User values and principles for ambiguous tradeoffs |

### Multi-Model & Evaluation

| Skill | Description |
|-------|-------------|
| [discussion-partners](.claude/skills/discussion-partners/) | Query OpenAI, Anthropic, or Google models for second opinions |
| [llm-judge](.claude/skills/llm-judge/) | LLM-as-judge evaluation for comparing outputs |
| [prompt-evolution](.claude/skills/prompt-evolution/) | Evolve prompts through mutation and crossover |

### Forecasting & Analysis

| Skill | Description |
|-------|-------------|
| [superforecaster](.claude/skills/superforecaster/) | Calibrated probabilistic forecasts with multi-model aggregation; also checks prediction market odds (Metaculus, Manifold, PredictIt, etc.) |
| [forecast](.claude/skills/forecast/) | Time series forecasting with R's auto.arima |
| [data-science](.claude/skills/data-science/) | Opinionated DS defaults: XGBoost, nested CV, no shap |
| [lean-prover](.claude/skills/lean-prover/) | Multi-agent Lean 4 theorem proving with search and repair |

### Knowledge Management

| Skill | Description |
|-------|-------------|
| [knowledge-system](.claude/skills/knowledge-system/) | Unified knowledge management: memory, obsidian vault, capture routing, reminders, maintenance |
| [web-grab](.claude/skills/web-grab/) | Fetch URL content and save to obsidian (Playwright for JS SPAs) |
| [pdf-to-markdown](.claude/skills/pdf-to-markdown/) | Convert PDFs to clean markdown |

### Workflow & Session

| Skill | Description |
|-------|-------------|
| [session-lifecycle](.claude/skills/session-lifecycle/) | Session lifecycle: daily briefing, session planning, end-of-session persistence |
| [heartbeat](.claude/skills/heartbeat/) | Autonomous agent on a schedule: picks up `ai:queued` issues, codes, reviews, ships |
| [slack-bridge](.claude/skills/slack-bridge/) | Phone-to-Claude capture via Slack MCP |

### Tools & Reference

| Skill | Description |
|-------|-------------|
| [claude-code-config](.claude/skills/claude-code-config/) | Claude Code config reference: settings, permissions, hooks, env vars, MCP |
| [skillcraft](.claude/skills/skillcraft/) | Author, extract, and maintain Agent Skills (reference + stealer + pruner) |
| [gh-cli](.claude/skills/gh-cli/) | GitHub CLI usage patterns and permissions |
| [gws-cli](.claude/skills/gws-cli/) | Google Workspace CLI for Drive, Gmail, Sheets, Calendar |
| [modal](.claude/skills/modal/) | Run GPU compute on Modal |
| [jina-grep](.claude/skills/jina-grep/) | Semantic grep using Jina embedding models on Apple Silicon |
| [api-key-checker](.claude/skills/api-key-checker/) | Verify AI provider API keys are configured and valid |
| [private-repo](.claude/skills/private-repo/) | Create or connect private GitHub repos for git-backed storage |

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
.claude/skills/my-skill/
├── SKILL.md           # Required: instructions + YAML frontmatter
└── scripts/           # Optional: bundled code
    └── my_script.py
```

```yaml
---
name: my-skill
description: >
  WHEN to use: <specific triggers>.
  WHEN NOT to use: <boundaries>.
---

Your instructions here. For skills with code, reference scripts:

uv run --directory SKILL_DIR python scripts/my_script.py $ARGUMENTS
```

Python skills use [Click](https://click.palletsprojects.com/) for CLIs and [UV](https://docs.astral.sh/uv/) for execution. Use `/skillcraft` to extract skills from URLs automatically.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_OBSIDIAN_DIR` | Vault root (default: `~/claude/obsidian`) |
| `OPENAI_API_KEY` | For `discussion-partners` (OpenAI models) |
| `ANTHROPIC_API_KEY` | For `discussion-partners` (Anthropic models) |
| `GOOGLE_API_KEY` | For `discussion-partners` (Google models) |

Add keys to `~/.zshrc` or `~/.bashrc`. Claude Code sources your shell profile at startup.

## License

MIT
