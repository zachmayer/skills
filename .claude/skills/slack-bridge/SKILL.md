---
name: slack-bridge
description: >
  Bridges Slack and Claude for reading, sending, and capturing messages via
  the official Slack MCP server. Use when the user says "check Slack",
  "send a Slack message", "read my messages", "capture from Slack", or
  mentions routing Slack content into memory or obsidian. Also triggers
  during autonomous heartbeat runs to poll a capture channel.
  Do NOT use for general Slack workspace administration or when no Slack
  MCP server is configured.
---

## Prerequisites

The official Slack MCP server must be configured. Check if it's available:

```
claude mcp list
```

If `slack` is not listed, the user needs to install it. The quickest method:

```
/plugin install slack
```

This authenticates via OAuth with their Slack workspace. Alternatively, add
it manually to `.mcp.json` — see [Slack's MCP docs](https://docs.slack.dev/ai/slack-mcp-server/connect-to-claude/).

## Capture Flow

1. **Check** — List channels to find the target, then read recent messages from it.
2. **Route** — Route each message through `/capture` for classification and filing.
3. **Acknowledge** — Reply in the Slack thread to confirm capture.

## Sending Messages

Post a message to the user's channel to send notifications or results back to their phone via Slack.

## Integration with Heartbeat

During autonomous heartbeat runs, check a designated capture channel for new messages and route them automatically. Use the channel-listing tool to resolve the channel name to its ID first. The channel name defaults to `#claude-capture` — ask the user for their preferred channel on first use.

If the channel is empty or has no new messages, skip silently — do not log "no messages."

## Failure Modes

- **MCP not configured**: If Slack MCP tools are not available, tell the user to run `/plugin install slack` or the manual setup command above.
- **Channel not found**: If the inbox channel does not exist, tell the user to create it in their Slack workspace.
- **OAuth expired**: If MCP calls fail with auth errors, tell the user to re-authorize: `/plugin install slack` (or re-run the manual `claude mcp add` command).
