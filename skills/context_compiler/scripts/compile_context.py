#!/usr/bin/env python3
"""Compile structured context documents from multiple sources."""

import json
import subprocess
from pathlib import Path
from typing import Any

import click

DEFAULT_MAX_CHARS = 100_000
DEFAULT_OBSIDIAN_DIR = "~/claude/obsidian"


def _run(cmd: list[str]) -> str:
    """Run a command and return stdout. Raises SystemExit on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"Command failed: {' '.join(cmd)}\n{result.stderr.strip()}", err=True)
        raise SystemExit(1)
    return result.stdout


def _truncate(text: str, max_chars: int, label: str) -> str:
    """Truncate text with a warning if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    click.echo(f"{label}: {len(text):,} chars, truncating to {max_chars:,}", err=True)
    return text[:max_chars] + f"\n\n[TRUNCATED — {label} too large]"


def _escape_xml(text: str) -> str:
    """Minimal XML escaping for attribute values."""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _parse_pr_ref(ref: str) -> tuple[str | None, str]:
    """Parse PR reference → (repo_or_none, number)."""
    if "github.com" in ref:
        parts = ref.rstrip("/").split("/")
        try:
            idx = parts.index("pull")
            return f"{parts[idx - 2]}/{parts[idx - 1]}", parts[idx + 1]
        except (ValueError, IndexError):
            raise click.BadParameter(f"Can't parse PR URL: {ref}")
    if "#" in ref and "/" in ref.split("#")[0]:
        repo, number = ref.split("#", 1)
        return repo, number
    number = ref.lstrip("#")
    if not number.isdigit():
        raise click.BadParameter(f"Can't parse PR reference: {ref}")
    return None, number


def _fetch_pr(repo: str | None, number: str) -> tuple[dict[str, Any], str]:
    """Fetch PR metadata and diff via gh CLI."""
    repo_args = ["--repo", repo] if repo else []
    meta_json = _run(
        [
            "gh",
            "pr",
            "view",
            number,
            *repo_args,
            "--json",
            "title,body,author,state,baseRefName,headRefName,files,url",
        ]
    )
    meta = json.loads(meta_json)
    diff = _run(["gh", "pr", "diff", number, *repo_args])
    return meta, diff


def _search_obsidian(query: str, obsidian_dir: Path) -> list[tuple[str, str]]:
    """Search obsidian vault for notes matching query. Returns [(rel_path, content)]."""
    results: list[tuple[str, str]] = []
    query_lower = query.lower()
    for md_file in sorted(obsidian_dir.rglob("*.md")):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if query_lower in content.lower() or query_lower in md_file.stem.lower():
            rel = str(md_file.relative_to(obsidian_dir))
            results.append((rel, content))
        if len(results) >= 5:
            break
    return results


# --- Formatters ---


def _xml_source(tag_type: str, content: str, **attrs: str) -> str:
    """Build an XML source element."""
    attr_str = " ".join(f'{k}="{_escape_xml(v)}"' for k, v in attrs.items())
    return f'<source type="{tag_type}" {attr_str}>\n{content}\n</source>'


def _md_source(heading: str, content: str) -> str:
    """Build a markdown section."""
    return f"## {heading}\n\n{content}"


def _format_pr_xml(meta: dict[str, Any], diff: str, ref: str) -> str:
    """Format PR data as XML."""
    files = meta.get("files") or []
    file_list = "\n".join(
        f"  {f.get('path', '?')} (+{f.get('additions', 0)} -{f.get('deletions', 0)})" for f in files
    )
    inner = "\n".join(
        [
            "<metadata>",
            f"  <title>{_escape_xml(meta.get('title', ''))}</title>",
            f"  <author>{_escape_xml(meta.get('author', {}).get('login', '?'))}</author>",
            f"  <url>{_escape_xml(meta.get('url', ''))}</url>",
            f"  <base>{_escape_xml(meta.get('baseRefName', '?'))}</base>",
            f"  <head>{_escape_xml(meta.get('headRefName', '?'))}</head>",
            f"  <state>{_escape_xml(meta.get('state', '?'))}</state>",
            "</metadata>",
            "<description>",
            meta.get("body") or "(no description)",
            "</description>",
            "<files>",
            file_list or "(no files)",
            "</files>",
            "<diff>",
            diff,
            "</diff>",
        ]
    )
    return _xml_source("pr", inner, ref=ref)


