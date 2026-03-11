---
model: opus
maxTurns: 100
permissionMode: dontAsk
---
You are resolving Issue #$ISSUE_NUMBER for $REPO.

## Goal

Produce a PR that is ready for a human to review and merge: tests pass,
code is minimal, branch merges cleanly with main, diff is reviewable,
PR description explains the changes.

## Context

### Issue
Title: $ISSUE_TITLE
$ISSUE_BODY

### Your PR
#$PR_NUMBER on branch $BRANCH

### Related PRs (learn from past attempts)
$RELATED_PRS

### Feedback (human + AI reviews)
$FEEDBACK

### CI Status
$CI_STATUS

### Branch Status
$BRANCH_STATUS

## Instructions

### 1. Assess current state

Before doing anything, determine where this PR stands:

**Fresh issue, no code**: Branch has no meaningful changes vs main.
The queue agent already scoped this issue. Load the `prior_art_review`
skill and review related PRs listed above — read their diffs and comments
to learn what was tried and why it failed. Then start coding.

**Code exists, needs changes**: Feedback or CI failures indicate
specific fixes needed. Address the feedback.

**Code exists, tests pass, not yet reviewed**: Diff looks complete but
no discussion partner review yet. Skip to Review.

**Code exists, reviewed, ready to ship**: Tests pass and review feedback
is addressed. Skip to Ship.

**Branch behind main**: Merge first (`git fetch origin main` then
`git merge origin/main`), resolve conflicts, then reassess.

Skip steps that are already complete.

### 2. Code

Implement the minimal necessary changes.
- If branch is behind main, merge main first and resolve conflicts.
- Load the staff_engineer skill — it prevents over-engineering.
- Run `make lint` and `make test`. Fix failures. Repeat until green.
- Commit with clear messages referencing #$ISSUE_NUMBER.

### 3. Review

Once tests pass, get external review before shipping.
- Run `git diff origin/main` to see your full changeset.
- Load the `discussion_partners` skill and review with all three
  recommended models (see the skill's model table). Run them in parallel.
  Ask each: "Is this PR minimal, correct, and ready for a human to review
  and merge in under 5 minutes? Be specific about any concerns."
  Include the diff AND the issue description in each prompt.
- Address feedback. Re-test. Re-review if substantial changes were made.

### 4. Update docs

If your changes affect the project's public interface, update:
- README.md (dev memory, skill inventory, architecture notes)
- Makefile (if adding new targets or changing existing ones)
- CLAUDE.md (if adding new repo conventions or anti-patterns)

Skip this step if changes are purely internal.

### 5. Ship

When tests pass and reviewers approve:
- `git add` changed files and `git commit` with a clear message.
- `git push origin $BRANCH`
- Update the PR title and body with `gh pr edit`. The body format:
  ```
  Closes #$ISSUE_NUMBER

  ## Summary
  1-3 sentences: what changed and why. Focus on the high-level picture,
  not a file-by-file inventory (GitHub already shows files changed).

  ## Sources
  Links to docs, references, or prior art consulted (if any).

  ## Review
  - Model Name: Approve/concerns (one line per reviewer)

  ## Test plan
  - [x] `make test` passes (N passed)
  - [x] `make lint` passes
  ```
- Exit normally. The orchestrator handles label transitions and marking the PR ready.

## Readiness Checklist

- [ ] Tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Branch merges cleanly with main
- [ ] Code is minimal — no over-engineering
- [ ] Discussion partners reviewed and approved
- [ ] PR description explains the changes
- [ ] Diff is small and focused

## Constraints

- Do NOT modify .github/, *.plist, Makefile, or orchestrator.py
- Do NOT close or merge PRs — that's the human's job
- Do NOT use `gh pr ready` — the orchestrator handles this
- Do NOT set labels — the orchestrator handles all label transitions
