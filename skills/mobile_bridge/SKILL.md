---
name: mobile_bridge
description: >
  Phone-to-Claude capture via Slack MCP. Use when the user wants to check
  their Slack inbox channel for messages to capture, or when the heartbeat
  should periodically process incoming messages from Slack.
  Do NOT use for general Slack operations (use the Slack MCP tools directly)
  or for sending messages TO the user (use ntfy or direct Slack MCP).
---

Reads messages from a designated Slack channel and routes each one through the `capture` skill.

## Prerequisites

One-time setup — the user must configure the Slack MCP server:

```bash
claude mcp add --transport http --scope user slack https://mcp.slack.com/mcp
```

This triggers an OAuth flow — authorize your Slack workspace when prompted. No API keys, no bot tokens, no admin approval needed.

Then create a `#claude-inbox` channel in your Slack workspace (or any channel — configure the name below).

## Configuration

The inbox channel name defaults to `#claude-inbox`. The user can override this by setting a different channel name in their Agent Goals or by telling the agent directly.

## Processing Workflow

When invoked (manually or by heartbeat):

1. **List recent messages** in the inbox channel using the Slack MCP `slack_list_channel_messages` tool (or equivalent — tool names vary by MCP server version). Look for unprocessed messages since the last check.

2. **For each message**, route through the `capture` skill:
   - The message text is the input
   - Let capture classify (ephemeral/durable/task/guidance) and route to the right destination
   - If the message contains a URL, also consider the `web_grab` skill

3. **Acknowledge** each processed message by replying in the Slack thread: "Captured → [destination]" so the user knows it was processed.

4. **Log** what was processed to `hierarchical_memory` as a daily note entry:
   ```
   Mobile bridge: processed N messages from #claude-inbox
   - "message summary" → destination
   ```

## Heartbeat Integration

When invoked from the heartbeat, check `#claude-inbox` for any messages posted since the last heartbeat cycle. Process each one. If the channel is empty or has no new messages, skip silently — do not log "no messages."

## Failure Modes

- **MCP not configured**: If Slack MCP tools are not available, tell the user to run the setup command above.
- **Channel not found**: If the inbox channel doesn't exist, tell the user to create it.
- **OAuth expired**: If MCP calls fail with auth errors, tell the user to re-authorize: `claude mcp add --transport http --scope user slack https://mcp.slack.com/mcp`
