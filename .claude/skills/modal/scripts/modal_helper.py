#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.0",
#     "modal>=1.0",
# ]
# ///
"""Helper utilities for the Modal compute skill."""

import os

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

    import modal

    try:
        modal.App.lookup("_auth_check", create_if_missing=True)
        click.echo("Auth: OK — Modal authenticated successfully.")
    except modal.exception.AuthError as e:
        click.echo(f"Auth: FAILED — {e}", err=True)
        click.echo("", err=True)
        click.echo("To authenticate, either:", err=True)
        click.echo("  1. Run: uv run modal token set", err=True)
        click.echo("  2. Set env vars in ~/.zshrc:", err=True)
        click.echo('     export MODAL_TOKEN_ID="your-token-id"', err=True)
        click.echo('     export MODAL_TOKEN_SECRET="your-token-secret"', err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
