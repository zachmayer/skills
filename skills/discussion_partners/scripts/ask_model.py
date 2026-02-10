#!/usr/bin/env python3
"""Ask a question to another AI model using pydantic-ai with thinking enabled."""

import os
import sys
from typing import Any
from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.settings import ModelSettings

KEY_NAMES: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}

# Recommended defaults per provider (thinking models)
DEFAULTS: dict[str, str] = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-6",
    "google": "gemini-3-pro-preview",
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
    # Pre-flight: check API key is set
    key_name = KEY_NAMES[provider]
    if not os.environ.get(key_name):
        shell = "~/.zshrc" if sys.platform == "darwin" else "~/.bashrc"
        click.echo(f"Error: {key_name} not set.", err=True)
        click.echo(f'Add to {shell}: export {key_name}="your-key"', err=True)
        click.echo(f"Then run: source {shell}", err=True)
        raise SystemExit(1)

    model_name = model or DEFAULTS[provider]
    model_id = f"{provider}:{model_name}" if provider != "google" else f"google-gla:{model_name}"

    agent = Agent(
        cast(KnownModelName, model_id),
        system_prompt=system
        or "You are a discussion partner. Think carefully and help discover the truth.",
    )
    try:
        result = agent.run_sync(
            question, model_settings=cast(ModelSettings, THINKING_SETTINGS[provider])
        )
    except Exception as e:
        msg = str(e)
        if "insufficient_quota" in msg:
            click.echo(f"Error: {provider} account has insufficient quota.", err=True)
            click.echo(
                "This is a billing issue — add credits at the provider's dashboard.", err=True
            )
        elif "invalid_api_key" in msg or "Incorrect API key" in msg:
            click.echo(f"Error: {key_name} is invalid.", err=True)
            click.echo("Check the key value and run: source ~/.zshrc", err=True)
        elif "rate_limit" in msg or "429" in msg:
            click.echo(f"Error: Rate limited by {provider}. Wait and retry.", err=True)
        else:
            click.echo(f"Error from {provider}: {msg}", err=True)
        raise SystemExit(1)
    click.echo(result.output)


if __name__ == "__main__":
    main()
