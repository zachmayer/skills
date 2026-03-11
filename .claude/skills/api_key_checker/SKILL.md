---
name: api_key_checker
description: >
  Verify which API keys are configured and valid. Check env vars, test
  endpoints, report status. Use when setting up a new machine, debugging
  API failures, or before running skills that need external APIs.
  Do NOT use during normal operation — only for diagnostics.
allowed-tools: Bash(uv run *)
---

Check which AI provider API keys are configured and working.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/check_keys.py
```

Reports status for each provider: configured (env var set), valid (endpoint responds), or missing.

Providers checked: OpenAI, Anthropic, Google (Gemini).
