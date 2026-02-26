# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.0",
#     "playwright>=1.58.0",
# ]
# ///
"""Fetch a JS-heavy page using Playwright and output clean text."""

import click
from browser import open_page


def _clean_text(raw: str) -> str:
    """Collapse whitespace runs and strip blank lines."""
    return "\n".join(line.strip() for line in raw.splitlines() if line.strip())


def _extract_main_content(page) -> str:  # type: ignore[no-untyped-def]
    """Try main/article selectors, fall back to full body text."""
    for selector in ["main", "article"]:
        el = page.query_selector(selector)
        if el:
            text = el.inner_text()
            if len(text.strip()) > 100:
                return text
    return page.inner_text("body")


@click.command()
@click.argument("url")
@click.option("--timeout", default=30000, help="Page load timeout in milliseconds.")
@click.option("--wait-for", default=None, help="CSS selector to wait for before extracting.")
@click.option("--selector", default=None, help="CSS selector to extract content from.")
@click.option("--full-page", is_flag=True, help="Extract full body instead of main content area.")
def fetch(
    url: str, timeout: int, wait_for: str | None, selector: str | None, full_page: bool
) -> None:
    """Fetch URL with a headless browser and print extracted text to stdout."""
    with open_page(url, timeout=timeout) as page:
        if wait_for:
            try:
                page.wait_for_selector(wait_for, timeout=10000)
            except Exception:
                click.echo(f"Warning: selector '{wait_for}' not found, proceeding.", err=True)

        title = page.title() or ""

        if selector:
            el = page.query_selector(selector)
            raw = el.inner_text() if el else page.inner_text("body")
        elif full_page:
            raw = page.inner_text("body")
        else:
            raw = _extract_main_content(page)

    content = _clean_text(raw)

    if not content or len(content) < 50:
        click.echo("Warning: extracted content is very short or empty.", err=True)
        click.echo(f"Page title: {title}", err=True)
        click.echo("Try --full-page or --selector <css>.", err=True)

    if title:
        click.echo(f"# {title}\n")
    click.echo(content)


if __name__ == "__main__":
    fetch()
