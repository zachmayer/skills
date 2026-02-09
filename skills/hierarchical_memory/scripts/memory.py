#!/usr/bin/env python3
"""Hierarchical memory management stored as markdown files."""

import os
from datetime import datetime
from pathlib import Path

import click

MEMORY_DIR = Path(
    os.environ.get("CLAUDE_MEMORY_DIR", str(Path.home() / "claude" / "obsidian" / "memory"))
)


def daily_path(date: datetime | None = None) -> Path:
    """Get the path for a daily notes file."""
    if date is None:
        date = datetime.now()
    return MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"


def monthly_path(date: datetime | None = None) -> Path:
    """Get the path for a monthly summary file."""
    if date is None:
        date = datetime.now()
    return MEMORY_DIR / f"{date.strftime('%Y-%m')}.md"


@click.group()
def cli() -> None:
    """Hierarchical memory: daily notes, monthly summaries, overall memory."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


@cli.command()
@click.argument("text")
def note(text: str) -> None:
    """Append a timestamped note to today's daily file."""
    now = datetime.now()
    path = daily_path(now)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")

    if not path.exists():
        path.write_text(f"# Notes for {now.strftime('%Y-%m-%d')}\n\n")

    with path.open("a") as f:
        f.write(f"- **{timestamp}**: {text}\n")

    click.echo(f"Saved to {path}")


@cli.command()
def today() -> None:
    """Show today's notes."""
    path = daily_path()
    if path.exists():
        click.echo(path.read_text())
    else:
        click.echo("No notes for today.")


@cli.command()
@click.argument("date_str")
def show(date_str: str) -> None:
    """Show notes for a specific date (YYYY-MM-DD) or month (YYYY-MM)."""
    path = MEMORY_DIR / f"{date_str}.md"
    if path.exists():
        click.echo(path.read_text())
    else:
        click.echo(f"No notes found for {date_str}")


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Search all notes for a query string."""
    query_lower = query.lower()
    results: list[str] = []

    for md_file in sorted(MEMORY_DIR.glob("*.md")):
        content = md_file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if query_lower in line.lower():
                results.append(f"{md_file.name}:{i}: {line.strip()}")

    if results:
        click.echo(f"Found {len(results)} matches:\n")
        for r in results:
            click.echo(r)
    else:
        click.echo(f"No matches for '{query}'")


if __name__ == "__main__":
    cli()
