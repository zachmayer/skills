"""Mobile bridge: capture messages from phone via ntfy into memory/obsidian."""

import json
import os
import subprocess
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

import click

NTFY_BASE = "https://ntfy.sh"


def _get_topic() -> str:
    """Get ntfy topic from environment."""
    topic = os.environ.get("CLAUDE_NTFY_TOPIC", "")
    if not topic:
        click.echo("Error: CLAUDE_NTFY_TOPIC not set. Run setup first.", err=True)
        sys.exit(1)
    return topic


def _get_obsidian_dir() -> Path:
    """Get obsidian vault directory."""
    raw = os.environ.get("CLAUDE_OBSIDIAN_DIR", "~/claude/obsidian")
    return Path(raw).expanduser()


def _poll_messages(topic: str, since: str = "24h") -> list[dict]:
    """Poll ntfy for messages in the given time window."""
    url = f"{NTFY_BASE}/{topic}/json?poll=1&since={since}"
    req = Request(url)
    try:
        with urlopen(req, timeout=10) as resp:
            lines = resp.read().decode().strip().split("\n")
    except URLError as e:
        click.echo(f"Error polling ntfy: {e}", err=True)
        return []

    messages = []
    for line in lines:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            if msg.get("event") == "message":
                messages.append(msg)
        except json.JSONDecodeError:
            continue
    return messages


def _format_message(msg: dict) -> str:
    """Format a single ntfy message for display."""
    ts = msg.get("time", 0)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    title = msg.get("title", "")
    body = msg.get("message", "")
    prefix = f"[{time_str}]"
    if title:
        return f"{prefix} {title}: {body}"
    return f"{prefix} {body}"


def _save_to_memory(messages: list[dict], obsidian_dir: Path) -> Path:
    """Append messages to today's memory daily note."""
    memory_dir = obsidian_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    daily_file = memory_dir / f"{today}.md"

    header = f"# Notes for {today}\n"
    existing = ""
    if daily_file.exists():
        existing = daily_file.read_text()

    if not existing:
        existing = header + "\n"

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    lines = []
    for msg in messages:
        body = msg.get("message", "").strip()
        title = msg.get("title", "").strip()
        if title:
            lines.append(f"- **{now}** [mobile]: {title} — {body}")
        else:
            lines.append(f"- **{now}** [mobile]: {body}")

    new_content = existing.rstrip() + "\n" + "\n".join(lines) + "\n"
    daily_file.write_text(new_content)
    return daily_file


def _save_to_obsidian(messages: list[dict], obsidian_dir: Path) -> Path:
    """Save messages as a note in the knowledge graph."""
    kg_dir = obsidian_dir / "knowledge_graph"
    kg_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    note_file = kg_dir / f"Mobile Captures {today}.md"

    lines = [
        f"# Mobile Captures {today}",
        "",
        "#mobile #capture",
        "",
        "Source: ntfy mobile bridge",
        f"Date: {today}",
        "",
    ]
    for msg in messages:
        body = msg.get("message", "").strip()
        title = msg.get("title", "").strip()
        ts = msg.get("time", 0)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        time_str = dt.strftime("%H:%M UTC")
        if title:
            lines.append(f"- **{time_str}** {title}: {body}")
        else:
            lines.append(f"- **{time_str}** {body}")

    lines.append("")
    note_file.write_text("\n".join(lines))
    return note_file


def _send_message(topic: str, message: str, title: str | None = None) -> bool:
    """Send a message to the ntfy topic (phone notification)."""
    url = f"{NTFY_BASE}/{topic}"
    headers = {"Content-Type": "text/plain"}
    if title:
        headers["Title"] = title

    data = message.encode()
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except URLError as e:
        click.echo(f"Error sending message: {e}", err=True)
        return False


@click.group()
def cli() -> None:
    """Mobile bridge: capture phone messages into memory/obsidian."""


@cli.command()
@click.option("--since", default="24h", help="Time window to check (e.g. 1h, 24h, 7d)")
def check(since: str) -> None:
    """Check for pending messages from phone."""
    topic = _get_topic()
    messages = _poll_messages(topic, since=since)

    if not messages:
        click.echo("No messages.")
        return

    click.echo(f"{len(messages)} message(s):\n")
    for msg in messages:
        click.echo(f"  {_format_message(msg)}")


@cli.command()
@click.option("--since", default="24h", help="Time window to process (e.g. 1h, 24h, 7d)")
@click.option(
    "--route",
    type=click.Choice(["memory", "obsidian", "both"]),
    default="memory",
    help="Where to save messages",
)
def process(since: str, route: str) -> None:
    """Process pending messages and save to memory/obsidian."""
    topic = _get_topic()
    obsidian_dir = _get_obsidian_dir()
    messages = _poll_messages(topic, since=since)

    if not messages:
        click.echo("No messages to process.")
        return

    click.echo(f"Processing {len(messages)} message(s)...")

    saved_to = []
    if route in ("memory", "both"):
        path = _save_to_memory(messages, obsidian_dir)
        saved_to.append(f"memory ({path})")

    if route in ("obsidian", "both"):
        path = _save_to_obsidian(messages, obsidian_dir)
        saved_to.append(f"obsidian ({path})")

    click.echo(f"Saved to: {', '.join(saved_to)}")

    # Git commit the obsidian changes
    try:
        subprocess.run(
            ["git", "-C", str(obsidian_dir), "add", "-A"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(obsidian_dir),
                "commit",
                "-m",
                f"mobile: {len(messages)} captured message(s)",
            ],
            check=True,
            capture_output=True,
        )
        click.echo("Committed to obsidian vault.")
    except subprocess.CalledProcessError:
        click.echo("No changes to commit (or not a git repo).")


@cli.command()
@click.argument("message")
@click.option("--title", default=None, help="Notification title")
def send(message: str, title: str | None) -> None:
    """Send a message to phone via ntfy."""
    topic = _get_topic()
    if _send_message(topic, message, title=title):
        click.echo("Sent.")
    else:
        click.echo("Failed to send.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
