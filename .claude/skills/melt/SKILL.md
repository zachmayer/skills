---
name: melt
description: >
  Full autonomous execution from triage to verified result. Takes a task, plans it,
  implements it, runs quality gates, verifies real behavior, and delivers (branch,
  commit, PR). Use WHEN the user says "/melt", "just do it", "go do this",
  "execute this end to end", "handle this autonomously", or gives a bounded task
  they want carried through to completion without back-and-forth. Do NOT use for
  multi-day feature development (use ralph-loop instead), pure analysis questions
  (use heavy instead), or tasks requiring ongoing iteration with human feedback.
  Melt is for single-shot execution: one request in, verified result out.
---

# Autonomous Execution With /melt

Use `/melt` when the user wants action, not a proposal. The job is to take a task from vague request to verified result.

This skill is for execution, not endless clarification. Make reasonable assumptions, move forward, and only ask once if blocked by missing credentials, missing target environment, or a risky irreversible choice.

Also apply these skills throughout execution:
- `ultra-think` for complex implementation decisions
- `staff-engineer` for engineering rigor, scope discipline, and debugging
- `mental-models` for structured reasoning -- OODA loop drives each phase
- `ask-questions` only if truly blocked -- prefer action over clarification

## Quick Start

```text
/melt fix the flaky login redirect
/melt add CSV export and open a PR
/melt refactor this service into smaller modules
/melt update the CI pipeline to cache dependencies
```

## Workflow

Print these labels as you go:

```text
[1/7] Activating execution mode
[2/7] Triaging complexity
[3/7] Planning the work
[4/7] Implementing changes
[5/7] Running quality gates
[6/7] Verifying real behavior
[7/7] Delivering the result
```

## 1. Activate

Ground yourself in the repo before touching anything:

- `git status` -- understand the current state, check for uncommitted work
- Read the nearest relevant docs (README, CLAUDE.md, CONTRIBUTING) before editing unfamiliar areas
- Identify whether the task should end in a branch/PR or is local-only
- If unrelated user changes exist, work around them -- never revert them unless explicitly asked

## 2. Triage Complexity

Classify the task before planning.

| Complexity | Signals | Execution style |
|---|---|---|
| Trivial | Small fix, rename, typo, one-file change | Direct implementation, no sub-agents |
| Standard | Clear feature or bugfix across a few files | Direct implementation with optional sub-agent for tests |
| Complex | Multiple subsystems, unclear approach, risky refactor | Plan first, then use Task tool for parallel sub-agents |
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
3. [what] -- [why]
-> Executing unless you redirect.
```

The plan should be concrete and execution-shaped:

- Inspect relevant files
- Implement targeted changes
- Run repo-native validation
- Verify real behavior
- Package delivery

Do not stop at the plan. The plan exists to drive execution.

For Complex/Deep tasks, use the **Task tool** to delegate bounded sub-tasks in parallel:

Good delegation:
- Test writing while you implement the feature
- README update while you refactor code
- Parallel edits in non-overlapping files

Bad delegation:
- Handing off the immediate blocker and then waiting
- Asking multiple agents to edit the same files

## 4. Implement

Implementation rules:

- Use Edit for surgical changes, Write only for new files
- Use Grep and Glob for search -- never guess at file locations
- Keep changes focused on the task -- no unsolicited cleanup
- Follow existing patterns in the codebase
- For git work, prefer a worktree when the current branch is occupied:

```bash
git worktree add ~/claude/worktrees/project-melt-fix main
```

## 5. Run Quality Gates

Run the checks the repo already expects. Look for these in order:

1. **Makefile targets**: `make test`, `make lint`, `make check`, `make ci`
2. **Package scripts**: check package.json scripts, pyproject.toml scripts
3. **Direct tools**: formatter, linter, type checker, test runner
4. **Build**: if the change affects build output

If the repo has no explicit tooling, run the closest credible checks. Do not claim validation you did not perform.

Do not ignore failures in touched areas. If unrelated failures exist, report them clearly but do not block delivery.

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

When delivery includes git:

- Create a feature branch (never commit to main)
- Write concise commit messages
- Push and open a PR via `gh pr create` when GitHub tooling is available

Your final handoff:

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

## Relationship to Other Skills

| Skill | When to use instead |
|---|---|
| `ralph-loop` | Multi-story feature development over hours with time-awareness and iteration |
| `heavy` | When the user needs analysis and perspectives, not execution |
| `orchestrate` | When the task is a DAG of independent work items needing coordination |
| `staff-engineer` | When the user wants code review or debugging guidance, not autonomous execution |
