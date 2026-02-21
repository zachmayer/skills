---
name: discussion_partners
description: >
  Ask a question to another AI model (OpenAI, Anthropic, or Google) with
  extended thinking enabled. Use when you are stuck on a difficult problem,
  suspect you are spinning your wheels, or sense there is an angle you have
  not considered. Do NOT use for routine tasks you can handle directly.
allowed-tools: Bash(uv run *)
---

Query another AI model for an outside perspective on a difficult problem. One message out, one message back — make it count.

## Recommended Models

**Always use the script default** (`openai:gpt-5.2`) unless you have a specific reason to change. Do NOT override with older models like o3 — they are expensive and superseded.

| Model | When to use | API key needed |
|-------|-------------|----------------|
| `openai:gpt-5.2` **(default)** | Primary partner. xhigh thinking, exceptional detail | `OPENAI_API_KEY` |
| `google-gla:gemini-3.1-pro-preview` | Second opinion, brilliantly intelligent reasoning | `GOOGLE_API_KEY` |
| `anthropic:claude-opus-4-6` | Third perspective, different reasoning style | `ANTHROPIC_API_KEY` |

Before calling, verify the required API key is set: `echo $OPENAI_API_KEY | head -c 8` (should show `sk-...`).

## Framing Your Question

You get **one message out and one message back**. There is no follow-up. Your partner has ZERO context about what you're working on — they see only what you send. The context window is finite and expensive, so treat it like a skill prompt: include everything needed, nothing that isn't.

**Your partner needs all context to answer your question.** They cannot read your files, see your conversation, or infer your situation. If you don't include it, they don't know it. But context is limited, so be surgical:

1. **Include all relevant context**: code, errors, constraints, what you tried. Use `mental_models` to structure your thinking before asking.
2. **State what you're stuck on**: "I tried A, B, C and none work because D" — not just "help me with X"
3. **Ask a specific question and set the frame**: what kind of answer you need (diagnosis, alternative approach, code review).
4. **Never include secrets**: API keys, credentials, tokens, or private repo URLs. Your question goes to an external API.

Bad: "How do I fix this auth bug?"
Good: "Here is my auth middleware [code]. Users with expired tokens get a 500 instead of 401. I have verified the token validation logic is correct and the error handler is registered. The 500 comes from [stack trace]. What could cause the error handler to be bypassed?"

## Usage

```bash
uv run --directory SKILL_DIR python scripts/ask_model.py -m <model> "Your detailed question with full context"
```

Where `SKILL_DIR` is the directory containing this skill. The `-m` flag takes a full [pydantic-ai model string](https://ai.pydantic.dev/api/models/) — the provider prefix determines which API key and thinking settings to use.

## Models

The default is `openai:gpt-5.2`. Thinking effort is automatically set to maximum for each provider.

```bash
# GPT-5.2 with xhigh reasoning (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py "question"

# Claude Opus 4.6 with adaptive thinking at max effort
uv run --directory SKILL_DIR python scripts/ask_model.py -m anthropic:claude-opus-4-6 "question"

# Gemini 3.1 Pro with thinking enabled
uv run --directory SKILL_DIR python scripts/ask_model.py -m google-gla:gemini-3.1-pro-preview "question"

# Codex models (via OpenAI Responses API)
uv run --directory SKILL_DIR python scripts/ask_model.py -m openai-responses:gpt-5-codex "question"
uv run --directory SKILL_DIR python scripts/ask_model.py -m openai-responses:codex-mini-latest "question"
```

## API Key Setup

Add keys to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export OPENAI_API_KEY="your-key"      # Required for openai: and openai-responses: models
export ANTHROPIC_API_KEY="your-key"   # Required for anthropic: models
export GOOGLE_API_KEY="your-key"      # Required for google-gla: models
```

The script checks for the key before calling the API. If missing, it tells you which
variable to set. If the key exists but the call fails, common errors:
- **insufficient_quota (429)**: Billing issue — add credits at the provider's dashboard.
- **invalid_api_key (401)**: Wrong key — check you exported the correct one and ran `source ~/.zshrc`.
- **rate_limit (429)**: Too many requests — wait and retry.

## Options

- `--model` / `-m`: Full pydantic-ai model string (default: `openai:gpt-5.2`)
- `--system` / `-s`: Optional system prompt override
- `--stream` / `--no-stream`: Stream tokens as they arrive (default: `--stream`). Use `--no-stream` to wait for the full response before printing.
- `--list-models` / `-l`: List known model names, optionally filtered by prefix (e.g. `-l openai`, `-l anthropic`). Codex models appear under `openai:` but must be called with `openai-responses:` prefix.

## Multiple Calls

Each call gets zero context from previous calls. For follow-ups, include the prior exchange: "I asked X, you answered Y, help me understand Z."
