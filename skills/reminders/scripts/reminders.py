#!/usr/bin/env python3
"""Time-aware reminder system stored as JSON in the obsidian vault."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import click

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
MEMORY_DIR = OBSIDIAN_DIR / "memory"
REMINDERS_FILE = MEMORY_DIR / "reminders.json"


def _load_reminders() -> list[dict]:
    """Load reminders from JSON file."""
    if not REMINDERS_FILE.exists():
        return []
    return json.loads(REMINDERS_FILE.read_text())


def _save_reminders(reminders: list[dict]) -> None:
    """Save reminders to JSON file."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    REMINDERS_FILE.write_text(json.dumps(reminders, indent=2) + "\n")


def _parse_due(due_str: str) -> datetime:
    """Parse a due date/time string. Supports YYYY-MM-DD and YYYY-MM-DDTHH:MM."""
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(due_str, fmt)
        except ValueError:
            continue
    raise click.BadParameter(
        f"Cannot parse '{due_str}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM.",
        param_hint="'due'",
    )


def _format_reminder(r: dict, now: datetime | None = None) -> str:
    """Format a single reminder for display."""
    if now is None:
        now = datetime.now()
    due = datetime.fromisoformat(r["due"])
    status = "DONE" if r.get("completed") else ("OVERDUE" if due <= now else "pending")
    return f"  [{status}] {r['id'][:8]}  due: {r['due']}  {r['text']}"


@click.group()
def cli() -> None:
    """Time-aware reminders stored in the obsidian vault."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


@cli.command()
@click.argument("text")
@click.argument("due")
def add(text: str, due: str) -> None:
    """Add a reminder. Args: TEXT DUE (YYYY-MM-DD or YYYY-MM-DDTHH:MM)."""
    due_dt = _parse_due(due)
    reminder = {
        "id": uuid.uuid4().hex,
        "text": text,
        "due": due_dt.isoformat(),
        "created": datetime.now().isoformat(),
        "completed": False,
    }
    reminders = _load_reminders()
    reminders.append(reminder)
    _save_reminders(reminders)
    click.echo(f"Added: {reminder['id'][:8]} — {text} (due {due_dt.strftime('%Y-%m-%d %H:%M')})")


@cli.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Include completed reminders.")
def list_cmd(show_all: bool) -> None:
    """List reminders. By default hides completed ones."""
    reminders = _load_reminders()
    if not reminders:
        click.echo("No reminders.")
        return

    now = datetime.now()
    visible = reminders if show_all else [r for r in reminders if not r.get("completed")]
    if not visible:
        click.echo("No active reminders. Use --all to see completed ones.")
        return

    # Sort: overdue first, then by due date
    visible.sort(key=lambda r: (r.get("completed", False), r["due"]))
    for r in visible:
        click.echo(_format_reminder(r, now))


@cli.command()
def due() -> None:
    """Show reminders that are due or overdue right now."""
    reminders = _load_reminders()
    now = datetime.now()
    due_reminders = [
        r for r in reminders if not r.get("completed") and datetime.fromisoformat(r["due"]) <= now
    ]
    if not due_reminders:
        click.echo("No reminders due.")
        return

    click.echo(f"{len(due_reminders)} reminder(s) due:\n")
    for r in sorted(due_reminders, key=lambda r: r["due"]):
        click.echo(_format_reminder(r, now))


@cli.command()
@click.argument("reminder_id")
def complete(reminder_id: str) -> None:
    """Mark a reminder as completed. Takes the 8-char short ID."""
    reminders = _load_reminders()
    matches = [r for r in reminders if r["id"].startswith(reminder_id)]
    if not matches:
        raise click.ClickException(f"No reminder found matching '{reminder_id}'.")
    if len(matches) > 1:
        raise click.ClickException(
            f"Ambiguous ID '{reminder_id}' — matches {len(matches)} reminders. Use more characters."
        )
    matches[0]["completed"] = True
    _save_reminders(reminders)
    click.echo(f"Completed: {matches[0]['text']}")


@cli.command()
@click.argument("reminder_id")
def remove(reminder_id: str) -> None:
    """Remove a reminder permanently. Takes the 8-char short ID."""
    reminders = _load_reminders()
    matches = [r for r in reminders if r["id"].startswith(reminder_id)]
    if not matches:
        raise click.ClickException(f"No reminder found matching '{reminder_id}'.")
    if len(matches) > 1:
        raise click.ClickException(
            f"Ambiguous ID '{reminder_id}' — matches {len(matches)} reminders. Use more characters."
        )
    reminders.remove(matches[0])
    _save_reminders(reminders)
    click.echo(f"Removed: {matches[0]['text']}")


if __name__ == "__main__":
    cli()
