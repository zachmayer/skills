---
name: llm-judge
description: >
  Evaluates AI outputs using LLM-as-judge with binary pass/fail scoring.
  Use when the user says "evaluate", "judge", "score outputs", "build evals",
  "compare prompt variants", "grade responses", "quality check", or wants
  to assess AI-generated content systematically. Also use when building
  automated evaluation pipelines or calibrating output quality.
  Do NOT use for checks expressible as code assertions (JSON validity,
  regex match, schema conformance).
allowed-tools: Bash(uv run *)
---

Evaluate AI outputs using structured LLM-as-judge methodology.

## Core Principles

1. **Binary pass/fail only** — no 1-5 scales. Use multiple independent binary checks for granularity.
2. **Every judgment needs a critique** — explain WHY with specific evidence.
3. **Narrow scope per judge** — one specific failure mode each. Not "is this good?" but "does this hallucinate facts not in the source material?"
4. **Code checks first** — if expressible as if/else, use code. Reserve LLM judges for subjective qualities.
5. **Criteria drift is normal** — draft criteria, review outputs, revise. Iterate.

## Building a Judge

### 1. Define the criterion

One narrow, specific failure mode:
- Bad: "Is the response helpful?"
- Good: "Does the response answer the user's specific question without introducing information not present in the provided context?"

### 2. Write the judge prompt

Use the `discussion-partners` skill to send the judge prompt to an external model:

Write the judge prompt to a file, then pass with `--file`:

```bash
# Write judge prompt to scratch file, then call discussion-partners
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/judge-prompt.txt
```

### 3. Calibrate with examples

Include 2-3 examples (both pass and fail) in the judge prompt. Draw from real outputs, not synthetic ones.

### 4. Validate alignment

Run the judge on a sample where you know the correct answer. Check:
- True positive rate (catches real failures)
- True negative rate (doesn't flag good outputs)

Target >90% on both. If not, refine the criterion or add examples.

## When Another Skill Calls This

Other skills (like `prompt-evolution`) can use this pattern by:
1. Defining their specific criterion
2. Launching a sub-agent that sends the judge prompt via `discussion-partners`
3. Parsing the PASS/FAIL result from the response
