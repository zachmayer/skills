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

## Recommended Model

**GPT-5.2 with xhigh thinking** (`--provider openai`) is the default and recommended discussion partner. It has exceptional attention to detail and a strong ability to detect subtle interactions and dependencies that can be difficult to spot from inside a problem. Use it when:

- You suspect a bug has a non-obvious root cause
- You are going in circles on an architectural decision
- You need someone to poke holes in your reasoning
- A problem has interacting constraints that are hard to hold in your head simultaneously

The other providers (Anthropic, Google) are available for comparison or when you want multiple perspectives.

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
uv run --directory SKILL_DIR python scripts/ask_model.py --provider <provider> "Your detailed question with full context"
```

Where `SKILL_DIR` is the directory containing this skill.

## Providers and Models

All providers default to their best thinking model with maximum thinking effort.

### OpenAI (requires OPENAI_API_KEY) — Recommended
```bash
# GPT-5.2 with xhigh reasoning (default)
uv run --directory SKILL_DIR python scripts/ask_model.py -p openai "question"
```

### Anthropic (requires ANTHROPIC_API_KEY)
```bash
# Claude Opus 4.6 with adaptive thinking at max effort
uv run --directory SKILL_DIR python scripts/ask_model.py -p anthropic "question"
```

### Google (requires GOOGLE_API_KEY)
```bash
# Gemini 2.5 Pro with thinking enabled
uv run --directory SKILL_DIR python scripts/ask_model.py -p google "question"
```

## API Key Setup

Add keys to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export OPENAI_API_KEY="your-key"      # Required for --provider openai
export ANTHROPIC_API_KEY="your-key"   # Required for --provider anthropic
export GOOGLE_API_KEY="your-key"      # Required for --provider google
```

The script checks for the key before calling the API. If missing, it tells you which
variable to set. If the key exists but the call fails, common errors:
- **insufficient_quota (429)**: Billing issue — add credits at the provider's dashboard.
- **invalid_api_key (401)**: Wrong key — check you exported the correct one and ran `source ~/.zshrc`.
- **rate_limit (429)**: Too many requests — wait and retry.

## Options

- `--provider` / `-p`: openai, anthropic, or google
- `--model` / `-m`: Override model name (defaults to best thinking model per provider)
- `--system` / `-s`: Optional system prompt override
