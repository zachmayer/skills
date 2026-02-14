"""Extract content from Google Docs and Sheets as markdown."""

import json
import os
import re
import sys
from pathlib import Path

import click


def _get_credentials_path() -> str:
    """Get the service account credentials path from env."""
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not path:
        click.echo(
            "Error: GOOGLE_APPLICATION_CREDENTIALS not set.\n"
            "Set it to the path of your Google service account JSON key file.\n"
            "See: skills/google_docs/SKILL.md for setup instructions.",
            err=True,
        )
        sys.exit(1)
    if not Path(path).exists():
        click.echo(f"Error: Credentials file not found: {path}", err=True)
        sys.exit(1)
    return path


def _build_service(api: str, version: str):
    """Build a Google API service client."""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        click.echo(
            "Error: google-api-python-client not installed.\nRun: uv sync --extra google",
            err=True,
        )
        sys.exit(1)

    creds_path = _get_credentials_path()
    scopes = [
        "https://www.googleapis.com/auth/documents.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return build(api, version, credentials=creds)


def _extract_doc_id(doc_id_or_url: str) -> str:
    """Extract document ID from a URL or return as-is if already an ID."""
    # Match Google Docs URL pattern
    m = re.match(r"https?://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)", doc_id_or_url)
    if m:
        return m.group(1)
    # Match Google Sheets URL pattern
    m = re.match(r"https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)", doc_id_or_url)
    if m:
        return m.group(1)
    # Assume it's already an ID
    return doc_id_or_url


def _structural_element_to_md(element: dict) -> str:
    """Convert a Google Docs structural element to markdown."""
    if "paragraph" in element:
        return _paragraph_to_md(element["paragraph"])
    if "table" in element:
        return _table_to_md(element["table"])
    if "sectionBreak" in element:
        return "\n---\n"
    return ""


def _paragraph_to_md(paragraph: dict) -> str:
    """Convert a Google Docs paragraph to markdown."""
    style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
    elements = paragraph.get("elements", [])

    text_parts = []
    for elem in elements:
        text_run = elem.get("textRun", {})
        content = text_run.get("content", "")
        text_style = text_run.get("textStyle", {})

        if text_style.get("bold"):
            content = f"**{content.strip()}** " if content.strip() else content
        if text_style.get("italic"):
            content = f"*{content.strip()}* " if content.strip() else content
        if text_style.get("link", {}).get("url"):
            url = text_style["link"]["url"]
            content = f"[{content.strip()}]({url}) " if content.strip() else content

        text_parts.append(content)

    text = "".join(text_parts).rstrip()

    # Map heading styles
    heading_map = {
        "HEADING_1": "# ",
        "HEADING_2": "## ",
        "HEADING_3": "### ",
        "HEADING_4": "#### ",
        "HEADING_5": "##### ",
        "HEADING_6": "###### ",
    }

    prefix = heading_map.get(style, "")

    if not text:
        return ""

    # Handle list items
    bullet = paragraph.get("bullet")
    if bullet:
        nesting = bullet.get("nestingLevel", 0)
        indent = "  " * nesting
        return f"{indent}- {text}"

    return f"{prefix}{text}"


def _table_to_md(table: dict) -> str:
    """Convert a Google Docs table to markdown."""
    rows = table.get("tableRows", [])
    if not rows:
        return ""

    md_rows = []
    for row in rows:
        cells = row.get("tableCells", [])
        cell_texts = []
        for cell in cells:
            cell_content = cell.get("content", [])
            parts = [_structural_element_to_md(e) for e in cell_content]
            cell_text = " ".join(p.strip() for p in parts if p.strip())
            cell_texts.append(cell_text)
        md_rows.append("| " + " | ".join(cell_texts) + " |")

    if len(md_rows) >= 1:
        # Add separator after header row
        num_cols = md_rows[0].count("|") - 1
        separator = "| " + " | ".join(["---"] * num_cols) + " |"
        md_rows.insert(1, separator)

    return "\n".join(md_rows)


def extract_doc(doc_id: str) -> str:
    """Extract a Google Doc as markdown."""
    service = _build_service("docs", "v1")
    doc = service.documents().get(documentId=doc_id).execute()

    title = doc.get("title", "Untitled")
    body = doc.get("body", {})
    content = body.get("content", [])

    parts = [f"# {title}", ""]
    for element in content:
        md = _structural_element_to_md(element)
        if md:
            parts.append(md)

    return "\n".join(parts)


def extract_sheet(sheet_id: str, sheet_name: str | None = None) -> str:
    """Extract a Google Sheet as markdown."""
    service = _build_service("sheets", "v4")

    # Get spreadsheet metadata
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    title = spreadsheet.get("properties", {}).get("title", "Untitled")
    sheets = spreadsheet.get("sheets", [])

    if sheet_name:
        target_sheets = [s for s in sheets if s["properties"]["title"] == sheet_name]
        if not target_sheets:
            available = [s["properties"]["title"] for s in sheets]
            click.echo(f"Error: Sheet '{sheet_name}' not found. Available: {available}", err=True)
            sys.exit(1)
    else:
        target_sheets = sheets

    parts = [f"# {title}", ""]

    for sheet_info in target_sheets:
        tab_title = sheet_info["properties"]["title"]
        range_name = f"'{tab_title}'"

        result = (
            service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        )

        values = result.get("values", [])
        if not values:
            parts.append(f"## {tab_title}")
            parts.append("*(empty)*")
            parts.append("")
            continue

        parts.append(f"## {tab_title}")
        parts.append("")

        # Normalize row lengths
        max_cols = max(len(row) for row in values)
        normalized = [row + [""] * (max_cols - len(row)) for row in values]

        # First row as header
        header = normalized[0]
        parts.append("| " + " | ".join(str(c) for c in header) + " |")
        parts.append("| " + " | ".join(["---"] * max_cols) + " |")

        for row in normalized[1:]:
            parts.append("| " + " | ".join(str(c) for c in row) + " |")

        parts.append("")

    return "\n".join(parts)


def parse_doc_id(doc_id_or_url: str) -> str:
    """Parse a document ID from a URL or raw ID."""
    return _extract_doc_id(doc_id_or_url)


@click.group()
def cli():
    """Extract content from Google Docs and Sheets."""
    pass


@cli.command()
@click.argument("doc_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: stdout)")
def doc(doc_id: str, output: str | None) -> None:
    """Extract a Google Doc as markdown."""
    doc_id = parse_doc_id(doc_id)
    md = extract_doc(doc_id)
    if output:
        Path(output).write_text(md)
        click.echo(f"Saved to {output}")
    else:
        click.echo(md)


@cli.command()
@click.argument("sheet_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: stdout)")
@click.option("--sheet-name", "-s", help="Extract a specific sheet tab")
def sheet(sheet_id: str, output: str | None, sheet_name: str | None) -> None:
    """Extract a Google Sheet as markdown."""
    sheet_id = parse_doc_id(sheet_id)
    md = extract_sheet(sheet_id, sheet_name)
    if output:
        Path(output).write_text(md)
        click.echo(f"Saved to {output}")
    else:
        click.echo(md)


@cli.command()
def check_auth() -> None:
    """Check if Google API credentials are configured."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path:
        click.echo("GOOGLE_APPLICATION_CREDENTIALS: not set")
        sys.exit(1)

    if not Path(creds_path).exists():
        click.echo(f"GOOGLE_APPLICATION_CREDENTIALS: {creds_path} (file not found)")
        sys.exit(1)

    try:
        with open(creds_path) as f:
            data = json.load(f)
        email = data.get("client_email", "unknown")
        project = data.get("project_id", "unknown")
        click.echo(f"GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
        click.echo(f"  Service account: {email}")
        click.echo(f"  Project: {project}")
        click.echo("  Status: OK (credentials file found)")
        click.echo(f"\nShare your Google Docs/Sheets with: {email}")
    except json.JSONDecodeError:
        click.echo(f"GOOGLE_APPLICATION_CREDENTIALS: {creds_path} (invalid JSON)")
        sys.exit(1)


if __name__ == "__main__":
    cli()
