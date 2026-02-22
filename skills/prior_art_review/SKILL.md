---
name: prior_art_review
description: >
  Review prior art (issues, PRs, comments) before acting on a GitHub item.
  Use before implementing an issue, reviewing a PR, or creating a new issue
  to prevent duplicate work and learn from history. Do NOT use for tasks
  unrelated to GitHub issue/PR workflows.
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

For each relevant match:
- **Issues**: read comments via `gh api "repos/OWNER/REPO/issues/N/comments"`
- **PRs**: read comments AND review the diff via `gh pr diff N --repo OWNER/REPO`

## For PR Reviews

Check recent merged and closed PRs to calibrate against repo standards:

```bash
gh pr list --repo OWNER/REPO --state merged --limit 5 --json number,title,url
gh pr list --repo OWNER/REPO --state closed --limit 5 --json number,title,url
```

Read diffs and comments on relevant matches to understand what gets approved, rejected, and common feedback themes.

## Interpreting State

Open vs closed means different things:

- **Open issue** -- work is pending. Don't duplicate; contribute to the existing one.
- **Closed issue (completed)** -- work was done. Understand what was built.
- **Closed issue (not completed)** -- understand why it was abandoned or rejected. If still relevant, reopen with a comment explaining what's different now.
- **Merged PR** -- code shipped. Understand the approach and build on it.
- **Unmerged/closed PR** -- attempt failed or was rejected. Read the diff and comments. Don't repeat the same mistakes.

## Output

After completing the review, summarize findings before proceeding:

```
PRIOR ART:
- [#N title] (state) -- what you learned
- [#N title] (state) -- what you learned
→ Proceeding with: [brief statement of how this informs your approach]
```
