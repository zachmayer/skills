---
name: vector_search
description: >
  Semantic search over memory files and obsidian vault via local embeddings.
  Use when the user asks "what do I know about X", needs to find related notes
  across memory and knowledge graph, or keyword search returns too many or too
  few results. Do NOT use for exact keyword search (use Grep), finding a specific
  file by name (use Glob), or reading a known file (use Read).
allowed-tools: Bash(uv run *)
---

Semantic vector search over `$CLAUDE_OBSIDIAN_DIR` using local sentence-transformers
and usearch (approximate nearest neighbors). No API keys required.

First run downloads the embedding model (~80MB). Subsequent runs use the cached model.

## Commands

All commands via:
```bash
uv run --script SKILL_DIR/scripts/vector_search.py <command> [args]
```

Where `SKILL_DIR` is the directory containing this skill.

### Build the index

```bash
# Index everything (memory + knowledge_graph)
uv run --script SKILL_DIR/scripts/vector_search.py index

# Force full rebuild
uv run --script SKILL_DIR/scripts/vector_search.py index --force
```

Incremental — skips rebuild if no files changed (by mtime). Full rebuild takes ~3-5 seconds on CPU for a typical vault.

### Search

```bash
# Semantic search
uv run --script SKILL_DIR/scripts/vector_search.py search "March Madness modeling"

# More results
uv run --script SKILL_DIR/scripts/vector_search.py search "pydantic ai tools" -k 10

# Filter to memory only
uv run --script SKILL_DIR/scripts/vector_search.py search "tax prep" --scope memory

# Minimum similarity threshold
uv run --script SKILL_DIR/scripts/vector_search.py search "board games" --threshold 0.3
```

### Check status

```bash
uv run --script SKILL_DIR/scripts/vector_search.py status
```

## How It Works

1. **Chunking**: Markdown split by `##` headers, then paragraphs if sections exceed 2000 chars
2. **Embedding**: `all-MiniLM-L6-v2` (384 dims, runs locally on CPU)
3. **Indexing**: usearch HNSW index for fast approximate nearest neighbor search
4. **Search**: Query embedded with same model, searched against index, top-k returned

Index stored as `.vector_search.usearch` + `.vector_search_meta.json` in the vault root (dotfiles, ignored by obsidian).
