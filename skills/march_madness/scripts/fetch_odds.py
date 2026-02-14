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


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("ODDS_API_KEY", "")
    if not key:
        click.echo("Error: ODDS_API_KEY environment variable not set.", err=True)
        click.echo("Set it in ~/.zshrc: export ODDS_API_KEY='your-key'", err=True)
        sys.exit(1)
    return key


def fetch(sport: str, markets: str = "h2h") -> tuple[list, dict]:
    """Fetch odds from the API. Returns (data, metadata)."""
    resp = httpx.get(
        f"{BASE_URL}/{sport}/odds",
        params={
            "apiKey": get_api_key(),
            "regions": "us",
            "markets": markets,
            "oddsFormat": "american",
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sport": sport,
        "markets": markets,
        "credits_used": resp.headers.get("x-requests-last", "unknown"),
        "credits_remaining": resp.headers.get("x-requests-remaining", "unknown"),
    }
    return resp.json(), metadata


def parse_futures(data: list) -> list[dict]:
    """Parse championship futures into wide format: one row per team, one column per bookmaker."""
    team_odds: dict[str, dict[str, int | None]] = {}
    all_bookmakers: set[str] = set()

    for event in data:
        for bk in event.get("bookmakers", []):
            title = bk["title"]
            all_bookmakers.add(title)
            for market in bk.get("markets", []):
                if market["key"] != "outrights":
                    continue
                for outcome in market["outcomes"]:
                    team_odds.setdefault(outcome["name"], {})[title] = outcome.get("price")

    sorted_bks = sorted(all_bookmakers)
    return [
        {"team_name": team, **{bk: team_odds[team].get(bk) for bk in sorted_bks}}
        for team in sorted(team_odds)
    ]


def parse_game_odds(data: list) -> list[dict]:
    """Parse game odds into long format: one row per team per game per bookmaker."""
    rows = []
    for event in data:
        game_id = event["id"]
        commence = event.get("commence_time", "")
        home = event.get("home_team", "")
        away = event.get("away_team", "")

        for bk in event.get("bookmakers", []):
            h2h: dict[str, int | None] = {}
            spreads: dict[str, tuple[float | None, int | None]] = {}
            totals: dict[str, float | int | None] = {}

            for market in bk.get("markets", []):
                for o in market["outcomes"]:
                    if market["key"] == "h2h":
                        h2h[o["name"]] = o.get("price")
                    elif market["key"] == "spreads":
                        spreads[o["name"]] = (o.get("point"), o.get("price"))
                    elif market["key"] == "totals":
                        totals["total_point"] = o.get("point")
                        if o["name"] == "Over":
                            totals["total_over"] = o.get("price")
                        elif o["name"] == "Under":
                            totals["total_under"] = o.get("price")

            for team in [home, away]:
                sp = spreads.get(team, (None, None))
                rows.append(
                    {
                        "game_id": game_id,
                        "commence_time": commence,
                        "team_name": team,
                        "is_home": team == home,
                        "bookmaker": bk["title"],
                        "h2h": h2h.get(team),
                        "spread_point": sp[0],
                        "spread_price": sp[1],
                        **totals,
                    }
                )
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to CSV."""
    if not rows:
        click.echo(f"  No data to write to {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    click.echo(f"  Wrote {len(rows)} rows to {path}")


def save_metadata(out: Path, key: str, metadata: dict) -> None:
    """Merge metadata into odds_metadata.json."""
    meta_path = out / "odds_metadata.json"
    existing = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    existing[key] = metadata
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(existing, indent=2))
    click.echo(
        f"  Credits used: {metadata['credits_used']}, remaining: {metadata['credits_remaining']}"
    )


def save_raw_json(data: list, path: Path) -> None:
    """Optionally save raw API JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    click.echo(f"  Raw JSON: {path}")


@click.group()
def cli():
    """Fetch NCAAB odds from The Odds API."""
    pass


@cli.command()
@click.option("--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR))
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
def futures(output_dir: str, json_raw: bool):
    """Fetch men's championship futures odds."""
    out = Path(output_dir)
    click.echo("Fetching men's championship futures...")
    data, metadata = fetch("basketball_ncaab_championship_winner", markets="outrights")
    write_csv(parse_futures(data), out / "mens_futures.csv")
    if json_raw:
        save_raw_json(data, out / "mens_futures_raw.json")
    save_metadata(out, "futures", metadata)


@cli.command("game-odds")
@click.option("--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR))
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
def game_odds(output_dir: str, json_raw: bool):
    """Fetch men's game odds (moneylines, spreads, totals)."""
    out = Path(output_dir)
    click.echo("Fetching men's game odds (h2h, spreads, totals)...")
    data, metadata = fetch("basketball_ncaab", markets="h2h,spreads,totals")
    write_csv(parse_game_odds(data), out / "game_odds.csv")
    if json_raw:
        save_raw_json(data, out / "game_odds_raw.json")
    save_metadata(out, "game_odds", metadata)


@cli.command("fetch-all")
@click.option("--output-dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR))
@click.option("--json-raw", is_flag=True, help="Also save raw API JSON")
@click.pass_context
def fetch_all(ctx: click.Context, output_dir: str, json_raw: bool):
    """Fetch all available odds data."""
    ctx.invoke(futures, output_dir=output_dir, json_raw=json_raw)
    click.echo()
    ctx.invoke(game_odds, output_dir=output_dir, json_raw=json_raw)


if __name__ == "__main__":
    cli()
