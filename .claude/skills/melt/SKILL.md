---
name: melt
description: >
  Single-shot end-to-end execution for one bounded task: inspect context,
  plan briefly, implement, validate, verify real behavior, and deliver.
  Use WHEN the user says "/melt", "execute this end to end", "take this
  through to completion", or explicitly wants one task carried to a verified
  result with minimal back-and-forth. Do NOT use for multi-story feature
  development (use ralph-loop), parallel DAG coordination (use orchestrate),
  pure analysis (use heavy), or open-ended autonomous sessions. Melt is
  single-shot: one request in, verified result out.
---

# Autonomous Execution With /melt

Use `/melt` when the user wants action, not a proposal. The job is to take a task from vague request to verified result.

This skill is for execution, not endless clarification. Make reasonable assumptions, move forward, and only ask once if blocked by missing credentials, missing target environment, or a risky irreversible choice.

Also apply these skills throughout execution:
- `ultra-think` for complex implementation decisions
- `staff-engineer` for engineering rigor, scope discipline, and debugging
- `mental-models` for structured reasoning -- OODA loop drives each phase
- `ask-questions` only if truly blocked -- prefer action over clarification

Print the current step as you work through each phase.

## 1. Activate

Ground yourself before touching anything: check `git status`, read the nearest relevant docs (README, CLAUDE.md), and identify whether the task ends in a PR or is local-only.

## 2. Triage

Classify the task before planning.

| Complexity | Signals | Execution style |
|---|---|---|
| Trivial | Small fix, rename, typo, one-file change | Direct implementation, no sub-agents |
| Standard | Clear feature or bugfix across a few files | Direct implementation with optional sub-agent for tests |
| Complex | Multiple subsystems, unclear approach, risky refactor | Plan first, then use Agent tool for parallel sub-agents |
| Deep | Cross-cutting architecture or high-stakes migration | Heavy planning, worker split across sub-agents |

Default to Standard.

State it explicitly:

```text
TRIAGE: STANDARD -> direct implementation + test sub-agent
```

## 3. Plan

For anything beyond Trivial, state the plan before executing:

```text
PLAN:
1. [what] -- [why]
2. [what] -- [why]
-> Executing unless you redirect.
```

Do not stop at the plan. The plan drives execution.

For Complex/Deep tasks, use the **Agent tool** to delegate bounded sub-tasks in parallel:

- Good: test writing while implementing, README update while refactoring, parallel edits in non-overlapping files
- Bad: handing off the immediate blocker and waiting, multiple agents editing the same files

## 4. Implement

Keep changes focused on the task. Follow existing patterns in the codebase.

## 5. Run Quality Gates

Run the repo's existing checks before declaring done. Do not claim validation you did not perform.

## 6. Verify Real Behavior

At least one check must be behavior-based, not just "exit code 0":

| Change type | Verification |
|---|---|
| Web UI | Run the browser harness or inspect rendered output |
| API | Call the endpoint and check status + response body |
| CLI | Run the command with real arguments and inspect output |
| Library | Write or run a consumer example |
| Config/infra | Validate the config parses and the service starts |
| Docs | Render or inspect the final artifact |

If verification is impossible in the current environment (e.g., no staging server), say so explicitly. Do not pretend you verified something you could not.

## 7. Deliver

Create a feature branch (never commit to main). Push and open a PR via `gh pr create`.

Final handoff:

```text
DONE:
- What changed: [summary]
- What I ran: [quality gates executed]
- What I verified: [behavior checks performed]
- Residual risk: [anything the user should watch for]
```

## Rules

- **Prefer action over clarification loops.** Make reasonable assumptions and move forward.
- **Do not stop after analysis when code should be written.** The user asked for execution.
- **Do not claim verification you did not perform.** Honest gaps beat dishonest claims.
- **Do not revert unrelated user changes.** Work around them.
- **Use sub-agents to accelerate, not to avoid ownership.** You own the result.
- **One shot, not a loop.** Melt handles a single bounded task end-to-end. For multi-story feature development over hours, use `ralph-loop` instead.
