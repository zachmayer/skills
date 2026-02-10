# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 34 agent skills following the Agent Skills open standard
- **Capture skills**: hierarchical_memory, web_grab, pdf_to_markdown, remember_session, skill_stealer
- **Organize skills**: obsidian, heartbeat, private_repo
- **Process skills**: ultra_think, mental_models, ask_questions, discussion_partners, data_science, forecast, lean_prover
- **Analyze skills**: antithesize, excavate, synthesize, negspace, rhetoricize, dimensionalize, inductify, rhyme, metaphorize, handlize
- **Build skills**: ralph_loop, beast_mode, staff_engineer, debug, concise_writing, gh_cli, prompt_evolution, llm_judge, skill_pruner
- Polars-based `status` command for memory aggregation staleness detection
- Progressive disclosure: 8 oversized skills split into SKILL.md + REFERENCE.md
- External skills sync from FUTURE_TOKENS via `make sync-external`
- Dependabot auto-merge workflow and grouped updates
- CLAUDE.md and AGENTS.md for repo context
- .claude-plugin/marketplace.json for Claude Code plugin registry
- Makefile targets: install-local, install-ci, install-heartbeat, uninstall-local, sync-external
- settings.template.json with gh CLI permissions (read-only allow, mutating deny)
- Heartbeat cron auth fix (sources ~/.claude/heartbeat.env)
- Time-aware ralph_loop with deadline pacing
- Hostname in daily memory notes for multi-machine disambiguation
- Pre-flight API key check and error disambiguation in ask_model.py
- Security deny list in settings.json for destructive operations
- Path traversal fix in memory.py show() command
- python-frontmatter library for robust YAML parsing
- yaml.safe_load + timeout in sync_external.py
- `--list-models` flag for discussion_partners

### Changed

- Renamed project from python-boilerplate to agent-skills
- Added click, httpx, polars, pydantic-ai, python-frontmatter as dependencies
- README reorganized around capture/organize/process narrative
- Skills grouped by pipeline stage in README
- Consolidated all env vars to single `CLAUDE_OBSIDIAN_DIR` (replaces CLAUDE_MEMORY_DIR, OBSIDIAN_ROOT, VAULT_DIR, CLAUDE_HEARTBEAT_TASKS)
- memory.py CLI simplified: removed search/today/show, added read-day/read-month/read-overall/read-current/list
- marker-pdf moved from optional dependency group to main dependencies
- Skills audit: net 12% reduction across all skills (gh_cli 246→44, ultra_think 169→50, obsidian 85→21)
- 7 FUTURE_TOKENS techniques compiled into mental_models
- All 10 FUTURE_TOKENS skills promoted to first-class
- Heartbeat derives paths from CLAUDE_OBSIDIAN_DIR, uses # CLAUDE_HEARTBEAT cron marker
- .expanduser() on CLAUDE_OBSIDIAN_DIR so ~/... env vars resolve
- Staleness detection refactored to pure dataframe join (no nested Python loops)

### Removed

- Boilerplate demo function and demo-script entry point
- `.env.example` (one source of truth: shell profile)
- 8 REFERENCE.md files (reversed progressive disclosure; full content in SKILL.md)
- 200-line test file

## [0.1.0] - 2025-10-28

### Added

- Basic framework for creating project with UV with dev dependencies
- Makefile for running install, build, test, upgrade, lint
- pre-commit setup
- Github actions for test running, updater and dependabot
- Branch ruleset to import and use
- CHANGELOG.md and README.md
