#!/usr/bin/env python3
"""Assemble structured PR context for review. No model calls — just gh + XML."""

import json
import subprocess
from pathlib import Path
from typing import Any

import click

MAX_DIFF_CHARS = 80_000


def _run_gh(*args: str) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"gh {' '.join(args)}: {result.stderr.strip()}", err=True)
        raise SystemExit(1)
    return result.stdout


def _parse_pr_ref(ref: str) -> tuple[str | None, str]:
    """Parse PR reference -> (repo_or_none, number).

    Accepts: URL, owner/repo#123, #123, or 123.
    Returns repo=None when using current repo.
    """
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
    """Fetch PR metadata and diff."""
    repo_args = ["--repo", repo] if repo else []

    meta_json = _run_gh(
        "pr",
        "view",
        number,
        *repo_args,
        "--json",
        "title,body,author,state,baseRefName,headRefName,files,url",
    )
    meta = json.loads(meta_json)

    diff = _run_gh("pr", "diff", number, *repo_args)
    return meta, diff


def _build_context(
    meta: dict[str, Any], diff: str, context_files: tuple[str, ...], max_diff: int
) -> str:
    """Assemble structured XML context document."""
    if len(diff) > max_diff:
        click.echo(f"Diff is {len(diff):,} chars, truncating to {max_diff:,}", err=True)
        diff = diff[:max_diff] + "\n\n[TRUNCATED — diff too large for full review]"

    files = meta.get("files") or []
    file_list = "\n".join(
        f"  {f.get('path', '?')} (+{f.get('additions', 0)} -{f.get('deletions', 0)})" for f in files
    )

    parts = [
        "<pr-review-context>",
        "<metadata>",
        f"  <title>{meta.get('title', '')}</title>",
        f"  <author>{meta.get('author', {}).get('login', '?')}</author>",
        f"  <url>{meta.get('url', '')}</url>",
        f"  <base>{meta.get('baseRefName', '?')}</base>",
        f"  <head>{meta.get('headRefName', '?')}</head>",
        f"  <state>{meta.get('state', '?')}</state>",
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

    for path in context_files:
        content = Path(path).read_text()
        parts.extend([f'<context-file path="{path}">', content, "</context-file>"])

    parts.append("</pr-review-context>")
    return "\n".join(parts)


@click.command()
@click.argument("pr_ref")
@click.option(
    "--context-file",
    "-c",
    multiple=True,
    type=click.Path(exists=True),
    help="Extra context files to include",
)
@click.option(
    "--max-diff",
    default=MAX_DIFF_CHARS,
    show_default=True,
    help="Max diff characters before truncation",
)
def main(pr_ref: str, context_file: tuple[str, ...], max_diff: int) -> None:
    """Assemble structured PR context for review.

    PR_REF can be a URL, owner/repo#123, #123, or just 123.
    Outputs XML context to stdout for piping to discussion_partners.
    """
    repo, number = _parse_pr_ref(pr_ref)
    display_repo = repo or "(current repo)"
    click.echo(f"Fetching PR #{number} from {display_repo}...", err=True)

    meta, diff = _fetch_pr(repo, number)
    context = _build_context(meta, diff, context_file, max_diff)
    click.echo(context)


if __name__ == "__main__":
    main()
