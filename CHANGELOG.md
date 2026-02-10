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

### Changed

- Renamed project from python-boilerplate to agent-skills
- Added click, httpx, polars, pydantic-ai as dependencies
- README reorganized around capture/organize/process narrative
- Skills grouped by pipeline stage in README

### Removed

- Boilerplate demo function and demo-script entry point

## [0.1.0] - 2025-10-28

### Added

- Basic framework for creating project with UV with dev dependencies
- Makefile for running install, build, test, upgrade, lint
- pre-commit setup
- Github actions for test running, updater and dependabot
- Branch ruleset to import and use
- CHANGELOG.md and README.md
