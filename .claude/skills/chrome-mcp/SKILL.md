---
name: chrome-mcp
description: >
  Chrome DevTools MCP server for browser automation via Chrome DevTools
  Protocol. Use when the user wants to inspect web pages, debug frontend code,
  take screenshots, run JavaScript in a browser console, check network
  requests, profile performance, or automate browser interactions. Use when
  the user says "open Chrome", "inspect the page", "take a screenshot",
  "check the console", "debug the frontend", "run JS in the browser",
  "check network requests", "profile performance", or "automate the browser".
  Do NOT use for fetching URL content to save as notes (use web-grab), for
  headless scraping without DevTools (use web-grab with Playwright tier), or
  for GitHub API interactions (use gh-cli).
---

# Chrome DevTools MCP

Control and inspect a live Chrome browser via the Chrome DevTools Protocol. The `chrome-devtools-mcp` npm package acts as an MCP server, exposing 29 tools for browser automation, debugging, and performance analysis.

**Package:** `chrome-devtools-mcp` on npm
**Source:** https://github.com/ChromeDevTools/chrome-devtools-mcp

## Installation

### Quick install (user scope, recommended)

```bash
claude mcp add chrome-devtools --scope user -- npx -y chrome-devtools-mcp@latest
```

This registers the MCP server in `~/.claude.json` and persists across projects.

### Project scope

Add to `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### Verify installation

After adding, restart Claude Code and confirm with `/mcp`. The `chrome-devtools` server should appear in the list. The browser launches on first tool use, not on server startup.

## Connection Modes

### 1. Default: MCP launches Chrome

No extra flags needed. The server starts a Chrome instance with a dedicated profile at `~/.cache/chrome-devtools-mcp/chrome-profile-stable`. State persists between runs.

### 2. Auto-connect to running Chrome (Chrome 144+)

Best for sharing state between manual browsing and agent-driven testing.

**Step 1:** In Chrome, navigate to `chrome://inspect/#remote-debugging` and enable remote debugging (follow the dialog to allow connections).

**Step 2:** Configure MCP:

```bash
claude mcp add chrome-devtools --scope user -- npx -y chrome-devtools-mcp@latest --autoConnect
```

Or in `.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--autoConnect"]
    }
  }
}
```

Chrome shows a permission dialog on first connection. Click Allow.

### 3. Connect via remote debugging port

Best for sandboxed environments or when you need explicit control.

**Step 1:** Launch Chrome with remote debugging:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Step 2:** Configure MCP with `--browser-url`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]
    }
  }
}
```

### 4. Connect via WebSocket endpoint

For direct WebSocket connections (e.g., behind auth proxies):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y", "chrome-devtools-mcp@latest",
        "--wsEndpoint=ws://127.0.0.1:9222/devtools/browser/<id>",
        "--wsHeaders={\"Authorization\":\"Bearer TOKEN\"}"
      ]
    }
  }
}
```

Get the WebSocket URL from `http://127.0.0.1:9222/json/version` (field: `webSocketDebuggerUrl`).

## Available Tools

### Input automation (9 tools)

`click`, `drag`, `fill`, `fill_form`, `handle_dialog`, `hover`, `press_key`, `type_text`, `upload_file`

### Navigation (6 tools)

`close_page`, `list_pages`, `navigate_page`, `new_page`, `select_page`, `wait_for`

### Emulation (2 tools)

`emulate`, `resize_page`

### Performance (4 tools)

`performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`, `take_memory_snapshot`

### Network (2 tools)

`list_network_requests`, `get_network_request`

### Debugging (6 tools)

`evaluate_script`, `list_console_messages`, `get_console_message`, `lighthouse_audit`, `take_screenshot`, `take_snapshot`

## Common Workflows

### Inspect a web page

1. `navigate_page` to the URL
2. `take_screenshot` to see the current state
3. `take_snapshot` to get an accessibility snapshot of the DOM
4. `evaluate_script` to query specific elements or extract data

### Debug frontend issues

1. `navigate_page` to the page
2. `list_console_messages` to check for errors/warnings
3. `get_console_message` to inspect a specific message (includes source-mapped stack traces)
4. `evaluate_script` to test fixes in the console
5. `list_network_requests` to check for failed requests

### Profile performance

1. `navigate_page` to the target page
2. `performance_start_trace` to begin recording
3. Interact with the page (navigate, click, scroll)
4. `performance_stop_trace` to end recording
5. `performance_analyze_insight` to get actionable recommendations

### Automate form filling

1. `navigate_page` to the form page
2. `fill_form` with field selectors and values (batch fill)
3. Or use `fill` for individual fields, `click` for buttons
4. `take_screenshot` to verify the result

### Test responsive design

1. `emulate` a device (e.g., "iPhone 15") or `resize_page` to specific dimensions
2. `take_screenshot` to capture the viewport
3. Compare screenshots at different sizes

### Run JavaScript in the browser

Use `evaluate_script` to execute arbitrary JS in the page context:
- Query the DOM: `document.querySelectorAll('.error').length`
- Read application state: `JSON.stringify(window.__APP_STATE__)`
- Modify styles: `document.body.style.background = 'red'`
- Call page APIs: `await fetch('/api/status').then(r => r.json())`

## Configuration Flags

| Flag | Description |
|:-----|:------------|
| `--autoConnect` | Auto-connect to running Chrome (Chrome 144+) |
| `--browser-url URL` | Connect to Chrome at URL (e.g., `http://127.0.0.1:9222`) |
| `--wsEndpoint URL` | WebSocket endpoint for direct connection |
| `--headless` | Run without visible browser window |
| `--isolated` | Use temporary profile, cleaned up on close |
| `--channel CHAN` | Chrome channel: `stable`, `canary`, `beta`, `dev` |
| `--executable-path PATH` | Path to custom Chrome binary |
| `--viewport WxH` | Initial viewport size (e.g., `1280x720`) |
| `--slim` | Expose only 3 tools: navigation, script execution, screenshots |
| `--no-usage-statistics` | Opt out of Google usage statistics collection |
| `--no-performance-crux` | Disable sending URLs to CrUX API for field data |
| `--log-file PATH` | Write debug logs to file (set `DEBUG=*` for verbose) |
| `--chrome-arg ARG` | Pass additional args to Chrome |
| `--proxy-server URL` | Proxy server for Chrome |
| `--accept-insecure-certs` | Ignore self-signed/expired cert errors |

### Slim mode

For basic browser tasks, use `--slim` to reduce the tool surface to 3 tools (navigate, evaluate_script, take_screenshot):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--slim", "--headless"]
    }
  }
}
```

## Headless mode

Add `--headless` for CI or environments without a display. In headless mode, max viewport is 3840x2160px. Combine with `--isolated` for clean, disposable sessions:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless", "--isolated"]
    }
  }
}
```

## Troubleshooting

- **Browser not starting:** Ensure Chrome is installed and `npx` is available. Try `npx -y chrome-devtools-mcp@latest --help` to verify the package works.
- **Connection refused:** If using `--browser-url`, confirm Chrome is running with `--remote-debugging-port=9222` and the port is accessible.
- **Tool not found in `/mcp`:** Restart Claude Code after adding the server config. Check that `.mcp.json` or `~/.claude.json` has correct JSON syntax.
- **Debug logging:** Use `--log-file ~/claude/scratch/chrome-mcp-debug.log` with env `DEBUG=*` to capture verbose logs.
- **Signed-in sites blocking automation:** Some sites detect WebDriver-controlled browsers. Use `--autoConnect` to connect to your normal Chrome session instead.
