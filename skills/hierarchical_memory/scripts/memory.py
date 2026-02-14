#!/usr/bin/env python3
"""Hierarchical memory management stored as markdown files."""

import os
import platform
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path

import click

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
MEMORY_DIR = OBSIDIAN_DIR / "memory"
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"

DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
MONTHLY_RE = re.compile(r"^\d{4}-\d{2}\.md$")
OVERALL_FILENAME = "overall_memory.md"

# Freshness: date patterns to extract from memory content
_ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_MONTH_YEAR_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})\b", re.IGNORECASE
)
_YYYY_MM_RE = re.compile(r"\b(\d{4}-\d{2})\b")
DEFAULT_FRESHNESS_DAYS = 30


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


def _parse_month_name(name: str) -> int:
    """Convert month name abbreviation to month number."""
    months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    return months.get(name[:3].lower(), 0)


@dataclass
class DatedFact:
    """A line from overall_memory.md with an extracted date."""

    line_num: int
    text: str
    date: datetime
    age_days: int


def _extract_dated_facts(content: str, now: datetime | None = None) -> list[DatedFact]:
    """Extract lines with date references from overall_memory.md content."""
    if now is None:
        now = datetime.now()
    facts: list[DatedFact] = []
    seen_lines: set[int] = set()

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        best_date: datetime | None = None

        # Try ISO dates first (most specific)
        for m in _ISO_DATE_RE.finditer(line):
            try:
                d = datetime.strptime(m.group(1), "%Y-%m-%d")
                if best_date is None or d > best_date:
                    best_date = d
            except ValueError:
                continue

        # Try "Month YYYY" patterns
        if best_date is None:
            for m in _MONTH_YEAR_RE.finditer(line):
                month_num = _parse_month_name(m.group(1))
                year = int(m.group(2))
                if month_num and 2000 <= year <= 2100:
                    d = datetime(year, month_num, 1)
                    if best_date is None or d > best_date:
                        best_date = d

        # Try YYYY-MM patterns (but not if already matched as YYYY-MM-DD)
        if best_date is None:
            for m in _YYYY_MM_RE.finditer(line):
                try:
                    d = datetime.strptime(m.group(1), "%Y-%m")
                    if best_date is None or d > best_date:
                        best_date = d
                except ValueError:
                    continue

        if best_date is not None and i not in seen_lines:
            seen_lines.add(i)
            age = (now - best_date).days
            facts.append(DatedFact(line_num=i, text=stripped, date=best_date, age_days=age))

    return facts


def _overall_age_days(now: datetime | None = None) -> int | None:
    """Return days since overall_memory.md was last modified, or None if missing."""
    path = MEMORY_DIR / OVERALL_FILENAME
    if not path.exists():
        return None
    if now is None:
        now = datetime.now()
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return (now - mtime).days


def _freshness_warning(now: datetime | None = None) -> str | None:
    """Return a one-line freshness warning if overall_memory.md is stale, else None."""
    age = _overall_age_days(now)
    if age is None:
        return None
    if age >= DEFAULT_FRESHNESS_DAYS:
        return f"[Freshness] overall_memory.md is {age} days old — facts may be stale. Run `freshness` to check."
    return None


@dataclass
class StalenessReport:
    """Aggregation staleness across monthly and overall files."""

    needs_create: list[dict[str, object]] = field(default_factory=list)  # month, daily_count
    needs_update: list[dict[str, object]] = field(default_factory=list)  # month, stale_files
    ok: list[str] = field(default_factory=list)  # months
    overall: str = ""  # "CREATE" | "UPDATE" | "OK" | "NO_MONTHLY" | ""


