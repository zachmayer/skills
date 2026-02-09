#!/usr/bin/env python3
"""Ask a question to another AI model using pydantic-ai with thinking enabled."""

from typing import Any
from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.settings import ModelSettings


def _build_settings(provider: str, thinking: bool) -> ModelSettings | None:
    """Build provider-specific model settings for thinking models."""
    if not thinking:
        return None

    settings: dict[str, Any] = {}
    if provider == "openai":
        settings["openai_reasoning_effort"] = "xhigh"
    elif provider == "anthropic":
        settings["anthropic_thinking"] = {"type": "adaptive"}
        settings["anthropic_effort"] = "max"
    elif provider == "google":
        settings["google_thinking_config"] = {"include_thoughts": True}

    return cast(ModelSettings, settings) if settings else None


# Recommended defaults per provider (thinking models)
DEFAULTS: dict[str, str] = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-6",
    "google": "gemini-2.5-pro",
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
@click.option(
    "--thinking/--no-thinking", default=True, help="Enable extended thinking (default: on)"
)
@click.argument("question")
def main(
    provider: str, model: str | None, system: str | None, thinking: bool, question: str
) -> None:
    """Ask a question to another AI model with extended thinking."""
    model_name = model or DEFAULTS[provider]
    model_id = f"{provider}:{model_name}" if provider != "google" else f"google-gla:{model_name}"

    settings = _build_settings(provider, thinking)
    agent = Agent(
        cast(KnownModelName, model_id),
        system_prompt=system or "You are a helpful assistant. Think carefully and thoroughly.",
    )
    result = agent.run_sync(question, model_settings=settings)
    click.echo(result.data)


if __name__ == "__main__":
    main()
