#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click>=8.3.0",
#     "marker-pdf>=1.10.0",
# ]
# ///
"""Convert a PDF file to markdown using marker."""

from pathlib import Path

import click
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output path. Defaults to <input>.md",
)
def convert(pdf_path: Path, output: Path | None) -> None:
    """Convert a PDF file to markdown using marker."""
    if output is None:
        output = pdf_path.with_suffix(".md")

    models = create_model_dict()
    converter = PdfConverter(artifact_dict=models)
    rendered = converter(str(pdf_path))

    markdown_text = rendered.markdown

    output.write_text(markdown_text)
    click.echo(f"Converted {pdf_path} -> {output}")
    click.echo(markdown_text)


if __name__ == "__main__":
    convert()
