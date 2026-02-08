#!/usr/bin/env python3
"""Ask a question to another AI model (OpenAI, Anthropic, or Google)."""

import os

import click
import httpx


def ask_openai(model: str, question: str, system: str | None, max_tokens: int) -> str:
    """Query an OpenAI model."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise click.ClickException("OPENAI_API_KEY environment variable not set")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})

    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages, "max_tokens": max_tokens},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def ask_anthropic(model: str, question: str, system: str | None, max_tokens: int) -> str:
    """Query an Anthropic model."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.ClickException("ANTHROPIC_API_KEY environment variable not set")

    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": question}],
    }
    if system:
        body["system"] = system

    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def ask_google(model: str, question: str, system: str | None, max_tokens: int) -> str:
    """Query a Google Gemini model."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise click.ClickException("GOOGLE_API_KEY environment variable not set")

    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": f"System: {system}"}]})
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
    contents.append({"role": "user", "parts": [{"text": question}]})

    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json={
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens},
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


PROVIDERS = {
    "openai": ask_openai,
    "anthropic": ask_anthropic,
    "google": ask_google,
}


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
@click.option("--max-tokens", default=4096, help="Max response tokens")
@click.argument("question")
def main(provider: str, model: str, system: str | None, max_tokens: int, question: str) -> None:
    """Ask a question to another AI model."""
    ask_fn = PROVIDERS[provider]
    try:
        response = ask_fn(model, question, system, max_tokens)
        click.echo(response)
    except httpx.HTTPStatusError as e:
        raise click.ClickException(f"API error: {e.response.status_code} - {e.response.text}")


if __name__ == "__main__":
    main()
