# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 13 agent skills following the Agent Skills open standard
- Skills: ask_questions, concise_writing, discussion_partners, heartbeat,
  hierarchical_memory, mental_models, obsidian, pdf_to_markdown, private_repo,
  ralph_loop, staff_engineer, skill_stealer, ultra_think
- Dependabot auto-merge workflow and grouped updates
- CLAUDE.md for repo context
- .claude-plugin/marketplace.json for Claude Code plugin registry
- Makefile targets: install-local, uninstall-local, pull-external

### Changed

- Renamed project from python-boilerplate to agent-skills
- Added click, httpx, marker-pdf as dependencies

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
