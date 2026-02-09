"""Ralph loop state management: init, status, complete, split, and add for prd.json."""

from __future__ import annotations

import json
from pathlib import Path

import click

PRD_FILE = Path("prd.json")


def _read_prd() -> dict:
    if not PRD_FILE.exists():
        raise click.ClickException(f"{PRD_FILE} not found. Run 'init' first.")
    return json.loads(PRD_FILE.read_text())


def _write_prd(data: dict) -> None:
    PRD_FILE.write_text(json.dumps(data, indent=2) + "\n")


@click.group()
def cli() -> None:
    """Ralph loop state management."""


@cli.command()
@click.argument("description")
@click.option("--branch", required=True, help="Feature branch name (e.g. ralph/feature-name)")
@click.option("--project", default="", help="Project name")
def init(description: str, branch: str, project: str) -> None:
    """Initialize a new ralph run with prd.json."""
    if PRD_FILE.exists():
        click.echo(f"{PRD_FILE} already exists. Delete it or switch branches first.")
        return

    prd = {
        "project": project or Path.cwd().name,
        "branchName": branch,
        "description": description,
        "userStories": [],
    }
    _write_prd(prd)
    click.echo(f"Created {PRD_FILE} for {branch}")


@cli.command()
def status() -> None:
    """Show current progress: incomplete and complete stories."""
    prd = _read_prd()
    stories = prd.get("userStories", [])
    total = len(stories)
    done = sum(1 for s in stories if s.get("passes"))
    incomplete = [s for s in stories if not s.get("passes")]

    click.echo(f"Project: {prd.get('project')} | Branch: {prd.get('branchName')}")
    click.echo(f"Progress: {done}/{total} stories complete\n")

    if incomplete:
        click.echo("Incomplete stories:")
        for s in sorted(incomplete, key=lambda x: x.get("priority", 99)):
            click.echo(f"  [{s['id']}] (priority {s.get('priority', '?')}) {s['title']}")
            for ac in s.get("acceptanceCriteria", []):
                click.echo(f"    - {ac}")
    else:
        click.echo("All stories complete!")


@cli.command()
@click.argument("story_id")
def complete(story_id: str) -> None:
    """Mark a story as passing in prd.json."""
    prd = _read_prd()
    story = next((s for s in prd["userStories"] if s["id"] == story_id), None)
    if not story:
        raise click.ClickException(f"Story {story_id} not found in {PRD_FILE}")

    story["passes"] = True
    _write_prd(prd)

    done = sum(1 for s in prd["userStories"] if s.get("passes"))
    total = len(prd["userStories"])
    click.echo(f"Marked {story_id} as passing ({done}/{total})")
    if done == total:
        click.echo("All stories complete!")


@cli.command()
@click.argument("story_id")
@click.argument("sub_titles", nargs=-1)
def split(story_id: str, sub_titles: tuple[str, ...]) -> None:
    """Split a story into sub-stories. Provide sub-story titles as arguments."""
    prd = _read_prd()
    idx = next((i for i, s in enumerate(prd["userStories"]) if s["id"] == story_id), None)
    if idx is None:
        raise click.ClickException(f"Story {story_id} not found")

    if not sub_titles:
        raise click.ClickException("Provide at least one sub-story title")

    parent = prd["userStories"][idx]
    base_priority = parent.get("priority", 1)

    new_stories = []
    for i, title in enumerate(sub_titles):
        sub_id = f"{story_id}-{chr(97 + i)}"
        new_stories.append(
            {
                "id": sub_id,
                "title": title,
                "description": f"Sub-story of {story_id}: {title}",
                "acceptanceCriteria": ["Typecheck passes", "Tests pass"],
                "priority": base_priority + i * 0.1,
                "passes": False,
            }
        )

    prd["userStories"] = prd["userStories"][:idx] + new_stories + prd["userStories"][idx + 1 :]
    _write_prd(prd)
    click.echo(f"Split {story_id} into {len(new_stories)} sub-stories:")
    for s in new_stories:
        click.echo(f"  [{s['id']}] {s['title']}")


@cli.command()
@click.argument("story_id")
@click.argument("title")
@click.argument("description", default="")
@click.option("--priority", type=float, default=0, help="Priority (0 = auto-append)")
@click.option("--criteria", "-c", multiple=True, help="Acceptance criteria")
def add(
    story_id: str, title: str, description: str, priority: float, criteria: tuple[str, ...]
) -> None:
    """Add a new user story to prd.json."""
    prd = _read_prd()
    if any(s["id"] == story_id for s in prd["userStories"]):
        raise click.ClickException(f"Story {story_id} already exists")

    if priority == 0:
        max_p = max((s.get("priority", 0) for s in prd["userStories"]), default=0)
        priority = max_p + 1

    ac = list(criteria) if criteria else ["Typecheck passes", "Tests pass"]

    prd["userStories"].append(
        {
            "id": story_id,
            "title": title,
            "description": description,
            "acceptanceCriteria": ac,
            "priority": priority,
            "passes": False,
        }
    )
    _write_prd(prd)
    click.echo(f"Added {story_id}: {title} (priority {priority})")


if __name__ == "__main__":
    cli()
