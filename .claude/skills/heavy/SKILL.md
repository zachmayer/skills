---
name: heavy
description: >
  Parallel multi-territory analysis using 3-5 sub-agents that inspect different
  evidence and return a synthesized recommendation. Use WHEN the user says
  "/heavy", "research this in parallel across different code areas", or when
  the answer improves by splitting research across code paths, tests, docs,
  history, or external sources — multi-subsystem root-cause analysis,
  architecture review, cross-cutting investigations. Do NOT use for
  single-thread reasoning (use ultra-think), one external second opinion
  (use discussion-partners), simple lookups, or execution tasks (use melt
  or ralph-loop).
---

# Heavy Multi-Perspective Analysis

Use `/heavy` when the answer gets better if multiple sub-agents inspect different evidence before a synthesis step.

The point is **information diversity**, not personality cosplay. Do not ask five agents to read the same files and then pretend the output is deep because the tones are different.

Also apply these skills as needed:
- `ultra-think` for the synthesis step when cruxes are complex
- `staff-engineer` for engineering rigor in code-related analysis
- `discussion-partners` to bring in an external model perspective on unresolved cruxes
- `ask-questions` if the question itself is ambiguous — clarify before spawning agents

## 1. Triage

Classify the question before spawning agents.

| Mode | Use when | Expected output |
|---|---|---|
| Evaluation | The user is deciding whether to do something | Recommendation with tradeoffs |
| Implementation | The user already wants to do it and needs the best path | Concrete plan or design |

| Complexity | Signals | Agent count |
|---|---|---|
| Quick | Small bounded decision | 2-3 |
| Standard | Several dimensions, but contained | 3-4 |
| Deep | Architectural, strategic, or high-stakes | 4-5 |

Default to Standard.

State the result explicitly:

```text
TRIAGE: IMPLEMENTATION / STANDARD -> 4 agents
```

## 2. Design the Agent Roster

Every agent must have:

1. A **perspective** -- what lens they use
2. A **research territory** -- what files, docs, or data they inspect
3. A **concrete question** to answer

### Good Territories

- Code paths and call sites
- Tests, fixtures, and failure cases
- Docs, ADRs, and runbooks
- Git history and recent regressions
- External docs or recent web sources when freshness matters
- Product impact, performance risk, or operational burden

### Bad Territories

- "Take a different vibe"
- "Be more optimistic"
- "Same evidence but pretend to disagree"

Output the roster before launching:

```text
AGENT ROSTER:
1. [Perspective] -- Territory: [what to inspect] -- Question: [specific question]
2. [Perspective] -- Territory: [what to inspect] -- Question: [specific question]
...
```

## 3. Launch Parallel Discovery

Use the **Agent tool** to launch sub-agents in parallel. Each sub-agent prompt must be completely self-contained -- sub-agents have zero context from this conversation.

Each prompt should include:

- The exact question
- The agent's unique territory (specific files, directories, or search patterns)
- The evidence to inspect first
- The required output format

### Required Output Format for Sub-Agents

Tell each sub-agent to structure their response as:

```text
## Discoveries
[What they found in their territory]

## Position
[Their answer to their specific question]

## Evidence
[File paths, code snippets, data points supporting the position]

## Uncertainties
[What they could not determine from their territory alone]
```

### Rules

- Do not duplicate territories -- each agent must inspect different evidence
- Include one adversarial agent for non-trivial questions (assigned to find reasons the obvious answer is wrong)
- Launch all agents simultaneously -- do not serialize
- Maximum 5 parallel sub-agents to keep synthesis tractable

## 4. Synthesize

Your synthesis is not a stitched summary. Compress the agents' findings into:

```text
## Answer
[Direct answer to the user's question]

## What The Agents Agreed On
[Consensus findings across territories]

## Where They Disagreed
[Tensions and contradictions between agents' evidence]

## Cruxes That Matter
[The 1-3 factual questions whose answers would change the recommendation]

## Recommendation
[Clear recommendation with confidence level]

## Open Questions
[What remains unknown and how to resolve it]
```

Apply `ultra-think` for the synthesis when findings are complex or contradictory.

## 5. Resolve Cruxes

If one or two unresolved cruxes determine the answer, spawn targeted follow-up agents only for those cruxes. Do not rerun the entire analysis.

If a crux requires external knowledge, use `discussion-partners` to query another model.

## 6. Rules

- **Different evidence over different opinions.** The value is in what each agent finds, not what they believe.
- **Include a downside-focused agent** for strategic or architectural questions.
- **Stop when the answer is materially better** than a single-agent response, not when every angle is exhausted.
