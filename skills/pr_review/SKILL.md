---
name: pr_review
description: >
  Review a GitHub PR using an external AI model. Use when reviewing PRs,
  getting a second opinion on code changes, or before merging. Do NOT use
  for local code review without a PR.
allowed-tools: Bash(uv run *), Bash(gh pr *), Bash(gh api *)
---

Get an external AI model to review a GitHub PR. This skill assembles structured PR context, then delegates to `discussion_partners` for the actual model call.

## Step 1: Assemble Context

Run the context assembly script to fetch the PR and build structured XML:

```bash
uv run --directory SKILL_DIR python scripts/review_pr.py <PR_REF> [OPTIONS]
```

`PR_REF` accepts: full URL, `owner/repo#123`, `#123`, or just `123` (last two use current repo).

Options:
- `--context-file` / `-c`: Extra files to include (repeatable). Use for CLAUDE.md, architecture docs, etc.
- `--max-diff`: Max diff chars before truncation (default: 80000).

The script prints XML context to stdout and status messages to stderr.

## Step 2: Send to discussion_partners

Pass the assembled context to the `discussion_partners` skill with a review-focused system prompt. Use this system prompt:

```
You are an expert code reviewer. Review the PR diff and report findings.
Rules:
- Focus on correctness, bugs, security issues, and design problems
- Skip style nits, formatting, and naming unless they cause confusion
- Each finding must reference a specific file and line/hunk
- Rate severity: critical (breaks things), warning (likely problem), note (worth considering)
- If the code looks good, say so briefly — don't invent issues
- Be direct. No filler.
```

Construct the question as:

```
Review this PR for real issues. Flag bugs, security problems, logic errors,
and design concerns. Skip style nits.

For each finding:
- **Severity**: critical / warning / note
- **Location**: file:line or file:hunk
- **Issue**: what's wrong
- **Suggestion**: how to fix it

If the PR looks clean, say so.

<CONTEXT FROM STEP 1>
```

Call `discussion_partners` with the `-s` flag for the system prompt and the question as the positional argument. Use whatever model is appropriate (default GPT-5.2 is recommended for reviews).

## Step 3: Triage

Not every finding is actionable. Read the review and classify each finding as:

- **Real issue**: fix it
- **False positive**: skip it (explain why if non-obvious)
- **Style nit**: skip unless it causes confusion

Implement fixes for real issues. Don't blindly apply every suggestion.

## Examples

```bash
# Assemble context for PR #33
uv run --directory SKILL_DIR python scripts/review_pr.py 33

# With extra context files
uv run --directory SKILL_DIR python scripts/review_pr.py 33 -c CLAUDE.md

# Security-focused review: override the question when calling discussion_partners
# to focus on "injection, auth bypass, SSRF, secrets in code"
```
