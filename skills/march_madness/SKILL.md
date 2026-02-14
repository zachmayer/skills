---
name: march_madness
description: >
  Fetch March Madness odds data from The Odds API. Use when the user asks
  about March Madness odds, basketball futures, game lines, or wants to
  refresh the odds data pipeline. Do NOT use for non-basketball sports.
---

Fetch and store NCAAB odds data for the March Madness model.

## Commands

```bash
# Fetch men's championship futures
uv run --directory SKILL_DIR python scripts/fetch_odds.py futures --output-dir OUTPUT_DIR

# Fetch men's game odds (moneylines, spreads, totals)
uv run --directory SKILL_DIR python scripts/fetch_odds.py game-odds --output-dir OUTPUT_DIR

# Fetch everything
uv run --directory SKILL_DIR python scripts/fetch_odds.py fetch-all --output-dir OUTPUT_DIR
```

`SKILL_DIR` = the skills repo root (where `pyproject.toml` lives).
`OUTPUT_DIR` = where to write CSVs. Default: `~/claude/obsidian/knowledge_graph/March_Madness/data/`.

## Environment

Requires `ODDS_API_KEY` environment variable. Set in `~/.zshrc`:
```bash
export ODDS_API_KEY="your-key-here"
```

## Output Schemas

### `mens_futures.csv`
Wide format: one row per team, one column per bookmaker. American odds integers.
```
team_name,FanDuel,DraftKings,BetMGM,BetRivers,Caesars,Bet365,...
```

### `game_odds.csv`
One row per team per game. American odds integers.
```
game_id,commence_time,team_name,is_home,h2h,spread_point,spread_price,total_point,total_over,total_under,bookmaker
```

### `odds_metadata.json`
Credits used, timestamp, API response headers.

## Sport Keys

| Purpose | Sport Key |
|---------|-----------|
| Men's game odds | `basketball_ncaab` |
| Men's championship futures | `basketball_ncaab_championship_winner` |
| Women's game odds | `basketball_wncaab` (may be inactive) |
| Women's futures | **Not available** via API — needs manual entry |

## Credit Costs

- Futures: 1 credit per pull
- Game odds (3 markets): 3 credits per pull
- Daily refresh for 4 weeks: ~112 credits total

## Integration

The madness repo (`zachmayer/madness`) reads these CSVs in `gambling.R`. It handles team name matching via `spell.csv` — this skill outputs team names as the API returns them.
