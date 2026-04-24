# discussion-partners — setup

One-time setup for the three invocation paths. Skip this if everything is already installed and configured; SKILL.md assumes you're past this step.

## Codex CLI (OpenAI path — GPT-5.5)

Install:

```bash
npm install -g @openai/codex   # requires Node.js
```

Authenticate (no env var — Codex uses ChatGPT account auth, not `OPENAI_API_KEY`):

```bash
codex login
```

Configure `~/.codex/config.toml`:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"   # low | medium | high | xhigh
service_tier = "fast"

[features]
fast_mode = true
```

Both `service_tier = "fast"` and `[features].fast_mode = true` are required for persistent fast mode. Fast mode costs ~2.5× credits on GPT-5.5 in exchange for ~1.5× speed.

Verify `gpt-5.5` is available to your account by sending a trivial smoke-test:

```bash
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="low" "Say OK." -o /tmp/codex_smoketest.txt
cat /tmp/codex_smoketest.txt
```

If this errors with `model "gpt-5.5" does not exist or you do not have access`, OpenAI's staged rollout hasn't reached this account yet — fall back to `-m gpt-5.4` in all examples until it does. (`codex --version` only prints the CLI version, not the model picker, so it can't verify model availability on its own.)

## ask_model.py (Gemini + OpenAI pro via Responses API)

No install step — the script uses PEP 723 inline metadata, so `uv run` resolves deps per-call.

Add provider API keys to `~/.zshrc` (or `~/.bashrc`):

```bash
export GOOGLE_API_KEY="your-key"    # Required: Gemini (ask_model.py default)
export OPENAI_API_KEY="your-key"    # Required: openai-responses:gpt-5.4-pro
```

Then `source ~/.zshrc`.

Verify keys are live (see `api-key-checker` skill for a one-shot test).

## Task sub-agent (Claude Opus)

No setup. The Task tool is built into Claude Code and inherits the session's auth. Sub-agents default to Opus in this environment per `~/CLAUDE.md` ("Default to Opus for subagents").

## Testing the full three-way flow

Once all three paths are configured, the skill's default behavior is to fire all three in parallel. A smoke test is a short prompt run through the skill; if any path errors, see `troubleshooting.md`.
