"""Shared Playwright browser utilities for web_grab scripts."""

import sys
from contextlib import contextmanager
from typing import Generator
from urllib.parse import urlparse

import click
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright


def validate_url(url: str) -> str:
    """Validate URL has http/https scheme and a hostname."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        click.echo(f"Error: only http/https URLs allowed, got: {parsed.scheme}", err=True)
        sys.exit(1)
    if not parsed.hostname:
        click.echo(f"Error: no hostname in URL: {url}", err=True)
        sys.exit(1)
    return url


@contextmanager
def open_page(url: str, timeout: int = 30000) -> Generator[Page, None, None]:
    """Launch headless Chromium, navigate to URL, yield the page, then close."""
    url = validate_url(url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        except Exception as e:
            click.echo(f"Error loading page: {e}", err=True)
            browser.close()
            sys.exit(1)
        try:
            yield page
        finally:
            browser.close()
