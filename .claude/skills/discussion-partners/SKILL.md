---
name: discussion-partners
description: >
  Queries another AI model (GPT-5.4, Gemini 3.1 Pro, Claude Opus, Codex)
  with extended thinking for an outside perspective. Use when stuck on a
  hard problem, spinning wheels, want a second opinion, need a code review
  from another model, or sense a blind spot. Trigger phrases: "ask GPT",
  "get another opinion", "second opinion", "what would GPT say", "ask
  another model", "discussion partner". Sends one message, gets one
  response — no multi-turn. Do NOT use for routine tasks, simple questions
  Claude can answer directly, or when no external API key is configured.
allowed-tools: Bash(uv run *), Bash(codex exec *)
---

Query another AI model for an outside perspective on a difficult problem. One message out, one message back — make it count.

## Recommended Models

**Default: GPT-5.4 xhigh via Codex CLI** — uses OpenAI subscription credits (no per-token billing), cheapest option. Do NOT use older models like o3 or gpt-5.2 — they are superseded.

There are two invocation methods: the **Codex CLI** (preferred, uses subscription credits) and the **pydantic-ai script** (for non-OpenAI models and gpt-5.4-pro).

### Codex CLI Models (via `codex exec`) — preferred

Uses credits from an OpenAI paid subscription (no per-token billing). Codex-only models are not accessible via the standard OpenAI API.

| Model | When to use | Notes |
|-------|-------------|-------|
| `gpt-5.4` **(default)** | Primary partner. Full GPT-5.4 with xhigh thinking | Subscription credits, cheapest option |
| `gpt-5.3-codex` | Coding specialist — code review, debugging, refactors | Default in `~/.codex/config.toml`, Codex-only |

Set reasoning effort via `-c model_reasoning_effort="xhigh"` (values: `low`, `medium`, `high`, `xhigh`). Default from config is `xhigh`.

### API Models (via `ask_model.py`)

Pay-per-token. Use for non-OpenAI models, or gpt-5.4-pro which isn't available through Codex CLI.

| Model | When to use | API key needed |
|-------|-------------|----------------|
| `openai:gpt-5.4` **(default)** | Primary partner. xhigh thinking, exceptional detail | `OPENAI_API_KEY` |
| `google-gla:gemini-3.1-pro-preview` | Brilliantly intelligent reasoning, fast | `GOOGLE_API_KEY` |
| `openai-responses:gpt-5.4-pro` | Maximum depth. Slow (~10-15 min) but extraordinary detail-oriented analysis. Use when you're willing to wait for the strongest intelligence available | `OPENAI_API_KEY` |
| `anthropic:claude-opus-4-6` | Third perspective, different reasoning style | `ANTHROPIC_API_KEY` |

**Note on gpt-5.4-pro**: Requires the `openai-responses:` prefix (Responses API). Does NOT work with `openai:` prefix (Chat Completions) or Codex CLI. Very slow but unmatched for deep, thoughtful analysis — use when correctness matters more than speed.

## Framing Your Question

You get **one message out and one message back**. There is no follow-up. Your partner has ZERO context about what you're working on — they see only what you send. The context window is finite and expensive, so treat it like a skill prompt: include everything needed, nothing that isn't.

**Your partner needs all context to answer your question.** They cannot read your files, see your conversation, or infer your situation. If you don't include it, they don't know it. But context is limited, so be surgical:

1. **Include all relevant context**: code, errors, constraints, what you tried. Use `mental-models` to structure your thinking before asking.
2. **State what you're stuck on**: "I tried A, B, C and none work because D" — not just "help me with X"
3. **Ask a specific question and set the frame**: what kind of answer you need (diagnosis, alternative approach, code review).
4. **Never include secrets**: API keys, credentials, tokens, or private repo URLs. Your question goes to an external API.

Bad: "How do I fix this auth bug?"
Good: "Here is my auth middleware [code]. Users with expired tokens get a 500 instead of 401. I have verified the token validation logic is correct and the error handler is registered. The 500 comes from [stack trace]. What could cause the error handler to be bypassed?"

## Usage: Codex CLI (preferred)

Uses OpenAI subscription credits — no per-token billing. **For short questions**, pass inline. **For long prompts, write to a file and pipe via stdin** — this avoids shell escaping issues with backticks and special characters.

