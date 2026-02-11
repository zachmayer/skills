---
name: web_grab
description: >
  WHEN: User shares a URL and wants to read, extract, or save its content.
  WHEN NOT: The URL is a GitHub repo (use gh CLI), a PDF (use pdf_to_markdown),
  or a skill to steal (use skill_stealer).
---

# Web Grab

Fetch a URL's content and save what's useful to obsidian as an atomic note, following the **MOC (Map of Content)** pattern.

## Step 1: Fetch content

Try these tiers in order. Stop at the first one that returns useful content:

1. **WebFetch tool** — built-in, works for most public pages
2. **`curl -sL <url>`** — raw HTML, useful for simple pages
3. **`wget -r -l 1 -np -A "*.html,*.htm" <url>`** — fetch a page and its immediate children (useful for multi-page content or site hierarchies)
4. **`gh api`** — if it's a GitHub URL (issues, PRs, files)
5. **Playwright headless browser** — for JS-heavy SPAs (Confluence, Atlassian, React apps) where tiers 1-2 return only JS bundles:
   ```bash
   uv run --directory SKILL_DIR python scripts/fetch_page.py <url>
   ```
   Options: `--timeout 60000` (slow pages), `--wait-for "css-selector"` (lazy content), `--full-page` (skip main-content detection). If content looks short or empty, retry with `--full-page`.
6. **Manual save** — if all automated methods fail (auth, JS rendering, bot blocking): ask the user to open the URL in Chrome, `Cmd+S` → "Webpage, Complete" or "HTML Only", and tell you the file path. Then read the saved HTML and extract meaningful content.

## Step 2: Discover related topics

Before saving, search the obsidian vault for related notes:

1. Identify 3-5 key topics/keywords from the fetched content
2. Use Grep/Glob on the obsidian vault (`$CLAUDE_OBSIDIAN_DIR/`) to find existing notes that match those topics
3. Collect filenames (without `.md`) for `[[wiki-links]]` and note any `#topic` tags already in use
4. Check if a MOC hub exists for this topic (e.g., `Factorio.md` for a Factorio blueprint)

## Step 3: Save as atomic note

1. Extract the useful content into clean markdown
2. Save as an **atomic note** (one URL = one note) via the `/obsidian` skill:
   - Descriptive filename (e.g., `Factorio Gleba Farm.md`, not `factoriobin-mrx1ek.md`)
   - **Source URL** and **Date grabbed** as required metadata (see below)
   - `#topic` tags — reuse existing vault tags, add new ones as needed
   - `[[wiki-links]]` to related notes found in Step 2
   - `## Related` section at the bottom with back-links
3. **Update the MOC hub** — if a hub note exists for this topic, add a link to the new note. If no hub exists but 2+ related notes now exist, create one.
4. Report what was saved, where, and what it links to

**MANDATORY metadata** — every web grab note MUST start with these two lines immediately after the title and tags. No exceptions. Never omit. If you skip this, the note is broken:

```markdown
Source: <full original URL — the exact URL the user shared, not a derived or cleaned URL>
Grabbed: <YYYY-MM-DD — today's date>
```

These lines are non-negotiable. A web grab note without Source and Grabbed metadata is incomplete and must be fixed before committing.

## Content-type hints

Special handling for specific content types. Add new entries as needed.

- **Factorio blueprints** (factoriobin.com) — Always include the full blueprint string. Check the page HTML for a CDN link (`cdn.factoriobin.com`) and curl it to get the raw string. Save it in a collapsible `<details>` block.
