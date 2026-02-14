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

# Provider prefix → env var name
PROVIDER_ENV: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "openai-responses": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google-gla": "GOOGLE_API_KEY",
}

# Models that only support reasoning_effort up to "high" (not "xhigh").
# Substring matching: if any of these appear in the model name, cap at "high".
OPENAI_HIGH_MAX_MODELS = ("mini",)

ANTHROPIC_EFFORT_MAP: dict[str, str] = {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "xhigh": "max",
}


def _default_openai_effort(model: str) -> str:
    """Return the default OpenAI reasoning effort for a model.

    Models containing 'mini' in the name only support up to 'high'.
    All others default to 'xhigh'.
    """
    model_name = model.split(":", 1)[-1] if ":" in model else model
    for pattern in OPENAI_HIGH_MAX_MODELS:
        if pattern in model_name.lower():
            return "high"
    return "xhigh"


def _validate_openai_effort(model: str, effort: str) -> str:
    """Validate and possibly cap the effort level for an OpenAI model."""
    model_name = model.split(":", 1)[-1] if ":" in model else model
    for pattern in OPENAI_HIGH_MAX_MODELS:
        if pattern in model_name.lower() and effort == "xhigh":
            click.echo(
                f"Warning: {model_name} only supports up to 'high' reasoning effort. "
                f"Capping from 'xhigh' to 'high'.",
                err=True,
            )
            return "high"
    return effort


def _build_thinking_settings(prefix: str, model: str, effort: str | None) -> dict[str, Any]:
    """Build provider-specific thinking settings from a reasoning effort level."""
    if prefix in ("openai", "openai-responses"):
        if effort is None:
            effort = _default_openai_effort(model)
        else:
            effort = _validate_openai_effort(model, effort)
        return {"openai_reasoning_effort": effort}

    if prefix == "anthropic":
        if effort is None:
            effort = "xhigh"
        anthropic_effort = ANTHROPIC_EFFORT_MAP[effort]
        return {"anthropic_thinking": {"type": "adaptive"}, "anthropic_effort": anthropic_effort}

    if prefix == "google-gla":
        if effort is not None:
            click.echo(
                "Warning: --reasoning-effort is ignored for Google models "
                "(thinking is always enabled).",
                err=True,
            )
        return {"google_thinking_config": {"include_thoughts": True}}

    return {}


def _parse_provider(model: str) -> tuple[str, str]:
    """Parse 'prefix:model_name' → (env_var, prefix).

    Raises click.BadParameter if the prefix is unknown.
    """
    prefix = model.rsplit(":", 1)[0] if ":" in model else model
    env_var = PROVIDER_ENV.get(prefix)
    if env_var is None:
        known = ", ".join(sorted(PROVIDER_ENV))
        raise click.BadParameter(
            f"Unknown model prefix '{prefix}'. Known prefixes: {known}",
            param_hint="'--model'",
        )
    return env_var, prefix


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
    "--reasoning-effort",
    "-r",
    type=click.Choice(["low", "medium", "high", "xhigh"]),
    default=None,
    help="Reasoning effort level. Auto-detected if not set (xhigh for most models, high for mini models).",
)
@click.option(
    "--list-models", "-l", default=None, help="List known models (optionally filter by prefix)"
)
@click.argument("question", required=False)
def main(
    model: str,
    system: str | None,
    reasoning_effort: str | None,
    list_models: str | None,
    question: str | None,
) -> None:
    """Ask a question to another AI model with extended thinking."""
    if list_models is not None:
        prefix_filter = list_models if list_models else None
        for name in _get_known_models():
            if prefix_filter is None or name.startswith(prefix_filter):
                click.echo(name)
        return

    if not question:
        raise click.UsageError("Missing argument 'QUESTION'.")

    key_name, prefix = _parse_provider(model)

    if not os.environ.get(key_name):
        shell = "~/.zshrc" if sys.platform == "darwin" else "~/.bashrc"
        click.echo(f"Error: {key_name} not set.", err=True)
        click.echo(f'Add to {shell}: export {key_name}="your-key"', err=True)
        click.echo(f"Then run: source {shell}", err=True)
        raise SystemExit(1)

    thinking = _build_thinking_settings(prefix, model, reasoning_effort)

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
