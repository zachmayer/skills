---
name: discussion_partners
description: >
  Ask a question to another AI model (OpenAI, Anthropic, or Google) with
  extended thinking enabled. Use when you are stuck on a difficult problem,
  suspect you are spinning your wheels, or sense there is an angle you have
  not considered. Do NOT use for routine tasks you can handle directly.
allowed-tools: Bash(uv run *)
---

Query another AI model for an outside perspective on a difficult problem.

## Why This Exists

Different models have different strengths. When you hit a wall — circling the same approaches, missing subtle interactions, or unable to see past your own framing — an outside perspective from a model with a different architecture and training can break the deadlock.

This is not delegation. This is consultation: you send one message, you get one message back. Make it count.

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

1. **Include all relevant context**: code snippets, error messages, constraints, what you have tried. Use the `mental_models` skill to structure your thinking before asking.
2. **State what you are stuck on**: not just "help me with X" but "I have tried A, B, C and none work because D"
3. **Ask a specific question**: "What am I missing?" or "Is there an interaction between X and Y I am not seeing?"
4. **Set the frame**: tell it what kind of answer you need (a diagnosis, an alternative approach, a code review, etc.)
5. **Cut the fluff**: No pleasantries, no restating the obvious. Every token should earn its place.

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

## Options

- `--provider` / `-p`: openai, anthropic, or google
- `--model` / `-m`: Override model name (defaults to best thinking model per provider)
- `--system` / `-s`: Optional system prompt override
