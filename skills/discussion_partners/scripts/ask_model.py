#!/usr/bin/env python3
"""Ask a question to another AI model using pydantic-ai with thinking enabled."""

from typing import Any
from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.settings import ModelSettings

# Recommended defaults per provider (thinking models)
DEFAULTS: dict[str, str] = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-6",
    "google": "gemini-2.5-pro",
}

# Max thinking settings per provider
THINKING_SETTINGS: dict[str, dict[str, Any]] = {
    "openai": {"openai_reasoning_effort": "xhigh"},
    "anthropic": {"anthropic_thinking": {"type": "adaptive"}, "anthropic_effort": "max"},
    "google": {"google_thinking_config": {"include_thoughts": True}},
}


@click.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic", "google"]),
    required=True,
    help="AI provider to query",
)
@click.option("--model", "-m", default=None, help="Model name (defaults to best thinking model)")
@click.option("--system", "-s", default=None, help="System prompt")
@click.argument("question")
def main(provider: str, model: str | None, system: str | None, question: str) -> None:
    """Ask a question to another AI model with extended thinking."""
    model_name = model or DEFAULTS[provider]
    model_id = f"{provider}:{model_name}" if provider != "google" else f"google-gla:{model_name}"

    agent = Agent(
        cast(KnownModelName, model_id),
        system_prompt=system or "You are a helpful assistant. Think carefully and thoroughly.",
    )
    result = agent.run_sync(
        question, model_settings=cast(ModelSettings, THINKING_SETTINGS[provider])
    )
    click.echo(result.data)


if __name__ == "__main__":
    main()
