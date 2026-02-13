# Skills Repository

A shared, open-source collection of agent skills following the Agent Skills open standard.

## Build & Test

- Install: `make install` (deps + settings + symlink skills)
- Install local only: `make install-local` (settings + symlink skills to ~/.claude/)
- Lint: `make lint`
- Test: `make test`


## Architecture

Skills live in `skills/<skill-name>/SKILL.md` following the Agent Skills standard. Skills with code bundle Python scripts in `skills/<skill-name>/scripts/` and use UV for execution.

All Python scripts use Click for CLIs and are run via `uv run python <script>`. **NEVER use `python` or `python3` directly** — always use `uv run python`. This ensures the correct virtualenv and dependencies are available.

## Dev Memory

Use README.md as the development memory for this repo. It contains the skill inventory, architecture notes, roadmap, and TODOs. Update it as you work.

## Anti-patterns

- **Root-cause before you build.** When something fails, diagnose the actual error before building infrastructure to work around it. Misreading `insufficient_quota` (billing) as "keys not found" (config) led to an hour of unnecessary .env plumbing. The fix was swapping one API key. Staff engineers solve the right problem; senior engineers write code for the wrong one.
- **One source of truth for config.** Shell profile (`~/.zshrc`) is the standard for personal dev tools. Don't layer .env files, UV_ENV_FILE, and settings.json on top — each layer adds precedence conflicts and debugging surface.

## Git Workflow

- **Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR. The human merges.
- **Use worktrees** when the current branch is occupied. `git worktree add /tmp/skills-<name> main` then branch from there. This prevents clobbering other in-progress work.
- **Atomic PRs.** Each PR should be independently mergeable. Don't bundle unrelated changes. If two features don't depend on each other, make two PRs.

## Conventions

- Each skill is a directory with `SKILL.md` as the entry point
- SKILL.md uses YAML frontmatter with `name` and `description`
- Descriptions use WHEN/WHEN NOT pattern for clear invocation boundaries
- **All Python CLIs use Click** — never argparse, never raw sys.argv. Click is the standard for this repo
- Python scripts use type hints and minimal dependencies
- Keep SKILL.md under 500 lines; it is the single source of truth for each skill
- **NEVER use `python` or `python3` directly** — always use `uv run python`. This ensures the correct virtualenv and dependencies are available.
