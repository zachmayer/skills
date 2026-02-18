---
name: checkpoint
description: >
  Mandatory review at fixed intervals, attempt budgets. Use when running
  multi-step tasks, debugging loops, autonomous work, or any situation where
  you might spin your wheels without noticing. Do NOT use for simple
  single-step tasks, quick lookups, or trivial edits where a checkpoint
  adds no value.
---

# Checkpoint System

Enforce mandatory self-review at fixed intervals and cap attempts on any single approach. This prevents the two most common failure modes of autonomous agents: **tunnel vision** (grinding on a broken approach without stepping back) and **context exhaustion** (filling the context window with failed attempts before recognizing the pattern).

Also apply the `staff_engineer` skill for anti-sycophancy — checkpoints only work if you're honest with yourself at each one.

## Setup

At the start of any non-trivial task, declare your checkpoint parameters:

```
CHECKPOINT CONFIG:
- Interval: every [N] steps (default: 5)
- Attempt budget: [M] tries per approach (default: 3)
- Time limit: [T] minutes total (default: none)
- Escalation: [what happens when budget is exhausted]
```

**Choosing the interval:** Match the cadence to the task. Debugging? Every 3 attempts. Feature implementation? Every 5 files touched. Research? Every 10 minutes. The right interval is one where you'd want a colleague to tap you on the shoulder and ask "is this actually working?"

**Choosing the attempt budget:** How many times should you try essentially the same approach before concluding it won't work? For most tasks, 3 is right. For flaky tests, 2. For complex debugging, 5.

## The Checkpoint

When you hit a checkpoint (interval reached, attempt budget consumed, or time limit hit), STOP and run this review:

```
CHECKPOINT [N]:
- Progress: [what's been accomplished since last checkpoint]
- Approach: [what I've been doing]
- Working? [yes/no/partially — be honest]
- Attempts used: [X/M on current approach]
- Remaining budget: [attempts left, time left]
- Next action: [continue / adjust / pivot / escalate]
```

### Decision rules

| Signal | Action |
|--------|--------|
| Progress is clear, approach is working | **Continue** — reset attempt counter for the next sub-task |
| Progress is partial, approach seems right | **Adjust** — tweak the approach, keep the attempt counter |
| No progress after 2+ attempts | **Pivot** — try a fundamentally different approach, reset counter |
| Attempt budget exhausted, no progress | **Escalate** — ask the user, consult `discussion_partners`, or document the blocker and move on |
| Time limit hit | **Wrap up** — finish what you can, document state for next session |

### What "pivot" means

A pivot is not a tweak. It means:
- Different algorithm or strategy (not different parameters to the same one)
- Different tool (not the same tool with different flags)
- Different framing of the problem (step back and ask "am I solving the right problem?")

If you can describe your new attempt in the same sentence as the old one, it's an adjustment, not a pivot. Adjustments don't reset the attempt counter.

## Patterns

### Debugging

```
CHECKPOINT CONFIG:
- Interval: every 3 attempts
- Attempt budget: 3 per hypothesis
- Escalation: add logging/prints, then ask user
```

Each hypothesis gets 3 attempts. If the third attempt doesn't confirm or rule out the hypothesis, pivot to a new hypothesis. After 3 hypotheses (9 total attempts), escalate.

### Feature implementation

```
CHECKPOINT CONFIG:
- Interval: every 5 steps
- Attempt budget: 3 per approach
- Escalation: ask user for direction
```

Review after every 5 meaningful actions (file edits, test runs, etc.). If you've tried 3 approaches to the same sub-problem, stop and get input.

### Research / exploration

```
CHECKPOINT CONFIG:
- Interval: every 10 minutes
- Attempt budget: N/A
- Escalation: summarize findings and ask if direction is right
```

Time-based checkpoints for open-ended work. No attempt budget because exploration doesn't have "attempts" — but time-boxing prevents rabbit holes.

### Test fixing

```
CHECKPOINT CONFIG:
- Interval: every 2 test runs
- Attempt budget: 2 per fix approach
- Escalation: pivot strategy or ask user
```

Tight intervals because test-fix cycles should converge fast. If the same test fails twice with different fixes, the diagnosis is probably wrong.

## Anti-patterns

- **Checkpoint theater**: Going through the motions without honest assessment. If your checkpoint always says "continue", you're not being critical enough.
- **Budget inflation**: Increasing the attempt budget mid-task because you "feel close." The budget exists precisely for when you feel close but aren't. Stick to it.
- **Skipping checkpoints**: "I'll check at the next one." No. The checkpoint is mandatory. That's the point.
- **Counting tweaks as pivots**: Changing a parameter is not a new approach. A pivot means a structurally different strategy.
