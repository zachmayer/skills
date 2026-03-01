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

### Prior PRs (learn from past attempts)
$PRIOR_PRS

### Human Feedback
$HUMAN_FEEDBACK

### CI Status
$CI_STATUS

### Branch Status
$BRANCH_STATUS

## Instructions

### 1. Assess current state

Before doing anything, determine where this PR stands:

**Fresh issue, no code**: Branch has no meaningful changes vs main.
Start at Scope.

**Code exists, needs changes**: Human feedback or CI failures indicate
specific fixes needed. Start at Code, addressing the feedback.

**Code exists, tests pass, not yet reviewed**: Diff looks complete but
no discussion partner review yet. Start at Review.

**Code exists, reviewed, ready to ship**: Tests pass and review feedback
is addressed. Start at Ship.

**Branch behind main**: Merge first (`git fetch origin main` then
`git merge origin/main`), resolve conflicts, then reassess.

Skip steps that are already complete.

### 2. Scope

Before writing any code, draft an execution plan:
- List the specific files you will modify or create.
- List the acceptance criteria (what "done" looks like).
- If you cannot identify exact files based on the repo, or if requirements
  are vague, too large for one PR, or you have questions:
  - Post your plan + questions as a comment on Issue #$ISSUE_NUMBER
    (`gh issue comment $ISSUE_NUMBER --repo $REPO --body "your plan and questions"`)
  - Transition: `gh issue edit $ISSUE_NUMBER --repo $REPO --add-label ai:human --remove-label ai:coding`
  - Stop. Do NOT proceed with ambiguous requirements.

If the plan is clear and fits in one PR, proceed.

### 3. Code

Implement the minimal necessary changes.
- If branch is behind main, merge main first and resolve conflicts.
- Load the staff_engineer skill — it prevents over-engineering.
- Run `make lint` and `make test` (if the repo has these targets).
  Fix failures. Repeat until green (max 3 attempts per target — if
  still failing, push the code, comment the error, and set ai:human).
- Commit with clear messages referencing #$ISSUE_NUMBER.

### 4. Review

Once tests pass, get external review before shipping.
- Run `git diff origin/main` to see your full changeset.
- Send the diff AND the issue description to discussion_partners.
  Ask: "Is this PR minimal, correct, and ready for a human to review
  and merge in under 5 minutes? Be specific about any concerns."
- Get reviews from at least 2 models (GPT-5.2 and Gemini).
- Address feedback. Re-test. Re-review if substantial changes were made.

### 5. Update docs

If your changes affect the project's public interface, update:
- README.md (dev memory, skill inventory, architecture notes)
- Makefile (if adding new targets or changing existing ones)
- CLAUDE.md (if adding new repo conventions or anti-patterns)

Skip this step if changes are purely internal.

### 6. Ship

When tests pass and reviewers approve:
- `git add` changed files and `git commit` with a clear message.
- `git push origin $BRANCH`
- Update the PR: `gh pr edit $PR_NUMBER --repo $REPO --title "..." --body "..."`
  Include what changed, why, and which reviewers approved.
- Transition: `gh issue edit $ISSUE_NUMBER --repo $REPO --add-label ai:human --remove-label ai:coding`
- The orchestrator will mark the PR ready for review after you finish.

## Readiness Checklist

- [ ] Tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Branch merges cleanly with main
- [ ] Code is minimal — no over-engineering
- [ ] Discussion partners reviewed and approved
- [ ] PR description explains the changes
- [ ] Diff is small and focused

## Constraints

- Do NOT modify .github/, *.plist, or orchestrator.py
- Do NOT close or merge PRs — that's the human's job
- Do NOT use `gh pr ready` — the orchestrator handles this
