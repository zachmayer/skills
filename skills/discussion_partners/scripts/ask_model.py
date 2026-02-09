#!/usr/bin/env python3
"""Ask a question to another AI model using pydantic-ai."""

from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName


@click.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic", "google"]),
    required=True,
    help="AI provider to query",
)
@click.option("--model", "-m", required=True, help="Model name")
@click.option("--system", "-s", default=None, help="System prompt")
@click.argument("question")
def main(provider: str, model: str, system: str | None, question: str) -> None:
    """Ask a question to another AI model."""
    model_id = f"{provider}:{model}" if provider != "google" else f"google-gla:{model}"
    agent = Agent(
        cast(KnownModelName, model_id),
        system_prompt=system or "You are a helpful assistant.",
    )
    result = agent.run_sync(question)
    click.echo(result.data)


if __name__ == "__main__":
    main()
