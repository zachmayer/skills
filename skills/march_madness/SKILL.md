---
name: march_madness
description: >
  Fetch and analyze NCAA March Madness odds data. WHEN: User wants to fetch
  basketball odds, refresh tournament data, or analyze March Madness futures.
  WHEN NOT: Non-basketball sports or general sports analysis.
---

## Fetch Odds Data

Fetch NCAA basketball odds from The Odds API. Requires `ODDS_API_KEY` environment variable.

```bash
# Fetch everything (game odds + futures)
uv run --directory SKILL_DIR python scripts/fetch_odds.py fetch-all

# Fetch only game odds (spreads, totals, moneyline)
uv run --directory SKILL_DIR python scripts/fetch_odds.py fetch-games

# Fetch only championship futures
uv run --directory SKILL_DIR python scripts/fetch_odds.py fetch-futures

# Custom output directory
uv run --directory SKILL_DIR python scripts/fetch_odds.py fetch-all --output-dir /path/to/output
```

### Output Files

All files written to `$CLAUDE_OBSIDIAN_DIR/knowledge_graph/March_Madness/data/` by default:

- `game_odds.csv` — Flattened game odds with columns: event_id, commence_time, home_team, away_team, bookmaker, market, outcome_name, price, point
- `mens_futures.csv` — Championship futures with columns: event_id, sport, bookmaker, market, team, price
- `last_refresh.txt` — Timestamp of last successful refresh

### Recurring Refresh Pattern

The heartbeat agent can refresh odds data daily during tournament season. See `knowledge_graph/Technical/Recurring_Odds_Refresh.md` in the obsidian vault for setup instructions.
