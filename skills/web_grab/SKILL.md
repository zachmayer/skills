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

## Step 3: Process and save

1. Extract the useful content into clean markdown
2. Use the `/obsidian` skill to save a note with:
   - Title from the page
   - Source URL as metadata
   - Key content in markdown
   - Tags based on topic
3. Add `[[wiki-links]]` to connect to related obsidian notes (by filename without `.md`)
4. Report what was saved and where
