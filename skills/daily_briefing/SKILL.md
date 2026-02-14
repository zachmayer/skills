---
name: daily_briefing
description: >
  Morning summary from memory, tasks, and vault. Use at the start of a work
  session, when the user says "daily briefing", "morning summary", "what's
  going on", or "catch me up". Do NOT use mid-session or for planning what
  to work on (use session_planner for that).
---

# Daily Briefing

Compile a morning summary so the user can start their day oriented.

This skill is a **read-only overview** — it surfaces what matters, it does not plan or execute. Use `session_planner` after the briefing to decide what to work on.

## Gather

Collect these in parallel (skip any that don't exist or error):

### 1. Memory

Read current memory state:

```bash
uv run --directory MEMORY_SKILL_DIR python scripts/memory.py read-current
```

Extract from overall memory:
- Active projects and their status
- Upcoming deadlines
- Outstanding TODOs
- Recent decisions or changes

Extract from today's/yesterday's daily notes:
- What happened in the last session
- Anything left unfinished

### 2. Git State

For each repo the user works in (check recent memory for active repos):

```bash
git status
git log --oneline -5
```

Note: uncommitted changes, unfinished branches, recent commits.

### 3. GitHub

```bash
gh pr list --author @me --state open
gh issue list --assignee @me --state open
```

Note: PRs awaiting review, PRs with review comments, assigned issues.

### 4. Obsidian TODOs

Search the vault for outstanding action items:

```bash
# Find TODOs and action items across the vault
```

Use Grep to search `$CLAUDE_OBSIDIAN_DIR` for patterns like `TODO`, `- [ ]`, `ASAP`, `deadline`.

### 5. Calendar Awareness

Check memory for any time-sensitive items mentioned (deadlines, meetings, appointments). The briefing is date-aware — flag anything due today or this week.

## Present

Output a single briefing in this format:

```
## Daily Briefing — <date>

### Urgent
- <anything due today or overdue, blockers, failing CI>

### Yesterday
- <1-3 bullet summary of last session's work>

### Active Work
- <open PRs, in-progress branches, uncommitted changes>
- <assigned issues>

### This Week
- <upcoming deadlines within 7 days>
- <scheduled events from memory>

### TODOs
- <top 5 outstanding action items from memory + vault, prioritized>

### FYI
- <recent changes or context worth knowing but not actionable today>
```

## Rules

- **Read-only.** Do not modify files, create branches, or take action.
- **Concise.** Each bullet is one line. No paragraphs. The briefing should fit on one screen.
- **Skip empty sections.** If there's nothing urgent, omit the Urgent section entirely.
- **Prioritize.** Surface the most important items first within each section. TODOs capped at 5.
- **Flag staleness.** If memory hasn't been aggregated recently, note it. If a TODO is weeks old, flag it.
- **Don't duplicate session_planner.** This skill says "here's what's going on." Session planner says "here's what to work on." The user runs this first, then optionally runs session_planner.
