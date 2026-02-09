---
name: gh_cli
description: >
  GitHub CLI (gh) reference for non-obvious patterns. Use when interacting with
  GitHub repos, PRs, issues, releases, actions, or the API. Do NOT use for
  local git operations (use git directly).
allowed-tools: Bash(gh *), Bash(git *)
---

Non-obvious gh CLI patterns. For standard commands (`gh pr create`, `gh issue list`, etc.), use `gh` directly — no reference needed.

## Reading File Contents Without Cloning

```bash
gh api repos/OWNER/REPO/contents/PATH --jq '.content' | base64 -d
gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH --jq '.content' | base64 -d
gh api repos/OWNER/REPO/contents/DIR --jq '.[].name'
gh api repos/OWNER/REPO/git/blobs/SHA --jq '.content' | base64 -d  # >1MB files
```

## PR Comments (Not Available via `gh pr view`)

```bash
gh api repos/OWNER/REPO/pulls/123/comments   # review (diff) comments
gh api repos/OWNER/REPO/issues/123/comments   # general PR comments
```

## Useful API Patterns

```bash
gh api ENDPOINT --jq '.field'          # filter JSON
gh api ENDPOINT --paginate             # auto-paginate (default page size is 30)
gh api ENDPOINT --paginate --slurp     # paginate into single array
gh api ENDPOINT --cache 3600s          # cache response
gh api user --jq '.login'              # get current username
```

## Tips

- `--json FIELDS` on most commands gives structured output, pipe to `--jq`
- `-R OWNER/REPO` targets a different repo without cloning
- PR and issue numbers are interchangeable in the issues API
- Add scopes: `gh auth refresh -s scope1,scope2`
