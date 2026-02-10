# Skills Repository

A shared, open-source collection of agent skills following the Agent Skills open standard.

## Build & Test

- Install: `make install` (deps + settings + symlink skills)
- Install local only: `make install-local` (settings + symlink skills to ~/.claude/)
- Lint: `make lint`
- Test: `make test`
- Sync external skills: `make sync-external`

## Architecture

Skills live in `skills/<skill-name>/SKILL.md` following the Agent Skills standard. Skills with code bundle Python scripts in `skills/<skill-name>/scripts/` and use UV for execution.

All Python scripts use Click for CLIs and are run via `uv run python <script>`.

## Dev Memory

Use README.md as the development memory for this repo. It contains the skill inventory, architecture notes, roadmap, and TODOs. Update it as you work.

## Conventions

- Each skill is a directory with `SKILL.md` as the entry point
- SKILL.md uses YAML frontmatter with `name` and `description`
- Descriptions use WHEN/WHEN NOT pattern for clear invocation boundaries
- Python scripts use Click, type hints, and minimal dependencies
- Keep SKILL.md under 200 lines; move detailed examples/reference to REFERENCE.md
