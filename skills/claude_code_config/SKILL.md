---
name: claude_code_config
description: >
  Claude Code configuration reference for settings, permissions, env vars,
  hooks, MCP, and CLAUDE.md format. Use when configuring Claude Code behavior,
  writing permission rules, setting up hooks, or adding MCP servers. Do NOT
  use for general Claude Code usage questions.
---

Claude Code configuration reference. For basic usage, consult `claude --help` — this covers the config surface area that's hard to remember.

## Settings Files & Precedence

Highest wins. Each level overrides the one below it.

| Precedence | Scope | Location |
|:--|:--|:--|
| 1 (highest) | Managed | macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`; Linux: `/etc/claude-code/managed-settings.json` |
| 2 | CLI flags | Command line arguments |
| 3 | Project | `.claude/settings.json` (committed to git) |
| 4 | Local | `.claude/settings.local.json` (gitignored) |
| 5 (lowest) | User | `~/.claude/settings.json` |

All settings files use JSON. Optional `$schema` property: `https://json.schemastore.org/claude-code-settings.json`

## CLAUDE.md Memory

| Type | Location | Loaded | Shared |
|:--|:--|:--|:--|
| Managed | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux: `/etc/claude-code/CLAUDE.md` | Always | Org-wide |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Always | Team (git) |
| Project rules | `./.claude/rules/*.md` | Always (or path-filtered) | Team (git) |
| User | `~/.claude/CLAUDE.md` | Always | No |
| Local | `./CLAUDE.local.md` (auto-gitignored) | Always | No |
| Auto memory | `~/.claude/projects/<project>/memory/MEMORY.md` | First 200 lines | No |

**Loading rules:**
- Files in parent directories of cwd: loaded in full at launch
- Files in child directories: loaded on demand when Claude reads files there
- More specific instructions take precedence over broader ones

**Imports:** Use `@path/to/file` to import. Relative paths resolve from the importing file. Max depth: 5 hops. Not evaluated inside code blocks.

```markdown
See @README for project overview and @package.json for available npm commands.
```

**Path-specific rules** (`.claude/rules/*.md`):

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Rules
Rules here only apply when working in matching paths.
```

Glob patterns: `**/*.ts`, `src/**/*`, `*.md`, `src/**/*.{ts,tsx}`, `{src,lib}/**/*.ts`

## Permission Modes

| Mode | Description |
|:--|:--|
| `default` | Prompts on first use |
| `acceptEdits` | Auto-accepts file edits for session |
| `plan` | Read-only — no modifications or commands |
| `dontAsk` | Auto-denies unless pre-approved via `permissions.allow` |
| `bypassPermissions` | Skips all prompts (requires safe environment) |

## Permission Rules

**Format:** `Tool` or `Tool(specifier)` — evaluated deny → ask → allow (first match wins).

```jsonc
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",       // commands starting with npm run
      "Edit(./src/**)",        // edit files in src recursively
      "Read(*.env)",           // read .env files
      "mcp__puppeteer",       // any tool from puppeteer MCP
      "Task(Explore)"          // the Explore subagent
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(//etc/shadow)"    // absolute paths use // prefix
    ]
  }
}
```

**Path prefix meanings:**

| Prefix | Meaning | Example |
|:--|:--|:--|
| `//path` | Absolute from filesystem root | `Read(//Users/alice/secrets/**)` |
| `~/path` | From home directory | `Read(~/Documents/*.pdf)` |
| `/path` | Relative to settings file | `Edit(/src/**/*.ts)` |
| `./path` or bare | Relative to cwd | `Read(*.env)` |

`*` matches one directory level; `**` matches recursively.

**Bash wildcard note:** `Bash(ls *)` (space before `*`) enforces word boundary — matches `ls -la` but NOT `lsof`. Claude Code is aware of `&&` so `Bash(safe-cmd *)` won't match `safe-cmd && evil-cmd`.

## Key Settings

### Model & API

```jsonc
{
  "model": "claude-sonnet-4-6",              // override default model
  "availableModels": ["sonnet", "haiku"],    // restrict model selection
  "alwaysThinkingEnabled": true,             // extended thinking by default
  "apiKeyHelper": "/path/to/script"          // custom auth script
}
```

### Sandbox

```jsonc
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker"],
    "network": {
      "allowedDomains": ["*.example.com"],
      "allowLocalBinding": false
    }
  }
}
```

