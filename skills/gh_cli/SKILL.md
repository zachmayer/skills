---
name: gh_cli
description: >
  GitHub CLI (gh) reference for repos, PRs, issues, releases, actions, secrets,
  rulesets, and the raw API. Use WHEN interacting with GitHub: creating PRs,
  reviewing code, checking CI, reading repo contents, managing secrets/variables,
  or querying the API. Do NOT use for local git operations (use git directly).
allowed-tools: Bash(gh *), Bash(git *)
---

## Auth

```bash
gh auth status                    # check login state
gh auth status --show-token       # show token
gh auth login                     # interactive login
gh auth refresh -s SCOPE          # add scopes (e.g. project, admin:org)
```

## Repos

```bash
gh repo view OWNER/REPO                     # repo info
gh repo view OWNER/REPO --json name,description,defaultBranchRef
gh repo list OWNER --limit 50               # list repos
gh repo clone OWNER/REPO                    # clone
gh repo create NAME --private --clone       # create + clone
gh repo create NAME --public --source=. --push  # from existing dir
gh repo edit OWNER/REPO --description "..." # edit settings
gh repo fork OWNER/REPO --clone             # fork + clone
gh repo delete OWNER/REPO --yes             # delete (destructive!)
```

## Pull Requests

### Read

```bash
gh pr list                                  # list open PRs
gh pr list --state all --limit 20
gh pr view 123                              # view PR details
gh pr view 123 --json title,body,reviews,mergeable,statusCheckRollup
gh pr diff 123                              # view diff
gh pr checks 123                            # CI status
gh pr status                                # PRs related to current branch
```

### Write

```bash
# Create PR (use HEREDOC for body)
gh pr create --title "Title" --body "$(cat <<'EOF'
## Summary
- Change description

## Test plan
- [ ] Tests pass
EOF
)"

# Create from fork or specific branch
gh pr create --head user:branch --base main

# Other flags
gh pr create --draft                        # draft PR
gh pr create --fill                         # auto-fill from commits
gh pr create --reviewer user1,team/name     # request review
gh pr create --label bug,urgent             # add labels

# Merge
gh pr merge 123 --squash --delete-branch    # squash merge
gh pr merge 123 --rebase                    # rebase merge
gh pr merge 123 --auto --squash             # auto-merge when checks pass

# Review
gh pr review 123 --approve
gh pr review 123 --comment --body "LGTM"
gh pr review 123 --request-changes --body "Fix X"

# Other mutations
gh pr edit 123 --title "New title" --add-label fix
gh pr close 123
gh pr reopen 123
gh pr checkout 123                          # check out locally
```

### Read PR comments and review comments

```bash
gh api repos/OWNER/REPO/pulls/123/comments  # review (diff) comments
gh api repos/OWNER/REPO/issues/123/comments  # general PR comments
```

## Issues

```bash
# Read
gh issue list --limit 20
gh issue list --label bug --state open
gh issue view 456
gh issue status                             # issues assigned to you

# Write
gh issue create --title "Bug" --body "Description" --label bug
gh issue close 456
gh issue edit 456 --add-label fix
```

## Reading File Contents from a Repo

Use the contents API to read files without cloning. Content is base64 encoded.

```bash
# Single file (base64 decode)
gh api repos/OWNER/REPO/contents/PATH --jq '.content' | base64 -d

# File from a specific branch/ref
gh api repos/OWNER/REPO/contents/PATH?ref=BRANCH --jq '.content' | base64 -d

# List directory contents
gh api repos/OWNER/REPO/contents/DIR --jq '.[].name'

# Get file at a specific commit
gh api repos/OWNER/REPO/contents/PATH?ref=COMMIT_SHA --jq '.content' | base64 -d

# Large files (>1MB): use the git blob API
gh api repos/OWNER/REPO/git/blobs/SHA --jq '.content' | base64 -d
```

## Releases

```bash
gh release list
gh release view v1.0.0
gh release create v1.0.0 --generate-notes
gh release create v1.0.0 --notes "Release notes" ./dist/*.tar.gz
gh release download v1.0.0 --pattern '*.tar.gz'
gh release delete v1.0.0 --yes
```

## Actions (Workflow Runs)

```bash
gh run list --limit 10
gh run view 12345                           # run summary
gh run view 12345 --log                     # full logs
gh run view 12345 --log-failed              # only failed step logs
gh run watch 12345                          # live watch
gh run rerun 12345                          # rerun failed
gh workflow list
gh workflow view ci.yml
gh workflow run ci.yml --ref main           # trigger workflow
```

## Secrets and Variables

```bash
# Secrets (values never readable after set)
gh secret list
gh secret set MY_SECRET --body "value"
gh secret set MY_SECRET < file.txt
gh secret set MY_SECRET --env production    # environment-scoped
gh secret delete MY_SECRET

# Variables (readable)
gh variable list
gh variable get MY_VAR
gh variable set MY_VAR --body "value"
gh variable delete MY_VAR
```

## Rulesets and Branch Protection

```bash
gh ruleset list
gh ruleset view 123
gh ruleset check main                       # rules applying to branch

# View via API (more detail)
gh api repos/OWNER/REPO/rulesets
gh api repos/OWNER/REPO/rulesets/123
gh api repos/OWNER/REPO/rules/branches/main

# Update ruleset via API (PUT)
gh api repos/OWNER/REPO/rulesets/ID --method PUT --input rules.json

# Legacy branch protection
gh api repos/OWNER/REPO/branches/main/protection
```

## Raw API (gh api)

Default method is GET. Adding `-f`/`-F`/`--input` auto-switches to POST.

```bash
# GET (read)
gh api repos/OWNER/REPO
gh api repos/OWNER/REPO/pulls --jq '.[].title'
gh api repos/OWNER/REPO/actions/runs --jq '.workflow_runs[:5] | .[].status'
gh api user --jq '.login'
gh api /orgs/ORG/repos --paginate --jq '.[].full_name'

# POST/PUT/PATCH/DELETE (write -- explicit method required for safety)
gh api repos/OWNER/REPO/issues -f title="Bug" -f body="Details"
gh api repos/OWNER/REPO/issues/1/labels -f 'labels[]=bug'
gh api repos/OWNER/REPO/rulesets/ID --method PUT --input rules.json
gh api repos/OWNER/REPO/git/refs/heads/branch --method DELETE
```

### Useful API flags

```bash
--jq '.field'             # filter JSON with jq syntax
--paginate                # auto-paginate all pages
--paginate --slurp        # paginate into single JSON array
--template '{{.field}}'   # Go template formatting
--cache 3600s             # cache response
-i                        # include HTTP headers in output
```

## Search

```bash
gh search repos "topic:python language:python" --limit 10
gh search issues "label:bug repo:OWNER/REPO"
gh search prs "review:approved repo:OWNER/REPO"
gh search code "func main repo:OWNER/REPO"
gh search commits "fix author:USER"
```

## Labels

```bash
gh label list
gh label create "bug" --color FF0000 --description "Something broken"
gh label delete "old-label" --yes
```

## Tips

- Use `--json FIELDS` on most commands to get structured output, pipe to `--jq`
- Use `-R OWNER/REPO` to target a different repo without cloning
- Use `gh api --paginate` for endpoints returning lists (default page size is 30)
- PR and issue numbers are interchangeable in the issues API (PRs are issues)
- Environment secrets/variables need `--env NAME` flag
- Add scopes with `gh auth refresh -s scope1,scope2`
