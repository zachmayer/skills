---
name: pr-review
description: >
  Reviews a GitHub pull request by running discussion-partners on the diff
  in parallel, then posting the result to GitHub. Use when the user says
  "review this PR", "check this pull request", "review PR #123", "is this
  PR ready to merge", or provides a GitHub PR URL. Also use before merging
  any PR. Do NOT use for local code review without a PR or for reviewing
  uncommitted changes.
allowed-tools: Bash(gh pr *), Bash(git diff *), Bash(git log *), Bash(uv run *), Task, Write
---

Thin wrapper around `discussion-partners`. That skill handles the parallel
multi-model review; this one stages the PR context and posts the result.

## 1. Fetch PR context

```bash
gh pr view <N> [--repo owner/repo] --json title,body,author,baseRefName,headRefName,files,url
gh pr diff <N> [--repo owner/repo]
```

Also read `CLAUDE.md` for repo conventions.

## 2. Run discussion-partners

Pass PR metadata + full diff + repo conventions as shared context. Invoke
`discussion-partners` in its default config. Framing: review for correctness,
security, design; skip style nits; LGTM is fine.

## 3. Triage and post

Drop false positives and style nits. Priority: correctness > security > design
> performance. If all reviewers flag the same thing, it's real.

```bash
gh pr review <N> --comment --body "..."   # issues found
gh pr review <N> --approve --body "..."   # clean
```

Don't invent issues. Don't pad with filler.
