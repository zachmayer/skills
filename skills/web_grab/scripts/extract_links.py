"""Extract all links from a JS-heavy page using Playwright."""

import json
import sys

import click
from playwright.sync_api import sync_playwright


@click.command()
@click.argument("url")
@click.option("--timeout", default=30000, help="Page load timeout in milliseconds.")
@click.option(
    "--filter", "url_filter", default=None, help="Only show links containing this substring."
)
def extract(url: str, timeout: int, url_filter: str | None) -> None:
    """Extract all links (href) from a rendered page. Outputs JSON array of {text, href}."""
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

        links = page.eval_on_selector_all(
            "a[href]",
            """elements => elements.map(el => ({
                text: el.innerText.trim().substring(0, 200),
                href: el.href
            }))""",
        )

        browser.close()

    if url_filter:
        links = [link for link in links if url_filter in link["href"]]

    # Deduplicate by href
    seen = set()
    unique = []
    for link in links:
        if link["href"] not in seen:
            seen.add(link["href"])
            unique.append(link)

    click.echo(json.dumps(unique, indent=2))


if __name__ == "__main__":
    extract()
