---
name: prompt_evolution
description: >
  Evolve prompts through genetic-style optimization using parallel sub-agents,
  LLM-as-judge scoring, and iterative selection. Use when you need to optimize
  a prompt for a specific task and have a clear evaluation criterion.
  Do NOT use for one-off prompts or when the criterion is unclear.
allowed-tools: Bash(uv run *)
---

Optimize prompts through evolutionary search: generate variants, score with `llm_judge`, keep the fittest, mutate and recombine, repeat.

## The Loop

### 1. Setup

Define before starting:
- **Seed prompt**: the starting prompt to optimize
- **Test inputs**: 3-5 representative inputs the prompt must handle
- **Judge criterion**: a specific, binary pass/fail criterion (see `llm_judge` skill)
- **Generations**: how many rounds to run (default: 3)
- **Population size**: variants per generation (default: 4)

### 2. Generate variants

Launch parallel sub-agents, each using `discussion_partners` to generate a prompt variant:

> Here is a prompt: [SEED]. Generate a variant that might perform better at [CRITERION]. Change the structure, wording, emphasis, or approach — but preserve the core intent. Return ONLY the new prompt text, nothing else.

For generation 1, all variants mutate from the seed. For later generations, also recombine: give the sub-agent the top 2 prompts and ask it to combine their strengths.

### 3. Score each variant

For each variant, for each test input:
1. Run the variant prompt against a test model (via `discussion_partners`)
2. Score the output using `llm_judge` with the defined criterion
3. Record pass/fail per input

Variant fitness = pass rate across all test inputs.

### 4. Select

Keep the top 50% of variants (minimum 2). These become parents for the next generation.

### 5. Repeat

Mutate and recombine the surviving variants to fill the population. Run for the specified number of generations.

### 6. Return the winner

Output the highest-fitness prompt with its score and the specific test results.

## Example

```
Seed: "Summarize this article in 3 bullet points"
Criterion: "Each bullet captures a distinct key point, no redundancy, no hallucinated claims"
Test inputs: [3 different articles]
Generations: 3, Population: 4
```

Generation 1: 4 variants of the seed, scored → keep top 2
Generation 2: 2 survivors + 2 offspring (mutated/recombined), scored → keep top 2
Generation 3: same → return winner

## Sub-Agent Orchestration

Each scoring round involves `population × test_inputs` parallel sub-agent calls. Structure:

1. **Variant generation**: parallel sub-agents, each uses `discussion_partners` to create one variant
2. **Output generation**: parallel sub-agents, each runs one variant × one test input via `discussion_partners`
3. **Judging**: parallel sub-agents, each scores one output via `llm_judge` pattern

Maximize parallelism at each step. Wait for all results before proceeding to selection.

## When to Stop Early

- If the top variant achieves 100% pass rate for 2 consecutive generations
- If fitness plateaus (no improvement for 2 generations)
