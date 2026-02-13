---
name: pr_review
description: >
  Review a GitHub PR using an external AI model. Use when reviewing PRs,
  getting a second opinion on code changes, or before merging. Do NOT use
  for local code review without a PR.
allowed-tools: Bash(uv run *), Bash(gh pr *), Bash(gh api *), Bash(git diff *), Bash(git log *)
---

Get an external AI model to review a GitHub PR. The script fetches the PR diff, metadata, and file list via `gh`, assembles structured context, and sends it to a model (default: GPT-5.2 with xhigh thinking) for review.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/review_pr.py <PR_REF> [OPTIONS]
```

`PR_REF` accepts: full URL, `owner/repo#123`, `#123`, or just `123` (last two use current repo).

## Options

- `--model` / `-m`: Model string (default: `openai:gpt-5.2`). Same format as `discussion_partners`.
- `--focus` / `-f`: Override the review focus prompt. Default asks for bugs, security, logic, design.
- `--context-file` / `-c`: Extra files to include (repeatable). Use for CLAUDE.md, architecture docs, etc.
- `--dry-run`: Print the assembled context without calling the model. Useful for checking what gets sent.

## Workflow: Review → Triage → Implement

1. **Review**: Run the script on a PR to get findings from an external model.
2. **Triage**: Read the findings. Classify each as: real issue, false positive, or style nit. Not every finding needs action.
3. **Implement**: Fix the real issues. Skip false positives and nits. Commit to the PR branch.

## Examples

```bash
# Review a PR in the current repo
uv run --directory SKILL_DIR python scripts/review_pr.py 33

# Review with extra context
uv run --directory SKILL_DIR python scripts/review_pr.py 33 -c CLAUDE.md

# Review with a different model
uv run --directory SKILL_DIR python scripts/review_pr.py 33 -m anthropic:claude-opus-4-6

# Security-focused review
uv run --directory SKILL_DIR python scripts/review_pr.py 33 -f "Focus on security: injection, auth bypass, SSRF, secrets in code"

# See what context gets sent (no API call)
uv run --directory SKILL_DIR python scripts/review_pr.py 33 --dry-run
```
