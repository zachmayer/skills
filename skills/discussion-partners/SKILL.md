---
name: discussion-partners
description: >
  Ask a question to another AI model (OpenAI, Anthropic, or Google). Use when
  you want a second opinion, need to compare model outputs, or want to delegate
  a subtask to a different model. Do NOT use for tasks you can handle directly.
allowed-tools: Bash(uv run *)
disable-model-invocation: true
---

Query another AI model for input on the current task.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/ask_model.py --provider <provider> --model <model> "Your question here"
```

Where `SKILL_DIR` is the directory containing this skill.

## Providers and Models

### OpenAI (requires OPENAI_API_KEY)
```bash
uv run ... --provider openai --model gpt-4o "question"
uv run ... --provider openai --model o1 "question"
```

### Anthropic (requires ANTHROPIC_API_KEY)
```bash
uv run ... --provider anthropic --model claude-sonnet-4-20250514 "question"
```

### Google (requires GOOGLE_API_KEY)
```bash
uv run ... --provider google --model gemini-2.0-flash "question"
```

## Options

- `--provider` / `-p`: openai, anthropic, or google
- `--model` / `-m`: Model name (provider-specific)
- `--system` / `-s`: Optional system prompt
- `--max-tokens`: Max response tokens (default: 4096)

## When to Use

- Getting a second opinion on architectural decisions
- Comparing how different models approach a problem
- Delegating specialized tasks (e.g., use o1 for math-heavy reasoning)
- Cross-checking your own analysis
