"""Normalize flat-file skills (skills/<name>.md) into directory format (skills/<name>/SKILL.md)."""

from pathlib import Path

import click


@click.command()
@click.option(
    "--skills-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default="skills",
    help="Skills directory to normalize.",
)
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes.")
def normalize(skills_dir: Path, dry_run: bool) -> None:
    """Convert flat-file skills into name/SKILL.md directories."""
    flat_files = sorted(f for f in skills_dir.glob("*.md") if f.is_file())

    if not flat_files:
        click.echo("No flat-file skills found.")
        return

    for flat_file in flat_files:
        name = flat_file.stem
        target_dir = skills_dir / name

        if target_dir.exists():
            click.echo(f"  SKIP {flat_file.name} — {name}/ already exists")
            continue

        if dry_run:
            click.echo(f"  WOULD {flat_file.name} → {name}/SKILL.md")
        else:
            target_dir.mkdir()
            flat_file.rename(target_dir / "SKILL.md")
            click.echo(f"  {flat_file.name} → {name}/SKILL.md")


if __name__ == "__main__":
    normalize()
