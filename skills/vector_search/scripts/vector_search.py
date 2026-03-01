#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click>=8.3.0",
#     "sentence-transformers>=3.0.0",
#     "usearch>=2.12.0",
#     "numpy>=1.26.0",
# ]
# ///
"""Semantic vector search over memory and obsidian vault."""

import json
import os
import time
from pathlib import Path

import click

# --- Configuration ---

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
MEMORY_DIR = OBSIDIAN_DIR / "memory"
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"
INDEX_PATH = OBSIDIAN_DIR / ".vector_search.usearch"
META_PATH = OBSIDIAN_DIR / ".vector_search_meta.json"

MODEL_NAME = "all-MiniLM-L6-v2"
NDIM = 384
MAX_CHUNK_CHARS = 2000
DEFAULT_TOP_K = 5


# --- Pure functions ---


def chunk_markdown(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split markdown by ## headers, then by paragraphs if sections are too long."""
    sections: list[str] = []
    current: list[str] = []
    for line in text.split("\n"):
        if line.startswith("## ") and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))

    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            paragraphs = section.split("\n\n")
            current_chunk: list[str] = []
            current_len = 0
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if current_len + len(para) + 2 > max_chars and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [para]
                    current_len = len(para)
                else:
                    current_chunk.append(para)
                    current_len += len(para) + 2
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

    return [c for c in chunks if c.strip()]


def collect_files(scope: str) -> list[Path]:
    """Collect markdown files by scope: 'all', 'memory', or 'knowledge'."""
    files: list[Path] = []
    if scope in ("all", "memory") and MEMORY_DIR.is_dir():
        files.extend(sorted(MEMORY_DIR.glob("*.md")))
    if scope in ("all", "knowledge") and KNOWLEDGE_DIR.is_dir():
        files.extend(sorted(KNOWLEDGE_DIR.rglob("*.md")))
    return files


def load_meta() -> dict:
    """Load metadata sidecar from disk."""
    if META_PATH.exists():
        return json.loads(META_PATH.read_text())
    return {}


def save_meta(meta: dict) -> None:
    """Save metadata sidecar to disk."""
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(meta))


# --- Heavy-dep wrappers (lazy imports, mockable in tests) ---