### Attribution

```jsonc
{
  "attribution": {
    "commit": "Co-Authored-By: Claude <noreply@anthropic.com>",
    "pr": "Generated with Claude Code"
  }
}
```

Empty string hides attribution. `includeCoAuthoredBy` is deprecated — use `attribution` instead.

### MCP Settings

```jsonc
{
  "enableAllProjectMcpServers": true,       // auto-approve .mcp.json servers
  "enabledMcpjsonServers": ["server-a"],    // approve specific servers
  "disabledMcpjsonServers": ["server-b"],   // reject specific servers
  // Managed only:
  "allowedMcpServers": [{"serverName": "allowed"}],
  "deniedMcpServers": [{"serverUrl": "*.evil.com"}]
}
```

### Other Useful Settings

```jsonc
{
  "env": { "MY_VAR": "value" },             // env vars for every session
  "permissions.defaultMode": "default",      // default permission mode
  "permissions.additionalDirectories": [],   // extra working directories
  "cleanupPeriodDays": 30,                   // session cleanup threshold
  "respectGitignore": true,                  // file picker respects .gitignore
  "language": "japanese",                    // preferred response language
  "plansDirectory": "~/.claude/plans"        // where plan files go
}
```

## Hooks

### Events

| Event | Matcher | Blocks? | Use Case |
|:--|:--|:--|:--|
| `PreToolUse` | Tool name | Yes | Gate tool calls, modify inputs |
| `PostToolUse` | Tool name | No | Feedback after tool success |
| `PostToolUseFailure` | Tool name | No | Feedback after tool failure |
| `PermissionRequest` | Tool name | Yes | Custom permission decisions |
| `UserPromptSubmit` | — | Yes | Validate/filter user input |
| `Stop` | — | Yes | Prevent premature stops |
| `SubagentStart` | Agent type | No | Monitor subagent spawns |
| `SubagentStop` | Agent type | Yes | Gate subagent completion |
| `SessionStart` | `startup`/`resume`/`clear`/`compact` | No | Session initialization |
| `SessionEnd` | `clear`/`logout`/etc. | No | Cleanup |
| `Notification` | `permission_prompt`/`idle_prompt`/etc. | No | Notification handling |
| `PreCompact` | `manual`/`auto` | No | Pre-compaction hook |
| `TaskCompleted` | — | Yes (exit 2) | Task validation |
| `TeammateIdle` | — | Yes (exit 2) | Keep agents alive |

### Handler Types

**Command:**
```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "/path/to/validator.sh",
          "timeout": 10
        }]
      }
    ]
  }
}
```

**Prompt** (sends to LLM):
```jsonc
{
  "type": "prompt",
  "prompt": "Check if this tool call is safe: $ARGUMENTS",
  "model": "haiku",
  "timeout": 30
}
```

**Agent** (launches a subagent):
```jsonc
{
  "type": "agent",
  "prompt": "Verify this tool call follows security policy: $ARGUMENTS",
  "timeout": 60
}
```

### Exit Codes

| Code | Effect |
|:--|:--|
| 0 | Success — stdout parsed as JSON |
| 2 | Blocking error — tool call blocked, stderr fed back |
| Other | Non-blocking error — stderr shown in verbose mode |

### Hook Output (JSON on stdout)

```jsonc
{
  "continue": true,              // false = stop processing entirely
  "stopReason": "...",           // shown when continue=false
  "suppressOutput": false,       // hide from verbose mode
  "systemMessage": "Warning..."  // shown to user
}
```

**PreToolUse** adds `hookSpecificOutput`:

```jsonc
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",    // "allow", "deny", or "ask"
    "permissionDecisionReason": "...",
    "updatedInput": { },              // modify tool input
    "additionalContext": "..."        // added to Claude's context
  }
}
```

### Hook Environment Variables

- `$CLAUDE_PROJECT_DIR` — project root
- `${CLAUDE_PLUGIN_ROOT}` — plugin root directory
- `$CLAUDE_ENV_FILE` — (SessionStart only) path for persisting env vars

## MCP (Model Context Protocol)

### Adding Servers

