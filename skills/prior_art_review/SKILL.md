---
name: prior_art_review
description: >
  Search existing issues and PRs before acting on a task. Prevents duplicate
  work and learns from history. Use before implementing an issue, reviewing a PR,
  or any time you need to understand what was already tried. Do NOT use for tasks
  with no GitHub context.
---

## Prior Art Review

Before acting on any item, check what came before. This prevents duplicate work and learns from history.

### For Issues (before implementing)

Search for related issues and PRs:

```bash
# Related issues (open + closed)
gh issue list --repo OWNER/REPO --state all --search "KEYWORDS" --json number,title,state,url --limit 20
# Related PRs (merged + unmerged)
gh pr list --repo OWNER/REPO --state all --search "issue-N OR KEYWORDS" --json number,title,state,mergedAt,url --limit 20
```

For each relevant match, read its comments (`gh api "repos/OWNER/REPO/issues/N/comments"`). For PRs, also review the diff (`gh pr diff N`).

### For PR Reviews (before reviewing)

Check recent merged and closed PRs to calibrate against the repo's standards — what gets approved, what gets rejected, common feedback themes:

```bash
gh pr list --repo OWNER/REPO --state merged --limit 5 --json number,title,url
gh pr list --repo OWNER/REPO --state closed --limit 5 --json number,title,url
```

### Interpreting Results

Open vs closed means different things:

- **Open issue** — work is pending. Don't duplicate — contribute to the existing one.
- **Closed issue (completed)** — work was done. Understand what was built.
- **Closed issue (not completed)** — understand why it was abandoned or rejected. If still relevant, reopen with a comment explaining what's different.
- **Merged PR** — code shipped. Understand the approach and build on it.
- **Unmerged/closed PR** — attempt failed or was rejected. Read the diff and comments. Don't repeat the same mistakes.
