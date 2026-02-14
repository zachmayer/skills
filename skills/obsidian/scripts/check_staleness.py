#!/usr/bin/env python3
"""Check obsidian knowledge graph notes for staleness and missing metadata."""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import click

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"

# Matches "Source: <value>" line (case-insensitive)
SOURCE_RE = re.compile(r"^Source:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
# Matches "Date: <YYYY-MM-DD>" line (case-insensitive)
DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE | re.IGNORECASE)
# Matches http/https URLs
URL_RE = re.compile(r"^https?://\S+$")

DEFAULT_STALE_DAYS = 90


@dataclass
class NoteMetadata:
    """Parsed metadata from a single obsidian note."""

    path: Path
    source: str | None
    date: str | None
    has_url: bool

    @property
    def missing_date(self) -> bool:
        return self.date is None

    @property
    def missing_source(self) -> bool:
        return self.source is None

    def days_old(self, now: datetime | None = None) -> int | None:
        """Days since the note's Date field. None if no date."""
        if self.date is None:
            return None
        if now is None:
            now = datetime.now()
        try:
            note_date = datetime.strptime(self.date, "%Y-%m-%d")
            return (now - note_date).days
        except ValueError:
            return None

    def is_stale(
        self, threshold_days: int = DEFAULT_STALE_DAYS, now: datetime | None = None
    ) -> bool:
        """True if the note has a fetchable URL and is older than threshold_days."""
        if not self.has_url:
            return False
        days = self.days_old(now)
        if days is None:
            return False
        return days > threshold_days


def parse_note(path: Path) -> NoteMetadata:
    """Parse Source and Date metadata from a note file."""
    content = path.read_text(errors="replace")

    source_match = SOURCE_RE.search(content)
    date_match = DATE_RE.search(content)

    source = source_match.group(1).strip() if source_match else None
    date = date_match.group(1) if date_match else None
    has_url = bool(source and URL_RE.match(source))

    return NoteMetadata(path=path, source=source, date=date, has_url=has_url)


def scan_vault(vault_dir: Path | None = None) -> list[NoteMetadata]:
    """Scan all .md files in the knowledge graph and parse metadata."""
    root = vault_dir or KNOWLEDGE_DIR
    if not root.is_dir():
        return []
    notes = []
    for md in sorted(root.rglob("*.md")):
        notes.append(parse_note(md))
    return notes


@click.group()
def cli() -> None:
    """Obsidian knowledge graph staleness checker."""


@cli.command()
@click.argument("file_path")
@click.option("--days", default=DEFAULT_STALE_DAYS, help="Staleness threshold in days.")
def check(file_path: str, days: int) -> None:
    """Check a single note for staleness.

    Outputs a structured report: metadata present, age, stale status.
    Exit code 0 = fresh or no URL, 1 = stale and should be refreshed.
    """
    path = Path(file_path).expanduser()
    if not path.exists():
        raise click.ClickException(f"File not found: {path}")

    note = parse_note(path)
    now = datetime.now()
    age = note.days_old(now)
    stale = note.is_stale(days, now)

    click.echo(f"File: {note.path.name}")
    click.echo(f"Source: {note.source or '(missing)'}")
    click.echo(f"Date: {note.date or '(missing)'}")
    click.echo(f"Has URL: {note.has_url}")
    click.echo(f"Age: {age if age is not None else '(unknown)'} days")
    click.echo(f"Stale: {stale} (threshold: {days} days)")

    if stale:
        click.echo(f"\nREFRESH RECOMMENDED: Re-fetch {note.source} and update this note.")
        raise SystemExit(1)


@cli.command()
@click.option("--days", default=DEFAULT_STALE_DAYS, help="Staleness threshold in days.")
@click.option(
    "--vault-dir",
    default=None,
    help="Override vault directory (default: $CLAUDE_OBSIDIAN_DIR/knowledge_graph).",
)
def audit(days: int, vault_dir: str | None) -> None:
    """Audit all knowledge graph notes for staleness and missing metadata.

    Reports: stale notes, missing dates, missing sources.
    """
    root = Path(vault_dir) if vault_dir else None
    notes = scan_vault(root)

    if not notes:
        click.echo("No notes found.")
        return

    stale = [n for n in notes if n.is_stale(days)]
    missing_date = [n for n in notes if n.missing_date]
    missing_source = [n for n in notes if n.missing_source]
    with_url = [n for n in notes if n.has_url]

    click.echo("## Obsidian Knowledge Graph Audit\n")
    click.echo(f"Total notes: {len(notes)}")
    click.echo(f"With Source URL: {len(with_url)}")
    click.echo(f"Missing Date: {len(missing_date)}")
    click.echo(f"Missing Source: {len(missing_source)}")
    click.echo(f"Stale (>{days} days, has URL): {len(stale)}")

    if stale:
        click.echo("\n### Stale Notes (refresh recommended)\n")
        for n in sorted(stale, key=lambda x: x.days_old() or 0, reverse=True):
            rel = (
                n.path.relative_to(root or KNOWLEDGE_DIR)
                if (root or KNOWLEDGE_DIR) in n.path.parents
                or n.path.parent == (root or KNOWLEDGE_DIR)
                else n.path.name
            )
            click.echo(f"- {rel} ({n.days_old()} days old) — {n.source}")

    if missing_date:
        click.echo("\n### Missing Date\n")
        for n in missing_date[:20]:
            rel = (
                n.path.relative_to(root or KNOWLEDGE_DIR)
                if (root or KNOWLEDGE_DIR) in n.path.parents
                or n.path.parent == (root or KNOWLEDGE_DIR)
                else n.path.name
            )
            click.echo(f"- {rel}")
        if len(missing_date) > 20:
            click.echo(f"  ... and {len(missing_date) - 20} more")

    if missing_source:
        click.echo("\n### Missing Source\n")
        for n in missing_source[:20]:
            rel = (
                n.path.relative_to(root or KNOWLEDGE_DIR)
                if (root or KNOWLEDGE_DIR) in n.path.parents
                or n.path.parent == (root or KNOWLEDGE_DIR)
                else n.path.name
            )
            click.echo(f"- {rel}")
        if len(missing_source) > 20:
            click.echo(f"  ... and {len(missing_source) - 20} more")


@cli.command(name="stale-urls")
@click.option("--days", default=DEFAULT_STALE_DAYS, help="Staleness threshold in days.")
@click.option(
    "--vault-dir",
    default=None,
    help="Override vault directory (default: $CLAUDE_OBSIDIAN_DIR/knowledge_graph).",
)
def stale_urls(days: int, vault_dir: str | None) -> None:
    """List just the stale notes with URLs, one per line.

    Output format: <file_path>|<source_url>|<age_days>
    Useful for piping into refresh workflows.
    """
    root = Path(vault_dir) if vault_dir else None
    notes = scan_vault(root)
    stale = [n for n in notes if n.is_stale(days)]

    for n in sorted(stale, key=lambda x: x.days_old() or 0, reverse=True):
        click.echo(f"{n.path}|{n.source}|{n.days_old()}")


if __name__ == "__main__":
    cli()
