# Environment Variables Reference

Complete reference for Claude Code environment variables. Set via shell profile, `env` in settings.json, or `SessionStart` hooks.

## Authentication

| Variable | Description |
|:---------|:------------|
| `ANTHROPIC_API_KEY` | API key (X-Api-Key header) |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header value |
| `ANTHROPIC_CUSTOM_HEADERS` | Custom headers (Name: Value, newline-separated) |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | Credential refresh interval for `apiKeyHelper` (ms) |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key |

## Model Configuration

| Variable | Description |
|:---------|:------------|
| `ANTHROPIC_MODEL` | Model to use |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Default Haiku model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Default Sonnet model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Default Opus model |
| `ANTHROPIC_SMALL_FAST_MODEL` | **Deprecated.** Haiku-class background model |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | AWS region for Haiku on Bedrock |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |
| `CLAUDE_CODE_EFFORT_LEVEL` | `low`, `medium`, `high` (default). Opus 4.6 only |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | `1` = disable adaptive reasoning |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | `1` = disable `anthropic-beta` headers |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | `1` = disable 1M context window |

## Cloud Providers

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_USE_BEDROCK` | Use Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY` | Use Microsoft Foundry |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | Skip AWS auth (for LLM gateways) |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | Skip Google auth |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | Skip Azure auth |
| `ANTHROPIC_FOUNDRY_API_KEY` | Foundry API key |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Foundry base URL |
| `ANTHROPIC_FOUNDRY_RESOURCE` | Foundry resource name |

## Bash Execution

| Variable | Description |
|:---------|:------------|
| `BASH_DEFAULT_TIMEOUT_MS` | Default timeout for bash commands |
| `BASH_MAX_TIMEOUT_MS` | Maximum timeout model can set |
| `BASH_MAX_OUTPUT_LENGTH` | Max chars before truncation |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Return to original dir after each command |
| `CLAUDE_CODE_SHELL` | Override auto shell detection |
| `CLAUDE_CODE_SHELL_PREFIX` | Prefix wrapping all bash commands |

## Context and Memory

| Variable | Description |
|:---------|:------------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | % of context (1-100) for auto-compaction trigger |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens (default: 32000, max: 64000) |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Override file read token limit |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | `1` = disable, `0` = force on |

## Telemetry and Updates

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1` = enable OpenTelemetry |
| `DISABLE_TELEMETRY` | `1` = opt out of Statsig |
| `DISABLE_ERROR_REPORTING` | `1` = opt out of Sentry |
| `DISABLE_AUTOUPDATER` | `1` = disable auto-updates |
| `DISABLE_BUG_COMMAND` | `1` = disable `/bug` command |
| `DISABLE_COST_WARNINGS` | `1` = disable cost warnings |
| `DISABLE_INSTALLATION_CHECKS` | `1` = disable installation warnings |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | `1` = disable flavor text calls |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Equivalent to all four DISABLE_ vars above |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` | `1` = disable session quality surveys |

## Prompt Caching

| Variable | Description |
|:---------|:------------|
| `DISABLE_PROMPT_CACHING` | `1` = disable for all models |
| `DISABLE_PROMPT_CACHING_HAIKU` | `1` = disable for Haiku |
| `DISABLE_PROMPT_CACHING_SONNET` | `1` = disable for Sonnet |
| `DISABLE_PROMPT_CACHING_OPUS` | `1` = disable for Opus |

## MCP

| Variable | Description |
|:---------|:------------|
| `ENABLE_TOOL_SEARCH` | `auto` (default), `auto:N`, `true`, `false` |
| `ENABLE_CLAUDEAI_MCP_SERVERS` | `false` = disable claude.ai MCP servers |

## UI and Display

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | `1` = disable terminal title updates |
| `CLAUDE_CODE_HIDE_ACCOUNT_INFO` | `1` = hide email/org |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | `false` = disable prompt suggestions |
| `CLAUDE_CODE_ENABLE_TASKS` | `false` = revert to old TODO list |

## Session and Workflow

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | Ms before auto-exit after idle |
| `CLAUDE_CODE_TASK_LIST_ID` | Shared task list ID across sessions |
| `CLAUDE_CODE_SIMPLE` | `1` = minimal system prompt, basic tools |
| `CLAUDE_CODE_DISABLE_FAST_MODE` | `1` = disable fast mode |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | `1` = disable background tasks |

## Directories and Paths

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CONFIG_DIR` | Custom config/data storage location |
| `CLAUDE_CODE_TMPDIR` | Override temp directory (appends `/claude/`) |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | `1` = load CLAUDE.md from `--add-dir` directories |

## Agent Teams

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` = enable agent teams |
| `CLAUDE_CODE_TEAM_NAME` | Agent team name (auto-set) |
| `CLAUDE_CODE_PLAN_MODE_REQUIRED` | Auto-set on teammates requiring plan approval |

## Security / mTLS

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_CLIENT_CERT` | Path to client certificate |
| `CLAUDE_CODE_CLIENT_KEY` | Path to client private key |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | Passphrase for encrypted key |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | `true` = proxy does DNS |

## SDK / Account

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_ACCOUNT_UUID` | Account UUID |
| `CLAUDE_CODE_USER_EMAIL` | User email |
| `CLAUDE_CODE_ORGANIZATION_UUID` | Org UUID |

## Plugins

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | Git timeout for plugin ops (default: 120000ms) |
| `FORCE_AUTOUPDATE_PLUGINS` | `true` = force plugin auto-updates |

## OpenTelemetry

| Variable | Description |
|:---------|:------------|
| `OTEL_METRICS_EXPORTER` | OTel metrics exporter type (e.g., `otlp`) |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` | OTel headers refresh interval (default: 1740000ms) |

## IDE

| Variable | Description |
|:---------|:------------|
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | Skip auto-installation of IDE extensions |
