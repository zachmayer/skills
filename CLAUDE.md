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

## Dependency Updates

- **Always stay on latest versions.** When dependabot opens a PR to bump a dependency, the update should be merged — not reverted. If a dependency bump breaks tests, **fix the tests and code to work with the new version**. Do not revert the bump or pin to an old version.
- **Tests validate the current API, not a frozen snapshot.** The `test_pydantic_ai_compat.py` test dynamically detects the correct `AgentRunResult` attribute from the installed version. If pydantic-ai renames fields again, update the scripts to match — the test will tell you what the correct attribute is.
- **Conflicting transitive deps get isolated.** If a heavy optional dependency (e.g. marker-pdf) pins a transitive dep (e.g. anthropic) to a range incompatible with core deps (e.g. pydantic-ai), use PEP 723 inline script metadata (`# /// script`) so the skill runs in its own isolated env via `uv run --script`. Do not hold back core dependency upgrades to accommodate optional extras.

## Anti-patterns

- **Root-cause before you build.** When something fails, diagnose the actual error before building infrastructure to work around it. Misreading `insufficient_quota` (billing) as "keys not found" (config) led to an hour of unnecessary .env plumbing. The fix was swapping one API key. Staff engineers solve the right problem; senior engineers write code for the wrong one.
- **One source of truth for config.** Shell profile (`~/.zshrc`) is the standard for personal dev tools. Don't layer .env files, UV_ENV_FILE, and settings.json on top — each layer adds precedence conflicts and debugging surface.
- **Verify before "fixing" dependency bumps.** When dependabot bumps a library, don't assume the API changed. Test the actual behavior (`uv run python -c "..."`) before modifying code. PR #24 introduced a bug by "fixing" a non-existent API rename in pydantic-ai. Always branch from `origin/main` (not a stale local main) and run tests against the current dependency versions.
- **Don't trust training data for library APIs.** Your knowledge cutoff may reflect a beta, a different version, or simply be wrong. Inspect the actual installed code to determine data structures: `uv run python -c "from lib import Class; print(dir(Class()))"`. Packages like pydantic-ai change fast — what you "know" about the API may be stale. If you believe an API changed but can't reproduce the error, your training data is wrong. Trust the installed version, not your memory.
- **Fix tests, don't revert dep bumps.** When a dependency update breaks tests, the tests need to be fixed — not the update reverted. Staying on old versions creates compounding tech debt. The compat test (`test_pydantic_ai_compat.py`) exists to detect pydantic-ai API changes; when it fires, update the code to match the new API.
- **Don't give the user indented heredocs.** `<<'EOF'` requires the closing `EOF` at column 0 — any leading whitespace prevents termination and the shell hangs. When giving the user shell commands, pass strings directly with flags (`--body "..."`) instead of `$(cat <<'EOF' ... EOF)` patterns.

## Git Workflow

- **Always use PRs.** Never commit directly to main. Create a feature branch, push it, and open a PR. The human merges.
- **Use worktrees** when the current branch is occupied. `git worktree add /tmp/skills-<name> main` then branch from there. This prevents clobbering other in-progress work.
- **Atomic PRs.** Each PR should be independently mergeable. Don't bundle unrelated changes. If two features don't depend on each other, make two PRs.
- **When superseding a PR**, remind the human to close the old PR. Give them the `gh pr close` command with a comment. Do NOT open the new PR until the human confirms the old one is closed. Keep reminding until you can verify closure with `gh pr view`.

## Conventions

- Each skill is a directory with `SKILL.md` as the entry point
- SKILL.md uses YAML frontmatter with `name` and `description`
- Descriptions use WHEN/WHEN NOT pattern for clear invocation boundaries
- **All Python CLIs use Click** — never argparse, never raw sys.argv. Click is the standard for this repo
- Python scripts use type hints and minimal dependencies
- Keep SKILL.md under 500 lines; it is the single source of truth for each skill
- **NEVER use `python` or `python3` directly** — always use `uv run python`. This ensures the correct virtualenv and dependencies are available.
