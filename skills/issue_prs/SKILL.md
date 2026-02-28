---
name: issue_prs
description: >
  Find all PRs linked to a GitHub issue and classify by state.
  Use when processing an issue that may have linked PRs (open, closed, or merged).
  Do NOT use for general PR searches unrelated to a specific issue.
---

## Discover linked PRs

**Primary query** — returns PRs with closing keywords (`Fixes #N`, `Closes #N`):

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    issue(number: NUMBER) {
      closedByPullRequestsReferences(first: 10) {
        nodes { number title state }
      }
    }
  }
}
'
```

**Fallback** — if primary returns empty but you suspect PRs exist, use the timeline to catch PRs that mention `#N` without closing keywords:

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    issue(number: NUMBER) {
      timelineItems(itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT], first: 50) {
        nodes {
          ... on CrossReferencedEvent { source { ... on PullRequest { number title state } } }
          ... on ConnectedEvent { subject { ... on PullRequest { number title state } } }
        }
      }
    }
  }
}
'
```

Replace OWNER, REPO, and NUMBER with actual values. Deduplicate by PR number.

## Classify results

- **OPEN** — active work
- **CLOSED** — failed/abandoned attempt (context only)
- **MERGED** — completed (issue may already be resolved)

Ignore empty `source`/`subject` objects (non-PR cross-references).

## Selected PR convention

When the lead agent selects a PR, it posts a machine-readable comment on the **issue**:

```
<!-- fsm:selected_pr=PR_NUMBER -->
[Lead Review] Reviewing PR #PR_NUMBER. [summary]
```

Dev agent checks for this comment before discovering PRs. If present, use that PR directly.