def _compute_staleness() -> StalenessReport | None:
    """Compute aggregation staleness from memory files. Returns None if no files."""
    md_files = list(MEMORY_DIR.glob("*.md"))
    if not md_files:
        return None

    # Pass 1: build lookup tables
    daily_by_month: dict[str, list[tuple[float, str]]] = defaultdict(list)
    monthly_mtime: dict[str, float] = {}
    overall_mtime: float | None = None

    for f in md_files:
        name = f.name
        mtime = f.stat().st_mtime
        kind = classify_file(name)
        if kind == "daily":
            daily_by_month[name[:7]].append((mtime, name))
        elif kind == "monthly":
            monthly_mtime[name[:7]] = mtime
        elif kind == "overall":
            overall_mtime = mtime

    # Pass 2: classify each month
    needs_create: list[dict[str, object]] = []
    needs_update: list[dict[str, object]] = []
    ok: list[str] = []

    for month in sorted(daily_by_month):
        dailies = daily_by_month[month]
        mm = monthly_mtime.get(month)
        if mm is None:
            needs_create.append({"month": month, "daily_count": len(dailies)})
        elif max(m for m, _ in dailies) > mm:
            stale_files = sorted(name for m, name in dailies if m > mm)
            needs_update.append({"month": month, "stale_files": stale_files})
        else:
            ok.append(month)

    # Overall status
    if overall_mtime is None and not monthly_mtime:
        overall_status = ""
    elif overall_mtime is None:
        overall_status = "CREATE"
    elif not monthly_mtime:
        overall_status = "NO_MONTHLY"
    elif max(monthly_mtime.values()) > overall_mtime:
        overall_status = "UPDATE"
    else:
        overall_status = "OK"

    return StalenessReport(
        needs_create=needs_create,
        needs_update=needs_update,
        ok=ok,
        overall=overall_status,
    )


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

    report = _compute_staleness()
    if report is None:
        click.echo("Aggregation: up to date")
        return
    issues = []
    for entry in report.needs_create:
        issues.append(f"{entry['month']} CREATE")
    for entry in report.needs_update:
        issues.append(f"{entry['month']} UPDATE")
    if report.overall in ("CREATE", "UPDATE"):
        issues.append(f"overall {report.overall}")
    click.echo(f"Aggregation stale: {', '.join(issues)}" if issues else "Aggregation: up to date")


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
    """Output overall_memory.md with freshness warning if stale."""
    path = MEMORY_DIR / OVERALL_FILENAME
    if path.exists():
        warning = _freshness_warning()
        if warning:
            click.echo(warning + "\n")
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
        warning = _freshness_warning()
        if warning:
            click.echo(warning + "\n")
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
@click.option(
    "--days", default=DEFAULT_FRESHNESS_DAYS, help="Flag facts older than this many days."
)
def freshness(days: int) -> None:
    """Check fact freshness in overall_memory.md. Flags dated facts older than --days."""
    path = MEMORY_DIR / OVERALL_FILENAME
    if not path.exists():
        click.echo("No overall memory file found.")
        return

    age = _overall_age_days()
    click.echo("## Fact Freshness Report\n")
    click.echo(f"overall_memory.md last modified: {age} days ago\n")

    content = path.read_text()
    facts = _extract_dated_facts(content)

    if not facts:
        click.echo("No dated facts found in overall_memory.md.")
        return

    stale = [f for f in facts if f.age_days >= days]
    fresh = [f for f in facts if f.age_days < days]

    if stale:
        click.echo(f"**STALE** ({len(stale)} facts older than {days} days):\n")
        for f in sorted(stale, key=lambda x: x.age_days, reverse=True):
            truncated = f.text[:120] + "..." if len(f.text) > 120 else f.text
            click.echo(f"  L{f.line_num} ({f.age_days}d): {truncated}")
        click.echo()

    click.echo(f"**Summary**: {len(stale)} stale, {len(fresh)} fresh (of {len(facts)} dated facts)")
    if stale:
        click.echo("\nConsider verifying stale facts with the user before relying on them.")


@cli.command()
def status() -> None:
    """Show aggregation status: which monthly summaries need creating or updating."""
    report = _compute_staleness()
    if report is None:
        click.echo("No memory files found.")
        return

    has_daily = report.needs_create or report.needs_update or report.ok

    if not has_daily:
        click.echo("No daily files found.")
    else:
        click.echo("## Monthly Aggregation Status\n")
        if report.needs_create:
            click.echo("**CREATE** — no monthly summary exists:")
            for entry in report.needs_create:
                click.echo(f"  - {entry['month']} ({entry['daily_count']} daily files)")
        if report.needs_update:
            click.echo("**UPDATE** — daily files newer than monthly summary:")
            for entry in report.needs_update:
                names = ", ".join(entry["stale_files"])
                click.echo(f"  - {entry['month']} (stale: {names})")
        if report.ok:
            click.echo("**OK** — monthly summary is up to date:")
            for month in report.ok:
                click.echo(f"  - {month}")

    # Overall status
    click.echo("\n## Overall Status\n")
    if report.overall == "":
        click.echo("No overall memory file found.")
    elif report.overall == "NO_MONTHLY":
        click.echo(f"{OVERALL_FILENAME} exists but no monthly summaries to compare against.")
    elif report.overall == "CREATE":
        click.echo(
            f"**CREATE** — no {OVERALL_FILENAME} exists but monthly summaries are available."
        )
    elif report.overall == "UPDATE":
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
