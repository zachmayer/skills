#!/usr/bin/env python3
"""Fetch NCAAB odds from The Odds API for March Madness modeling."""

import csv
import os
from collections import defaultdict

import click
import httpx

API_BASE = "https://api.the-odds-api.com/v4"

SPORT_NCAAB = "basketball_ncaab"
SPORT_NCAAB_CHAMP = "basketball_ncaab_championship_winner"
SPORT_WNCAAB = "basketball_wncaab"


def _get_api_key() -> str:
    """Get ODDS_API_KEY from environment or exit."""
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        click.echo("Error: ODDS_API_KEY not set.", err=True)
        click.echo('Add to ~/.zshrc: export ODDS_API_KEY="your-key"', err=True)
        raise SystemExit(1)
    return key


def _fetch_odds(sport: str, markets: str = "h2h", odds_format: str = "american") -> dict:
    """Fetch odds from the API. Returns dict with status, data, headers."""
    api_key = _get_api_key()
    url = f"{API_BASE}/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": markets,
        "oddsFormat": odds_format,
    }
    resp = httpx.get(url, params=params, timeout=30.0)

    if resp.status_code == 422:
        return {"status": "inactive", "data": [], "headers": dict(resp.headers)}

    if resp.status_code == 401:
        click.echo("Error: Invalid ODDS_API_KEY.", err=True)
        raise SystemExit(1)

    if resp.status_code == 429:
        click.echo("Error: Rate limited. Wait and retry.", err=True)
        raise SystemExit(1)

    if resp.status_code != 200:
        click.echo(f"Error: API returned {resp.status_code}: {resp.text}", err=True)
        raise SystemExit(1)

    remaining = resp.headers.get("x-requests-remaining", "?")
    used = resp.headers.get("x-requests-last", "?")
    click.echo(f"Credits used: {used}, remaining: {remaining}", err=True)

    return {"status": "ok", "data": resp.json(), "headers": dict(resp.headers)}


def _parse_game_odds(events: list[dict]) -> list[dict]:
    """Parse game odds events into rows: one per team with bookmaker columns."""
    bookmaker_names: set[str] = set()
    for event in events:
        for bm in event.get("bookmakers", []):
            bookmaker_names.add(bm["key"])

    bookmakers_sorted = sorted(bookmaker_names)

    rows: list[dict] = []
    for event in events:
        bm_prices: dict[str, dict[str, int]] = {}
        for bm in event.get("bookmakers", []):
            for market in bm.get("markets", []):
                if market["key"] == "h2h":
                    prices = {}
                    for outcome in market.get("outcomes", []):
                        prices[outcome["name"]] = outcome["price"]
                    bm_prices[bm["key"]] = prices

        for team_key in ("home_team", "away_team"):
            team_name = event[team_key]
            row: dict[str, str | int] = {"teamname": team_name}
            for bm_key in bookmakers_sorted:
                price = bm_prices.get(bm_key, {}).get(team_name, "")
                row[bm_key] = price
            rows.append(row)

    return rows


def _parse_futures(events: list[dict]) -> list[dict]:
    """Parse championship futures into rows: one per team with bookmaker columns."""
    bookmaker_names: set[str] = set()
    for event in events:
        for bm in event.get("bookmakers", []):
            bookmaker_names.add(bm["key"])

    bookmakers_sorted = sorted(bookmaker_names)

    team_odds: dict[str, dict[str, int]] = defaultdict(dict)
    for event in events:
        for bm in event.get("bookmakers", []):
            for market in bm.get("markets", []):
                for outcome in market.get("outcomes", []):
                    team_odds[outcome["name"]][bm["key"]] = outcome["price"]

    rows: list[dict] = []
    for team_name in sorted(team_odds):
        row: dict[str, str | int] = {"teamname": team_name}
        for bm_key in bookmakers_sorted:
            row[bm_key] = team_odds[team_name].get(bm_key, "")
        rows.append(row)

    return rows


def _write_csv(rows: list[dict], output: str) -> None:
    """Write rows to CSV file."""
    if not rows:
        click.echo("No data to write.", err=True)
        return

    fieldnames = list(rows[0].keys())
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    click.echo(f"Wrote {len(rows)} rows to {output}")


@click.group()
def cli() -> None:
    """Fetch NCAAB odds from The Odds API."""


@cli.command("game-odds")
@click.option("--output", "-o", default="game_odds.csv", help="Output CSV path")
def game_odds(output: str) -> None:
    """Fetch men's NCAAB game odds (h2h moneylines)."""
    result = _fetch_odds(SPORT_NCAAB, markets="h2h")
    if result["status"] != "ok":
        click.echo("Men's game odds are not currently available.", err=True)
        raise SystemExit(1)

    rows = _parse_game_odds(result["data"])
    _write_csv(rows, output)


@cli.command("mens-futures")
@click.option("--output", "-o", default="mens_futures.csv", help="Output CSV path")
def mens_futures(output: str) -> None:
    """Fetch men's NCAAB championship futures."""
    result = _fetch_odds(SPORT_NCAAB_CHAMP, markets="outrights")
    if result["status"] != "ok":
        click.echo("Men's championship futures are not currently available.", err=True)
        raise SystemExit(1)

    rows = _parse_futures(result["data"])
    _write_csv(rows, output)


@cli.command("womens-game-odds")
@click.option("--output", "-o", default="womens_game_odds.csv", help="Output CSV path")
def womens_game_odds(output: str) -> None:
    """Fetch women's NCAAB game odds (h2h moneylines).

    The basketball_wncaab sport key may be inactive outside tournament season.
    """
    result = _fetch_odds(SPORT_WNCAAB, markets="h2h")
    if result["status"] != "ok":
        click.echo(
            "Women's game odds (basketball_wncaab) are not currently active. "
            "This is expected outside tournament season.",
        )
        return

    rows = _parse_game_odds(result["data"])
    _write_csv(rows, output)


@cli.command("fetch-all")
@click.option("--output-dir", "-d", default=".", help="Output directory for CSV files")
def fetch_all(output_dir: str) -> None:
    """Fetch all available odds (mens game, mens futures, womens game)."""
    os.makedirs(output_dir, exist_ok=True)

    # Men's game odds
    click.echo("--- Men's game odds ---", err=True)
    result = _fetch_odds(SPORT_NCAAB, markets="h2h")
    if result["status"] == "ok":
        rows = _parse_game_odds(result["data"])
        _write_csv(rows, os.path.join(output_dir, "game_odds.csv"))
    else:
        click.echo("Men's game odds not available, skipping.", err=True)

    # Men's futures
    click.echo("--- Men's championship futures ---", err=True)
    result = _fetch_odds(SPORT_NCAAB_CHAMP, markets="outrights")
    if result["status"] == "ok":
        rows = _parse_futures(result["data"])
        _write_csv(rows, os.path.join(output_dir, "mens_futures.csv"))
    else:
        click.echo("Men's futures not available, skipping.", err=True)

    # Women's game odds (non-fatal if inactive)
    click.echo("--- Women's game odds ---", err=True)
    result = _fetch_odds(SPORT_WNCAAB, markets="h2h")
    if result["status"] == "ok":
        rows = _parse_game_odds(result["data"])
        _write_csv(rows, os.path.join(output_dir, "womens_game_odds.csv"))
    else:
        click.echo(
            "Women's game odds (basketball_wncaab) not active, skipping. "
            "Expected outside tournament season.",
            err=True,
        )


if __name__ == "__main__":
    cli()
