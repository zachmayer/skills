---
name: llm_judge
description: >
  Evaluate AI outputs using LLM-as-judge with binary pass/fail scoring.
  Inspired by Hamel Husain's evaluation methodology. Use when you need to
  score prompt variants, evaluate output quality, or build automated evals.
  Do NOT use for tasks where a code assertion would suffice.
allowed-tools: Bash(uv run *)
---

Evaluate AI outputs using structured LLM-as-judge methodology.

## Core Principles

1. **Binary pass/fail only** — never use 1-5 scales. They create false precision. If you need granularity, use multiple independent binary checks on specific failure modes.

2. **Every judgment needs a critique** — explain WHY something passed or failed with specific evidence. A score without reasoning is worthless.

3. **Narrow scope per judge** — each judge targets ONE specific failure mode. "Is this good?" is not a valid criterion. "Does this hallucinate facts not in the source material?" is.

4. **Code checks first** — if you can express the check as an if/else (JSON validity, regex match, schema conformance), use code. Reserve LLM judges for subjective qualities only.

5. **Criteria drift is normal** — you cannot fully define evaluation criteria before reviewing outputs. Draft criteria, review outputs, revise criteria. Iterate.

## Building a Judge

### 1. Define the criterion

One narrow, specific failure mode:
- Bad: "Is the response helpful?"
- Good: "Does the response answer the user's specific question without introducing information not present in the provided context?"

### 2. Write the judge prompt

Use the `discussion_partners` skill to send the judge prompt to an external model:

```bash
# SKILL_DIR below refers to the discussion_partners skill directory
uv run --directory SKILL_DIR python scripts/ask_model.py -p openai "$(cat <<'EOF'
You are evaluating an AI response for [CRITERION].

Context: [what the AI was asked to do]
Input: [the user's request]
Output: [the AI's response]

Evaluate ONLY whether [specific criterion]. Ignore all other quality dimensions.

Respond in this exact format:
CRITIQUE: [2-3 sentences explaining your reasoning with specific evidence from the output]
RESULT: PASS or FAIL
EOF
)"
```

### 3. Calibrate with examples

Include 2-3 examples (both pass and fail) in the judge prompt. Draw from real outputs, not synthetic ones.

### 4. Validate alignment

Run the judge on a sample where you know the correct answer. Check:
- True positive rate (catches real failures)
- True negative rate (doesn't flag good outputs)

Target >90% on both. If not, refine the criterion or add examples.

## When Another Skill Calls This

Other skills (like `prompt_evolution`) can use this pattern by:
1. Defining their specific criterion
2. Launching a sub-agent that sends the judge prompt via `discussion_partners`
3. Parsing the PASS/FAIL result from the response