```bash
# GPT-5.4 xhigh (default recommendation) — short question
codex exec --full-auto -m gpt-5.4 -c model_reasoning_effort="xhigh" "Your question" -o ~/claude/scratch/codex_output.txt

# GPT-5.4 xhigh — long prompt from file
codex exec --full-auto -m gpt-5.4 -c model_reasoning_effort="xhigh" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# gpt-5.3-codex — coding specialist (default model in ~/.codex/config.toml)
codex exec --full-auto -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# GPT-5.4 with low reasoning (faster, good for large prompts)
codex exec --full-auto -m gpt-5.4 -c model_reasoning_effort="low" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt
```

The `-o` flag writes the final agent message to a file for easy consumption. Use `--full-auto` for non-interactive execution with workspace-write sandboxing.

### Codex CLI Setup

Install: `npm install -g @openai/codex` (requires Node.js). Configure `~/.codex/config.toml`:

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "xhigh"
```

Auth: `codex login` (uses your OpenAI account). No `OPENAI_API_KEY` needed — Codex CLI authenticates separately.

## Usage: API Models (ask_model.py)

Pay-per-token. Use for Gemini, Claude, gpt-5.4-pro, or when you need multi-provider diversity. For short questions, pass directly as an argument. **For long prompts, always use `--file`** — long shell arguments break unpredictably.

Where `SKILL_DIR` is the directory containing this skill. The `-m` flag takes a full [pydantic-ai model string](https://ai.pydantic.dev/api/models/). Thinking effort is automatically set to maximum for each provider.

```bash
# GPT-5.4 with xhigh reasoning (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt.txt

# GPT-5.4 with low reasoning (fast, good for large prompts)
uv run --directory SKILL_DIR python scripts/ask_model.py -t low -f ~/claude/scratch/prompt.txt

# GPT-5.4 Pro — maximum depth, slow (~10-15 min), extraordinary analysis
uv run --directory SKILL_DIR python scripts/ask_model.py -m openai-responses:gpt-5.4-pro -f ~/claude/scratch/prompt.txt

# Gemini 3.1 Pro — brilliantly intelligent, fast
uv run --directory SKILL_DIR python scripts/ask_model.py -m google-gla:gemini-3.1-pro-preview -f ~/claude/scratch/prompt.txt

# Claude Opus 4.6 with adaptive thinking at max effort
uv run --directory SKILL_DIR python scripts/ask_model.py -m anthropic:claude-opus-4-6 -f ~/claude/scratch/prompt.txt
```

### ask_model.py Options

- `--model` / `-m`: Full pydantic-ai model string (default: `openai:gpt-5.4`)
- `--thinking` / `-t`: Override thinking level. OpenAI: `low`/`medium`/`high`/`xhigh` (default: `xhigh`). Gemini: `low`/`high`. Use `low` for large prompts where speed matters more than depth.
- `--system` / `-s`: Optional system prompt override
- `--file` / `-f`: Read question from a file instead of a CLI argument (use for long prompts)
- `--list-models` / `-l`: List known model names, optionally filtered by prefix (e.g. `-l openai`, `-l anthropic`).

### When to Use Codex CLI vs ask_model.py

- **Codex CLI** (preferred): Uses subscription credits. GPT-5.4 xhigh is the default recommendation. Codex-only models (`gpt-5.3-codex`) are only available here.
- **ask_model.py**: For Gemini, Claude, gpt-5.4-pro, or when you need multi-provider opinions. Pay-per-token.

## API Key Setup

Add keys to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export OPENAI_API_KEY="your-key"      # Required for openai: models via ask_model.py
export ANTHROPIC_API_KEY="your-key"   # Required for anthropic: models
export GOOGLE_API_KEY="your-key"      # Required for google-gla: models
```

Codex CLI authenticates via `codex login` — no env var needed.

The script checks for the key before calling the API. If missing, it tells you which
variable to set. If the key exists but the call fails, common errors:
- **insufficient_quota (429)**: Billing issue — add credits at the provider's dashboard.
- **invalid_api_key (401)**: Wrong key — check you exported the correct one and ran `source ~/.zshrc`.
- **rate_limit (429)**: Too many requests — wait and retry.

## Multiple Calls

Each call gets zero context from previous calls. For follow-ups, include the prior exchange: "I asked X, you answered Y, help me understand Z."
