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

Launch parallel sub-agents, each using `discussion_partners` to produce one variant. Apply two genetic operators:

**Mutation** (always): Literally change words in the prompt. Swap synonyms, delete filler, add specificity, reorder sentences, strengthen or weaken qualifiers. Each mutation should change 1-5 words or phrases — small, targeted edits, not wholesale rewrites.

> Here is a prompt: [SEED]. Mutate it: change 1-5 specific words or phrases to potentially improve [CRITERION]. Keep the core intent. Return ONLY the new prompt text.

**Crossover** (generation 2+): Literally splice sections from two parent prompts. Split each parent into numbered sections (by paragraph or logical block), then take section 1 from parent A, section 2 from parent B, etc. — producing a child that inherits concrete text from both parents.

> Here are two prompts that scored well:
> Parent A: [PROMPT_A]
> Parent B: [PROMPT_B]
> Split each into sections. Combine: take some sections from A and some from B to create a child prompt. Then apply 1-3 word-level mutations. Return ONLY the new prompt text.

For generation 1, all variants mutate from the seed. For later generations, half the population uses crossover from the top 2 parents, half uses mutation from a random survivor.

**Reflexion pass** (before scoring): After generating each variant, critically review it against the archive of prior variants before sending it to the judge. Ask: (1) Is this actually different from what we've already tried? (2) Are there obvious mistakes? (3) Can it be improved without changing the design? Discard or revise duplicates. This prevents wasting evaluation budget on near-copies. (From ADAS two-pass reflexion.)

### 2b. Feed history as context

When generating variants in generation 2+, include the **full history** of all prior variants and their scores (survivors AND dead variants) as context to the generator. The generator should see what worked, what failed, and why — so it can explicitly reason about what to try next rather than blindly mutating. The archive IS the prompt engineering; accumulating it gives the generator more signal over time.

### 3. Score each variant

For each variant, for each test input:
1. Run the variant prompt against a test model (via `discussion_partners`)
2. Score the output using `llm_judge` with the defined criterion
3. Record pass/fail per input

Variant fitness = pass rate across all test inputs.

### 4. Select

Keep the top 50% of variants (minimum 2). These become parents for the next generation.

**Parent selection for next generation**: Don't always mutate from the top scorer. Penalize parents that already have many children — a parent used 3 times should be less likely to be picked than an equally-scored parent used once. This prevents over-exploiting one lineage and encourages exploring diverse approaches. (From DGM score-child proportional selection.)

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

## Archive Persistence

After evolution completes, persist the winning prompt and runner-up to the obsidian vault. This lets future runs seed from proven prompts instead of starting from scratch — the single biggest improvement from meta-learning research (ADAS, Clune lab).

**Save to** `$CLAUDE_OBSIDIAN_DIR/prompt_archive/<task-slug>.md`:

```markdown
# <Task Name>

## Best Prompt (score: <fitness>)
<the winning prompt text>

## Runner-Up (score: <fitness>)
<second-best prompt text>

## Metadata
- Criterion: <judge criterion used>
- Generations: <N>
- Date: <ISO date>
- Test inputs: <count>
```

**Before starting a new evolution run**, check the archive for an existing entry matching the task. If found, use the archived best prompt as the seed instead of the user's naive seed. Tell the user: "Found archived prompt for this task (score: X). Using it as seed."

This creates a ratchet: each evolution run builds on the best result from prior runs rather than re-evolving from scratch.
