#!/usr/bin/env python3
"""Evergreen maintenance: housekeeping for repos, knowledge graph, and memory."""

import os
import re
import subprocess
from collections import Counter
from pathlib import Path

import click

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"
MEMORY_DIR = OBSIDIAN_DIR / "memory"


def _run(cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and return result."""
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


# ---------------------------------------------------------------------------
# Repo-scoped maintenance
# ---------------------------------------------------------------------------


@click.group()
def cli() -> None:
    """Evergreen maintenance CLI — housekeeping for repos, knowledge, and memory."""


@cli.command("repo")
@click.argument("repo_path", type=click.Path(exists=True))
@click.option(
    "--prune", is_flag=True, help="Actually delete merged branches and dangling worktrees"
)
def repo_maintenance(repo_path: str, prune: bool) -> None:
    """Repo-scoped maintenance: find merged branches, dangling worktrees."""
    repo = Path(repo_path).resolve()

    # 1. Find merged local branches (excluding main/master and current)
    click.echo("## Merged local branches")
    result = _run(["git", "branch", "--merged", "main"], cwd=repo)
    if result.returncode != 0:
        result = _run(["git", "branch", "--merged", "master"], cwd=repo)

    merged = []
    if result.returncode == 0:
        for line in result.stdout.strip().splitlines():
            branch = line.strip().lstrip("* ")
            if branch and branch not in ("main", "master"):
                merged.append(branch)

    if merged:
        for b in merged:
            click.echo(f"  - {b}")
        if prune:
            for b in merged:
                r = _run(["git", "branch", "-d", b], cwd=repo)
                if r.returncode == 0:
                    click.echo(f"    deleted: {b}")
                else:
                    click.echo(f"    FAILED to delete {b}: {r.stderr.strip()}")
    else:
        click.echo("  (none)")

    # 2. Find dangling worktrees
    click.echo("\n## Dangling worktrees")
    result = _run(["git", "worktree", "list", "--porcelain"], cwd=repo)
    dangling = []
    if result.returncode == 0:
        current_worktree: str | None = None
        for line in result.stdout.strip().splitlines():
            if line.startswith("worktree "):
                current_worktree = line[len("worktree ") :]
            elif line == "prunable" and current_worktree:
                dangling.append(current_worktree)

    if dangling:
        for wt in dangling:
            click.echo(f"  - {wt}")
        if prune:
            r = _run(["git", "worktree", "prune"], cwd=repo)
            if r.returncode == 0:
                click.echo("    pruned dangling worktrees")
            else:
                click.echo(f"    FAILED: {r.stderr.strip()}")
    else:
        click.echo("  (none)")

    # 3. Summary
    click.echo(f"\nTotal: {len(merged)} merged branches, {len(dangling)} dangling worktrees")


# ---------------------------------------------------------------------------
# Knowledge-scoped maintenance
# ---------------------------------------------------------------------------


def _find_md_files(directory: Path) -> list[Path]:
    """Find all markdown files recursively."""
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.md"))


def _extract_wikilinks(content: str) -> set[str]:
    """Extract [[wikilink]] targets from content."""
    return set(re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content))


def _note_title(path: Path) -> str:
    """Get the note title (filename without extension)."""
    return path.stem


@cli.command("knowledge")
@click.option(
    "--vault",
    type=click.Path(exists=True),
    default=None,
    help="Obsidian vault root (default: $CLAUDE_OBSIDIAN_DIR)",
)
def knowledge_maintenance(vault: str | None) -> None:
    """Knowledge-scoped maintenance: orphans, duplicates, missing metadata."""
    vault_path = Path(vault) if vault else OBSIDIAN_DIR
    kg_dir = vault_path / "knowledge_graph"

    if not kg_dir.exists():
        click.echo("knowledge_graph/ not found")
        return

    md_files = _find_md_files(kg_dir)
    if not md_files:
        click.echo("No markdown files found in knowledge_graph/")
        return

    # Build link graph
    titles: dict[str, Path] = {}
    all_links: set[str] = set()
    notes_with_links: dict[str, set[str]] = {}

    for f in md_files:
        title = _note_title(f)
        titles[title] = f
        content = f.read_text(errors="replace")
        links = _extract_wikilinks(content)
        notes_with_links[title] = links
        all_links.update(links)

    # 1. Orphan notes: not linked FROM any other note
    linked_titles = set()
    for links in notes_with_links.values():
        linked_titles.update(links)

    orphans = [t for t in titles if t not in linked_titles]
    click.echo(f"## Orphan notes (not linked from any other note): {len(orphans)}")
    for t in sorted(orphans):
        click.echo(f"  - {t}")

    # 2. Broken wikilinks: link targets that don't exist as files
    broken: list[tuple[str, str]] = []
    # Also check memory dir titles
    memory_titles = {_note_title(f) for f in _find_md_files(vault_path / "memory")}
    all_titles = set(titles.keys()) | memory_titles

    for source, links in notes_with_links.items():
        for link in links:
            if link not in all_titles:
                broken.append((source, link))

    click.echo(f"\n## Broken wikilinks: {len(broken)}")
    for source, target in sorted(broken):
        click.echo(f"  - [[{target}]] in {source}")

    # 3. Duplicate titles (same stem in different directories)
    stem_counts: Counter[str] = Counter()
    stem_paths: dict[str, list[Path]] = {}
    for f in md_files:
        stem = f.stem
        stem_counts[stem] += 1
        stem_paths.setdefault(stem, []).append(f)

    dupes = {k: v for k, v in stem_paths.items() if len(v) > 1}
    click.echo(f"\n## Duplicate note names: {len(dupes)}")
    for stem, paths in sorted(dupes.items()):
        click.echo(f"  - {stem}:")
        for p in paths:
            click.echo(f"      {p.relative_to(vault_path)}")

    # 4. Missing metadata (Source/Date)
    missing_source: list[str] = []
    missing_date: list[str] = []
    for f in md_files:
        content = f.read_text(errors="replace")
        if not re.search(r"^Source:", content, re.MULTILINE):
            missing_source.append(_note_title(f))
        if not re.search(r"^Date:", content, re.MULTILINE):
            missing_date.append(_note_title(f))

    click.echo(f"\n## Missing Source metadata: {len(missing_source)}")
    for t in sorted(missing_source)[:20]:
        click.echo(f"  - {t}")
    if len(missing_source) > 20:
        click.echo(f"  ... and {len(missing_source) - 20} more")

    click.echo(f"\n## Missing Date metadata: {len(missing_date)}")
    for t in sorted(missing_date)[:20]:
        click.echo(f"  - {t}")
    if len(missing_date) > 20:
        click.echo(f"  ... and {len(missing_date) - 20} more")

    # Summary
    click.echo(
        f"\nTotal: {len(md_files)} notes, {len(orphans)} orphans, "
        f"{len(broken)} broken links, {len(dupes)} duplicate names, "
        f"{len(missing_source)} missing Source, {len(missing_date)} missing Date"
    )


# ---------------------------------------------------------------------------
# Memory-scoped maintenance
# ---------------------------------------------------------------------------


def _extract_entries(content: str) -> list[str]:
    """Extract individual log entries from a daily memory file.

    Entries start with '- **YYYY-MM-DDTHH:MM:SS**' or '- **timestamp**'.
    Returns normalized (stripped, lowered) content for dedup comparison.
    """
    entries = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- **"):
            # Extract everything after the timestamp+context prefix
            # Pattern: - **2026-02-14T04:42:14** [context]: CONTENT
            match = re.match(r"- \*\*[^*]+\*\*\s*(?:\[[^\]]*\]\s*:?\s*)?(.*)", line)
            if match:
                entries.append(match.group(1).strip().lower())
    return entries


@cli.command("memory")
@click.option(
    "--vault",
    type=click.Path(exists=True),
    default=None,
    help="Obsidian vault root (default: $CLAUDE_OBSIDIAN_DIR)",
)
def memory_maintenance(vault: str | None) -> None:
    """Memory-scoped maintenance: find duplicate entries across daily notes."""
    vault_path = Path(vault) if vault else OBSIDIAN_DIR
    mem_dir = vault_path / "memory"

    if not mem_dir.exists():
        click.echo("memory/ directory not found")
        return

    daily_files = sorted(mem_dir.glob("????-??-??.md"))
    if not daily_files:
        click.echo("No daily memory files found")
        return

    # Collect all entries with their source file
    all_entries: list[tuple[str, str, str]] = []  # (normalized, original_line, filename)
    for f in daily_files:
        content = f.read_text(errors="replace")
        for line in content.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("- **"):
                match = re.match(r"- \*\*[^*]+\*\*\s*(?:\[[^\]]*\]\s*:?\s*)?(.*)", line_stripped)
                if match:
                    normalized = match.group(1).strip().lower()
                    if normalized:
                        all_entries.append((normalized, line_stripped, f.name))

    # Find exact duplicates (same content after normalization)
    content_counts: Counter[str] = Counter()
    content_sources: dict[str, list[str]] = {}
    for normalized, original, filename in all_entries:
        content_counts[normalized] += 1
        content_sources.setdefault(normalized, []).append(filename)

    dupes = {k: v for k, v in content_sources.items() if len(v) > 1}
    click.echo(f"## Duplicate entries across daily notes: {len(dupes)}")
    for content, files in sorted(dupes.items(), key=lambda x: -len(x[1])):
        unique_files = sorted(set(files))
        click.echo(f"  - ({len(files)}x in {', '.join(unique_files)}): {content[:80]}...")

    # Find near-duplicates: entries sharing >80% of words
    click.echo(
        f"\nTotal: {len(daily_files)} daily files, {len(all_entries)} entries, {len(dupes)} duplicates"
    )


@cli.command("all")
@click.argument("repo_path", type=click.Path(exists=True), required=False, default=None)
@click.option("--vault", type=click.Path(exists=True), default=None)
@click.option("--prune", is_flag=True)
def run_all(repo_path: str | None, vault: str | None, prune: bool) -> None:
    """Run all maintenance scopes."""
    ctx = click.get_current_context()

    if repo_path:
        click.echo("=" * 60)
        click.echo("REPO MAINTENANCE")
        click.echo("=" * 60)
        ctx.invoke(repo_maintenance, repo_path=repo_path, prune=prune)

    click.echo("\n" + "=" * 60)
    click.echo("KNOWLEDGE MAINTENANCE")
    click.echo("=" * 60)
    ctx.invoke(knowledge_maintenance, vault=vault)

    click.echo("\n" + "=" * 60)
    click.echo("MEMORY MAINTENANCE")
    click.echo("=" * 60)
    ctx.invoke(memory_maintenance, vault=vault)


if __name__ == "__main__":
    cli()
