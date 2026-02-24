---
name: google_docs
description: >
  Extract content from Google Docs or Sheets into obsidian. Use when the user
  shares a Google Docs/Sheets URL or asks to import a Google document. Do NOT
  use for non-Google URLs (use web_grab), PDFs (use pdf_to_markdown), or when
  the user wants to edit/write Google Docs.
allowed-tools: Bash(curl *)
---

# Google Docs Importer

Extract Google Docs and Sheets content as markdown or CSV, then save to obsidian.

## Step 1: Extract the document ID

The document ID is the long alphanumeric string in the URL:

- Docs: `https://docs.google.com/document/d/{DOC_ID}/edit`
- Sheets: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

## Step 2: Fetch content

The document must be shared as "Anyone with the link can view." Use the Google export URL with `curl -sL` (the `-L` flag follows Google's redirects):

**Google Docs** — export as markdown:

```bash
curl -sL "https://docs.google.com/document/d/{DOC_ID}/export?format=markdown"
```

Other formats: `txt` (plain text), `html`, `docx`, `pdf`.

**Google Sheets** — export as CSV:

```bash
curl -sL "https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
```

Target a specific tab by adding `&gid={SHEET_GID}` (the `gid` is in the URL when viewing that tab). Other formats: `tsv`, `xlsx`.

If `curl` returns an HTML login page or error, the document is not publicly shared. Ask the user to either:
1. Share the document with "Anyone with the link" (viewer access), or
2. Set up the Google Drive MCP server for private document access (see below).

## Step 3: Save to obsidian

Follow the `web_grab` pattern:

1. Save as an atomic note with a descriptive filename
2. Include mandatory metadata:
   ```markdown
   Source: <original Google Docs/Sheets URL>
   Date: <YYYY-MM-DD>
   ```
3. Add `#topic` tags and `[[wiki-links]]` to related vault notes
4. For Sheets: convert CSV to a markdown table for readability
5. Update or create a MOC hub if related notes exist

## Private documents: Google Drive MCP

For documents that cannot be shared publicly, use Anthropic's Google Drive MCP server. This requires one-time setup:

### Setup

1. Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com/)
2. Enable the **Google Drive API**
3. Create an **OAuth Client ID** (Desktop App type) under Credentials
4. Download the OAuth keys JSON, save as `~/.config/google/gcp-oauth.keys.json`
5. Run the auth flow:
   ```bash
   GDRIVE_OAUTH_PATH=~/.config/google/gcp-oauth.keys.json \
   npx -y @modelcontextprotocol/server-gdrive auth
   ```
6. Register the MCP server with Claude Code:
   ```bash
   claude mcp add gdrive -- npx -y @modelcontextprotocol/server-gdrive
   ```

### Usage

Once configured, the `gdrive_search` and `gdrive_read_file` MCP tools are available. Docs auto-convert to markdown, Sheets to CSV.
