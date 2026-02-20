---
name: pr_review
description: >
  Review a GitHub PR for bugs, security issues, and design problems.
  Use when reviewing PRs or before merging. Do NOT use for local code
  review without a PR.
allowed-tools: Bash(gh pr *), Bash(gh api *), Bash(git diff *), Bash(git log *), Bash(uv run *)
---

## Step 1: Fetch Context

Given a PR reference (number, URL, or `owner/repo#123`), fetch everything the reviewers will need:

```bash
gh pr view <N> [--repo owner/repo] --json title,body,author,state,baseRefName,headRefName,files,url
gh pr diff <N> [--repo owner/repo]
```

Also read `CLAUDE.md` and any relevant project docs so reviewers understand repo conventions.

Capture the PR owner, repo, and number for Step 4.

## Step 2: Parallel Review

Launch BOTH in parallel — do not wait for one before starting the other.

**Subagent** (Task tool, `general-purpose`): Pass all context from Step 1 with this system prompt:

> You are an expert code reviewer. Review the PR diff. Focus on correctness, bugs, security, and design. Skip style nits, formatting, and naming unless they cause real confusion. Each finding: severity (critical/warning/note), file, line, issue, suggested fix. If the code is clean, say so. Be direct. No filler.

**discussion_partners**: Send the same context to an external model for an independent review.

```bash
# SKILL_DIR below refers to the discussion_partners skill directory
uv run --directory SKILL_DIR python scripts/ask_model.py \
  -s "You are an expert code reviewer. Focus on correctness, bugs, security, and design. Skip style nits. Each finding: severity (critical/warning/note), file, line, issue, suggested fix. If the code is clean, say so. Be direct." \
  "Review this PR. <include PR metadata, diff, and repo conventions here>"
```

## Step 3: Synthesize and Triage

Combine findings from both sources. For each finding, classify:

- **Real issue** — bugs, security holes, logic errors, design problems, correctness failures
- **False positive** — reviewer misread the code or missed context. Drop it.
- **Style nit** — formatting, naming, style. Drop it unless it causes genuine confusion.

Priority order: correctness > security > design > performance. Apply the staff engineer lens: is this a real problem, or is the reviewer inventing work? If both reviewers flag the same thing, it is almost certainly real. If only one flags it and the reasoning is weak, it is probably noise.

Only real issues survive triage.

## Step 4: Post Review to GitHub

Map each surviving finding to inline comments with severity tags:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  --method POST \
  --input - <<'JSON'
{
  "event": "COMMENT",
  "body": "Review summary here",
  "comments": [
    {"path": "file.py", "line": 42, "body": "**warning**: Description\n\nSuggested fix: ..."}
  ]
}
JSON
```

If findings cannot be mapped to specific lines, fall back to:

```bash
gh pr review <N> --comment --body "review body"
```

If the PR has no real issues, approve it:

```bash
gh pr review <N> --approve --body "Clean PR. No issues found."
```

Do not invent issues. Do not add "great work" filler. If it is clean, approve and move on.
