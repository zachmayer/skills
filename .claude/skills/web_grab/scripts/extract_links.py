# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.0",
#     "playwright>=1.58.0",
# ]
# ///
"""Extract all links from a JS-heavy page using Playwright."""

import json

import click
from browser import open_page


@click.command()
@click.argument("url")
@click.option("--timeout", default=30000, help="Page load timeout in milliseconds.")
@click.option(
    "--filter", "url_filter", default=None, help="Only show links containing this substring."
)
def extract(url: str, timeout: int, url_filter: str | None) -> None:
    """Extract all links (href) from a rendered page. Outputs JSON array of {text, href}."""
    with open_page(url, timeout=timeout) as page:
        links = page.eval_on_selector_all(
            "a[href]",
            """elements => elements.map(el => ({
                text: el.innerText.trim().substring(0, 200),
                href: el.href
            }))""",
        )

    if url_filter:
        links = [link for link in links if url_filter in link["href"]]

    # Deduplicate by href
    seen = set()
    unique = []
    for link in links:
        if link["href"] not in seen:
            seen.add(link["href"])
            unique.append(link)

    click.echo(json.dumps(unique))


if __name__ == "__main__":
    extract()
