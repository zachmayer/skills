---
name: march_madness
description: >
  Fetch March Madness odds data from The Odds API. Use when you need to pull
  NCAAB game odds, championship futures, or refresh odds data for the madness
  model. Do NOT use for non-basketball sports or general sports betting.
allowed-tools: Bash(uv run *)
---

Fetch NCAAB odds from The Odds API for March Madness modeling.

## Prerequisites

Set `ODDS_API_KEY` in `~/.zshrc`:

```bash
export ODDS_API_KEY="your-key"
```

## Commands

```bash
SKILL_DIR="skills/march_madness"

# Men's game odds (h2h moneylines)
uv run python $SKILL_DIR/scripts/fetch_odds.py game-odds --output game_odds.csv

# Men's championship futures
uv run python $SKILL_DIR/scripts/fetch_odds.py mens-futures --output mens_futures.csv

# Women's game odds (may be inactive outside tournament season)
uv run python $SKILL_DIR/scripts/fetch_odds.py womens-game-odds --output womens_game_odds.csv

# Fetch all available odds
uv run python $SKILL_DIR/scripts/fetch_odds.py fetch-all --output-dir output/
```

## Sport Keys

| Key | Purpose |
|-----|---------|
| `basketball_ncaab` | Men's game odds (h2h, spreads, totals) |
| `basketball_ncaab_championship_winner` | Men's championship futures |
| `basketball_wncaab` | Women's game odds (may be inactive) |

Women's championship futures do NOT exist in this API.

## Credit Costs

Each odds pull costs 1 credit per market per region. Daily pulls are cheap (~3 credits/day for all commands).
