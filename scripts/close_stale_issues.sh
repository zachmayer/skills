#!/usr/bin/env bash
# Close stale agent-task issues (Issue #97)
# Run: bash scripts/close_stale_issues.sh
# Requires: gh CLI authenticated with repo access

set -euo pipefail

REPO="zachmayer/skills"

echo "=== Closing DONE issues ==="

# #76 - Multi-repo support (done in PR #81, merged)
gh issue close 76 --repo "$REPO" \
  --comment "Completed. Multi-repo support implemented in PR #81 (merged). heartbeat.sh reads repos from ~/.claude/heartbeat-repos.conf."

# #47 - README reorganization (done in PR #35, merged)
gh issue close 47 --repo "$REPO" \
  --comment "Completed. README reorganized in PR #35 (merged). Skill inventory updated across multiple subsequent PRs."

echo "=== Closing VAGUE issues (no acceptance criteria) ==="

# #46 - Run skills stealer on ideas (vague, no AC)
gh issue close 46 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific skills to steal and clear AC if still wanted."

# #60 - Modal skill (one-liner, no AC)
gh issue close 60 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific use cases, API patterns, and clear AC if still wanted."

# #58 - Claude constitution skill (one-liner, no AC)
gh issue close 58 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific values/principles to encode and clear AC if still wanted."

# #55 - Checkpoint system skill (one-liner, no AC)
gh issue close 55 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific checkpoint behavior, intervals, and clear AC if still wanted."

# #54 - Complexity router skill (one-liner, no AC; PR #87 open)
gh issue close 54 --repo "$REPO" \
  --comment "Closing: original issue lacked acceptance criteria. PR #87 is open with implementation — merge the PR to complete this work."

# #53 - Blueprint tracker skill (one-liner, no AC)
gh issue close 53 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific tracking format, dependency model, and clear AC if still wanted."

# #52 - Agent coordinator skill (one-liner, no AC)
gh issue close 52 --repo "$REPO" \
  --comment "Closing: no acceptance criteria. Reopen with specific orchestration patterns, agent types, and clear AC if still wanted."

echo "=== Verification ==="
echo "Remaining open agent-task issues:"
gh issue list --repo "$REPO" --label agent-task --state open

echo ""
echo "Done. Verify that remaining issues all have clear acceptance criteria."
