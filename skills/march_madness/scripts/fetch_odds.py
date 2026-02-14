"""Fetch NCAAB odds from The Odds API for March Madness modeling."""

import csv
import json
import os
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path

import click
import httpx

BASE_URL = "https://api.the-odds-api.com/v4/sports"
DEFAULT_OUTPUT_DIR = (
    Path.home() / "claude" / "obsidian" / "knowledge_graph" / "March_Madness" / "data"
)

# Bookmaker key → display name mapping
BOOKMAKER_NAMES: dict[str, str] = {
    "fanduel": "FanDuel",
    "draftkings": "DraftKings",
    "betmgm": "BetMGM",
    "betrivers": "BetRivers",
    "williamhill_us": "Caesars",
    "bet365": "Bet365",
    "bovada": "Bovada",
    "pointsbetus": "PointsBet",
    "unibet_us": "Unibet",
    "betus": "BetUS",
    "betonlineag": "BetOnline",
    "mybookieag": "MyBookie",
    "superbook": "SuperBook",
    "lowvig": "LowVig",
    "espnbet": "ESPNBet",
    "fliff": "Fliff",
    "hardrockbet": "HardRock",
    "fanatics": "Fanatics",
}


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("ODDS_API_KEY", "")
    if not key:
        click.echo("Error: ODDS_API_KEY environment variable not set.", err=True)
        click.echo("Set it in ~/.zshrc: export ODDS_API_KEY='your-key'", err=True)
        sys.exit(1)
    return key


def display_name(bookmaker_key: str) -> str:
    """Map API bookmaker key to display name."""
    return BOOKMAKER_NAMES.get(bookmaker_key, bookmaker_key)


def fetch_odds(
    sport: str, markets: str = "h2h", odds_format: str = "american"
) -> tuple[list, dict]:
    """Fetch odds from the API. Returns (data, metadata)."""
    api_key = get_api_key()
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": markets,
        "oddsFormat": odds_format,
    }

    url = f"{BASE_URL}/{sport}/odds"
    resp = httpx.get(url, params=params, timeout=30.0)
    resp.raise_for_status()

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sport": sport,
        "markets": markets,
        "credits_used": resp.headers.get("x-requests-last", "unknown"),
        "credits_remaining": resp.headers.get("x-requests-remaining", "unknown"),
        "total_used": resp.headers.get("x-requests-used", "unknown"),
    }

    return resp.json(), metadata


def parse_futures(data: list) -> list[dict]:
    """Parse championship futures into wide format (one row per team, one col per bookmaker)."""
    # Collect all teams and their odds by bookmaker
    team_odds: dict[str, dict[str, int | None]] = {}
    all_bookmakers: set[str] = set()

    for event in data:
        for bookmaker in event.get("bookmakers", []):
            bk_name = display_name(bookmaker["key"])
            all_bookmakers.add(bk_name)
            for market in bookmaker.get("markets", []):
                if market["key"] == "outrights":
                    for outcome in market["outcomes"]:
                        team = outcome["name"]
                        price = outcome.get("price")
                        if team not in team_odds:
                            team_odds[team] = {}
                        team_odds[team][bk_name] = price

    # Build rows sorted by team name
    sorted_bookmakers = sorted(all_bookmakers)
    rows = []
    for team in sorted(team_odds.keys()):
        row: dict[str, str | int | None] = {"team_name": team}
        for bk in sorted_bookmakers:
            row[bk] = team_odds[team].get(bk)
        rows.append(row)

    return rows