```bash
# HTTP (recommended)
claude mcp add --transport http my-server https://api.example.com/mcp
claude mcp add --transport http my-server https://api.example.com/mcp \
  --header "Authorization: Bearer $TOKEN"

# stdio (local process)
claude mcp add --transport stdio my-server -- npx -y @some/mcp-server
claude mcp add --transport stdio --env API_KEY=val my-server -- /path/to/binary

# From JSON
claude mcp add-json my-server '{"type":"http","url":"https://example.com/mcp"}'

# Import from Claude Desktop
claude mcp add-from-claude-desktop

# Management
claude mcp list
claude mcp get <name>
claude mcp remove <name>
```

### Scopes

| Scope | Flag | Storage | Shared |
|:--|:--|:--|:--|
| local (default) | `-s local` | `~/.claude.json` (per project) | No |
| project | `-s project` | `.mcp.json` (project root) | Yes (git) |
| user | `-s user` | `~/.claude.json` | No |

### `.mcp.json` Format

```json
{
  "mcpServers": {
    "my-server": {
      "command": "/path/to/server",
      "args": ["--config", "config.json"],
      "env": { "API_KEY": "${API_KEY:-default_value}" }
    }
  }
}
```

Env var expansion: `${VAR}` and `${VAR:-default}`. Works in `command`, `args`, `env`, `url`, `headers`.

### OAuth

```bash
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

### Tool Search (`ENABLE_TOOL_SEARCH`)

| Value | Behavior |
|:--|:--|
| `auto` (default) | Activates when MCP tools exceed 10% of context |
| `auto:N` | Custom threshold (e.g., `auto:5` for 5%) |
| `true` | Always enabled |
| `false` | Disabled, all tools loaded upfront |

Requires Sonnet 4+ or Opus 4+.

## Key Environment Variables

### Authentication

| Variable | Description |
|:--|:--|
| `ANTHROPIC_API_KEY` | API key for direct API access |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header value |
| `ANTHROPIC_MODEL` | Override default model |

### Cloud Providers

```bash
# AWS Bedrock
CLAUDE_CODE_USE_BEDROCK=1

# Google Vertex AI
CLAUDE_CODE_USE_VERTEX=1

# Microsoft Foundry
CLAUDE_CODE_USE_FOUNDRY=1
```

### Performance & Limits

| Variable | Default | Description |
|:--|:--|:--|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 32000 | Max output tokens (max 64000) |
| `MAX_THINKING_TOKENS` | 31999 | Extended thinking budget (0 disables) |
| `CLAUDE_CODE_EFFORT_LEVEL` | `high` | `low`, `medium`, `high` |
| `BASH_DEFAULT_TIMEOUT_MS` | — | Default bash timeout |
| `BASH_MAX_TIMEOUT_MS` | — | Max bash timeout |
| `BASH_MAX_OUTPUT_LENGTH` | — | Max bash output chars |

### Context & Caching

| Variable | Description |
|:--|:--|
| `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` | Context % for auto-compaction (1-100, default ~95) |
| `DISABLE_PROMPT_CACHING` | Disable prompt caching globally (`1`) |

### Shell & Sandbox

| Variable | Description |
|:--|:--|
| `CLAUDE_CODE_SHELL` | Override shell detection |
| `CLAUDE_CODE_SHELL_PREFIX` | Command wrapper prefix |
| `HTTP_PROXY` / `HTTPS_PROXY` | Proxy servers |
| `NO_PROXY` | Domains to bypass proxy |

### MCP

| Variable | Default | Description |
|:--|:--|:--|
| `MAX_MCP_OUTPUT_TOKENS` | 25000 | Max tokens in MCP responses |
| `MCP_TIMEOUT` | — | Server startup timeout (ms) |
| `MCP_TOOL_TIMEOUT` | — | Tool execution timeout (ms) |

### UI & Telemetry

| Variable | Description |
|:--|:--|
| `DISABLE_AUTOUPDATER` | Disable auto-updates (`1`) |
| `DISABLE_TELEMETRY` | Opt out of telemetry (`1`) |
| `DISABLE_ERROR_REPORTING` | Opt out of error reporting (`1`) |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable all non-essential network traffic |

Source: [Claude Code Settings](https://code.claude.com/docs/en/settings), [Permissions](https://code.claude.com/docs/en/permissions), [Hooks](https://code.claude.com/docs/en/hooks), [MCP](https://code.claude.com/docs/en/mcp), [Memory](https://code.claude.com/docs/en/memory)
