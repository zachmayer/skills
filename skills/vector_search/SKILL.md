---
name: vector_search
description: >
  Semantic search over memory files and obsidian vault via embeddings.
  WHEN: User asks "what do I know about X", needs to find related notes
  across memory and knowledge graph, or keyword search returns too many
  or too few results. Also useful for finding thematically related notes.
  WHEN NOT: Exact keyword search (use Grep), finding a specific file by
  name (use Glob), or reading a known file (use Read).
---

Semantic vector search over `$CLAUDE_OBSIDIAN_DIR` using OpenAI embeddings.

Requires `OPENAI_API_KEY` environment variable.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `index` | Build/update embedding index (only re-embeds changed files) |
| `search "query"` | Find semantically similar chunks |
| `status` | Show index stats (chunks, files, size) |

## Commands

All commands:
```bash
uv run --directory SKILL_DIR python scripts/vector_search.py <command> [args]
```

Where `SKILL_DIR` is the directory containing this skill.

### Build the index

```bash
# Index everything (memory + knowledge_graph)
uv run --directory SKILL_DIR python scripts/vector_search.py index

# Index only memory files
uv run --directory SKILL_DIR python scripts/vector_search.py index --scope memory

# Force full re-index (ignore cache)
uv run --directory SKILL_DIR python scripts/vector_search.py index --force
```

Incremental by default — only re-embeds files whose mtime changed. Uses `text-embedding-3-small` at 256 dimensions for a compact index.

### Search

```bash
# Basic semantic search
uv run --directory SKILL_DIR python scripts/vector_search.py search "March Madness modeling approach"

# More results
uv run --directory SKILL_DIR python scripts/vector_search.py search "Board game development" -k 10

# Filter to memory only
uv run --directory SKILL_DIR python scripts/vector_search.py search "tax prep" --scope memory

# Set minimum similarity threshold
uv run --directory SKILL_DIR python scripts/vector_search.py search "pydantic ai tools" --threshold 0.3
```

Returns top-k results ranked by cosine similarity, with file path, score, and text preview.

### Check status

```bash
uv run --directory SKILL_DIR python scripts/vector_search.py status
```

Shows model, dimensions, last indexed time, chunk/file counts, and index file size.

## When to Use

| Need | Tool | Why |
|------|------|-----|
| "What do I know about X?" | `vector_search search` | Finds semantically related content across all files |
| Exact keyword match | `Grep` | Faster, no API call needed |
| Find file by name | `Glob` | Pattern matching, no index needed |
| Browse a specific file | `Read` | Direct access |

## How It Works

1. **Chunking**: Markdown files are split by `##` headers, then by paragraphs if sections are too long (max 2000 chars per chunk)
2. **Embedding**: Each chunk is embedded via OpenAI `text-embedding-3-small` (256 dimensions)
3. **Storage**: Index stored as `.vector_index.json` in the obsidian vault root (dotfile, ignored by obsidian)
4. **Search**: Query is embedded, cosine similarity computed against all indexed chunks, top-k returned

## Maintenance

Re-index periodically or after adding many notes. The index command is incremental — unchanged files are skipped. Use `--force` to rebuild from scratch if the index seems stale.

The index file is gitignored (dotfile). It does not need to be committed or synced.
