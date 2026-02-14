#!/usr/bin/env python3
"""Transcribe audio files using OpenAI Whisper API."""

import os
from pathlib import Path

import click

SUPPORTED_FORMATS = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".mpeg", ".mpga", ".oga", ".ogg"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--language",
    "-l",
    default=None,
    help="ISO-639-1 language code (e.g. en, es, ja). Auto-detected if omitted.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Write transcript to this file instead of stdout.",
)
@click.option(
    "--model",
    "-m",
    default="gpt-4o-mini-transcribe",
    help="Whisper model to use.",
)
def transcribe(file: Path, language: str | None, output: Path | None, model: str) -> None:
    """Transcribe an audio file using OpenAI Whisper API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise click.ClickException("OPENAI_API_KEY environment variable is not set")

    suffix = file.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise click.ClickException(
            f"Unsupported format '{suffix}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    file_size = file.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise click.ClickException(
            f"File too large ({file_size / 1024 / 1024:.1f}MB). Max is 25MB."
        )

    import openai

    client = openai.OpenAI(api_key=api_key)

    with open(file, "rb") as audio_file:
        kwargs: dict = {
            "model": model,
            "file": audio_file,
        }
        if language is not None:
            kwargs["language"] = language

        transcript = client.audio.transcriptions.create(**kwargs)

    text = transcript.text if hasattr(transcript, "text") else str(transcript)

    if output is not None:
        output.write_text(text)
        click.echo(f"Transcript written to {output}")
    else:
        click.echo(text)


if __name__ == "__main__":
    transcribe()
