# Hooks Reference

Complete reference for Claude Code hooks. Source: [Hooks Reference](https://code.claude.com/docs/en/hooks-reference).

## Configuration

Three levels of nesting: event > matcher group > hook handler.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "./script.sh", "timeout": 600 }
        ]
      }
    ]
  }
}
```

### Hook locations

| Location | Scope |
|:---------|:------|
| `~/.claude/settings.json` | All projects |
| `.claude/settings.json` | Single project (committable) |
| `.claude/settings.local.json` | Single project (gitignored) |
| Managed policy | Organization-wide |
| Plugin `hooks/hooks.json` | When plugin enabled |
| Skill/agent frontmatter | While component active |

### Handler types

**Command** (`type: "command"`): shell command, JSON on stdin, exit code + stdout output.

**HTTP** (`type: "http"`): POST request with JSON body. Non-2xx = non-blocking error. To block, return 2xx with decision JSON.

**Prompt** (`type: "prompt"`): single-turn Claude evaluation, yes/no decision.

**Agent** (`type: "agent"`): subagent with Read/Grep/Glob tools, returns decision.

### Common handler fields

| Field | Required | Description |
|:------|:---------|:------------|
| `type` | yes | `"command"`, `"http"`, `"prompt"`, `"agent"` |
| `timeout` | no | Seconds. Defaults: 600 (command), 30 (prompt), 60 (agent) |
| `statusMessage` | no | Custom spinner message |
| `once` | no | Run only once per session (skills only) |

### Command-specific fields

| Field | Description |
|:------|:------------|
| `command` | Shell command to execute |
| `async` | If `true`, runs in background without blocking |

### HTTP-specific fields

| Field | Description |
|:------|:------------|
| `url` | POST endpoint URL |
| `headers` | Key-value pairs. Values support `$VAR_NAME` / `${VAR_NAME}` interpolation |
| `allowedEnvVars` | Env vars allowed for header interpolation |

### Prompt/agent-specific fields

| Field | Description |
|:------|:------------|
| `prompt` | Prompt text. `$ARGUMENTS` = hook input JSON |
| `model` | Override model |

## Matcher Patterns

Matcher is a regex filtering when hooks fire.

| Event | Matches on | Example |
|:------|:-----------|:--------|
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` | tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | session start type | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | end reason | `clear`, `logout`, `prompt_input_exit` |
| `Notification` | notification type | `permission_prompt`, `idle_prompt` |
| `SubagentStart`, `SubagentStop` | agent type | `Bash`, `Explore`, `Plan` |
| `PreCompact` | trigger | `manual`, `auto` |
| `ConfigChange` | config source | `user_settings`, `project_settings`, `skills` |
| `UserPromptSubmit`, `Stop`, `TeammateIdle`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove` | (no matcher) | Always fires |

MCP tools: `mcp__<server>__<tool>` (e.g., `mcp__memory__.*` matches all memory server tools).

## Input and Output

### Common input fields (all events)

| Field | Description |
|:------|:------------|
| `session_id` | Current session ID |
| `transcript_path` | Path to conversation JSON |
| `cwd` | Current working directory |
| `permission_mode` | `"default"`, `"plan"`, `"acceptEdits"`, `"dontAsk"`, `"bypassPermissions"` |
| `hook_event_name` | Event name |

### Exit codes (command hooks)

| Code | Meaning |
|:-----|:--------|
| 0 | Success. Parse stdout for JSON |
| 2 | Blocking error. stderr fed to Claude. Blocks tool call (PreToolUse), rejects prompt (UserPromptSubmit), etc. |
| Other | Non-blocking error. stderr shown in verbose mode |

### JSON output fields (exit 0)

| Field | Default | Description |
|:------|:--------|:------------|
| `continue` | `true` | `false` = stop Claude entirely |
| `stopReason` | — | Message to user when `continue: false` |
| `suppressOutput` | `false` | Hide stdout from verbose mode |
| `systemMessage` | — | Warning shown to user |

### Decision control by event

| Events | Pattern | Key fields |
|:-------|:--------|:-----------|
| UserPromptSubmit, PostToolUse, PostToolUseFailure, Stop, SubagentStop, ConfigChange | Top-level `decision` | `decision: "block"`, `reason` |
| TeammateIdle, TaskCompleted | Exit code only | Exit 2 blocks; stderr = feedback |
| PreToolUse | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask), `permissionDecisionReason`, `updatedInput`, `additionalContext` |
| PermissionRequest | `hookSpecificOutput` | `decision.behavior` (allow/deny), `updatedInput`, `updatedPermissions`, `message` |
| WorktreeCreate | stdout path | Print absolute worktree path |
| WorktreeRemove, Notification, SessionEnd, PreCompact | None | Side effects only |

### Exit code 2 behavior

| Event | Can block? | Effect |
|:------|:-----------|:-------|
| PreToolUse | Yes | Blocks tool call |
| PermissionRequest | Yes | Denies permission |
| UserPromptSubmit | Yes | Blocks and erases prompt |
| Stop | Yes | Prevents stopping, continues conversation |
| SubagentStop | Yes | Prevents subagent from stopping |
| TeammateIdle | Yes | Prevents idle (teammate continues) |
| TaskCompleted | Yes | Prevents task completion |
| ConfigChange | Yes | Blocks config change (except policy) |
| PostToolUse, PostToolUseFailure | No | Shows stderr to Claude |
| Notification, SubagentStart, SessionStart, SessionEnd, PreCompact | No | Shows stderr to user only |
| WorktreeCreate | Yes | Non-zero = creation fails |
| WorktreeRemove | No | Logged in debug mode |

## Hook Events

### SessionStart

Fires when session begins/resumes. Matcher: `startup`, `resume`, `clear`, `compact`.

Extra input: `source`, `model`, `agent_type` (optional).

Output: `additionalContext` in `hookSpecificOutput`. Plain stdout also added as context.

**Environment persistence**: write `export VAR=value` to `$CLAUDE_ENV_FILE` (only available in SessionStart hooks).

### UserPromptSubmit

Fires before Claude processes user prompt.

Extra input: `prompt` (user's text).

Output: `decision: "block"` + `reason` to reject. `additionalContext` to add context. Plain stdout also works.

### PreToolUse

Fires before tool execution. Matcher: tool name.

Extra input: `tool_name`, `tool_input`, `tool_use_id`.

Output via `hookSpecificOutput`:
- `permissionDecision`: `"allow"` (bypass permissions), `"deny"` (block), `"ask"` (prompt user)
- `permissionDecisionReason`: shown to user (allow/ask) or Claude (deny)
- `updatedInput`: modify tool parameters before execution
- `additionalContext`: add context for Claude

### PermissionRequest

Fires when permission dialog shown. Matcher: tool name.

Extra input: `tool_name`, `tool_input`, `permission_suggestions`.

Output via `hookSpecificOutput.decision`:
- `behavior`: `"allow"` or `"deny"`
- `updatedInput`: modify parameters (allow only)
- `updatedPermissions`: apply "always allow" rules (allow only)
- `message`: tell Claude why denied (deny only)
- `interrupt`: stop Claude (deny only)

### PostToolUse

Fires after successful tool execution. Matcher: tool name.

Extra input: `tool_name`, `tool_input`, `tool_response`, `tool_use_id`.

Output: `decision: "block"` + `reason`. `additionalContext`. `updatedMCPToolOutput` (MCP tools only).

### Stop

Fires when Claude finishes responding.

Output: `decision: "block"` + `reason` to continue conversation. Exit 2 also prevents stopping.

### Path variables

- `$CLAUDE_PROJECT_DIR`: project root
- `${CLAUDE_PLUGIN_ROOT}`: plugin root directory
- `$CLAUDE_CODE_REMOTE`: `"true"` in remote web environments

## Skill/Agent Frontmatter Hooks

```yaml
---
name: my-skill
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
---
```

For agents, `Stop` hooks auto-convert to `SubagentStop`.
