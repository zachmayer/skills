---
name: vector_search
description: >
  Semantic search over memory files and obsidian vault via embeddings.
  Use when you need to find notes by meaning rather than exact keywords,
  when exploring related concepts, or when keyword search returns too many
  or too few results. Do NOT use for exact keyword lookups (use grep),
  reading specific known files, or non-text content.
allowed-tools: Bash(uv run *)
---

Semantic search over markdown files using local sentence-transformers embeddings and FAISS.

Embeds whole files (not chunks). Caches embeddings with timestamps so only changed files are re-embedded. Returns filenames only — read the matched files yourself.

## Commands

### Index the vault

```bash
uv run --script SKILL_DIR/scripts/vector_search.py index "$CLAUDE_OBSIDIAN_DIR"
```

Embeds every markdown file using `all-MiniLM-L6-v2` (runs locally, no API keys needed). Stores a FAISS index and embedding cache in `$CLAUDE_OBSIDIAN_DIR/.vector_index/`.

Only re-embeds files that changed since last index. Re-indexing a vault where most files are cached is near-instant.

### Search

```bash
uv run --script SKILL_DIR/scripts/vector_search.py search "$CLAUDE_OBSIDIAN_DIR" "your query here"
```

Returns matching filenames ranked by cosine similarity. Read the files yourself to find what you need.

Options:
- `-k N` — number of results (default: 5)
- `--scope PREFIX` — filter to files under a path prefix (e.g. `--scope memory/` or `--scope knowledge_graph/`)

### Check index status

```bash
uv run --script SKILL_DIR/scripts/vector_search.py status "$CLAUDE_OBSIDIAN_DIR"
```

Shows how many files are indexed, how many need re-indexing.

## When to use

- "Find notes related to X" — semantic similarity finds conceptually related content
- "What have I written about Y?" — searches across memory and knowledge graph
- Exploring connections between ideas that don't share exact keywords
- Scoping search to memory vs knowledge graph with `--scope`
