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
allowed-tools: Bash(uv run *), Bash(codex exec *), Agent
---

Query another AI model for an outside perspective on a difficult problem. One message out, one message back — make it count.

## Default invocation: three models in parallel

When invoked for a second opinion, **run all three paths concurrently** — one model per family, three independent perspectives. Fire them in a single message (parallel tool calls, not sequential); triage agreements vs disagreements when they return.

1. **OpenAI GPT-5.5 xhigh fast** via Codex CLI (`run_in_background: true` — can take 5–30 min at xhigh)
2. **Google Gemini 3.1 Pro** via `ask_model.py`
3. **Anthropic Opus** via an Opus sub-agent (Agent tool, `model="opus"`)

Send the same prompt to all three. Differences in framing across families catch hand-waving that a single model would paper over.

For a quick single opinion (not worth firing all three), **default to Codex CLI with GPT-5.5 xhigh fast** — it's the cheapest (subscription credits, no per-token), strongest OpenAI option, and the most common path.

For **maximum depth** on a hard correctness problem, add `openai-responses:gpt-5.4-pro` via `ask_model.py` (slow ~10–15 min, but extraordinary detail — currently the latest OpenAI pro model available via API).

## Three invocation paths

| Path | Models | Billing | Auth |
|------|--------|---------|------|
| **Codex CLI** (`codex exec`) — preferred for OpenAI | GPT-5.5 | ChatGPT subscription credits | `codex login` |
| **`ask_model.py`** — Gemini, OpenAI pro (via Responses API) | Gemini 3.1 Pro *(default)*; `openai-responses:gpt-5.4-pro` | Pay-per-token | Provider API keys |
| **Sub-agent** — preferred for Claude | Opus | — | Inherited from Claude Code |

- **Codex CLI** (preferred for OpenAI): uses subscription credits — cheapest option. GPT-5.5 xhigh fast is the default recommendation.
- **`ask_model.py`**: the only programmatic path to OpenAI **pro** models. As of 2026-04-24, `openai-responses:gpt-5.4-pro` is the latest pro available via API; `gpt-5.5-pro` is ChatGPT-only pending API rollout. Also the path to Gemini.
- **Sub-agent** (preferred for Claude): use the Agent tool with `model="opus"`. Better than `ask_model.py -m anthropic:...` — the sub-agent inherits Claude Code's auth, has full tool access (can read files, search the codebase, run commands), and integrates with your conversation context.

### Codex CLI — GPT-5.5

| Model | When to use |
|-------|-------------|
| `gpt-5.5` **(default)** | Primary OpenAI partner. `xhigh` for depth, `low` for speed on large prompts |

- **Reasoning effort**: `-c model_reasoning_effort="xhigh"` (values: `low`/`medium`/`high`/`xhigh`; config default is `xhigh`).
- **Fast mode**: `-c service_tier="fast"` (or set in config). 2× credits, ~2× faster — clear win at xhigh.
- **Model-upgrade caveat**: Codex resets reasoning to the new model's default when you accept an upgrade. Re-apply xhigh, or rely on `config.toml`.
- **GPT-5.5 Pro is not in Codex CLI** (no `*-pro` variants in the Codex picker). Use `ask_model.py` with `openai-responses:gpt-5.5-pro` once OpenAI ships it to the API; for now, `openai-responses:gpt-5.4-pro` is the latest available.

### ask_model.py — Gemini + OpenAI pro

| Model | When to use | API key needed |
|-------|-------------|----------------|
| `google-gla:gemini-3.1-pro-preview` **(default)** | Brilliantly intelligent, fast. Google family | `GOOGLE_API_KEY` |
| `openai-responses:gpt-5.4-pro` | Maximum depth. Slow (~10-15 min), extraordinary detail. Latest OpenAI pro model available via API. Responses API only — **not** Chat Completions, **not** Codex CLI | `OPENAI_API_KEY` |

When OpenAI ships `gpt-5.5` and `gpt-5.5-pro` to the API, `ask_model.py -m openai:gpt-5.5` and `-m openai-responses:gpt-5.5-pro` will work transparently — no skill change needed.

Thinking effort is auto-set to max for each provider.

### Sub-agent — Opus

Use the Agent tool with `model="opus"` for a Claude-side perspective:

```
Agent(
  subagent_type="general-purpose",
  model="opus",
  description="Discussion partner review",
  prompt="<full context and question>"
)
```

The sub-agent inherits your Claude Code auth, so no API key is required. It also gets tool access, so for questions where it'd help to read files or search the codebase, the sub-agent can do that — unlike `ask_model.py` which is pure text in/text out.

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

## Usage: ask_model.py

Pay-per-token via provider API keys. For short questions, pass inline. **For long prompts, always use `--file`** — long shell arguments break unpredictably.

`SKILL_DIR` is the directory containing this skill. `-m` takes a full [pydantic-ai model string](https://ai.pydantic.dev/api/models/).

```bash
# Gemini 3.1 Pro — brilliantly intelligent, fast (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt.txt

# Gemini with low thinking (fast, good for large prompts)
uv run --directory SKILL_DIR python scripts/ask_model.py -t low -f ~/claude/scratch/prompt.txt

# GPT-5.4 Pro — maximum depth, slow (~10-15 min). Latest OpenAI pro available via API
uv run --directory SKILL_DIR python scripts/ask_model.py -m openai-responses:gpt-5.4-pro -f ~/claude/scratch/prompt.txt
```

For Claude Opus, use a sub-agent instead of `ask_model.py` (see "Sub-agent — Opus" above).

### ask_model.py Options

- `--model` / `-m`: Full pydantic-ai model string (default: `google-gla:gemini-3.1-pro-preview`)
- `--thinking` / `-t`: Override thinking level. Gemini: `low`/`high` (default: max). OpenAI: `low`/`medium`/`high`/`xhigh` (default: `xhigh`). Use `low` for large prompts where speed matters more than depth.
- `--system` / `-s`: Optional system prompt override
- `--file` / `-f`: Read question from a file instead of a CLI argument (use for long prompts)
- `--list-models` / `-l`: List known model names, optionally filtered by prefix (e.g. `-l google`, `-l openai`).

## API Key Setup

```bash
export GOOGLE_API_KEY="your-key"       # Required for google-gla: models (ask_model.py default)
export OPENAI_API_KEY="your-key"       # Required for openai-responses:gpt-5.4-pro via ask_model.py
```

Codex CLI authenticates via `codex login` — no env var needed. Sub-agents inherit Claude Code's auth — no env var needed.

Common errors from `ask_model.py`:
- **insufficient_quota (429)**: Billing issue — add credits at the provider's dashboard.
- **invalid_api_key (401)**: Wrong key — check you exported the correct one and ran `source ~/.zshrc`.
- **rate_limit (429)**: Too many requests — wait and retry.
- **model_not_found (404)** for `openai:gpt-5.5` or `openai-responses:gpt-5.5-pro`: API rollout not complete yet — use Codex CLI (for 5.5) or `openai-responses:gpt-5.4-pro` (for a pro-tier fallback via API).

## Multiple Calls

Each call gets zero context from previous calls. For follow-ups, include the prior exchange: "I asked X, you answered Y, help me understand Z."
