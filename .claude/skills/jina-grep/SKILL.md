---
name: jina-grep
description: >
  Semantic grep using Jina embedding models on Apple Silicon via MLX.
  Use when the user says "semantic search", "find code that does X",
  "natural language grep", "fuzzy search", "find similar code",
  "classify these lines", or wants meaning-based file search rather than
  exact string matching. Also use for zero-shot text classification over
  local files. Do NOT use for exact string matching (use grep/rg directly)
  or on non-macOS systems.
allowed-tools: Bash(jina-grep *)
---

Local semantic search over files using Jina embedding models on Apple Silicon (MLX). Requires `jina-grep` to be installed.

## Installation

```bash
uv tool install git+https://github.com/jina-ai/jina-grep-cli.git
```

Requires Python 3.10+ and Apple Silicon.

## Modes

### Pipe mode — rerank grep output semantically

```bash
grep -rn "error" src/ | jina-grep "error handling logic"
grep -rn "TODO" . | jina-grep "performance optimization"
```

### Standalone mode — search files with natural language

```bash
jina-grep "memory leak" src/
jina-grep -r --threshold 0.3 "database connection pooling" .
jina-grep --top-k 5 "retry with exponential backoff" *.py
```

### Code search — use code-specific models

```bash
jina-grep --model jina-code-embeddings-1.5b --task nl2code "sort a list in descending order" src/
jina-grep --model jina-code-embeddings-0.5b --task code2code "for i in range(len(arr))" src/
```

Code tasks: `nl2code`, `code2code`, `code2nl`, `code2completion`, `qa`.

### Zero-shot classification — label lines

```bash
jina-grep -e "bug" -e "feature" -e "docs" src/
jina-grep -o -e "positive" -e "negative" -e "neutral" reviews.txt
```

## Key Flags

| Flag | Purpose |
|---|---|
| `--threshold` | Cosine similarity cutoff (default: 0.5) |
| `--top-k` | Max results (default: 10) |
| `--model` | Model choice (default: `jina-embeddings-v5-nano`) |
| `--task` | Task type for model family |
| `--granularity` | `line`, `paragraph`, `sentence`, or `token` (default: token) |
| `-r` | Recursive search |
| `-n` | Show line numbers |
| `-A/-B/-C NUM` | Context lines (like grep) |
| `--include/--exclude` | Glob filters |
| `-v` | Invert match |
| `-l` | Filenames only |

## Models

| Model | Best for |
|---|---|
| `jina-embeddings-v5-nano` (default) | Fast general search |
| `jina-embeddings-v5-small` | Higher quality general search |
| `jina-code-embeddings-0.5b` | Fast code search |
| `jina-code-embeddings-1.5b` | Higher quality code search |

## Persistent Server

For repeated queries, start the server to avoid model reload:

```bash
jina-grep serve start
jina-grep serve stop
jina-grep serve status
```

Serverless mode auto-detects a running server.
