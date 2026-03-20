---
name: chrome-mcp
description: >
  Chrome DevTools MCP tools for live browser interaction. WHEN the user wants
  to inspect web pages, debug frontend code, take screenshots, run JavaScript
  in a browser console, check network requests, profile performance, or
  automate browser interactions. WHEN NOT fetching URL content to save as
  notes (use web-grab) or headless scraping without DevTools (use web-grab
  with Playwright tier).
---

# Chrome DevTools MCP

Control a live Chrome browser via MCP tools. Run `/mcp` to confirm the `chrome-devtools` server is connected. If missing, ask the user to run `make install-chrome-mcp` (from the skills repo) and restart Claude Code.

## Tools

**Navigation:** `navigate_page`, `new_page`, `close_page`, `list_pages`, `select_page`, `wait_for`

**Input:** `click`, `drag`, `fill`, `fill_form`, `handle_dialog`, `hover`, `press_key`, `type_text`, `upload_file`

**Screenshots & DOM:** `take_screenshot`, `take_snapshot` (accessibility tree), `evaluate_script`

**Network:** `list_network_requests`, `get_network_request`

**Console:** `list_console_messages`, `get_console_message` (includes source-mapped stack traces)

**Performance:** `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`, `take_memory_snapshot`, `lighthouse_audit`

**Emulation:** `emulate` (device presets like "iPhone 15"), `resize_page`

## Gotchas

- **Browser launches on first tool use**, not on server startup. First call may be slow.
- **`take_snapshot`** returns an accessibility tree, not raw HTML. Use `evaluate_script` with `document.querySelector(...)` for DOM queries.
- **`fill_form`** takes a map of selectors to values for batch filling. Use `fill` for single fields.
- **`evaluate_script`** runs in the page context. Use `await` for async operations. Return values must be JSON-serializable.
- **Console messages** from `list_console_messages` are summaries. Use `get_console_message` with the message ID for full details and stack traces.
- **Performance traces** must be explicitly started and stopped. Call `performance_analyze_insight` after stopping to get actionable recommendations.
