#!/usr/bin/env python3
"""Hierarchical memory management stored as markdown files."""

import os
import platform
import re
from datetime import datetime
from pathlib import Path

import click

MEMORY_DIR = Path(
    os.environ.get("CLAUDE_MEMORY_DIR", str(Path.home() / "claude" / "obsidian" / "memory"))
)
OBSIDIAN_ROOT = Path.home() / "claude" / "obsidian"
VAULT_DIR = OBSIDIAN_ROOT / "Zach"

DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
MONTHLY_RE = re.compile(r"^\d{4}-\d{2}\.md$")


def classify_file(filename: str) -> str:
    """Classify a memory file as 'daily', 'monthly', or 'overall'."""
    if DAILY_RE.match(filename):
        return "daily"
    if MONTHLY_RE.match(filename):
        return "monthly"
    return "overall"


def month_from_filename(filename: str) -> str | None:
    """Extract YYYY-MM from a daily or monthly filename, or None for overall."""
    if DAILY_RE.match(filename):
        return filename[:7]
    if MONTHLY_RE.match(filename):
        return filename[:7]
    return None


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

    hostname = platform.node().split(".")[0]
    with path.open("a") as f:
        f.write(f"- **{timestamp}** [{hostname}]: {text}\n")

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
    """Show notes for a specific date (YYYY-MM-DD), month (YYYY-MM), or overall (memory)."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}$|^memory$", date_str):
        raise click.BadParameter(
            "Expected YYYY-MM-DD, YYYY-MM, or 'memory'", param_hint="'date_str'"
        )
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


@cli.command()
def status() -> None:
    """Show aggregation status: which monthly summaries need creating or updating."""
    import polars as pl

    md_files = sorted(MEMORY_DIR.glob("*.md"))
    if not md_files:
        click.echo("No memory files found.")
        return

    rows = []
    for f in md_files:
        rows.append(
            {
                "filename": f.name,
                "file_type": classify_file(f.name),
                "month": month_from_filename(f.name),
                "modified": datetime.fromtimestamp(f.stat().st_mtime),
            }
        )

    df = pl.DataFrame(rows)

    # Daily files grouped by month
    daily = df.filter(pl.col("file_type") == "daily")
    monthly = df.filter(pl.col("file_type") == "monthly")
    overall = df.filter(pl.col("file_type") == "overall")

    if daily.is_empty():
        click.echo("No daily files found.")
    else:
        daily_by_month = daily.group_by("month").agg(
            pl.col("modified").max().alias("latest_daily"),
            pl.col("filename").count().alias("daily_count"),
            pl.col("filename").alias("daily_files"),
        )

        monthly_lookup = monthly.select(
            pl.col("month"), pl.col("modified").alias("monthly_modified")
        )
        joined = daily_by_month.join(monthly_lookup, on="month", how="left")

        needs_create = joined.filter(pl.col("monthly_modified").is_null())
        needs_update = joined.filter(
            pl.col("monthly_modified").is_not_null()
            & (pl.col("latest_daily") > pl.col("monthly_modified"))
        )
        ok = joined.filter(
            pl.col("monthly_modified").is_not_null()
            & (pl.col("latest_daily") <= pl.col("monthly_modified"))
        )

        click.echo("## Monthly Aggregation Status\n")
        if not needs_create.is_empty():
            click.echo("**CREATE** — no monthly summary exists:")
            for row in needs_create.sort("month").iter_rows(named=True):
                click.echo(f"  - {row['month']} ({row['daily_count']} daily files)")
        if not needs_update.is_empty():
            click.echo("**UPDATE** — daily files newer than monthly summary:")
            for row in needs_update.sort("month").iter_rows(named=True):
                stale_files = [
                    f
                    for f, m in zip(
                        daily.filter(pl.col("month") == row["month"])["filename"].to_list(),
                        daily.filter(pl.col("month") == row["month"])["modified"].to_list(),
                    )
                    if m > row["monthly_modified"]
                ]
                click.echo(f"  - {row['month']} (stale: {', '.join(stale_files)})")
        if not ok.is_empty():
            click.echo("**OK** — monthly summary is up to date:")
            for row in ok.sort("month").iter_rows(named=True):
                click.echo(f"  - {row['month']}")

    # Overall status
    click.echo("\n## Overall Status\n")
    if overall.is_empty():
        if not monthly.is_empty():
            click.echo("**CREATE** — no memory.md exists but monthly summaries are available.")
        else:
            click.echo("No overall memory file found.")
    elif not monthly.is_empty():
        overall_modified = overall["modified"].max()
        latest_monthly = monthly["modified"].max()
        if latest_monthly > overall_modified:
            click.echo("**UPDATE** — monthly summaries are newer than memory.md.")
        else:
            click.echo("**OK** — memory.md is up to date.")
    else:
        click.echo("memory.md exists but no monthly summaries to compare against.")

    # Obsidian vault listing
    if VAULT_DIR.is_dir():
        click.echo("\n## Obsidian Vault\n")
        subdirs: dict[str, list[str]] = {}
        for md in sorted(VAULT_DIR.rglob("*.md")):
            rel = md.relative_to(VAULT_DIR)
            parent = str(rel.parent) if rel.parent != Path(".") else "(root)"
            subdirs.setdefault(parent, []).append(rel.name)
        for subdir in sorted(subdirs):
            click.echo(f"**{subdir}/** ({len(subdirs[subdir])} files)")
            for name in subdirs[subdir][:5]:
                click.echo(f"  - {name}")
            if len(subdirs[subdir]) > 5:
                click.echo(f"  - ... and {len(subdirs[subdir]) - 5} more")


if __name__ == "__main__":
    cli()
