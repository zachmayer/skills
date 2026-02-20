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

Semantic search over markdown files using local sentence-transformers embeddings and FAISS approximate nearest neighbor search.

## Commands

### Index the vault

Builds (or rebuilds) the search index for all markdown files:

```bash
uv run --script SKILL_DIR/scripts/vector_search.py index "$CLAUDE_OBSIDIAN_DIR"
```

This embeds every markdown file using `all-MiniLM-L6-v2` (runs locally, no API keys needed) and stores a FAISS HNSW index in `$CLAUDE_OBSIDIAN_DIR/.vector_index/`.

Re-run after adding or changing notes. Indexing a few hundred files takes ~10-30 seconds.

### Search

```bash
uv run --script SKILL_DIR/scripts/vector_search.py search "$CLAUDE_OBSIDIAN_DIR" "your query here"
```

Options:
- `-k N` — number of results (default: 5)
- `--scope PREFIX` — filter to files under a path prefix (e.g. `--scope memory/` or `--scope knowledge_graph/`)

### Check index status

```bash
uv run --script SKILL_DIR/scripts/vector_search.py status "$CLAUDE_OBSIDIAN_DIR"
```

## How it works

1. **Chunking**: Markdown files are split by `##` headers. Each section becomes a searchable chunk.
2. **Embedding**: Chunks are embedded locally using `all-MiniLM-L6-v2` (384 dimensions, sentence-transformers).
3. **Indexing**: Embeddings are stored in a FAISS HNSW index for fast approximate nearest neighbor search.
4. **Search**: Query is embedded with the same model, then searched against the index. Results are ranked by cosine similarity.

## When to use

- "Find notes related to X" — semantic similarity finds conceptually related content
- "What have I written about Y?" — searches across memory and knowledge graph
- Exploring connections between ideas that don't share exact keywords
- Scoping search to memory vs knowledge graph with `--scope`
