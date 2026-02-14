#!/usr/bin/env python3
"""Ask a question to another AI model using pydantic-ai with thinking enabled."""

import os
import sys
import typing
from typing import Any
from typing import cast

import click
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.settings import ModelSettings

DEFAULT_MODEL = "openai:gpt-5.2"

# Prefix → (env var name, thinking settings)
PROVIDER_CONFIG: dict[str, tuple[str, dict[str, Any]]] = {
    "openai": (
        "OPENAI_API_KEY",
        {"openai_reasoning_effort": "xhigh"},
    ),
    "openai-responses": (
        "OPENAI_API_KEY",
        {"openai_reasoning_effort": "xhigh"},
    ),
    "anthropic": (
        "ANTHROPIC_API_KEY",
        {"anthropic_thinking": {"type": "adaptive"}, "anthropic_effort": "max"},
    ),
    "google-gla": (
        "GOOGLE_API_KEY",
        {"google_thinking_config": {"include_thoughts": True}},
    ),
}


def _cap_reasoning_effort(model: str, thinking: dict[str, Any]) -> dict[str, Any]:
    """Cap reasoning effort to 'high' for mini models (they don't support 'xhigh')."""
    if "mini" in model and thinking.get("openai_reasoning_effort") == "xhigh":
        return {**thinking, "openai_reasoning_effort": "high"}
    return thinking


def _parse_provider(model: str) -> tuple[str, str, dict[str, Any]]:
    """Parse 'prefix:model_name' → (env_var, key_name, thinking_settings).

    Raises click.BadParameter if the prefix is unknown.
    """
    prefix = model.rsplit(":", 1)[0] if ":" in model else model
    config = PROVIDER_CONFIG.get(prefix)
    if config is None:
        known = ", ".join(sorted(PROVIDER_CONFIG))
        raise click.BadParameter(
            f"Unknown model prefix '{prefix}'. Known prefixes: {known}",
            param_hint="'--model'",
        )
    key_name, thinking = config
    thinking = _cap_reasoning_effort(model, thinking)
    return key_name, prefix, thinking


def _get_known_models() -> list[str]:
    """Extract all known model names from pydantic-ai's KnownModelName type."""
    return sorted(typing.get_args(KnownModelName.__value__))


@click.command()
@click.option(
    "--model",
    "-m",
    default=DEFAULT_MODEL,
    show_default=True,
    help="Full pydantic-ai model string (e.g. openai:gpt-5.2, anthropic:claude-opus-4-6)",
)
@click.option("--system", "-s", default=None, help="System prompt")
@click.option(
    "--list-models", "-l", default=None, help="List known models (optionally filter by prefix)"
)
@click.argument("question", required=False)
def main(model: str, system: str | None, list_models: str | None, question: str | None) -> None:
    """Ask a question to another AI model with extended thinking."""
    if list_models is not None:
        prefix_filter = list_models if list_models else None
        for name in _get_known_models():
            if prefix_filter is None or name.startswith(prefix_filter):
                click.echo(name)
        return

    if not question:
        raise click.UsageError("Missing argument 'QUESTION'.")

    key_name, prefix, thinking = _parse_provider(model)

    if not os.environ.get(key_name):
        shell = "~/.zshrc" if sys.platform == "darwin" else "~/.bashrc"
        click.echo(f"Error: {key_name} not set.", err=True)
        click.echo(f'Add to {shell}: export {key_name}="your-key"', err=True)
        click.echo(f"Then run: source {shell}", err=True)
        raise SystemExit(1)

    agent = Agent(
        cast(KnownModelName, model),
        system_prompt=system
        or "You are a discussion partner. Think carefully and help discover the truth.",
    )
    try:
        result = agent.run_sync(question, model_settings=cast(ModelSettings, thinking))
    except Exception as e:
        msg = str(e)
        if "insufficient_quota" in msg:
            click.echo(f"Error: {prefix} account has insufficient quota.", err=True)
            click.echo(
                "This is a billing issue — add credits at the provider's dashboard.",
                err=True,
            )
        elif "invalid_api_key" in msg or "Incorrect API key" in msg:
            click.echo(f"Error: {key_name} is invalid.", err=True)
            click.echo("Check the key value and run: source ~/.zshrc", err=True)
        elif "rate_limit" in msg or "429" in msg:
            click.echo(f"Error: Rate limited by {prefix}. Wait and retry.", err=True)
        else:
            click.echo(f"Error from {prefix}: {msg}", err=True)
        raise SystemExit(1)
    click.echo(result.output)


if __name__ == "__main__":
    main()