def _format_pr_md(meta: dict[str, Any], diff: str, ref: str) -> str:
    """Format PR data as markdown."""
    files = meta.get("files") or []
    file_list = "\n".join(
        f"- {f.get('path', '?')} (+{f.get('additions', 0)} -{f.get('deletions', 0)})" for f in files
    )
    parts = [
        f"**Title:** {meta.get('title', '')}",
        f"**Author:** {meta.get('author', {}).get('login', '?')}",
        f"**URL:** {meta.get('url', '')}",
        f"**Base:** {meta.get('baseRefName', '?')} ← {meta.get('headRefName', '?')}",
        "",
        meta.get("body") or "(no description)",
        "",
        "### Files",
        file_list or "(no files)",
        "",
        "### Diff",
        "```diff",
        diff,
        "```",
    ]
    return _md_source(f"PR #{ref}", "\n".join(parts))


class ContextCompiler:
    """Assembles structured context from multiple sources."""

    def __init__(
        self, fmt: str = "xml", max_chars: int = DEFAULT_MAX_CHARS, obsidian_dir: Path | None = None
    ) -> None:
        self.fmt = fmt
        self.max_chars = max_chars
        self.obsidian_dir = obsidian_dir
        self.sections: list[str] = []

    def add_diff(self, ref: str) -> None:
        """Add git diff output."""
        diff = _run(["git", "diff", ref])
        diff = _truncate(diff, self.max_chars // 2, f"diff {ref}")
        if self.fmt == "xml":
            self.sections.append(_xml_source("diff", diff, ref=ref))
        else:
            self.sections.append(_md_source(f"Git Diff: `{ref}`", f"```diff\n{diff}\n```"))

    def add_log(self, ref: str) -> None:
        """Add git log output."""
        log = _run(["git", "log", "--oneline", ref])
        if self.fmt == "xml":
            self.sections.append(_xml_source("log", log, ref=ref))
        else:
            self.sections.append(_md_source(f"Git Log: `{ref}`", f"```\n{log}\n```"))

    def add_pr(self, pr_ref: str) -> None:
        """Add PR metadata and diff."""
        repo, number = _parse_pr_ref(pr_ref)
        meta, diff = _fetch_pr(repo, number)
        diff = _truncate(diff, self.max_chars // 2, f"PR #{number} diff")
        if self.fmt == "xml":
            self.sections.append(_format_pr_xml(meta, diff, number))
        else:
            self.sections.append(_format_pr_md(meta, diff, number))

    def add_file(self, path: str) -> None:
        """Add a file's contents."""
        try:
            content = Path(path).read_text()
        except (OSError, UnicodeDecodeError) as e:
            click.echo(f"Warning: Can't read {path}: {e}", err=True)
            return
        content = _truncate(content, self.max_chars // 4, path)
        if self.fmt == "xml":
            self.sections.append(_xml_source("file", content, path=path))
        else:
            self.sections.append(_md_source(f"File: `{path}`", f"```\n{content}\n```"))

    def add_glob(self, pattern: str) -> None:
        """Add files matching a glob pattern."""
        matches = sorted(Path(".").glob(pattern))
        if not matches:
            click.echo(f"Warning: No files match '{pattern}'", err=True)
            return
        for match in matches[:20]:  # cap at 20 files
            self.add_file(str(match))

    def add_memory(self, rel_path: str) -> None:
        """Add a memory/obsidian file by relative path."""
        if self.obsidian_dir is None:
            click.echo("Warning: No obsidian dir configured, skipping memory", err=True)
            return
        full_path = self.obsidian_dir / rel_path
        if not full_path.exists():
            click.echo(f"Warning: Memory file not found: {full_path}", err=True)
            return
        content = full_path.read_text()
        content = _truncate(content, self.max_chars // 4, rel_path)
        if self.fmt == "xml":
            self.sections.append(_xml_source("memory", content, path=rel_path))
        else:
            self.sections.append(_md_source(f"Memory: `{rel_path}`", content))

    def add_obsidian_search(self, query: str) -> None:
        """Search obsidian vault and add matching notes."""
        if self.obsidian_dir is None:
            click.echo("Warning: No obsidian dir configured, skipping search", err=True)
            return
        results = _search_obsidian(query, self.obsidian_dir)
        if not results:
            click.echo(f"Warning: No obsidian notes match '{query}'", err=True)
            return
        if self.fmt == "xml":
            inner = "\n".join(
                f'<result path="{_escape_xml(path)}">\n{content}\n</result>'
                for path, content in results
            )
            self.sections.append(_xml_source("obsidian-search", inner, query=query))
        else:
            parts = []
            for path, content in results:
                parts.append(f"### `{path}`\n\n{content}")
            self.sections.append(
                _md_source(f"Obsidian Search: `{query}`", "\n\n---\n\n".join(parts))
            )

    def compile(self) -> str:
        """Compile all sections into final output."""
        if not self.sections:
            click.echo("No sources added. Use --help for options.", err=True)
            raise SystemExit(1)
        if self.fmt == "xml":
            body = "\n".join(self.sections)
            output = f"<context>\n{body}\n</context>"
        else:
            output = "\n\n---\n\n".join(self.sections)
        return _truncate(output, self.max_chars, "total output")


@click.command()
@click.option("--diff", "diffs", multiple=True, help="Git diff ref (e.g., main..HEAD)")
@click.option("--log", "logs", multiple=True, help="Git log ref (e.g., main..HEAD, -5)")
@click.option("--pr", "prs", multiple=True, help="PR number, URL, or owner/repo#N")
@click.option("--file", "files", multiple=True, type=click.Path(), help="File to include")
@click.option("--glob", "globs", multiple=True, help="Glob pattern for files")
@click.option("--memory", "memories", multiple=True, help="Obsidian relative path")
@click.option("--obsidian-search", "searches", multiple=True, help="Search query for obsidian")
@click.option(
    "--obsidian-dir",
    envvar="CLAUDE_OBSIDIAN_DIR",
    default=DEFAULT_OBSIDIAN_DIR,
    help="Obsidian vault directory",
)
@click.option("--max-chars", default=DEFAULT_MAX_CHARS, show_default=True, help="Max output chars")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["xml", "markdown"]),
    default="xml",
    show_default=True,
    help="Output format",
)
def main(
    diffs: tuple[str, ...],
    logs: tuple[str, ...],
    prs: tuple[str, ...],
    files: tuple[str, ...],
    globs: tuple[str, ...],
    memories: tuple[str, ...],
    searches: tuple[str, ...],
    obsidian_dir: str,
    max_chars: int,
    fmt: str,
) -> None:
    """Compile structured context from git diffs, files, memory, and obsidian notes."""
    obs_path = Path(obsidian_dir).expanduser()
    if not obs_path.exists():
        obs_path = None  # type: ignore[assignment]

    compiler = ContextCompiler(fmt=fmt, max_chars=max_chars, obsidian_dir=obs_path)

    for ref in diffs:
        compiler.add_diff(ref)
    for ref in logs:
        compiler.add_log(ref)
    for pr_ref in prs:
        compiler.add_pr(pr_ref)
    for path in files:
        compiler.add_file(path)
    for pattern in globs:
        compiler.add_glob(pattern)
    for rel_path in memories:
        compiler.add_memory(rel_path)
    for query in searches:
        compiler.add_obsidian_search(query)

    click.echo(compiler.compile())


if __name__ == "__main__":
    main()
