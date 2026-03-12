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

**Always use the script default** (`openai:gpt-5.4`) unless you have a specific reason to change. Do NOT override with older models like o3 or gpt-5.2 — they are superseded.

There are two invocation methods: the **pydantic-ai script** (for API models) and the **Codex CLI** (for Codex-surface models). See usage sections below for each.

### API Models (via `ask_model.py`)

| Model | When to use | API key needed |
|-------|-------------|----------------|
| `openai:gpt-5.4` **(default)** | Primary partner. xhigh thinking, exceptional detail | `OPENAI_API_KEY` |
| `google-gla:gemini-3.1-pro-preview` | Second opinion, brilliantly intelligent reasoning | `GOOGLE_API_KEY` |
| `anthropic:claude-opus-4-6` | Third perspective, different reasoning style | `ANTHROPIC_API_KEY` |

### Codex CLI Models (via `codex exec`)

Codex models are **only available through the Codex CLI** — they are not accessible via the standard OpenAI API. The Codex CLI uses credits from an OpenAI paid subscription (no per-token billing), making it a cost-effective way to get strong coding opinions.

| Model | When to use | Notes |
|-------|-------------|-------|
| `gpt-5.3-codex` **(recommended)** | Code review, debugging, refactors. Strong coding specialist | Default in `~/.codex/config.toml` |
| `gpt-5.4` | Full GPT-5.4 reasoning through Codex harness. xhigh thinking | Good for deep architectural questions |

Set reasoning effort via `-c model_reasoning_effort="xhigh"` (values: `low`, `medium`, `high`, `xhigh`). Default from config is `xhigh`.

Before calling, verify the required API key is set: `echo $GOOGLE_API_KEY | head -c 8` (should show `AIza...`).

## Framing Your Question

You get **one message out and one message back**. There is no follow-up. Your partner has ZERO context about what you're working on — they see only what you send. The context window is finite and expensive, so treat it like a skill prompt: include everything needed, nothing that isn't.

**Your partner needs all context to answer your question.** They cannot read your files, see your conversation, or infer your situation. If you don't include it, they don't know it. But context is limited, so be surgical:

1. **Include all relevant context**: code, errors, constraints, what you tried. Use `mental-models` to structure your thinking before asking.
2. **State what you're stuck on**: "I tried A, B, C and none work because D" — not just "help me with X"
3. **Ask a specific question and set the frame**: what kind of answer you need (diagnosis, alternative approach, code review).
4. **Never include secrets**: API keys, credentials, tokens, or private repo URLs. Your question goes to an external API.

Bad: "How do I fix this auth bug?"
Good: "Here is my auth middleware [code]. Users with expired tokens get a 500 instead of 401. I have verified the token validation logic is correct and the error handler is registered. The 500 comes from [stack trace]. What could cause the error handler to be bypassed?"

## Usage: API Models (ask_model.py)

For short questions, pass directly as an argument. **For long prompts (PR diffs, large code, etc.), always use `--file`** — long shell arguments break unpredictably.

```bash
# Short question — inline argument
uv run --directory SKILL_DIR python scripts/ask_model.py -m <model> "Your question"

# Long prompt — write to file first, then pass with --file
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt.txt
```

Where `SKILL_DIR` is the directory containing this skill. The `-m` flag takes a full [pydantic-ai model string](https://ai.pydantic.dev/api/models/) — the provider prefix determines which API key and thinking settings to use.

The default is `openai:gpt-5.4`. Thinking effort is automatically set to maximum for each provider. Use `--thinking low` for fast responses on large prompts (~1.5 min vs ~7 min for xhigh on ~1000-line reviews).

```bash
# GPT-5.4 with xhigh reasoning (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt.txt

# GPT-5.4 with low reasoning (fast, good for large prompts)
uv run --directory SKILL_DIR python scripts/ask_model.py -t low -f ~/claude/scratch/prompt.txt

# Claude Opus 4.6 with adaptive thinking at max effort
uv run --directory SKILL_DIR python scripts/ask_model.py -m anthropic:claude-opus-4-6 -f ~/claude/scratch/prompt.txt

# Gemini 3.1 Pro with thinking enabled
uv run --directory SKILL_DIR python scripts/ask_model.py -m google-gla:gemini-3.1-pro-preview -f ~/claude/scratch/prompt.txt
```

### ask_model.py Options

- `--model` / `-m`: Full pydantic-ai model string (default: `openai:gpt-5.4`)
- `--thinking` / `-t`: Override thinking level. OpenAI: `low`/`medium`/`high`/`xhigh` (default: `xhigh`). Gemini: `low`/`high`. Use `low` for large prompts where speed matters more than depth.
- `--system` / `-s`: Optional system prompt override
- `--file` / `-f`: Read question from a file instead of a CLI argument (use for long prompts)
- `--list-models` / `-l`: List known model names, optionally filtered by prefix (e.g. `-l openai`, `-l anthropic`).

## Usage: Codex CLI

Codex models are only available through the `codex` CLI (not the standard OpenAI API). Uses credits from an OpenAI paid subscription — no per-token billing.

**For short questions**, pass inline. **For long prompts, write to a file and pipe via stdin** — this avoids shell escaping issues with backticks and special characters.

```bash
# Short question — gpt-5.3-codex (default from ~/.codex/config.toml)
codex exec --full-auto "Your question" -o ~/claude/scratch/codex_output.txt

# Long prompt — write to file, pipe via stdin
codex exec --full-auto -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# GPT-5.4 through Codex harness with xhigh reasoning
codex exec --full-auto -m gpt-5.4 -c model_reasoning_effort="xhigh" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# Override reasoning effort (values: low, medium, high, xhigh)
codex exec --full-auto -c model_reasoning_effort="low" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt
```

The `-o` flag writes the final agent message to a file for easy consumption. Use `--full-auto` for non-interactive execution with workspace-write sandboxing.

### Codex CLI Setup

Install: `npm install -g @openai/codex` (requires Node.js). Configure `~/.codex/config.toml`:

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "xhigh"
```

Auth: `codex login` (uses your OpenAI account). No `OPENAI_API_KEY` needed — Codex CLI authenticates separately.

### When to Use Codex CLI vs ask_model.py

- **Codex CLI**: Coding tasks (reviews, debugging, refactors). Uses subscription credits. Codex models (`gpt-5.3-codex`) are only available here.
- **ask_model.py**: Multi-provider support (GPT, Gemini, Claude). Pay-per-token API. Better for non-coding questions.
- **Both support `gpt-5.4`**: Use Codex CLI to leverage subscription credits, or ask_model.py for pay-per-token.

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
