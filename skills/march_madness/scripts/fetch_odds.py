"""Fetch NCAA basketball odds from The Odds API and write CSV files."""

import csv
import json
import os
from datetime import datetime
from datetime import timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import click

BASE_URL = "https://api.the-odds-api.com/v4/sports"
SPORT = "basketball_ncaab"

DEFAULT_OUTPUT_DIR = (
    Path(os.environ.get("CLAUDE_OBSIDIAN_DIR", os.path.expanduser("~/claude/obsidian")))
    / "knowledge_graph"
    / "March_Madness"
    / "data"
)


class OddsAPIError(click.ClickException):
    """Raised when the Odds API key is missing or a request fails."""

    pass


def _api_key() -> str:
    key = os.environ.get("ODDS_API_KEY", "")
    if not key:
        raise OddsAPIError("ODDS_API_KEY environment variable is not set.")
    return key


def _getjson(url: str) -> dict | list:
    """Fetch JSON from a URL and return parsed data."""
    with urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _fetch_odds(regions: str = "us", markets: str = "h2h,spreads,totals") -> list[dict]:
    """Fetch game odds for NCAA basketball."""
    key = _api_key()
    url = (
        f"{BASE_URL}/{SPORT}/odds"
        f"?apiKey={key}&regions={regions}&markets={markets}&oddsFormat=american"
    )
    return _getjson(url)


def _fetch_futures(regions: str = "us") -> list[dict]:
    """Fetch championship futures/outrights for NCAA basketball."""
    key = _api_key()
    url = (
        f"{BASE_URL}/{SPORT}_championship_winner/odds"
        f"?apiKey={key}&regions={regions}&markets=outrights&oddsFormat=american"
    )
    return _getjson(url)


def _flatten_game_odds(events: list[dict]) -> list[dict]:
    """Flatten nested odds JSON into rows for CSV."""
    rows = []
    for event in events:
        base = {
            "event_id": event.get("id", ""),
            "commence_time": event.get("commence_time", ""),
            "home_team": event.get("home_team", ""),
            "away_team": event.get("away_team", ""),
        }
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    row = {
                        **base,
                        "bookmaker": bookmaker.get("key", ""),
                        "market": market.get("key", ""),
                        "outcome_name": outcome.get("name", ""),
                        "price": outcome.get("price", ""),
                        "point": outcome.get("point", ""),
                    }
                    rows.append(row)
    return rows


def _flatten_futures(events: list[dict]) -> list[dict]:
    """Flatten futures JSON into rows for CSV."""
    rows = []
    for event in events:
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    row = {
                        "event_id": event.get("id", ""),
                        "sport": event.get("sport_key", ""),
                        "bookmaker": bookmaker.get("key", ""),
                        "market": market.get("key", ""),
                        "team": outcome.get("name", ""),
                        "price": outcome.get("price", ""),
                    }
                    rows.append(row)
    return rows


def _write_csv(rows: list[dict], path: Path) -> None:
    """Write list of dicts to CSV."""
    if not rows:
        click.echo(f"  No data to write for {path.name}")
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
    """Fetch NCAA basketball odds data from The Odds API."""
    pass


@cli.command()
@click.option(
    "--output-dir", type=click.Path(), default=None, help="Output directory for CSV files"
)
def fetch_games(output_dir: str | None):
    """Fetch game odds (spreads, totals, moneyline)."""
    out = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    click.echo("Fetching game odds...")
    events = _fetch_odds()
    rows = _flatten_game_odds(events)
    _write_csv(rows, out / "game_odds.csv")


@cli.command()
@click.option(
    "--output-dir", type=click.Path(), default=None, help="Output directory for CSV files"
)
def fetch_futures(output_dir: str | None):
    """Fetch championship futures/outrights."""
    out = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    click.echo("Fetching futures odds...")
    events = _fetch_futures()
    rows = _flatten_futures(events)
    _write_csv(rows, out / "mens_futures.csv")
    teams = {r["team"] for r in rows}
    click.echo(f"  Unique teams: {len(teams)}")


@cli.command()
@click.option(
    "--output-dir", type=click.Path(), default=None, help="Output directory for CSV files"
)
def fetch_all(output_dir: str | None):
    """Fetch both game odds and futures."""
    out = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    click.echo(f"Fetching all odds data at {now}")

    click.echo("\n--- Game Odds ---")
    try:
        events = _fetch_odds()
        rows = _flatten_game_odds(events)
        _write_csv(rows, out / "game_odds.csv")
    except (HTTPError, OddsAPIError) as e:
        click.echo(f"Error fetching game odds: {e}", err=True)

    click.echo("\n--- Futures ---")
    try:
        events = _fetch_futures()
        rows = _flatten_futures(events)
        _write_csv(rows, out / "mens_futures.csv")
        teams = {r["team"] for r in rows}
        click.echo(f"  Unique teams: {len(teams)}")
    except (HTTPError, OddsAPIError) as e:
        click.echo(f"Error fetching futures: {e}", err=True)

    # Write metadata
    meta_path = out / "last_refresh.txt"
    meta_path.write_text(f"Last refresh: {now}\n")
    click.echo(f"\nDone. Metadata written to {meta_path}")


if __name__ == "__main__":
    cli()
