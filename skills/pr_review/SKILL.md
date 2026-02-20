---
name: pr_review
description: >
  Review a GitHub PR for bugs, security issues, and design problems.
  Use when reviewing PRs, getting a second opinion on code changes, or
  before merging. Do NOT use for local code review without a PR.
allowed-tools: Bash(gh pr *), Bash(gh api *), Bash(git diff *), Bash(git log *)
---

Review a GitHub PR. Two modes: **quick** (subagent, default) or **thorough** (external model via `discussion_partners`).

## Step 1: Fetch Context

The reviewer has zero context — you MUST fetch everything before reviewing.

Given a PR reference (number, `#123`, `owner/repo#123`, or full URL), run:

```bash
gh pr view <N> [--repo owner/repo] --json title,body,author,state,baseRefName,headRefName,files,url
gh pr diff <N> [--repo owner/repo]
```

Also read `CLAUDE.md` and any relevant project docs from the repo so the reviewer understands repo conventions.

## Step 2: Review

Choose a mode based on the PR's complexity and the user's request.

### Quick Review (default)

Launch a **Task tool subagent** (`general-purpose`) with all the context from Step 1 and this system prompt:

> You are an expert code reviewer. Review the PR diff and report findings.
> Rules:
> - Focus on correctness, bugs, security issues, and design problems
> - Skip style nits, formatting, and naming unless they cause confusion
> - Each finding must reference a specific file and line/hunk
> - Rate severity: critical / warning / note
> - If the code looks good, say so briefly — don't invent issues
> - Be direct. No filler.

Ask the subagent to review for real issues — bugs, security problems, logic errors, design concerns — and format each finding with severity, location, issue, and suggestion.

### Thorough Review

Use the `discussion_partners` skill to send the context to an external model. Include the same system prompt as above using the `-s` flag, and pass the PR context plus review instructions as the question.

Use thorough mode when:
- The PR is large or touches critical code
- Design decisions need outside perspective
- The user explicitly requests a thorough or external review

## Step 3: Triage

Not every finding is actionable. Classify each as:

- **Real issue** — fix it
- **False positive** — skip (explain why if non-obvious)
- **Style nit** — skip unless it causes confusion

Implement fixes for real issues. Don't blindly apply every suggestion.
