#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.0",
# ]
# ///
"""Helper utilities for the Modal compute skill."""

import os
import subprocess

import click


@click.group()
def cli() -> None:
    """Modal compute skill helpers."""


@cli.command()
def check_auth() -> None:
    """Check if Modal authentication is configured and working."""
    token_id = os.environ.get("MODAL_TOKEN_ID")
    token_secret = os.environ.get("MODAL_TOKEN_SECRET")

    if token_id and token_secret:
        click.echo("Environment: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET are set.")
    else:
        click.echo("Environment: MODAL_TOKEN_ID / MODAL_TOKEN_SECRET not set (may use token file).")

    try:
        result = subprocess.run(
            ["modal", "app", "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        click.echo("Auth: FAILED — modal CLI not found. Install with: uv add modal", err=True)
        raise SystemExit(1)

    if result.returncode == 0:
        click.echo("Auth: OK — Modal CLI authenticated successfully.")
    else:
        stderr = result.stderr.strip()
        click.echo(f"Auth: FAILED — {stderr}", err=True)
        click.echo("", err=True)
        click.echo("To authenticate, either:", err=True)
        click.echo("  1. Run: modal token set", err=True)
        click.echo("  2. Set env vars in ~/.zshrc:", err=True)
        click.echo('     export MODAL_TOKEN_ID="your-token-id"', err=True)
        click.echo('     export MODAL_TOKEN_SECRET="your-token-secret"', err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
