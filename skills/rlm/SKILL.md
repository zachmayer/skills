---
name: rlm
description: >
  Analyze large files that exceed a single LLM context window using Recursive Language
  Model (RLM): a root LLM iteratively writes Python code to chunk and explore a file,
  delegating focused semantic analysis to cheap sub-LLMs via llmQuery(). Use when the
  user has a large log, transcript, dataset, or document and asks "analyze this file",
  "what's in here", or needs systematic extraction from content too large for a single
  prompt. Do NOT use for small files that fit in context, simple questions answerable
  from a snippet, or general web/code tasks.
---

Run RLM analysis on $ARGUMENTS.

## Quick Start

```bash
uv run python skills/rlm/scripts/rlm.py -c <file> -q "<question>"

# Fast mode (3 iterations)
uv run python skills/rlm/scripts/rlm.py -c ./data.log -q "What errors occurred?" --quick
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --context` | required | Path to context file |
| `-q, --query` | required | Question to answer |
| `-m, --max-iterations` | 10 | Max REPL iterations |
| `--root-model` | claude-sonnet-4-5-20250514 | Orchestrator LLM |
| `--sub-model` | claude-haiku-4-5-20251001 | Chunk analysis LLM |
| `--quick` | — | Fast mode: 3 iterations |

## How It Works

The root LLM writes Python code blocks that run in a persistent namespace:
- `contextPath` — absolute path to the file
- `llmQuery(prompt)` → str — ask sub-LLM a focused question about a chunk
- `open`, `re`, `json`, `os` — pre-injected, no imports needed
- Variables persist across all iterations

**3-phase strategy:**
1. **Recon** — Read file, check size, identify format and natural chunk boundaries
2. **Filter + Analyze** — Split by structure, call `llmQuery()` on relevant sections
3. **Synthesize** — Aggregate, output `FINAL(answer)` or `FINAL_VAR(varname)`

## Tips

- Be specific: `"Why did the upload fail in step 3?"` beats `"What happened?"`
- Small files (<10K): `--quick` (3 iterations) is enough
- Large files (100K+): use `-m 15` or higher
- Plain text and structured formats (JSON lines, markdown, `---` delimiters) chunk best
