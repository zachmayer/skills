---
name: web_grab
description: >
  WHEN: User shares a URL and wants to read, extract, or save its content.
  WHEN NOT: The URL is a GitHub repo (use gh CLI), a PDF (use pdf_to_markdown),
  or a skill to steal (use skill_stealer).
---

# Web Grab

Fetch a URL's content and save what's useful to obsidian. Try automated methods first, fall back to manual.

## Step 1: Try automated fetch

Try these in order. Stop at the first one that returns useful content:

1. **WebFetch tool** — built-in, works for most public pages
2. **`curl -sL <url>`** — raw HTML, useful for simple pages
3. **`gh api`** — if it's a GitHub URL (issues, PRs, files)

## Step 2: If automated fails

If the page requires auth, JavaScript rendering, or blocks bots:

1. Tell the user: "I can't fetch this automatically. Please:"
   - Open the URL in Chrome
   - Press `Cmd+S` (Save As)
   - Save as **"Webpage, Complete"** or **"Webpage, HTML Only"**
   - Tell me the file path (or drag it into the terminal)
2. Read the saved HTML file
3. Extract the meaningful content (strip nav, ads, boilerplate)

## Step 3: Discover related topics

Before saving, search the obsidian vault for related notes:

1. Identify 3-5 key topics/keywords from the fetched content
2. Use Grep/Glob on `~/claude/obsidian/` to find existing notes that match those topics
3. Collect filenames (without `.md`) for `[[wiki-links]]` and note any `#topic` tags already in use

## Step 4: Process and save

1. Extract the useful content into clean markdown
2. Use the `/obsidian` skill to save a note with:
   - Title from the page
   - **Source URL** — always include the full original URL
   - **Date grabbed** — ISO date (YYYY-MM-DD) of when the content was fetched
   - Key content in markdown
   - `#topic` tags — reuse existing vault tags where applicable, add new ones as needed
3. Add `[[wiki-links]]` to connect to related obsidian notes found in Step 3
4. Report what was saved, where, and what it links to

**Required metadata** — every web grab note MUST start with:

```markdown
Source: <full original URL>
Grabbed: <YYYY-MM-DD>
```

## Content-type hints

Special handling for specific content types. Add new entries as needed.

- **Factorio blueprints** (factoriobin.com) — Always include the full blueprint string. Check the page HTML for a CDN link (`cdn.factoriobin.com`) and curl it to get the raw string. Save it in a code block in the note.
