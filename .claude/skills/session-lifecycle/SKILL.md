---
name: session-lifecycle
description: >
  Manages a work session: orient or re-orient, plan, and close out. Use when the
  user is starting the day, returning after a break, or ending a session. Triggers:
  "daily briefing", "morning summary", "what's going on", "catch me up", "start of
  day", "what did I miss", "status update", "what should I work on", "plan my
  session", "what's next", "what should I focus on", "let's get started",
  "remember this session", "save what we did", "wrap up", "end of session", or
  "I'm back, what happened". Covers three phases: orient (what happened?), plan
  (what to work on?), persist the session as a whole (save what we did). Do NOT use
  for mid-session task execution, casual questions, single-note capture, or
  reminders — those go to knowledge-system even if the user says "save" or
  "remember".
allowed-tools: Bash(uv run *), Bash(git *), Bash(gh *), Read, Write, Glob, Grep
---

Session lifecycle in three phases: orient, plan, persist.

## Quick Lookup

| Timing | Need | Reference |
|--------|------|-----------|
| Start of session | Morning summary, "catch me up", "what's going on" | [daily-briefing.md](daily-briefing.md) |
| After orientation | "What should I work on", "plan my session" | [session-planner.md](session-planner.md) |
| End of session | "Wrap up", "remember this session", "save what we did" | [remember-session.md](remember-session.md) |

## Typical Flow

1. **Orient** — Read [daily-briefing.md](daily-briefing.md) to compile a morning summary from memory, git state, GitHub, and vault TODOs
2. **Plan** — Read [session-planner.md](session-planner.md) to propose a prioritized task list (3 tasks max, scaled to time budget)
3. *...user works...*
4. **Persist** — Read [remember-session.md](remember-session.md) to save completed work, decisions, learnings, and TODOs to the vault

Each phase is independent — the user can invoke any phase alone. "Daily briefing" doesn't require planning afterward. "Wrap up" works even without a briefing.

## Related Skills

- **knowledge-system** — The underlying storage that remember-session writes to (memory tiers, obsidian vault)
- **ralph-loop** — For executing the plan produced by session-planner
