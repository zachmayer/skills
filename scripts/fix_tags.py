"""Fix junk tags in obsidian vault notes."""

import re
from pathlib import Path

import click

# Tags that are clearly junk (episode numbers, hex codes, IDs)
JUNK_PATTERN = re.compile(r"^(\d+|[0-9a-f]{4,}|gid|p\d+)$", re.IGNORECASE)

# Normalizations: old -> new
NORMALIZE = {
    "blueprint": "blueprints",
    "LTN": "ltn",
}


def is_junk_tag(tag: str) -> bool:
    """Check if a tag is junk (numeric, hex, ID)."""
    return bool(JUNK_PATTERN.match(tag))


def fix_tag_line(line: str) -> tuple[str, list[str]]:
    """Fix a tag line, returning (new_line, list_of_changes)."""
    changes = []
    tags = re.findall(r"#([a-zA-Z0-9_-]+)", line)
    if not tags:
        return line, changes

    new_line = line
    for tag in tags:
        if is_junk_tag(tag):
            # Remove junk tag
            new_line = re.sub(rf"\s*#{re.escape(tag)}\b", "", new_line)
            changes.append(f"removed #{tag}")
        elif tag in NORMALIZE:
            new_tag = NORMALIZE[tag]
            new_line = new_line.replace(f"#{tag}", f"#{new_tag}")
            changes.append(f"#{tag} -> #{new_tag}")

    # Clean up extra spaces
    new_line = re.sub(r"  +", " ", new_line).strip()
    return new_line, changes


@click.command()
@click.argument("vault_dir")
@click.option("--prefix", default="Factorio", help="Filter notes by filename prefix.")
@click.option("--dry-run", is_flag=True, help="Show changes without writing.")
def fix(vault_dir: str, prefix: str, dry_run: bool) -> None:
    """Fix junk tags in vault notes."""
    vault = Path(vault_dir).expanduser()
    notes = sorted(vault.rglob("*.md"))
    if prefix:
        notes = [n for n in notes if n.stem.startswith(prefix)]

    total_changes = 0

    for note_path in notes:
        content = note_path.read_text()
        lines = content.splitlines()
        new_lines = []
        note_changes = []

        for line in lines:
            # Only fix tag lines (lines that start with # but aren't headings)
            if re.match(r"^#[a-zA-Z]", line) and not line.startswith("##"):
                new_line, changes = fix_tag_line(line)
                new_lines.append(new_line)
                note_changes.extend(changes)
            else:
                new_lines.append(line)

        if note_changes:
            total_changes += len(note_changes)
            click.echo(f"{note_path.stem}:")
            for c in note_changes:
                click.echo(f"  {c}")

            if not dry_run:
                note_path.write_text(
                    "\n".join(new_lines) + "\n" if content.endswith("\n") else "\n".join(new_lines)
                )

    click.echo(
        f"\n{'Would fix' if dry_run else 'Fixed'} {total_changes} tags across {len(notes)} notes."
    )


if __name__ == "__main__":
    fix()
