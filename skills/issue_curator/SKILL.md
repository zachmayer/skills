---
name: issue_curator
description: >
  Review and curate GitHub issues: merge duplicates, close bad ideas, improve
  descriptions, and reopen relevant closed issues. Use when maintaining issue
  quality across a repo, during heartbeat triage, or when issue lists have grown
  stale. Do NOT use for creating new issues or for implementation work.
---

Curate a repo's GitHub issues to keep the backlog healthy. Curation before creation — clean up what exists before proposing new work.

## Process

### 1. Gather all issues

Fetch open and closed issues. Use `gh api` to search across states:

```bash
# All open issues
gh api "repos/OWNER/REPO/issues?state=open&per_page=100" --jq '[.[] | select(.pull_request == null) | {number, title, body, state, labels: [.labels[].name]}]'

# Recently closed issues (last 90 days)
gh api "repos/OWNER/REPO/issues?state=closed&since=$(date -u -v-90d +%Y-%m-%dT%H:%M:%SZ)&per_page=100" --jq '[.[] | select(.pull_request == null) | {number, title, body, state, labels: [.labels[].name]}]'
```

### 2. Identify duplicates

Group issues by theme. Two issues are duplicates if resolving one would resolve the other. When found:

1. Pick the better-specified issue as the survivor
2. Comment on the duplicate: "Duplicate of #N. Closing in favor of the better-specified issue."
3. Close the duplicate with `gh issue close`
4. Comment on the survivor linking the duplicate for context

### 3. Close issues that won't work

An issue should be closed if:
- Research or prior PR attempts revealed it's infeasible
- The underlying problem was solved a different way
- The approach described is fundamentally flawed
- It depends on blocked prerequisites with no path forward

When closing, comment with a clear explanation of WHY it won't work. Reference specific evidence (PRs, commits, external constraints). Never close without explanation.

### 4. Reopen relevant closed issues

A closed issue should be reopened if:
- The original reason for closing no longer applies
- New capabilities or context make it feasible now
- It was closed as a duplicate but the survivor was also closed without resolution

When reopening, comment explaining what changed and why it's worth revisiting.

### 5. Improve issue descriptions

For issues that survive curation, improve them if:
- The title is vague (rewrite to be specific and actionable)
- Acceptance criteria are missing (add them via comment)
- The body has typos or unclear language (edit via `gh api` PATCH)
- Dependencies aren't documented (add blocking/blocked-by references)

Do NOT rewrite issues that are already clear. Only touch what needs improvement.

### 6. Report

After curation, summarize what you did:
- Issues closed as duplicates (with survivor references)
- Issues closed as infeasible (with reasons)
- Issues reopened (with justification)
- Issues improved (with what changed)
- Remaining open issue count

## Constraints

- **At most 5 actions per session.** Curation is sensitive — don't mass-close.
- **Always explain closures.** A comment is required before closing.
- **Preserve intent.** When editing issue descriptions, keep the original author's intent. Add clarity, don't change direction.
- **No code changes.** Curation is planning, not implementation.
