---
name: mental-models
description: >
  Apply mental models to reason about problems, decisions, and systems.
  Use when making architectural decisions, debugging complex issues, evaluating
  trade-offs, or when the user asks for a structured way to think about something.
  Do NOT use for straightforward implementation tasks with clear requirements.
---

When analyzing the problem, select and apply the most relevant mental models from this toolkit:

## Decision Making

**Inversion** - Instead of asking "how do I succeed?", ask "what would guarantee failure?" and avoid those things.

**Second-Order Thinking** - Ask "and then what?" at least twice. First-order: "This speeds up the build." Second-order: "Developers skip tests because the build is fast enough without them." Third-order: "Bug rate increases."

**Reversibility** - Is this decision easily reversible? If yes, move fast. If no, slow down and invest in getting it right. Two-way doors vs. one-way doors.

**Opportunity Cost** - What are you NOT doing by choosing this? Every yes is a no to something else.

## Systems Thinking

**Bottleneck Analysis** - The system is only as fast as its slowest component. Find the constraint before optimizing anything else.

**Feedback Loops** - Identify reinforcing loops (growth/collapse) and balancing loops (stability). Most bugs in complex systems are feedback loops you didn't see.

**Map vs. Territory** - Your model of the system is not the system. When the model disagrees with reality, update the model.

**Emergence** - Simple rules produce complex behavior. Look for the simple rules underneath complex systems.

## Problem Solving

**First Principles** - Decompose the problem to its fundamental truths. Reason up from there instead of reasoning by analogy.

**Occam's Razor** - The simplest explanation that fits the facts is usually correct. Don't add complexity until simple explanations fail.

**Pareto Principle** - 80% of the effect comes from 20% of the causes. Find the 20% before optimizing the rest.

**Pre-Mortem** - Imagine the project failed. What went wrong? Fix those things now.

## Application

When applying a model:
1. Name the model you're using and why
2. Walk through the reasoning step by step
3. State what the model suggests
4. Note where the model might mislead (every model has limits)
