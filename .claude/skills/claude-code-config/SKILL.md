---
name: claude-code-config
description: >
  Reference for Claude Code configuration: settings.json, permissions,
  hooks, environment variables, MCP servers, CLAUDE.md, sandbox, and
  plugins. Use when the user says "configure Claude Code", "add a
  permission", "set up hooks", "MCP server config", "settings.json",
  "allow this tool", "deny this command", "env vars", "sandbox", or asks
  how Claude Code settings work. Covers managed policies, permission
  precedence, hook lifecycle events, and all top-level settings keys.
  Do NOT use for writing SKILL.md files (use skillcraft instead).
---

# Claude Code Configuration Reference

Complete reference for configuring Claude Code. Source: [Claude Code Settings](https://code.claude.com/docs/en/settings).

## Settings Files

### Locations (highest to lowest priority)

| Priority | Location | Scope | Shared |
|:---------|:---------|:------|:-------|
| 1 | Managed policy | All org users | Admin-controlled |
| 2 | CLI arguments | Session | No |
| 3 | `.claude/settings.local.json` | Project | No (gitignored) |
| 4 | `.claude/settings.json` | Project | Yes (committed) |
| 5 | `~/.claude/settings.json` | User | No |

**Managed policy paths:**
- macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
- Linux/WSL: `/etc/claude-code/managed-settings.json`
- macOS MDM: `com.anthropic.claudecode` plist

**Array settings MERGE across scopes** (concatenated + deduplicated), not replaced.

### Other config files

| File | Purpose |
|:-----|:--------|
| `~/.claude.json` | OAuth, MCP (user scope), per-project state |
| `.mcp.json` | Project-scoped MCP servers |
| `~/.claude/agents/` | User subagents |
| `.claude/agents/` | Project subagents |
| `~/.claude/CLAUDE.md` | Global instructions |
| `CLAUDE.md` / `.claude/CLAUDE.md` | Project instructions |
| `CLAUDE.local.md` | Local project instructions (unshared) |

## Permissions

### Rule syntax

Format: `Tool` or `Tool(specifier)` with glob wildcards.

```json
{
  "permissions": {
    "allow": ["Bash(npm run lint)", "Read(~/.zshrc)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Bash(curl *)", "Read(./.env)", "Read(./secrets/**)"]
  }
}
```

**Evaluation order**: deny > ask > allow (first match wins).

### Rule examples

| Rule | Matches |
|:-----|:--------|
| `Bash` | All bash commands |
| `Bash(npm run *)` | Commands starting with `npm run` |
| `Read(./.env)` | Reading `.env` file |
| `Read(./secrets/**)` | Anything under `secrets/` |
| `Edit(./src/**)` | Editing files under `src/` |
| `WebFetch(domain:example.com)` | Fetch requests to example.com |
| `MCP(server-name)` | MCP server tool use |
| `Agent` | Subagent tool use |

### Bash wildcard bypass warning

Permission rules like `Bash(safe-cmd *)` use simple prefix matching on the command string — they do NOT parse shell operators. `Bash(safe-cmd *)` WILL match `safe-cmd ; evil-cmd` or `safe-cmd && evil-cmd` because the pattern matches the prefix.

**Primary defense: auto mode's server-side classifier.** With `"permissions.defaultMode": "auto"` set, Claude Code evaluates the real-world impact of each command rather than the surface text, explicitly handling `&&` chains, write-then-execute patterns, and shell wrappers as a single action. See [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode). The deny list is the second layer for specific operations you never want to allow regardless of classifier judgment (e.g. `git push --force`, `gh repo delete`).

### Additional permission keys

| Key | Type | Description |
|:----|:-----|:------------|
| `additionalDirectories` | string[] | Extra working directories |
| `defaultMode` | string | `"acceptEdits"` etc. |
| `disableBypassPermissionsMode` | string | `"disable"` to block `--dangerously-skip-permissions` |

## CLAUDE.md

### Locations (loaded in order)

| Scope | Path |
|:------|:-----|
| User global | `~/.claude/CLAUDE.md` |
| Project root | `CLAUDE.md` or `.claude/CLAUDE.md` |
| Local (unshared) | `CLAUDE.local.md` |
| Additional dirs | Loaded if `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` |

Instructions and context loaded at startup. Supports project-specific conventions, coding standards, workflow instructions. Use `--append-system-prompt` for additional system prompt content.

## Top-Level Settings

| Key | Type | Description |
|:----|:-----|:------------|
| `model` | string | Override default model |
| `availableModels` | string[] | Restrict selectable models |
| `env` | object | Environment variables per session |
| `language` | string | Preferred response language |
| `cleanupPeriodDays` | number | Days before inactive sessions deleted |
| `companyAnnouncements` | string[] | Messages shown at startup |
| `autoUpdatesChannel` | string | `"stable"` or `"latest"` |
| `alwaysThinkingEnabled` | boolean | Enable extended thinking |
| `showTurnDuration` | boolean | Show turn duration after responses |
| `plansDirectory` | string | Where plan files are stored |
| `outputStyle` | string | Adjust system prompt style |
| `apiKeyHelper` | string | Script to generate auth value |
| `statusLine` | object | Custom status line config |
| `fileSuggestion` | object | Custom `@` file autocomplete |
| `respectGitignore` | boolean | `@` picker respects `.gitignore` (default: true) |
| `forceLoginMethod` | string | `"claudeai"` or `"console"` |
| `forceLoginOrgUUID` | string | Auto-select org UUID on login |
| `spinnerVerbs` | object | Custom action verbs in spinner |
| `spinnerTipsEnabled` | boolean | Show tips while Claude works (default: true) |
| `spinnerTipsOverride` | object | Custom spinner tips (`excludeDefault`, `tips[]`) |
| `terminalProgressBarEnabled` | boolean | Terminal progress bar (default: true) |
| `prefersReducedMotion` | boolean | Reduce/disable UI animations |
| `fastModePerSessionOptIn` | boolean | Fast mode requires per-session opt-in |
| `teammateMode` | string | `"auto"`, `"in-process"`, or `"tmux"` |
| `otelHeadersHelper` | string | Script for dynamic OpenTelemetry headers |
| `awsAuthRefresh` | string | Script that modifies `.aws` directory |
| `awsCredentialExport` | string | Script outputting JSON with AWS credentials |

### Attribution

```json
{
  "attribution": {
    "commit": "Co-Authored-By: Claude <noreply@anthropic.com>",
    "pr": "Generated with Claude Code"
  }
}
```

Empty string `""` hides attribution entirely.

### Managed-only settings

| Key | Description |
|:----|:------------|
| `allowManagedHooksOnly` | Block user/project/plugin hooks |
| `allowManagedPermissionRulesOnly` | Only managed permission rules apply |
| `allowManagedMcpServersOnly` | Only managed MCP allowlist applies |
| `disableAllHooks` | Disable all hooks and custom status line |
| `allowedHttpHookUrls` | URL pattern allowlist for HTTP hooks (`*` wildcards) |
| `httpHookAllowedEnvVars` | Env vars HTTP hooks can interpolate into headers |

## Hooks

Hooks run commands at lifecycle events. See [hooks.md](hooks.md) for complete reference.

### Quick reference

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": "./check.sh" }]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "./format.sh" }]
    }]
  }
}
```

**Events**: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `Notification`, `SubagentStart`, `SubagentStop`, `Stop`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `SessionEnd`

**Handler types**: `command`, `http`, `prompt`, `agent`

**Exit codes**: 0 = success (parse stdout JSON), 2 = blocking error (stderr fed to Claude), other = non-blocking error

## Environment Variables

See [env-vars.md](env-vars.md) for complete reference.

### Key variables

| Variable | Description |
|:---------|:------------|
| `ANTHROPIC_API_KEY` | API key |
| `ANTHROPIC_MODEL` | Model to use |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Override default Haiku model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Override default Sonnet model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Override default Opus model |
| `CLAUDE_CODE_USE_BEDROCK` | Use Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI |
| `CLAUDE_CODE_EFFORT_LEVEL` | `low`, `medium`, `high` (Opus 4.6 only) |
| `BASH_DEFAULT_TIMEOUT_MS` | Default bash timeout |

## MCP Server Configuration

See [advanced.md](advanced.md) for MCP, sandbox, and plugin details.

### Quick reference

Project scope (`.mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

User scope: same format in `~/.claude.json`.

## Sandbox

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["//tmp/build"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}
```

**Path prefixes**: `//` = absolute from root, `~/` = home, `/` = relative to settings file, `./` = relative.

See [advanced.md](advanced.md) for full sandbox reference.
