---
name: mobile_bridge
description: >
  Capture messages from phone into Claude's memory and obsidian vault.
  WHEN: User wants to send quick notes from phone to Claude, set up mobile
  capture, check ntfy inbox, or process captured messages. Also when user
  says "check my messages" or "what did I send from my phone".
  WHEN NOT: For full mobile Claude Code sessions (use Happy Coder directly),
  for outbound notifications only (use Claude Code hooks + ntfy).
---

# Mobile Bridge

Capture quick thoughts from your phone into hierarchical memory and obsidian.

The bridge uses **ntfy** (ntfy.sh) as a zero-account message transport. Send a message from the ntfy app on your phone → a script polls and saves it to memory.

## Setup

### 1. Generate a topic

```bash
# One-time setup — add to ~/.zshrc
export CLAUDE_NTFY_TOPIC="claude-capture-$(whoami)-$(openssl rand -hex 6)"
echo "export CLAUDE_NTFY_TOPIC=\"$CLAUDE_NTFY_TOPIC\"" >> ~/.zshrc
```

The topic name is the only auth. Keep it secret.

### 2. Subscribe on phone

1. Install **ntfy** app (iOS App Store / Google Play)
2. Subscribe to your topic: tap "+" → enter your `$CLAUDE_NTFY_TOPIC` value
3. Test: send a message from the app → verify with `curl -s "ntfy.sh/$CLAUDE_NTFY_TOPIC/json?poll=1"`

### 3. Capture messages

Check for and process messages from your phone:

```bash
uv run --directory SKILL_DIR python scripts/capture.py check
```

Process all pending messages (saves to memory, clears inbox):

```bash
uv run --directory SKILL_DIR python scripts/capture.py process
```

Process and route to a specific destination:

```bash
uv run --directory SKILL_DIR python scripts/capture.py process --route memory
uv run --directory SKILL_DIR python scripts/capture.py process --route obsidian
uv run --directory SKILL_DIR python scripts/capture.py process --route both
```

Send a message back to the phone:

```bash
uv run --directory SKILL_DIR python scripts/capture.py send "PR #42 merged, all tests passing"
```

## Routing

When processing captured messages, route by content:

| Content | Route to | Example |
|---------|----------|---------|
| Quick thought / idea | `memory` daily note | "Look into GRPO for prompt optimization" |
| Reference / fact | `obsidian` knowledge_graph | "Board SDK v2 drops Feb 28" |
| Action item | `memory` daily note as TODO | "TODO: file taxes by March 16" |
| Both durable + timely | `both` | "CPA meeting moved to Thursday — Dimov Tax" |

If `--route` is not specified, defaults to `memory` (daily note).

## Heartbeat Integration

During heartbeat cycles, check for captured messages:

```bash
uv run --directory SKILL_DIR python scripts/capture.py check
```

If messages exist, process them before other work. This gives the user a way to send instructions to the heartbeat agent from their phone.

## Full Mobile Sessions

For interactive Claude Code from your phone (not just capture), use **Happy Coder**:

```bash
npm install -g happy-coder
happy    # scan QR code with Happy app
```

See [[Claude Code Mobile Bridge]] in obsidian for full setup details.