def parse_game_odds(data: list) -> list[dict]:
    """Parse game odds into long format (one row per team per game per bookmaker)."""
    rows = []

    for event in data:
        game_id = event["id"]
        commence = event.get("commence_time", "")
        home = event.get("home_team", "")
        away = event.get("away_team", "")

        for bookmaker in event.get("bookmakers", []):
            bk_name = display_name(bookmaker["key"])
            markets_data: dict[str, dict[str, int | float | None]] = {}

            for market in bookmaker.get("markets", []):
                mkey = market["key"]
                for outcome in market["outcomes"]:
                    team = outcome["name"]
                    price = outcome.get("price")
                    point = outcome.get("point")

                    if team not in markets_data:
                        markets_data[team] = {}

                    if mkey == "h2h":
                        markets_data[team]["h2h"] = price
                    elif mkey == "spreads":
                        markets_data[team]["spread_point"] = point
                        markets_data[team]["spread_price"] = price
                    elif mkey == "totals":
                        label = outcome.get("name", "").lower()
                        markets_data[team]["total_point"] = point
                        if label == "over":
                            markets_data[team]["total_over"] = price
                        elif label == "under":
                            markets_data[team]["total_under"] = price

            # For totals, the "team" is Over/Under, not actual teams
            # Merge totals into team rows
            totals_data: dict[str, int | float | None] = {}
            for t in list(markets_data.keys()):
                if t in ("Over", "Under"):
                    totals_data.update(markets_data.pop(t))

            for team_name in [home, away]:
                team_data = markets_data.get(team_name, {})
                rows.append(
                    {
                        "game_id": game_id,
                        "commence_time": commence,
                        "team_name": team_name,
                        "is_home": team_name == home,
                        "bookmaker": bk_name,
                        "h2h": team_data.get("h2h"),
                        "spread_point": team_data.get("spread_point"),
                        "spread_price": team_data.get("spread_price"),
                        "total_point": totals_data.get("total_point"),
                        "total_over": totals_data.get("total_over"),
                        "total_under": totals_data.get("total_under"),
                    }
                )

    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to CSV."""
    if not rows:
        click.echo(f"  No data to write to {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    click.echo(f"  Wrote {len(rows)} rows to {path}")


@click.group()
def cli():
    """Fetch NCAAB odds from The Odds API."""
    pass


@cli.command()
@click.option(
    "--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR), help="Output directory"
)
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
def futures(output_dir: str, json_raw: bool):
    """Fetch men's championship futures odds."""
    out = Path(output_dir)
    click.echo("Fetching men's championship futures...")

    data, metadata = fetch_odds("basketball_ncaab_championship_winner", markets="outrights")
    rows = parse_futures(data)

    write_csv(rows, out / "mens_futures.csv")

    if json_raw:
        raw_path = out / "mens_futures_raw.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(data, indent=2))
        click.echo(f"  Raw JSON: {raw_path}")

    meta_path = out / "odds_metadata.json"
    # Merge with existing metadata if present
    existing: dict = {}
    if meta_path.exists():
        existing = json.loads(meta_path.read_text())
    existing["futures"] = metadata
    meta_path.write_text(json.dumps(existing, indent=2))

    click.echo(
        f"  Credits used: {metadata['credits_used']}, remaining: {metadata['credits_remaining']}"
    )


@cli.command("game-odds")
@click.option(
    "--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR), help="Output directory"
)
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
def game_odds(output_dir: str, json_raw: bool):
    """Fetch men's game odds (moneylines, spreads, totals)."""
    out = Path(output_dir)
    click.echo("Fetching men's game odds (h2h, spreads, totals)...")

    data, metadata = fetch_odds("basketball_ncaab", markets="h2h,spreads,totals")
    rows = parse_game_odds(data)

    write_csv(rows, out / "game_odds.csv")

    if json_raw:
        raw_path = out / "game_odds_raw.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(data, indent=2))
        click.echo(f"  Raw JSON: {raw_path}")

    meta_path = out / "odds_metadata.json"
    existing: dict = {}
    if meta_path.exists():
        existing = json.loads(meta_path.read_text())
    existing["game_odds"] = metadata
    meta_path.write_text(json.dumps(existing, indent=2))

    click.echo(
        f"  Credits used: {metadata['credits_used']}, remaining: {metadata['credits_remaining']}"
    )


@cli.command("fetch-all")
@click.option(
    "--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR), help="Output directory"
)
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
@click.pass_context
def fetch_all(ctx: click.Context, output_dir: str, json_raw: bool):
    """Fetch all available odds data."""
    ctx.invoke(futures, output_dir=output_dir, json_raw=json_raw)
    click.echo()
    ctx.invoke(game_odds, output_dir=output_dir, json_raw=json_raw)


if __name__ == "__main__":
    cli()
