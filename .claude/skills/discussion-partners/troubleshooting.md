# discussion-partners — troubleshooting

Reference for when one of the three paths errors. Read this after checking `setup.md`.

## Codex CLI

### `codex: command not found`

Codex CLI isn't installed. See `setup.md`.

### `codex login` rejected

Run `codex login` again. The CLI uses ChatGPT account auth (Plus / Pro / Business / Enterprise / Edu tiers). If login succeeds but calls still fail, your tier may not include Codex usage.

### Reasoning effort silently lowered after upgrade

When Codex accepts a model upgrade mid-session, it resets reasoning to the new model's default. Re-apply `-c model_reasoning_effort="xhigh"`, or rely on `~/.codex/config.toml` which persists.

## ask_model.py

### `model_not_found` / `does not exist` / 404

The model string is valid in pydantic-ai but the OpenAI API doesn't serve it. As of 2026-04-24, this affects:

- `openai:gpt-5.5` — not in the API yet. Use Codex CLI instead.
- `openai-responses:gpt-5.5-pro` — not in the API yet. Fall back to `openai-responses:gpt-5.4-pro`.

### `insufficient_quota (429)`

Billing issue. Add credits at the provider's dashboard:

- OpenAI: https://platform.openai.com/account/billing
- Google: https://console.cloud.google.com/billing
- Anthropic: https://console.anthropic.com/settings/billing

### `invalid_api_key (401)` / `Incorrect API key`

Wrong or stale key. Check `~/.zshrc` has the right export, then `source ~/.zshrc` in the current shell. Re-run `api-key-checker` skill to verify.

### `rate_limit (429)`

Too many requests in a short window. Wait and retry. For long-running pro-tier calls, consider running them serially rather than in parallel.

### `GOOGLE_API_KEY not set` (or OPENAI/ANTHROPIC)

The script checks for the key before calling the API. Export it in `~/.zshrc` and re-source.

### Foreground call died at 10 minutes

Bash tool timeout is 10 min max. Pro-tier models (`gpt-5.4-pro`, `gpt-5.5-pro`) take 10–15+ min at max thinking. Always invoke with `run_in_background: true`. SKILL.md specifies this for the default flow.

## Task sub-agent

### Sub-agent returns immediately with no work done

The `prompt=` arg is too thin. Sub-agents get zero conversation context — they only see what you put in `prompt=`. Include: the question, relevant file paths, what you've tried, what kind of answer you need. They have tool access so pointers to files beat inlined code.

### Sub-agent doesn't seem to be running on Opus

The parent session's default (per `~/CLAUDE.md`) is Opus for sub-agents. If a specific invocation should force Opus, pass `model: "opus"` in the Task call. Verify by asking the sub-agent to identify itself.

## All three paths

### Three-way parallel default returns partial results

Fast paths (Gemini, Opus sub-agent) return in ~30–60 s. Codex at xhigh takes 5–30 min. The default flow is:

1. Fire all three in background.
2. Synthesize fast-returning results immediately.
3. Tell the user Codex is still in flight; surface its output when it lands.

Don't block the turn waiting for Codex.

### Need to skip one path (e.g. no `GOOGLE_API_KEY` set)

Graceful degradation: run the two paths whose prereqs are met; note which one was skipped and why. Don't fail the whole invocation because one provider is unconfigured.
