---
name: api-key-checker
description: >
  Checks which AI provider API keys (OpenAI, Anthropic, Google/Gemini) are
  configured and working. Tests env vars against live endpoints, reports
  configured/valid/missing status. Use when user says "check my API keys",
  "which keys are set up", "why is the API failing", "test my credentials",
  or when setting up a new machine. Also use before running any skill that
  calls external AI APIs. Do NOT use during normal operation — only for
  setup and diagnostics.
allowed-tools: Bash(uv run *)
---

# Check API Keys

Run the checker:

```bash
uv run --directory SKILL_DIR python scripts/check_keys.py
```

Reports per-provider status: configured (env var set), valid (endpoint responds), or missing. Providers: OpenAI, Anthropic, Google (Gemini).
