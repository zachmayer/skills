# Skills Repository

A shared, open-source collection of agent skills following the Agent Skills open standard.

## Build & Test

- Install: `make install` (full: deps + settings + external + local skills)
- Install local only: `make install-local` (settings + symlink skills to ~/.claude/)
- Lint: `make lint`
- Test: `make test`
- Pull external skills: `make pull-external`

## Architecture

Skills live in `skills/<skill-name>/SKILL.md` following the Agent Skills standard. Skills with code bundle Python scripts in `skills/<skill-name>/scripts/` and use UV for execution.

All Python scripts use Click for CLIs and are run via `uv run python <script>`.

## Conventions

- Each skill is a directory with `SKILL.md` as the entry point
- SKILL.md uses YAML frontmatter with `name` and `description`
- Descriptions use WHEN/WHEN NOT pattern for clear invocation boundaries
- Python scripts use Click, type hints, and minimal dependencies
- Keep SKILL.md under 500 lines; move reference material to separate files
