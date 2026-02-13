#!/usr/bin/env python3
"""Review a GitHub PR using an external AI model via pydantic-ai."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.settings import ModelSettings

DEFAULT_MODEL = "openai:gpt-5.2"
MAX_DIFF_CHARS = 80_000

# Mirror of discussion_partners provider config (prefix → env var, thinking settings)
PROVIDER_CONFIG: dict[str, tuple[str, dict[str, Any]]] = {
    "openai": ("OPENAI_API_KEY", {"openai_reasoning_effort": "xhigh"}),
    "openai-responses": ("OPENAI_API_KEY", {"openai_reasoning_effort": "xhigh"}),
    "anthropic": (
        "ANTHROPIC_API_KEY",
        {"anthropic_thinking": {"type": "adaptive"}, "anthropic_effort": "max"},
    ),
    "google-gla": (
        "GOOGLE_API_KEY",
        {"google_thinking_config": {"include_thoughts": True}},
    ),
}

REVIEW_SYSTEM = (
    "You are an expert code reviewer. Review the PR diff and report findings.\n"
    "Rules:\n"
    "- Focus on correctness, bugs, security issues, and design problems\n"
    "- Skip style nits, formatting, and naming unless they cause confusion\n"
    "- Each finding must reference a specific file and line/hunk\n"
    "- Rate severity: critical (breaks things), warning (likely problem), note (worth considering)\n"
    "- If the code looks good, say so briefly — don't invent issues\n"
    "- Be direct. No filler."
)

DEFAULT_FOCUS = (
    "Review this PR for real issues. Flag bugs, security problems, logic errors, "
    "and design concerns. Skip style nits.\n\n"
    "For each finding:\n"
    "- **Severity**: critical / warning / note\n"
    "- **Location**: file:line or file:hunk\n"
    "- **Issue**: what's wrong\n"
    "- **Suggestion**: how to fix it\n\n"
    "If the PR looks clean, say so."
)


def _run_gh(*args: str) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"gh {' '.join(args)}: {result.stderr.strip()}", err=True)
        raise SystemExit(1)
    return result.stdout


def _parse_pr_ref(ref: str) -> tuple[str | None, str]:
    """Parse PR reference → (repo_or_none, number).

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


def _build_context(meta: dict[str, Any], diff: str, context_files: tuple[str, ...]) -> str:
    """Assemble structured XML context document."""
    if len(diff) > MAX_DIFF_CHARS:
        click.echo(f"Diff is {len(diff):,} chars, truncating to {MAX_DIFF_CHARS:,}", err=True)
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[TRUNCATED — diff too large for full review]"

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
@click.option("--model", "-m", default=DEFAULT_MODEL, show_default=True, help="Model for review")
@click.option("--focus", "-f", default=None, help="Review focus prompt override")
@click.option(
    "--context-file",
    "-c",
    multiple=True,
    type=click.Path(exists=True),
    help="Extra context files to include",
)
@click.option("--dry-run", is_flag=True, help="Print context without calling model")
def main(
    pr_ref: str,
    model: str,
    focus: str | None,
    context_file: tuple[str, ...],
    dry_run: bool,
) -> None:
    """Review a GitHub PR using an external AI model.

    PR_REF can be a URL, owner/repo#123, #123, or just 123.
    """
    repo, number = _parse_pr_ref(pr_ref)
    display_repo = repo or "(current repo)"
    click.echo(f"Fetching PR #{number} from {display_repo}...", err=True)

    meta, diff = _fetch_pr(repo, number)
    context = _build_context(meta, diff, context_file)

    if dry_run:
        click.echo(context)
        return

    # Resolve provider
    prefix = model.rsplit(":", 1)[0] if ":" in model else model
    config = PROVIDER_CONFIG.get(prefix)
    if config is None:
        known = ", ".join(sorted(PROVIDER_CONFIG))
        raise click.BadParameter(f"Unknown prefix '{prefix}'. Known: {known}")

    key_name, thinking = config
    if not os.environ.get(key_name):
        shell = "~/.zshrc" if sys.platform == "darwin" else "~/.bashrc"
        click.echo(f"{key_name} not set. Add to {shell}.", err=True)
        raise SystemExit(1)

    question = f"{focus or DEFAULT_FOCUS}\n\n{context}"
    click.echo(f"Sending to {model} for review...", err=True)

    agent = Agent(cast(KnownModelName, model), system_prompt=REVIEW_SYSTEM)
    try:
        result = agent.run_sync(question, model_settings=cast(ModelSettings, thinking))
    except Exception as e:
        click.echo(f"Review failed: {e}", err=True)
        raise SystemExit(1)

    click.echo(result.output)


if __name__ == "__main__":
    main()
