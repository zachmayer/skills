---
name: superforecaster
description: >
  Make calibrated probabilistic forecasts on binary questions using structured
  reasoning, web research, and multi-model aggregation. Use when the user asks
  "what's the probability of X?", wants a forecast, or needs a calibrated
  prediction on a future event. Do NOT use for sports betting odds (use
  check_odds) or for questions with known answers.
allowed-tools: WebSearch, WebFetch, Bash(curl *), Task
---

# Superforecaster

Generate calibrated probabilistic forecasts on binary questions. Based on Halawi et al. (NeurIPS 2024) and the Metaculus forecasting-tools framework.

## Pipeline

For each question, execute these steps in order:

### 1. Frame the Question

Restate the question as a precise binary (Yes/No) with:
- **Resolution criteria**: What exactly counts as Yes?
- **Resolution date**: When will we know?
- **Base rate**: How often do events like this happen? Search for historical precedent.

If the user's question is vague, clarify before forecasting.

### 2. Gather Evidence

**Run in parallel:**

a) **Market prior** — Use `check_odds` to get prediction market consensus. This is your initial anchor. If no markets exist, note that explicitly.

b) **Web research** — Use WebSearch for 3-5 targeted queries:
   - The question itself
   - Key sub-questions that would shift the probability
   - Recent developments / status quo

   For each result, assess relevance (skip paywalled, error pages, stale content). Summarize each source as bullet points preserving dates, numbers, and quotes.

c) **Base rate search** — Search for the historical frequency of similar events. "How often has [category of event] happened in [relevant timeframe]?"

### 3. Reason (Structured Scratchpad)

Write out your reasoning following this exact structure:

```
TIME REMAINING: [duration until resolution]

STATUS QUO: [what happens if nothing changes — this is the most likely outcome]

SCENARIO FOR NO:
- [concrete pathway to No]
- Strength: [weak/moderate/strong]

SCENARIO FOR YES:
- [concrete pathway to Yes]
- Strength: [weak/moderate/strong]

BASE RATE: [X% — historical frequency of similar events]

MARKET CONSENSUS: [X% from check_odds, or "no markets"]

KEY EVIDENCE:
- [evidence point 1 — for/against, strength]
- [evidence point 2 — for/against, strength]
- [evidence point 3 — for/against, strength]

INITIAL PROBABILITY: X%
```

**Critical debiasing rules:**
- **Status quo bias is correct.** The world changes slowly. Put extra weight on the status quo outcome. LLMs over-predict dramatic change.
- **Clamp to [2%, 98%].** Never assign extreme certainty. You don't know what you don't know.
- **Anchor on base rates.** Start from how often this type of event happens, then update based on specific evidence.
- **Don't anchor on round numbers.** 73% is more calibrated than 75%.

### 4. Critique and Adjust

After your initial probability, challenge it:

- Is this excessively confident or not confident enough?
- What am I missing? What would change my mind?
- Am I anchoring too heavily on one piece of evidence?
- Does my probability reflect the time remaining? (More time = more uncertainty = closer to base rate)
- Am I being swayed by a dramatic narrative over boring base rates?

Adjust if warranted. State what changed and why.

### 5. Multi-Model Aggregation (Optional, for high-stakes questions)

For important forecasts, get independent predictions from other models using `discussion_partners`:

Frame the question with ALL context (the partner has zero context). Include:
- The exact binary question and resolution criteria
- Resolution date
- All evidence gathered in step 2
- The base rate

Ask: "You are a professional superforecaster interviewing for a job. Given this evidence, what is the probability of [question]? Walk through your reasoning, then output your final answer as 'Probability: ZZ%'."

Query 2-3 models. Aggregate via **median** (robust to outliers).

If your solo forecast and the multi-model median diverge by >15 percentage points, investigate why. The disagreement is informative — don't just average it away.

### 6. Output

```
## Forecast: [question]

**Probability: X%**

### Evidence Summary
- [key evidence, 3-5 bullets]

### Reasoning
[2-3 sentences on the key drivers]

### Confidence Notes
- Market consensus: [X% or "no markets found"]
- Base rate: [X%]
- Multi-model range: [X%-Y%] (if step 5 was used)
- Key uncertainty: [what could most change this forecast]

### Sources
- [source 1]
- [source 2]
```

## Calibration Principles

These come from Tetlock's superforecasting research and Metaculus tournament winners:

1. **Status quo is king.** Most questions resolve to the boring default. Overweight it.
2. **Update incrementally.** Each piece of evidence should move your probability a little, not a lot. Bayesian updates, not vibes.
3. **Distinguish confidence from extremity.** High confidence in an uncertain outcome is still ~50%. Confidence means your uncertainty estimate is precise, not that the probability is extreme.
4. **Time horizon matters.** More time = more variance = probabilities closer to base rates. Less time = more certainty = probabilities can be more extreme.
5. **Aggregate > individual.** Multiple independent forecasts averaged together beat any single forecast. Use markets and multi-model when available.
6. **Beware narrative bias.** Compelling stories feel more probable than they are. Boring statistical regularity beats vivid anecdote.
