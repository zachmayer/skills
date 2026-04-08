---
name: gws-cli
description: >
  Google Workspace CLI (gws) for Drive, Gmail, Sheets, and Calendar. Use when
  the user says "check my email", "send an email", "search Drive", "list
  calendar events", "create a spreadsheet", "triage inbox", or any Google
  Workspace task. Covers helper commands (+send, +triage, +reply), raw API
  calls, multi-account profiles, pagination, and schema introspection. Do NOT
  use for Google Cloud Platform tasks (use gcloud) or non-Google services.
allowed-tools: Bash(gws *), Bash(*/gws-as.sh *)
---

Google Workspace CLI reference. Source and docs: https://github.com/googleworkspace/cli

Commands follow `gws <service> <resource> <method>`. The CLI dynamically discovers all API methods via Google's Discovery Service — if a Workspace API supports it, `gws` can call it.

## Safety

- **Confirm with the user before write/delete commands.** Sending email, creating events, and deleting files are not reversible.
- Prefer `--dry-run` for destructive operations to preview the request first.

## Defaults

- **Inbox = `is:inbox`.** When the user asks about their inbox, use `--query 'is:inbox'`. Use `in:anywhere` only when explicitly searching beyond the inbox.

## Helper Commands (Preferred)

Use helper commands (`+verb`) instead of raw API calls when available — they're simpler and handle encoding:

```bash
# Gmail
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi Alice!'
gws gmail +triage --max 10 --query 'is:inbox'  # inbox
gws gmail +reply --id MSG_ID --body 'Thanks!'
gws gmail +reply-all --id MSG_ID --body 'Acknowledged.'
gws gmail +forward --id MSG_ID --to bob@example.com
gws gmail +watch                    # stream new emails (NDJSON)

# Calendar
gws calendar +insert --summary 'Meeting' --attendees alice@example.com --start '2026-03-12T10:00' --duration 30
```

## Raw API Commands

When helpers don't cover your use case, use the raw API:

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
gws sheets spreadsheets values get --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1!A1:D10"}'
gws sheets spreadsheets values append --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1", "valueInputOption": "USER_ENTERED"}' --json '{"values": [["a", "b", "c"]]}'
gws sheets spreadsheets create --json '{"properties": {"title": "New Sheet"}}'
```

### Gmail

```bash
gws gmail users messages list --params '{"userId": "me", "q": "is:unread after:2026/03/01"}'
gws gmail users messages get --params '{"userId": "me", "id": "MSG_ID"}'
```

### Calendar

```bash
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-03-11T00:00:00Z", "timeMax": "2026-03-12T00:00:00Z"}'
gws calendar freebusy query --json '{"timeMin": "...", "timeMax": "...", "items": [{"id": "alice@example.com"}, {"id": "bob@example.com"}]}'
```

## Key Flags

| Flag | Description |
|------|-------------|
| `--params '{"key": "val"}'` | Query and path parameters |
| `--json '{...}'` | Request body |
| `--page-all` | Auto-paginate (NDJSON output) |
| `--page-limit <N>` | Max pages when using --page-all (default: 10) |
| `--page-delay <MS>` | Delay between pages in ms (default: 100) |
| `--upload <file>` | Multipart upload (Drive, Gmail attachments) |
| `-o, --output <PATH>` | Save binary responses to file |
| `--dry-run` | Preview request without sending |
| `--format json\|yaml\|table\|csv` | Output format (default: json) |

## Schema Introspection

When unsure about parameters, inspect the schema:

```bash
gws schema drive.files.list
gws schema gmail.users.messages.send
gws gmail --help            # list all gmail resources
gws drive files --help      # list all file methods
```

## Multiple Accounts

Supports multiple Google accounts (home, work, school, etc.) via `~/.claude/gws-accounts.json`:

```json
{
  "default": {
    "path": "~/.config/gws",
    "email": "alice@gmail.com",
    "description": "Personal account"
  },
  "work": {
    "path": "~/.config/gws/profiles/work",
    "email": "alice@company.com",
    "description": "Work account"
  }
}
```

**Rules:**
- Bare `gws ...` uses the default account. No env var needed.
- For non-default accounts, use the wrapper script: `~/.claude/skills/gws-cli/scripts/gws-as.sh <profile> <gws args...>`
- If the user names an account, email, or domain, use the matching profile.
- If ambiguous and the action is a write/send/delete, ask which account.
- If `gws-accounts.json` is missing, assume only the default account exists.

```bash
# Default account
gws gmail +triage

# Non-default account
~/.claude/skills/gws-cli/scripts/gws-as.sh work gmail +triage
```

## Auth

On a new machine, run `gws auth setup` first — it creates a GCP project, enables Workspace APIs, and generates an OAuth client. This is a one-time prerequisite before `gws auth login` will work. Requires `gcloud` CLI (`brew install google-cloud-sdk`).

```bash
gws auth setup     # one-time per machine: GCP project + OAuth client
gws auth login     # OAuth login, select scopes
gws auth login -s drive,sheets,gmail  # login with specific scopes only
```

### Scope selection and RAPT

**WARNING: The `-s` flag silently includes `cloud-platform` scope.** Even when you specify only Workspace services (e.g. `-s gmail,drive`), the `gws` CLI adds `cloud-platform` to the token request. This triggers RAPT (Re-Authentication Proof Token) session control, which forces re-authentication every 1-24 hours (max 24hr, configured by Google Workspace admin). Workspace-only scopes (gmail, drive, docs, calendar, etc.) are NOT subject to RAPT and would produce long-lived tokens -- but you only get that benefit if `cloud-platform` is truly excluded from the token.

**Workaround (unconfirmed):** Using `--scopes` with explicit full scope URLs (e.g. `https://www.googleapis.com/auth/gmail.modify`) instead of the `-s` shorthand *may* avoid the silent `cloud-platform` inclusion, but this has not been verified as of 2026-04-07.

Request only the Workspace scopes you need:

```bash
gws auth login -s gmail,calendar,drive,docs,sheets,slides,tasks
```

Do NOT include `cloud-platform` scope unless you need GCP resource management. The `--full` flag also includes `cloud-platform` -- avoid it unless you specifically need GCP access. If you are being prompted to re-authenticate frequently (daily/weekly), the cause is almost certainly `cloud-platform` scope triggering RAPT. Re-login with only Workspace scopes to fix it.

### Adding an account

```bash
mkdir -p ~/.config/gws/profiles/<name>
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws/profiles/<name> gws auth setup
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws/profiles/<name> gws auth login
```

Then add the profile to `~/.claude/gws-accounts.json`. Each entry needs `path` (config dir) and `description`. `email` is optional but helps with disambiguation. If the file doesn't exist, create it:

```json
{
  "default": {
    "path": "~/.config/gws",
    "email": "user@gmail.com",
    "description": "Personal account"
  },
  "<name>": {
    "path": "~/.config/gws/profiles/<name>",
    "email": "user@company.com",
    "description": "Work account"
  }
}
```

The `default` entry is the account used by bare `gws` commands. All other entries require `~/.claude/skills/gws-cli/scripts/gws-as.sh <name>` to use.

## Tips

- JSON output by default — pipe to `jq` for filtering
- `--page-all` streams NDJSON; use `jq -s '.'` to collect into an array
- Drive queries use [Drive search syntax](https://developers.google.com/drive/api/guides/search-files) in the `q` param
- Gmail queries use the same syntax as the Gmail search box
- File IDs are in Drive URLs: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
