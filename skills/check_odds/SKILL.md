---
name: check_odds
description: >
  Check prediction market odds on a topic. Searches Metaculus, Manifold,
  Polymarket, and Kalshi in that order for relevant forecasts. Use when the
  user wants to know what prediction markets say about a question, check
  probabilities, or research forecasts. Do NOT use for sports betting odds
  or non-prediction-market price lookups.
allowed-tools: Bash(curl *), WebSearch, WebFetch
---

# Check Odds

Search prediction markets for forecasts on a topic. Platforms are searched in priority order: **Metaculus > Manifold > Polymarket > Kalshi**.

## Platform Weighting

When synthesizing across platforms, weight by calibration quality:

| Tier | Platform | Weight | Why |
|------|----------|--------|-----|
| 1 | **Metaculus** | Anchor | Superforecaster-calibrated, best track record, non-speculative |
| 2 | **Manifold** | Strong signal | Good coverage, real-money liquidity, solid community |
| 3 | **Polymarket, Kalshi** | Cross-reference | Speculative markets, regulatory constraints, lower calibration |
| 4 | **New/niche platforms** | Weak signal | Unproven track record, thin markets |

When platforms disagree, trust higher tiers. The summary should primarily reflect Metaculus, with Manifold as supporting evidence and Poly/Kalshi as color.

## Process

Given a topic or question from the user:

### 1. Metaculus (API)

Search via the public API — no auth needed:

```bash
curl -s "https://www.metaculus.com/api2/questions/?search=QUERY&limit=5&status=open&type=binary"
```

Extract from each result:
- `question.title` — the question text
- `question.aggregations.recency_weighted.latest.centers[0]` — community prediction (0-1, may be `null` if not yet revealed)
- `nr_forecasters` — number of forecasters
- URL: `https://www.metaculus.com/questions/{id}/`

Note: Metaculus hides community predictions until `cp_reveal_time`. If `centers` is null, report "prediction hidden" and still include the question.

### 2. Manifold Markets (API)

Search via the public API — no auth needed:

```bash
curl -s "https://api.manifold.markets/v0/search-markets?term=QUERY&sort=liquidity&filter=open&limit=5"
```

Extract from each result:
- `question` — the market question
- `probability` — current probability (0-1, display as percentage)
- `url` — link to the market
- `volume` — total trading volume (indicator of market depth)
- `uniqueBettorCount` — number of unique bettors

### 3. Polymarket (WebSearch)

Polymarket's API requires authentication, so use WebSearch:

```
WebSearch: site:polymarket.com QUERY
```

Visit the top results with WebFetch to extract current odds. Look for the probability percentage displayed on the market page.

### 4. Kalshi (WebSearch)

Kalshi's API is structured around event tickers, not free-text search. Use WebSearch:

```
WebSearch: site:kalshi.com QUERY
```

Visit the top results with WebFetch to extract current odds.

## Output Format

Present results as a table, one row per relevant market found:

```
## Prediction Market Odds: <topic>

| Platform | Question | Probability | Forecasters/Volume | Link |
|----------|----------|-------------|-------------------|------|
| Metaculus | ... | 72% | 150 forecasters | [link] |
| Manifold | ... | 68% | $45k volume | [link] |
| Polymarket | ... | 70% | $1.2M volume | [link] |
| Kalshi | ... | 65% | — | [link] |

### Summary
<1-3 sentences synthesizing what prediction markets collectively suggest>

### Caveats
<note any thin markets, wide disagreements between platforms, or hidden predictions>
```

## Rules

- **Search all four platforms**, even if the first one returns good results. Cross-platform comparison is the whole point.
- **Weight by tier.** Anchor the summary on the Metaculus forecast. Use Manifold as supporting evidence. Treat Polymarket/Kalshi as cross-references, not primary sources. If Metaculus has no market but others do, say so explicitly — the absence on Metaculus is informative.
- **Flag disagreements.** If platforms diverge by >15 percentage points, call it out explicitly.
- **Report "no markets found"** for a platform rather than omitting it — the absence of a market is informative.
- **URL-encode the search query** in API calls. Replace spaces with `+` or `%20`.
- **Don't editorialize.** Report what the markets say. Add caveats about market limitations (thin markets, manipulation risk, regulatory constraints) only when relevant.
