---
name: heavy
description: >
  Multi-perspective analysis using 3-5 parallel sub-agents with separate research
  territories. The insight comes from information diversity — each agent greps
  different parts of the codebase — not opinion diversity. Use WHEN the user says
  "/heavy", "analyze this from multiple angles", "debate this decision", "think
  about this deeply from different perspectives", or when a question benefits from
  parallel evidence gathering across different parts of a codebase or domain.
  Do NOT use for simple questions, single-file analysis, quick lookups, or tasks
  that need execution rather than analysis (use melt or ralph-loop instead).
  Do NOT use when a single discussion-partners call suffices — heavy is for
  internal parallel research, not external model queries.
---

# Heavy Multi-Perspective Analysis

Use `/heavy` when the answer gets better if multiple sub-agents inspect different evidence before a synthesis step.

The point is **information diversity**, not personality cosplay. Do not ask five agents to read the same files and then pretend the output is deep because the tones are different.

Also apply these skills as needed:
- `ultra-think` for the synthesis step when cruxes are complex
- `staff-engineer` for engineering rigor in code-related analysis
- `discussion-partners` to bring in an external model perspective on unresolved cruxes
- `ask-questions` if the question itself is ambiguous — clarify before spawning agents

## Quick Start

```text
/heavy should we move this service to Go?
/heavy debate this architecture decision
/heavy why does this queue keep collapsing under load?
/heavy what are the tradeoffs of splitting this monolith?
```

## Workflow

Print these labels as you go:

```text
[1/6] Triaging question
[2/6] Designing the agent roster
[3/6] Launching parallel discovery
[4/6] Synthesizing findings
[5/6] Resolving open cruxes
[6/6] Delivering the final answer
```

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

Use the **Task tool** to launch sub-agents in parallel. Each sub-agent prompt must be completely self-contained -- sub-agents have zero context from this conversation.

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

Good follow-ups:
- "Check whether the bottleneck is actually Redis saturation or app-side serialization"
- "Verify whether this API limit changed recently"
- "Count the actual call sites for this interface to confirm migration scope"

If a crux requires external knowledge, use `discussion-partners` to query another model.

## 6. Rules

- **Different evidence over different opinions.** The value is in what each agent finds, not what they believe.
- **When freshness matters, use WebFetch or WebSearch** in sub-agent prompts for current sources.
- **When the question is about code, cite files and symbols.** Every claim should trace back to a file path and line range.
- **When the question is strategic, include at least one downside-focused agent** whose job is to find reasons the popular answer is wrong.
- **Stop when the answer is materially better than a single-agent response**, not when every possible angle is exhausted.

## Relationship to Other Skills

| Skill | When to use instead |
|---|---|
| `orchestrate` | When the task needs parallel *execution* (writing code, running tests), not parallel *analysis* |
| `discussion-partners` | When you want one external model's opinion, not internal multi-territory research |
| `ultra-think` | When the question needs deep single-thread reasoning, not broad evidence gathering |
| `ralph-loop` | When the task needs iterative implementation over time, not analysis |
