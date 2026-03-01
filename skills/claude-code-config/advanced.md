# Advanced Configuration Reference

MCP servers, sandbox, plugins, and other advanced settings.

## MCP Server Configuration

### Project scope (`.mcp.json`)

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

### User scope

Same format in `~/.claude.json`. Applies to all projects.

### Managed MCP

Allowlist/denylist in managed settings. Deny takes precedence.

| Setting | Description |
|:--------|:------------|
| `allowedMcpServers` | `[{"serverName": "github"}]` — allowed servers |
| `deniedMcpServers` | `[{"serverName": "filesystem"}]` — blocked servers |

### MCP approval settings

| Setting | Type | Description |
|:--------|:-----|:------------|
| `enableAllProjectMcpServers` | boolean | Auto-approve all `.mcp.json` servers |
| `enabledMcpjsonServers` | string[] | Approve specific servers by name |
| `disabledMcpjsonServers` | string[] | Reject specific servers by name |

### Tool search

```
ENABLE_TOOL_SEARCH=auto        # Enable at 10% context (default)
ENABLE_TOOL_SEARCH=auto:5      # Enable at 5% context
ENABLE_TOOL_SEARCH=true        # Always on
ENABLE_TOOL_SEARCH=false       # Disabled
```

## Sandbox Configuration

Bash sandboxing for macOS, Linux, and WSL2.

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker", "git"],
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "allowWrite": ["//tmp/build", "~/.kube"],
      "denyWrite": ["//etc", "//usr/local/bin"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowUnixSockets": ["~/.ssh/agent-socket"],
      "allowAllUnixSockets": false,
      "allowLocalBinding": true,
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "allowManagedDomainsOnly": false,
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    },
    "enableWeakerNestedSandbox": false
  }
}
```

### Sandbox keys

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `enabled` | boolean | false | Enable bash sandboxing |
| `autoAllowBashIfSandboxed` | boolean | true | Auto-approve bash when sandboxed |
| `excludedCommands` | string[] | — | Commands that run outside sandbox |
| `allowUnsandboxedCommands` | boolean | true | Allow `dangerouslyDisableSandbox` escape |
| `enableWeakerNestedSandbox` | boolean | false | For unprivileged Docker (Linux/WSL2) |

### Filesystem keys

| Key | Description |
|:----|:------------|
| `allowWrite` | Paths sandboxed commands can write |
| `denyWrite` | Paths sandboxed commands cannot write |
| `denyRead` | Paths sandboxed commands cannot read |

### Network keys

| Key | Type | Description |
|:----|:-----|:------------|
| `allowUnixSockets` | string[] | Accessible Unix socket paths |
| `allowAllUnixSockets` | boolean | Allow all Unix socket connections |
| `allowLocalBinding` | boolean | Bind to localhost (macOS only) |
| `allowedDomains` | string[] | Allowed outbound domains (`*.` wildcards) |
| `allowManagedDomainsOnly` | boolean | Managed only — restrict to managed domains |
| `httpProxyPort` | number | Bring-your-own HTTP proxy port |
| `socksProxyPort` | number | Bring-your-own SOCKS5 proxy port |

### Path prefixes

| Prefix | Meaning | Example |
|:-------|:--------|:--------|
| `//` | Absolute from filesystem root | `//tmp/build` = `/tmp/build` |
| `~/` | Relative to home | `~/.kube` = `$HOME/.kube` |
| `/` | Relative to settings file dir | `/build` = `$SETTINGS_DIR/build` |
| `./` or none | Relative (resolved at runtime) | `./output` |

## Plugin Configuration

### Enabling plugins

```json
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "analyzer@security-plugins": false
  }
}
```

### Adding marketplaces

```json
{
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    }
  }
}
```

### Marketplace source types

| Type | Required fields | Example |
|:-----|:----------------|:--------|
| `github` | `repo` | `{"source": "github", "repo": "org/plugins"}` |
| `git` | `url` | `{"source": "git", "url": "https://git.example.com/plugins.git"}` |
| `url` | `url` | `{"source": "url", "url": "https://plugins.example.com/marketplace.json"}` |
| `npm` | `package` | `{"source": "npm", "package": "@acme/claude-plugins"}` |
| `file` | `path` (absolute) | `{"source": "file", "path": "/usr/local/share/marketplace.json"}` |
| `directory` | `path` (absolute) | `{"source": "directory", "path": "/opt/plugins"}` |
| `hostPattern` | `hostPattern` (regex) | `{"source": "hostPattern", "hostPattern": "^github\\.example\\.com$"}` |

Optional fields: `ref` (git ref), `path` (subdirectory), `headers` (for URL type).

### Managed marketplace controls

| Setting | Description |
|:--------|:------------|
| `strictKnownMarketplaces` | Allowlist (undefined=no restrictions, []=lockdown, list=exact match) |
| `blockedMarketplaces` | Blocklist of marketplace sources |

## File Suggestion

Custom `@` file autocomplete:

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}
```

Script receives `{"query": "src/comp"}` on stdin, outputs newline-separated paths (max 15).

## Spinner Customization

```json
{
  "spinnerVerbs": { "mode": "append", "verbs": ["Pondering"] },
  "spinnerTipsEnabled": false,
  "spinnerTipsOverride": {
    "excludeDefault": true,
    "tips": ["Use /help for commands"]
  }
}
```

## Status Line

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```
