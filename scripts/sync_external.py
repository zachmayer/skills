"""Sync external skills from upstream repositories.

Reads external_skills.yaml and downloads each skill's SKILL.md from
its upstream URL. Patches frontmatter: ensures `name` matches local
directory and injects any extra fields from the manifest (e.g. max_lines).
"""

import re
from pathlib import Path
from urllib.request import urlopen

import click
import yaml

RESERVED_KEYS = {"name", "url"}


@click.command()
@click.option(
    "--manifest",
    default="external_skills.yaml",
    type=click.Path(exists=True),
    help="YAML manifest mapping skill names to upstream URLs.",
)
def sync(manifest: str) -> None:
    """Pull external skills listed in the manifest."""
    skills: list[dict[str, str]] = yaml.safe_load(Path(manifest).read_text())

    for entry in skills:
        name = entry["name"]
        url = entry["url"]
        extras = {k: v for k, v in entry.items() if k not in RESERVED_KEYS}
        dest = Path("skills") / name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)

        click.echo(f"  {name} <- {url}")
        content = urlopen(url).read().decode()  # noqa: S310

        # Ensure frontmatter name matches local directory name
        content = re.sub(
            r"^(name:\s*)\S+",
            rf"\g<1>{name}",
            content,
            count=1,
            flags=re.MULTILINE,
        )

        # Inject extra manifest fields into frontmatter
        if extras:
            extra_yaml = "\n".join(f"{k}: {v}" for k, v in extras.items())
            content = re.sub(
                r"^(name:\s*.+)$",
                rf"\1\n{extra_yaml}",
                content,
                count=1,
                flags=re.MULTILINE,
            )

        dest.write_text(content)

    click.echo(f"Synced {len(skills)} external skills.")


if __name__ == "__main__":
    sync()
