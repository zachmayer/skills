"""Audit obsidian vault notes for metadata, hierarchy, and tag consistency."""

import re
from pathlib import Path

import click


def parse_note(path: Path) -> dict:
    """Parse a note file and extract metadata."""
    content = path.read_text()
    lines = content.splitlines()

    result = {
        "path": str(path),
        "filename": path.stem,
        "lines": len(lines),
        "has_source": False,
        "source_url": "",
        "has_date": False,
        "date_value": "",
        "tags": [],
        "wiki_links": [],
        "has_related_section": False,
        "related_links": [],
        "issues": [],
    }

    for line in lines:
        # Check for Source
        if re.match(r"^Source:\s*", line):
            result["has_source"] = True
            result["source_url"] = line.split("Source:", 1)[1].strip()

        # Check for Grabbed or Date
        if re.match(r"^(Grabbed|Date):\s*", line):
            result["has_date"] = True
            result["date_value"] = re.split(r":\s*", line, 1)[1].strip()

        # Extract tags
        tag_matches = re.findall(r"#([a-zA-Z0-9_-]+)", line)
        if tag_matches and not line.startswith("##"):
            result["tags"].extend(tag_matches)

        # Extract wiki-links
        link_matches = re.findall(r"\[\[([^\]]+)\]\]", line)
        result["wiki_links"].extend(link_matches)

        # Check for Related section
        if line.strip().startswith("## Related"):
            result["has_related_section"] = True

    # Related links (wiki-links after ## Related)
    in_related = False
    for line in lines:
        if line.strip().startswith("## Related"):
            in_related = True
            continue
        if in_related and line.startswith("##"):
            break
        if in_related:
            links = re.findall(r"\[\[([^\]]+)\]\]", line)
            result["related_links"].extend(links)

    # Identify issues
    if not result["has_source"]:
        result["issues"].append("MISSING Source")
    if not result["has_date"]:
        result["issues"].append("MISSING Date/Grabbed")
    if not result["has_related_section"]:
        result["issues"].append("NO Related section")
    if not result["tags"]:
        result["issues"].append("NO tags")
    if "factorio" not in [t.lower() for t in result["tags"]]:
        result["issues"].append("MISSING #factorio tag")

    return result


@click.command()
@click.argument("vault_dir")
@click.option("--prefix", default="Factorio", help="Filter notes by filename prefix.")
@click.option("--issues-only", is_flag=True, help="Only show notes with issues.")
def audit(vault_dir: str, prefix: str, issues_only: bool) -> None:
    """Audit vault notes for metadata completeness and hierarchy."""
    vault = Path(vault_dir).expanduser()
    if not vault.exists():
        click.echo(f"Vault directory not found: {vault}", err=True)
        return

    notes = sorted(vault.rglob("*.md"))
    if prefix:
        notes = [n for n in notes if n.stem.startswith(prefix)]

    # Skip memory/ and heartbeat/ dirs
    notes = [n for n in notes if "/memory/" not in str(n) and "/heartbeat/" not in str(n)]

    all_filenames = {n.stem for n in notes}
    all_tags: dict[str, int] = {}
    hub_notes = []
    atomic_notes = []
    results = []

    for note_path in notes:
        info = parse_note(note_path)
        results.append(info)

        for tag in info["tags"]:
            all_tags[tag] = all_tags.get(tag, 0) + 1

        # Check for broken wiki-links
        for link in info["wiki_links"]:
            if link not in all_filenames:
                info["issues"].append(f"BROKEN link: [[{link}]]")

        # Classify as hub or atomic
        content = note_path.read_text()
        if "## Topics" in content or "## Sub-Hubs" in content or content.count("[[") > 5:
            hub_notes.append(info["filename"])
        else:
            atomic_notes.append(info["filename"])

    # Print summary
    click.echo("\n=== AUDIT SUMMARY ===")
    click.echo(f"Total notes: {len(results)}")
    click.echo(f"Hub notes: {len(hub_notes)}")
    click.echo(f"Atomic notes: {len(atomic_notes)}")
    click.echo(f"Notes with issues: {sum(1 for r in results if r['issues'])}")

    # Tag frequency
    click.echo("\n=== TAG FREQUENCY ===")
    for tag, count in sorted(all_tags.items(), key=lambda x: -x[1]):
        click.echo(f"  #{tag}: {count}")

    # Hub hierarchy
    click.echo("\n=== HUB NOTES ===")
    for h in hub_notes:
        click.echo(f"  {h}")

    # Issues
    click.echo("\n=== ISSUES ===")
    for r in results:
        if issues_only and not r["issues"]:
            continue
        status = " | ".join(r["issues"]) if r["issues"] else "OK"
        click.echo(f"  {r['filename']} ({r['lines']}L) — {status}")
        if r["related_links"]:
            click.echo(f"    Related: {', '.join(r['related_links'])}")


if __name__ == "__main__":
    audit()
