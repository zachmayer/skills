---
name: prior-art-review
description: >
  Searches existing GitHub issues, PRs, and their comments before acting on a
  task. Prevents duplicate work, learns from failed attempts, and calibrates
  against repo standards. Use when implementing an issue, reviewing a PR,
  starting work on a feature, or when the user says "check what's been tried",
  "any related issues", "has this been done before", or "search prior PRs".
  Do NOT use for tasks with no GitHub context or repos without issue tracking.
allowed-tools: Bash(gh issue list *), Bash(gh issue view *), Bash(gh pr list *), Bash(gh pr view *), Bash(gh pr diff *), Bash(gh api *)
---

Before acting on any GitHub item, check what came before. This prevents duplicate work and learns from history.

## For Issues

Search for related issues and PRs across all states:

```bash
# Related issues (open + closed)
gh issue list --repo OWNER/REPO --state all --search "KEYWORDS" --json number,title,state,url --limit 20
# Related PRs (merged + unmerged)
gh pr list --repo OWNER/REPO --state all --search "issue-N OR KEYWORDS" --json number,title,state,mergedAt,url --limit 20
```

For each relevant match, read its comments (`gh api "repos/OWNER/REPO/issues/N/comments"`). For PRs, also review the diff (`gh pr diff N`).

## For PR Reviews

Check recent merged and closed PRs to calibrate against the repo's standards — what gets approved, what gets rejected, common feedback themes:

```bash
gh pr list --repo OWNER/REPO --state merged --limit 5 --json number,title,url
gh pr list --repo OWNER/REPO --state closed --limit 5 --json number,title,url
```

## Interpreting Results

Open vs closed means different things:

- **Open issue** — work is pending. Don't duplicate — contribute to the existing one.
- **Closed issue (completed)** — work was done. Understand what was built.
- **Closed issue (not completed)** — understand why it was abandoned or rejected. If still relevant, reopen with a comment explaining what's different.
- **Merged PR** — code shipped. Understand the approach and build on it.
- **Unmerged/closed PR** — attempt failed or was rejected. Read the diff and comments. Don't repeat the same mistakes.

## Output

After reviewing, summarize findings in this format:

```
PRIOR ART SUMMARY
- Related issues: #N (open/closed), #M (closed — completed)
- Related PRs: #X (merged), #Y (closed — rejected: reason)
- Key learnings: what shipped, what failed, what to avoid
- Recommendation: proceed / contribute to #N / reopen #M
```
