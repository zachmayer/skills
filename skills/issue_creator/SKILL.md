---
name: issue_creator
description: >
  Create well-specified GitHub issues from Agent Goals. Use when the heartbeat
  enters triage mode (no open issues or PRs need work) and the triage cooldown
  has expired. Do NOT use for interactive work, one-time tasks, or when issues
  already exist in the queue.
---

# Issue Creator

Prompt-only skill for generating well-specified GitHub issues when the work queue is empty. This is triage mode — planning only, no code modifications.

## Protocol

### 1. Read direction

Load the Agent Goals note from the obsidian vault:

```
$CLAUDE_OBSIDIAN_DIR/knowledge_graph/Technical/Agent Goals.md
```

Only create issues that advance **Active Goals**. Never create issues for **Not Now** items.

### 2. Gather context

- Read hierarchical memory (overall + recent daily) for context on what's been done
- Check the repo's README.md for roadmap and lessons learned
- Scan `skills/` for existing patterns and gaps

### 3. Prior art review

Before creating any issue, search for duplicates and prior attempts:

```bash
# Related issues (open + closed)
gh issue list --repo OWNER/REPO --state all --search "KEYWORDS" --json number,title,state,url --limit 20

# Related PRs (merged + unmerged)
gh pr list --repo OWNER/REPO --state all --search "KEYWORDS" --json number,title,state,mergedAt,url --limit 20
```

For each relevant match, read its comments. For PRs, also review the diff.

**Interpret state correctly:**
- Open issue → don't duplicate, contribute to existing one
- Closed issue (completed) → understand what was built
- Closed issue (not completed) → understand why abandoned. If still relevant, reopen with comment explaining what's different
- Merged PR → code shipped, understand the approach
- Unmerged/closed PR → attempt failed. Read diff and comments. Don't repeat same mistakes

### 4. Create issues

Create **at most 2 issues** per triage session. Each issue must have:

- **Clear title** — specific and actionable (not vague like "improve X")
- **Acceptance criteria** — agent can self-verify completion
- **`agent-task` label** — so the heartbeat picks it up
- **Completable in ~30 minutes** — one heartbeat cycle

```bash
gh issue create --repo OWNER/REPO \
  --title "Short, specific title" \
  --label agent-task \
  --body "Description with acceptance criteria"
```

### 5. Constraints

- **No code modifications.** Triage is planning only.
- **Don't duplicate.** If an open issue already covers the work, skip it.
- **Prefer data/research tasks** over infrastructure (per Agent Goals principles).
- **Respect cooldown.** The heartbeat runner enforces a 6-hour cooldown between triage sessions.
