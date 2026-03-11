---
model: opus
maxTurns: 100
permissionMode: dontAsk
---
You are scoping Issue #$ISSUE_NUMBER for $REPO.

## Issue
Title: $ISSUE_TITLE
$ISSUE_BODY

## Related PRs
$RELATED_PRS

## Task
Assess whether this issue is actionable:
1. Are requirements clear and specific enough to code?
2. Can you identify the specific files to modify?
3. Does it fit in one PR?

If YES — draft an execution plan as a comment on the issue:
- `gh issue comment $ISSUE_NUMBER --repo $REPO --body "your plan"`
- List specific files to modify and acceptance criteria
- Write: `echo actionable > $RESULT_FILE`

If NO — post your questions as a comment:
- `gh issue comment $ISSUE_NUMBER --repo $REPO --body "your questions"`
- Write: `echo blocked > $RESULT_FILE`
- The orchestrator will remove labels and wait for the human to answer.
