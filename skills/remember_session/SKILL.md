---
name: remember_session
description: >
  Review the current session and persist what matters to the obsidian vault.
  Use at the end of a work session, when the user says "remember this session",
  "take notes", or "save what we did". Do NOT use mid-session.
allowed-tools: Bash(uv run *), Bash(git *), Read, Write, Glob, Grep
---

End-of-session ritual. Review what happened, persist what matters, aggregate.

## Steps

### 1. Review the session

Scan the full conversation. Identify:
- **What was done**: features built, bugs fixed, decisions made, files changed
- **What was learned**: new tools, patterns, preferences, corrections
- **What changed**: facts about the user, project, or environment that updated
- **What's pending**: TODOs, deferred work, open questions

### 2. Read today's existing notes

Before writing anything, read today's daily file to see what's already been saved:

```bash
uv run --directory MEMORY_SKILL_DIR python scripts/memory.py read-day
```

Only write notes for topics NOT already captured. Skip duplicates.

### 3. Save new daily notes

Use the `hierarchical_memory` skill to save timestamped notes to today's daily file:

```bash
uv run --directory MEMORY_SKILL_DIR python scripts/memory.py note "NOTE_TEXT"
```

Save one note per distinct topic that isn't already in today's file. Include:
- Completed work (prefix with `DONE:`)
- Decisions and their rationale
- New preferences or corrections the user made
- Remaining TODOs (prefix with `TODO:`)
- Facts that changed (new job, new tool, moved repo, etc.)

Be specific. "Updated auth" is useless. "Replaced JWT middleware with session cookies because latency was too high on mobile" is useful.

Use `[[wiki-links]]` to connect related notes. Link to existing obsidian notes by filename (without `.md`). For example: `See [[authentication-architecture]]` or `Related to [[2026-02-08]]`.

### 4. Save big-picture items to obsidian notes

If the session produced anything worth finding later — a new project, an architectural decision, a research finding, a personal milestone — create or update a note in the obsidian vault using the `obsidian` skill.

Daily work goes to `memory/` subdirectory via hierarchical_memory. Durable knowledge goes to `knowledge_graph/` topic notes in the vault.

### 5. Aggregate memory

If any `note` outputs showed stale aggregations (e.g. `Aggregation stale: 2026-02 CREATE, overall UPDATE`), aggregate. If all notes said `Aggregation: up to date`, skip this step.

There is no CLI command for aggregation — it requires LLM summarization. For each stale month, launch a Task tool sub-agent with this prompt:

> Read all daily notes for YYYY-MM in `$CLAUDE_OBSIDIAN_DIR/memory/` (files matching `YYYY-MM-*.md`). Read the existing monthly summary at `$CLAUDE_OBSIDIAN_DIR/memory/YYYY-MM.md` if it exists. Write an updated monthly summary that incorporates the new daily notes. Organize by theme, not by date. Drop noise. Tag themes with `#topic` tags. Include `[[wiki-links]]` to related vault notes. Keep it concise.

If `status` also shows overall needs UPDATE, launch a second sub-agent after monthly aggregation:

> Read all monthly summaries in `$CLAUDE_OBSIDIAN_DIR/memory/` chronologically. Write `$CLAUDE_OBSIDIAN_DIR/memory/overall_memory.md` as a current-state working memory. Facts use last-write-wins. Compress events to milestones. The result should read like a living profile, not a changelog.

### 6. Commit and push

Everything is in the obsidian vault now — one commit covers both memory and notes:

```bash
git -C $CLAUDE_OBSIDIAN_DIR add -A && git -C $CLAUDE_OBSIDIAN_DIR commit -m "session update" && git -C $CLAUDE_OBSIDIAN_DIR push
```
