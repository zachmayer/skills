---
name: discussion-partners
description: >
  Queries another AI model (GPT-5.5, Gemini 3.1 Pro, Claude Opus, Codex)
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

**Default: GPT-5.5 xhigh fast via Codex CLI.** GPT-5.5 (released 2026-04-23) is the first fully retrained base model since GPT-4.5 — 1M context, stronger coding than 5.4, and fewer tokens for the same results in Codex.

### Two invocation paths

| Path | Models | Billing | Auth |
|------|--------|---------|------|
| **Codex CLI** (`codex exec`) — OpenAI models | GPT-5.5 | ChatGPT subscription credits | `codex login` |
| **`ask_model.py`** — non-OpenAI models | Gemini 3.1 Pro, Claude Opus 4.6 | Pay-per-token | Provider API keys |

**Why Codex CLI for OpenAI models:** GPT-5.5 and GPT-5.5 Pro are **not in the OpenAI public API** (neither Chat Completions nor Responses) as of the 2026-04-23 launch. OpenAI ships new models to ChatGPT/Codex first and the public API rollout is staged. Codex CLI authenticates via ChatGPT, so it works today. Once OpenAI enables GPT-5.5 in the API, `ask_model.py -m openai:gpt-5.5` will work transparently — no skill changes needed.

### Codex CLI Models (OpenAI)

| Model | When to use |
|-------|-------------|
| `gpt-5.5` **(default)** | Primary partner. `xhigh` for depth, `low` for speed on large prompts |

- **Reasoning effort**: `-c model_reasoning_effort="xhigh"` (values: `low`/`medium`/`high`/`xhigh`; config default is `xhigh`).
- **Fast mode**: `-c service_tier="fast"` (or set in config). 2× credits, ~2× faster — clear win at xhigh.
- **Model-upgrade caveat**: Codex resets reasoning to the new model's default when you accept an upgrade. Re-apply xhigh, or rely on `config.toml`.
- **GPT-5.5 Pro is ChatGPT-only** — not selectable in Codex CLI and not in the API. Skip it for programmatic use until OpenAI ships it somewhere callable.

### ask_model.py Models (Gemini / Claude)

| Model | When to use | API key needed |
|-------|-------------|----------------|
| `google-gla:gemini-3.1-pro-preview` **(default)** | Brilliantly intelligent, fast | `GOOGLE_API_KEY` |
| `anthropic:claude-opus-4-6` | Third perspective, different reasoning style | `ANTHROPIC_API_KEY` |

Thinking effort is auto-set to max for each provider. For OpenAI models, use Codex CLI — not this script.

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
# GPT-5.5 xhigh fast (default recommendation) — short question
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="xhigh" "Your question" -o ~/claude/scratch/codex_output.txt

# GPT-5.5 xhigh fast — long prompt from file
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="xhigh" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# GPT-5.5 with low reasoning fast (faster still, good for large prompts)
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="low" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt

# Enable web search (--search gives the model a web_search tool)
codex exec --full-auto --search -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="xhigh" -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt.txt
```

The `-o` flag writes the final agent message to a file for easy consumption. Use `--full-auto` for non-interactive execution with workspace-write sandboxing.

**Timeouts**: Deep thinking models can take 5-30+ minutes on complex prompts. The Bash tool's max timeout is 600,000ms (10 min) — not enough. **Always use `run_in_background: true`** for discussion partner calls. This has no timeout limit; you get notified when it finishes. Never use a foreground Bash call for these — it will SIGKILL the process mid-thought.

**Additional capabilities**: `--search` enables live web search (native Responses `web_search` tool, no per-call approval). Codex also supports MCP servers for additional tools (`codex mcp add`), and has a built-in `codex review` command for code review. Run `codex --help` and `codex exec --help` to see all available options.

### Codex CLI Setup

Install: `npm install -g @openai/codex` (requires Node.js). Configure `~/.codex/config.toml`:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
service_tier = "fast"
```

Auth: `codex login` (uses your OpenAI account). No `OPENAI_API_KEY` needed — Codex CLI authenticates separately.

## Usage: ask_model.py (Gemini / Claude)

Pay-per-token via provider API keys. For short questions, pass inline. **For long prompts, always use `--file`** — long shell arguments break unpredictably.

`SKILL_DIR` is the directory containing this skill. `-m` takes a full [pydantic-ai model string](https://ai.pydantic.dev/api/models/).

```bash
# Gemini 3.1 Pro — brilliantly intelligent, fast (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt.txt

# Gemini with low thinking (fast, good for large prompts)
uv run --directory SKILL_DIR python scripts/ask_model.py -t low -f ~/claude/scratch/prompt.txt

# Claude Opus 4.6 with adaptive thinking at max effort
uv run --directory SKILL_DIR python scripts/ask_model.py -m anthropic:claude-opus-4-6 -f ~/claude/scratch/prompt.txt
```

### ask_model.py Options

- `--model` / `-m`: Full pydantic-ai model string (default: `google-gla:gemini-3.1-pro-preview`)
- `--thinking` / `-t`: Override thinking level. Gemini: `low`/`high` (default: max). OpenAI: `low`/`medium`/`high`/`xhigh` (once GPT-5.5 ships to the API). Use `low` for large prompts where speed matters more than depth.
- `--system` / `-s`: Optional system prompt override
- `--file` / `-f`: Read question from a file instead of a CLI argument (use for long prompts)
- `--list-models` / `-l`: List known model names, optionally filtered by prefix (e.g. `-l google`, `-l anthropic`).

## API Key Setup

```bash
export GOOGLE_API_KEY="your-key"       # Required for google-gla: models (ask_model.py default)
export ANTHROPIC_API_KEY="your-key"    # Required for anthropic: models
```

Codex CLI authenticates via `codex login` — no env var needed.

Common errors from `ask_model.py`:
- **insufficient_quota (429)**: Billing issue — add credits at the provider's dashboard.
- **invalid_api_key (401)**: Wrong key — check you exported the correct one and ran `source ~/.zshrc`.
- **rate_limit (429)**: Too many requests — wait and retry.
- **model_not_found (404)** for `openai:gpt-5.5` / `openai-responses:gpt-5.5-pro`: API rollout not complete yet — use Codex CLI instead (for 5.5) or wait (for 5.5 Pro).

## Multiple Calls

Each call gets zero context from previous calls. For follow-ups, include the prior exchange: "I asked X, you answered Y, help me understand Z."
