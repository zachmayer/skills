---
name: google_docs
description: >
  WHEN: User wants to extract content from Google Docs or Sheets into obsidian
  notes, or needs to read a Google Doc/Sheet programmatically.
  WHEN NOT: For non-Google URLs (use web_grab), for local files, or when the
  user wants to write/edit Google Docs.
---

# Google Docs Importer

Extract content from Google Docs and Sheets into obsidian notes.

## Prerequisites

### 1. Google Cloud Service Account

This skill requires a Google Cloud service account with the Google Docs and Sheets APIs enabled.

**One-time setup** (human task):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable the **Google Docs API** and **Google Sheets API**
4. Create a **Service Account** (IAM & Admin → Service Accounts)
5. Create a JSON key for the service account and download it
6. Set the path in your shell profile:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/google/service-account.json"
   ```
7. **Share each Doc/Sheet** with the service account email (found in the JSON key file as `client_email`)

### 2. Install optional dependency

```bash
uv sync --extra google
```

## Usage

Extract a Google Doc to markdown:

```bash
uv run --directory SKILL_DIR python scripts/google_docs.py doc <DOC_ID>
```

Extract a Google Sheet to markdown:

```bash
uv run --directory SKILL_DIR python scripts/google_docs.py sheet <SHEET_ID>
```

Options:
- `--output FILE` — write to file instead of stdout
- `--sheet-name NAME` — (sheets only) extract a specific sheet tab

### Finding the document ID

The document ID is in the URL:
- Docs: `https://docs.google.com/document/d/<DOC_ID>/edit`
- Sheets: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

## After extraction

Save the extracted content to obsidian following the `web_grab` pattern:
1. Save as atomic note with Source URL and Date metadata
2. Add topic tags and wiki-links
3. Update or create MOC hub if needed
