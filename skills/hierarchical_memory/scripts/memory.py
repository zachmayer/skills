#!/usr/bin/env python3
"""Hierarchical memory management stored as markdown files."""

import os
import platform
import re
import subprocess
from datetime import datetime
from pathlib import Path

import click
import polars as pl

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
MEMORY_DIR = OBSIDIAN_DIR / "memory"
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"

DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
MONTHLY_RE = re.compile(r"^\d{4}-\d{2}\.md$")
OVERALL_FILENAME = "overall_memory.md"


def classify_file(filename: str) -> str:
    """Classify a memory file as 'daily', 'monthly', 'overall', or 'unknown'."""
    if DAILY_RE.match(filename):
        return "daily"
    if MONTHLY_RE.match(filename):
        return "monthly"
    if filename == OVERALL_FILENAME:
        return "overall"
    return "unknown"


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


def _repo_name() -> str:
    """Get the current git repo basename, or 'shell' if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).name
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return "shell"


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
    repo = _repo_name()
    with path.open("a") as f:
        f.write(f"- **{timestamp}** [{hostname}:{repo}]: {text}\n")

    click.echo(f"Saved to {path}")


@cli.command(name="list")
def list_cmd() -> None:
    """List all memory files with type and modification date."""
    md_files = sorted(MEMORY_DIR.glob("*.md"))
    if not md_files:
        click.echo("No memory files found.")
        return

    for f in md_files:
        ftype = classify_file(f.name)
        modified = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        marker = " [!]" if ftype == "unknown" else ""
        click.echo(f"  {f.name}  ({ftype})  modified: {modified}{marker}")

    unknowns = [f for f in md_files if classify_file(f.name) == "unknown"]
    if unknowns:
        click.echo(f"\nWarning: {len(unknowns)} unknown file(s) — not daily/monthly/overall.")


@cli.command(name="read-day")
@click.argument("date_str", default="")
def read_day(date_str: str) -> None:
    """Output a day's content. Default: today. Format: YYYY-MM-DD."""
    if date_str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            raise click.BadParameter("Expected YYYY-MM-DD", param_hint="'date_str'")
        path = MEMORY_DIR / f"{date_str}.md"
    else:
        path = daily_path()

    if path.exists():
        click.echo(path.read_text())
    else:
        date_label = date_str or datetime.now().strftime("%Y-%m-%d")
        click.echo(f"No notes for {date_label}.")


@cli.command(name="read-month")
@click.argument("month_str", default="")
def read_month(month_str: str) -> None:
    """Output a month's summary. Default: current month. Format: YYYY-MM."""
    if month_str:
        if not re.match(r"^\d{4}-\d{2}$", month_str):
            raise click.BadParameter("Expected YYYY-MM", param_hint="'month_str'")
        path = MEMORY_DIR / f"{month_str}.md"
    else:
        path = monthly_path()

    if path.exists():
        click.echo(path.read_text())
    else:
        month_label = month_str or datetime.now().strftime("%Y-%m")
        click.echo(f"No monthly summary for {month_label}.")


@cli.command(name="read-overall")
def read_overall() -> None:
    """Output overall_memory.md."""
    path = MEMORY_DIR / OVERALL_FILENAME
    if path.exists():
        click.echo(path.read_text())
    else:
        click.echo("No overall memory file found.")


@cli.command(name="read-current")
def read_current() -> None:
    """Output overall + current month + current day in one call."""
    overall_path = MEMORY_DIR / OVERALL_FILENAME
    month_path = monthly_path()
    day_path = daily_path()

    if overall_path.exists():
        click.echo("## Overall Memory\n")
        click.echo(overall_path.read_text())
    else:
        click.echo("## Overall Memory\n\n(not yet created)\n")

    click.echo("---\n")

    if month_path.exists():
        click.echo(f"## Current Month ({datetime.now().strftime('%Y-%m')})\n")
        click.echo(month_path.read_text())
    else:
        click.echo(f"## Current Month ({datetime.now().strftime('%Y-%m')})\n\n(not yet created)\n")

    click.echo("---\n")

    if day_path.exists():
        click.echo(f"## Today ({datetime.now().strftime('%Y-%m-%d')})\n")
        click.echo(day_path.read_text())
    else:
        click.echo(f"## Today ({datetime.now().strftime('%Y-%m-%d')})\n\n(no notes yet)\n")


@cli.command()
def status() -> None:
    """Show aggregation status: which monthly summaries need creating or updating."""
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
        monthly_lookup = monthly.select(
            pl.col("month"), pl.col("modified").alias("monthly_modified")
        )

        # Join each daily file with its month's summary timestamp
        daily_with_monthly = daily.join(monthly_lookup, on="month", how="left")

        # Stale files: daily files newer than their monthly summary
        stale = daily_with_monthly.filter(
            pl.col("monthly_modified").is_not_null()
            & (pl.col("modified") > pl.col("monthly_modified"))
        )
        stale_by_month = stale.group_by("month").agg(
            pl.col("filename").alias("stale_files"),
        )

        # Aggregate daily counts per month
        daily_by_month = daily.group_by("month").agg(
            pl.col("modified").max().alias("latest_daily"),
            pl.col("filename").count().alias("daily_count"),
        )
        joined = daily_by_month.join(monthly_lookup, on="month", how="left")

        needs_create = joined.filter(pl.col("monthly_modified").is_null())
        needs_update = joined.filter(
            pl.col("monthly_modified").is_not_null()
            & (pl.col("latest_daily") > pl.col("monthly_modified"))
        ).join(stale_by_month, on="month", how="left")
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
                names = ", ".join(row["stale_files"])
                click.echo(f"  - {row['month']} (stale: {names})")
        if not ok.is_empty():
            click.echo("**OK** — monthly summary is up to date:")
            for row in ok.sort("month").iter_rows(named=True):
                click.echo(f"  - {row['month']}")

    # Overall status
    click.echo("\n## Overall Status\n")
    if overall.is_empty() and monthly.is_empty():
        click.echo("No overall memory file found.")
    elif overall.is_empty():
        click.echo(
            f"**CREATE** — no {OVERALL_FILENAME} exists but monthly summaries are available."
        )
    elif monthly.is_empty():
        click.echo(f"{OVERALL_FILENAME} exists but no monthly summaries to compare against.")
    elif monthly["modified"].max() > overall["modified"].max():
        click.echo(f"**UPDATE** — monthly summaries are newer than {OVERALL_FILENAME}.")
    else:
        click.echo(f"**OK** — {OVERALL_FILENAME} is up to date.")

    # Knowledge graph listing
    if KNOWLEDGE_DIR.is_dir():
        click.echo("\n## Knowledge Graph\n")
        subdirs: dict[str, list[str]] = {}
        for md in sorted(KNOWLEDGE_DIR.rglob("*.md")):
            rel = md.relative_to(KNOWLEDGE_DIR)
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
