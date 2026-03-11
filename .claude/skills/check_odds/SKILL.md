---
name: check_odds
description: >
  Check prediction market odds on a topic. Searches multiple platforms
  (Metaculus, Manifold, PredictIt, Polymarket, Kalshi, and others) for
  relevant forecasts. Use when the user wants to know what prediction
  markets say about a question, check probabilities, or research forecasts.
  Do NOT use for sports betting odds or non-prediction-market price lookups.
allowed-tools: Bash(curl *), WebSearch, WebFetch
---

# Check Odds

Search prediction markets for forecasts on a topic. **Launch all platform searches in parallel via subagents** — each platform is independent, so search them concurrently using the Task tool.

## Platform Weighting

When synthesizing across platforms, weight by calibration quality:

| Tier | Platform | Weight | Why |
|------|----------|--------|-----|
| 1 | **Metaculus** | Anchor | Superforecaster-calibrated, best track record, non-speculative |
| 2 | **Manifold**, **PredictIt** | Strong signal | Manifold: good coverage, solid community. PredictIt: 93% accuracy on US politics (CFTC-regulated) |
| 3 | **Polymarket**, **Kalshi** | Cross-reference | Speculative markets, lower calibration |
| 4 | **Betfair**, **Smarkets** | Regional cross-ref | Deep liquidity but exchange/gambling model, non-US |
| — | **Good Judgment Open** | Reference only | 0.01 calibration (best anywhere) but no API, not searchable |

When platforms disagree, trust higher tiers. The summary should anchor on Metaculus, with Manifold/PredictIt as supporting evidence and lower tiers as color.

## Process

Given a topic, **launch parallel subagents** for each platform. Use the Task tool with `subagent_type="general-purpose"` for each. Pass the search query and platform-specific instructions below. Gather results, then synthesize.

### 1. Metaculus (API — no auth)

```bash
curl -s "https://www.metaculus.com/api2/questions/?search=QUERY&limit=5&status=open&type=binary"
```

Extract: `title`, `aggregations.recency_weighted.latest.centers[0]` (probability, may be `null` if hidden), `nr_forecasters`, URL: `https://www.metaculus.com/questions/{id}/`

Note: Metaculus hides predictions until `cp_reveal_time`. If null, report "prediction hidden".

### 2. Manifold Markets (API — no auth)

```bash
curl -s "https://api.manifold.markets/v0/search-markets?term=QUERY&sort=liquidity&filter=open&limit=5"
```

Extract: `question`, `probability` (0-1), `url`, `volume`, `uniqueBettorCount`.

### 3. PredictIt (API — no auth)

```bash
curl -s "https://www.predictit.org/api/marketdata/all/"
```

Returns all markets (no server-side search). Filter client-side by **whole-word** match on `Name` or `ShortName` — substring matching will produce false positives (e.g. "Maine" matching "ai"). Extract: `Name`, `Contracts[].LastTradePrice` (0-1 probability), `Contracts[].BestBuyYesCost`, `URL`.

Rate limit: ~1 req/min. Political markets only (US elections, policy). Non-commercial use.

### 4. Polymarket (WebSearch)

No free-text search API. Use WebSearch:
```
site:polymarket.com QUERY
```
Visit top results with WebFetch to extract probability percentages.

### 5. Kalshi (WebSearch)

API uses event tickers, not free-text. Use WebSearch:
```
site:kalshi.com QUERY
```
Visit top results with WebFetch to extract odds.

### 6. Betfair Exchange (WebSearch)

Betfair's trading API requires auth. Use WebSearch:
```
site:betfair.com/exchange QUERY
```
Best global liquidity on political events. Not available in US. API docs: https://developer.betfair.com

### 7. Smarkets (WebSearch)

Smarkets API is hierarchical (categories → regions → events), not free-text searchable. Use WebSearch:
```
site:smarkets.com QUERY
```
Not available in US. 2% commission exchange model. API docs: https://docs.smarkets.com

## Output Format

```
## Prediction Market Odds: <topic>

| Platform | Question | Probability | Depth | Link |
|----------|----------|-------------|-------|------|
| Metaculus | ... | 72% | 150 forecasters | [link] |
| Manifold | ... | 68% | $45k volume | [link] |
| PredictIt | ... | 71% | — | [link] |
| Polymarket | ... | 70% | $1.2M volume | [link] |
| Kalshi | ... | 65% | — | [link] |
| Betfair | ... | 69% | £500k matched | [link] |
| Smarkets | ... | 67% | — | [link] |

### Summary
<1-3 sentences anchored on Metaculus, noting agreement/disagreement across tiers>

### Caveats
<thin markets, hidden predictions, wide disagreements, geo-restrictions>
```

## Rules

- **Search all platforms in parallel.** Use subagents — don't search sequentially. Cross-platform comparison is the whole point.
- **Weight by tier.** Anchor on Metaculus. Use Manifold/PredictIt as supporting evidence. Lower tiers are cross-references only. If Metaculus has no market but others do, say so explicitly.
- **Flag disagreements.** If platforms diverge by >15 percentage points, call it out.
- **Report "no markets found"** per platform rather than omitting — absence is informative.
- **URL-encode search queries.** Replace spaces with `+` or `%20`.
- **Don't editorialize.** Report what markets say. Add caveats only when relevant.
- **Skip platforms that can't help.** PredictIt is politics-only. Betfair/Smarkets are non-US. If the query clearly doesn't match a platform's coverage, skip it and note why.
