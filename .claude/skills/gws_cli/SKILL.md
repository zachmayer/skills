---
name: gws_cli
description: >
  Google Workspace CLI (gws) reference for Drive, Gmail, Sheets, Calendar, and
  other Workspace APIs. Use when interacting with Google Workspace services.
  Do NOT use for Google Cloud Platform (use gcloud directly).
allowed-tools: Bash(gws *)
---

Google Workspace CLI reference. Commands follow the pattern `gws <service> <resource> <method>`. The CLI dynamically discovers all API methods — if a Workspace API supports it, `gws` can call it.

## Common Commands

### Drive

```bash
gws drive files list --params '{"q": "name contains \"report\""}'
gws drive files list --params '{"q": "mimeType = \"application/vnd.google-apps.folder\""}' --page-all
gws drive files get --params '{"fileId": "FILE_ID"}'
gws drive files create --json '{"name": "test.txt", "mimeType": "text/plain"}' --upload ./test.txt
gws drive files export --params '{"fileId": "FILE_ID", "mimeType": "text/csv"}' > output.csv
```

### Sheets

```bash
gws sheets spreadsheets get --params '{"spreadsheetId": "SHEET_ID"}'
gws sheets spreadsheets values get --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1!A1:D10"}'
gws sheets spreadsheets values append --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1", "valueInputOption": "USER_ENTERED"}' --json '{"values": [["a", "b", "c"]]}'
gws sheets spreadsheets create --json '{"properties": {"title": "New Sheet"}}'
```

### Gmail

```bash
gws gmail users messages list --params '{"userId": "me", "q": "is:unread after:2026/03/01"}'
gws gmail users messages get --params '{"userId": "me", "id": "MSG_ID"}'
gws gmail users labels list --params '{"userId": "me"}'
```

### Calendar

```bash
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-03-11T00:00:00Z", "timeMax": "2026-03-12T00:00:00Z"}'
gws calendar events insert --params '{"calendarId": "primary"}' --json '{"summary": "Meeting", "start": {"dateTime": "2026-03-11T10:00:00-05:00"}, "end": {"dateTime": "2026-03-11T11:00:00-05:00"}}'
```

## Key Flags

- `--params '{"key": "val"}'` — query and path parameters
- `--json '{...}'` — request body
- `--page-all` — auto-paginate (NDJSON output, one object per line)
- `--upload <file>` — multipart upload (Drive, Gmail attachments)
- `--dry-run` — preview the HTTP request without sending
- `--output-format json|yaml|table` — output format

## Schema Introspection

When unsure about parameters for a method, inspect the schema:

```bash
gws schema drive files list       # see available params for Drive files list
gws schema sheets spreadsheets values get  # see params for Sheets read
```

## Auth

```bash
gws auth setup     # one-time: creates GCP project, enables APIs (requires gcloud)
gws auth login     # OAuth login, select scopes
gws auth login -s drive,sheets,gmail  # login with specific scopes only
gws auth export --unmasked > creds.json  # export for headless/CI use
```

## Tips

- All output is JSON by default — pipe to `jq` for filtering
- `--page-all` streams NDJSON; use `jq -s '.'` to collect into an array
- Drive queries use the [Drive search syntax](https://developers.google.com/drive/api/guides/search-files) in the `q` parameter
- Gmail queries use the same syntax as the Gmail search box
- File IDs are in Drive URLs: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