def _embed(texts: list[str]) -> list:
    """Embed texts using sentence-transformers. Returns array of shape (n, NDIM)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)


def _build_usearch(embeddings) -> object:
    """Build a usearch HNSW index from embeddings. Returns the index object."""
    import numpy as np
    from usearch.index import Index

    idx = Index(ndim=NDIM, metric="cos", dtype="f32")
    for i in range(len(embeddings)):
        idx.add(i, np.array(embeddings[i], dtype=np.float32))
    return idx


def _query_usearch(index_path: Path, query_emb, k: int) -> list[tuple[int, float]]:
    """Query a usearch index. Returns [(key, distance), ...] sorted by distance."""
    import numpy as np
    from usearch.index import Index

    idx = Index.restore(str(index_path), view=True)
    matches = idx.search(np.array(query_emb, dtype=np.float32), k)
    return [(int(key), float(dist)) for key, dist in zip(matches.keys, matches.distances)]


# --- CLI ---


@click.group()
def cli() -> None:
    """Semantic vector search over memory and obsidian vault."""


@cli.command()
@click.option("--force", is_flag=True, help="Rebuild index from scratch.")
def index(force: bool) -> None:
    """Build or update the vector search index."""
    files = collect_files("all")
    if not files:
        click.echo("No files found to index.")
        return

    # Check if anything changed since last index
    meta = load_meta() if not force else {}
    file_mtimes = meta.get("file_mtimes", {})
    current_mtimes: dict[str, float] = {}
    changed = force
    for fpath in files:
        rel = str(fpath.relative_to(OBSIDIAN_DIR))
        current_mtimes[rel] = fpath.stat().st_mtime
        if rel not in file_mtimes or file_mtimes[rel] != current_mtimes[rel]:
            changed = True
    if set(file_mtimes.keys()) != set(current_mtimes.keys()):
        changed = True

    if not changed:
        click.echo("All files up to date, nothing to re-index.")
        return

    # Chunk all files
    entries: list[dict] = []
    for fpath in files:
        rel = str(fpath.relative_to(OBSIDIAN_DIR))
        text = fpath.read_text(errors="replace")
        for ci, chunk in enumerate(chunk_markdown(text)):
            entries.append({"file": rel, "chunk_index": ci, "text": chunk})

    if not entries:
        click.echo("No content to index.")
        return

    # Embed and build index
    texts = [e["text"] for e in entries]
    click.echo(f"Embedding {len(texts)} chunks from {len(files)} files...")
    embeddings = _embed(texts)

    click.echo("Building search index...")
    idx = _build_usearch(embeddings)
    idx.save(str(INDEX_PATH))

    save_meta(
        {
            "model": MODEL_NAME,
            "dimensions": NDIM,
            "indexed_at": time.time(),
            "file_mtimes": current_mtimes,
            "entries": {
                str(i): {"file": e["file"], "chunk_index": e["chunk_index"], "text": e["text"]}
                for i, e in enumerate(entries)
            },
        }
    )

    click.echo(f"Index built: {len(entries)} chunks from {len(files)} files.")


@cli.command()
@click.argument("query")
@click.option("-k", "--top-k", default=DEFAULT_TOP_K, help="Number of results to return.")
@click.option(
    "--scope",
    type=click.Choice(["all", "memory", "knowledge"]),
    default="all",
    help="Filter results by scope.",
)
@click.option("--threshold", type=float, default=0.0, help="Minimum similarity score.")
def search(query: str, top_k: int, scope: str, threshold: float) -> None:
    """Search the index semantically. Returns top-k most similar chunks."""
    if not INDEX_PATH.exists() or not META_PATH.exists():
        click.echo("No index found. Run 'index' first.")
        return

    meta = load_meta()
    entries = meta.get("entries", {})
    if not entries:
        click.echo("Index is empty. Run 'index' first.")
        return

    # Embed query
    query_emb = _embed([query])[0]

    # Search with extra candidates to compensate for post-filtering
    search_k = min(len(entries), top_k * 10)
    matches = _query_usearch(INDEX_PATH, query_emb, search_k)

    # Filter by scope and threshold
    results: list[tuple[float, dict]] = []
    for key, distance in matches:
        entry = entries.get(str(key))
        if entry is None:
            continue
        similarity = 1.0 - distance
        if similarity < threshold:
            continue
        if scope == "memory" and not entry["file"].startswith("memory/"):
            continue
        if scope == "knowledge" and not entry["file"].startswith("knowledge_graph/"):
            continue
        results.append((similarity, entry))
        if len(results) >= top_k:
            break

    if not results:
        click.echo("No results above threshold.")
        return

    for i, (score, entry) in enumerate(results, 1):
        click.echo(f"\n--- Result {i} (score: {score:.4f}) ---")
        click.echo(f"File: {entry['file']}")
        preview = entry["text"][:300]
        if len(entry["text"]) > 300:
            preview += "..."
        click.echo(preview)


@cli.command()
def status() -> None:
    """Show index statistics."""
    if not META_PATH.exists():
        click.echo("No index found. Run 'index' to build one.")
        return

    meta = load_meta()
    entries = meta.get("entries", {})
    indexed_at = meta.get("indexed_at", 0)

    files: set[str] = set()
    memory_chunks = 0
    knowledge_chunks = 0
    for entry in entries.values():
        files.add(entry["file"])
        if entry["file"].startswith("memory/"):
            memory_chunks += 1
        elif entry["file"].startswith("knowledge_graph/"):
            knowledge_chunks += 1

    from datetime import datetime

    ts = datetime.fromtimestamp(indexed_at).strftime("%Y-%m-%d %H:%M:%S") if indexed_at else "never"

    click.echo(f"Model: {meta.get('model', 'unknown')}")
    click.echo(f"Dimensions: {meta.get('dimensions', 'unknown')}")
    click.echo(f"Last indexed: {ts}")
    click.echo(f"Total chunks: {len(entries)}")
    click.echo(f"Total files: {len(files)}")
    click.echo(f"  Memory chunks: {memory_chunks}")
    click.echo(f"  Knowledge chunks: {knowledge_chunks}")

    if INDEX_PATH.exists():
        size_kb = INDEX_PATH.stat().st_size / 1024
        click.echo(f"Index size: {size_kb:.1f} KB")


if __name__ == "__main__":
    cli()
