"""Fetch a JS-heavy page using Playwright and output clean markdown."""

import sys

import click
from playwright.sync_api import sync_playwright


def _clean_text(raw: str) -> str:
    """Collapse whitespace runs and strip blank lines."""
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)


def _extract_main_content(page) -> str:  # type: ignore[no-untyped-def]
    """Try to extract the main content area, falling back to full body text."""
    # Confluence/Atlassian wiki
    for selector in [
        "#main-content",
        "[data-testid='renderer-page']",
        'article[role="article"]',
        "article",
        "main",
        '[role="main"]',
    ]:
        el = page.query_selector(selector)
        if el:
            text = el.inner_text()
            if len(text.strip()) > 100:
                return text

    return page.inner_text("body")


@click.command()
@click.argument("url")
@click.option("--timeout", default=30000, help="Page load timeout in milliseconds.")
@click.option(
    "--wait-for",
    default=None,
    help="CSS selector to wait for before extracting content.",
)
@click.option("--full-page", is_flag=True, help="Extract full body instead of main content area.")
def fetch(url: str, timeout: int, wait_for: str | None, full_page: bool) -> None:
    """Fetch URL with a headless browser and print extracted text to stdout.

    Renders JavaScript, waits for network idle, then extracts the main
    content area as clean text. Designed for JS SPAs (Confluence, React
    apps, etc.) where curl/WebFetch return only JS bundles.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=timeout)
        except Exception as e:
            click.echo(f"Error loading page: {e}", err=True)
            browser.close()
            sys.exit(1)

        # Extra wait for dynamic content
        if wait_for:
            try:
                page.wait_for_selector(wait_for, timeout=10000)
            except Exception:
                click.echo(
                    f"Warning: selector '{wait_for}' not found, proceeding anyway.",
                    err=True,
                )

        # Dismiss common cookie/consent banners
        for dismiss_selector in [
            "button[id*='accept']",
            "button[id*='cookie']",
            "button[class*='accept']",
            "[data-testid='close-button']",
        ]:
            btn = page.query_selector(dismiss_selector)
            if btn:
                try:
                    btn.click(timeout=2000)
                    page.wait_for_timeout(500)
                except Exception:
                    pass

        # Extract title
        title = page.title() or ""

        # Extract content
        if full_page:
            raw = page.inner_text("body")
        else:
            raw = _extract_main_content(page)

        browser.close()

    content = _clean_text(raw)

    if not content or len(content) < 50:
        click.echo("Warning: extracted content is very short or empty.", err=True)
        click.echo(f"Page title: {title}", err=True)
        click.echo("Try --full-page or --wait-for <selector>.", err=True)

    # Output with title header
    if title:
        click.echo(f"# {title}\n")
    click.echo(content)


if __name__ == "__main__":
    fetch()
