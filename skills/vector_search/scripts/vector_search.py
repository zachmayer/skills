#!/usr/bin/env python3
"""Semantic vector search over memory and obsidian vault files."""

import json
import math
import os
import time
from pathlib import Path

import click
import openai

OBSIDIAN_DIR = Path(
    os.environ.get("CLAUDE_OBSIDIAN_DIR", str(Path.home() / "claude" / "obsidian"))
).expanduser()
MEMORY_DIR = OBSIDIAN_DIR / "memory"
KNOWLEDGE_DIR = OBSIDIAN_DIR / "knowledge_graph"
INDEX_PATH = OBSIDIAN_DIR / ".vector_index.json"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 256  # reduced dimensions for smaller index, still good quality
MAX_CHUNK_CHARS = 2000
DEFAULT_TOP_K = 5


def _get_client() -> openai.OpenAI:
    """Create OpenAI client. Requires OPENAI_API_KEY env var."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise click.ClickException("OPENAI_API_KEY environment variable not set")
    return openai.OpenAI(api_key=api_key)


def _chunk_markdown(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split markdown into chunks by sections, falling back to paragraphs.

    Tries to split on ## headers first. If a section is still too long,
    splits on paragraphs (double newline). Preserves the header in each chunk.
    """
    chunks: list[str] = []

    # Split on ## headers (keep the header with its content)
    sections = []
    current: list[str] = []
    for line in text.split("\n"):
        if line.startswith("## ") and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))

    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            # Split long sections on paragraphs
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


def _collect_files(scope: str) -> list[Path]:
    """Collect markdown files based on scope: 'all', 'memory', or 'knowledge'."""
    files: list[Path] = []
    if scope in ("all", "memory") and MEMORY_DIR.is_dir():
        files.extend(sorted(MEMORY_DIR.glob("*.md")))
    if scope in ("all", "knowledge") and KNOWLEDGE_DIR.is_dir():
        files.extend(sorted(KNOWLEDGE_DIR.rglob("*.md")))
    return files


def _load_index() -> dict:
    """Load the vector index from disk."""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text())
    return {"model": EMBEDDING_MODEL, "dimensions": EMBEDDING_DIMENSIONS, "entries": []}


def _save_index(index: dict) -> None:
    """Save the vector index to disk."""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index))


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_texts(client: openai.OpenAI, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using OpenAI API. Handles batching."""
    all_embeddings: list[list[float]] = []
    batch_size = 100  # OpenAI supports up to 2048, but keep batches reasonable
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
            dimensions=EMBEDDING_DIMENSIONS,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


@click.group()
def cli() -> None:
    """Semantic vector search over memory and obsidian vault."""


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["all", "memory", "knowledge"]),
    default="all",
    help="Which files to index.",
)
@click.option("--force", is_flag=True, help="Re-index all files, ignoring mtime cache.")
def index(scope: str, force: bool) -> None:
    """Build or update the vector search index.

    Scans memory and knowledge_graph files, chunks them, and generates
    embeddings via OpenAI. Only re-embeds files that changed since last index.
    """
    existing = _load_index()

    # Build mtime lookup from existing index
    existing_lookup: dict[str, dict] = {}
    if not force:
        for entry in existing.get("entries", []):
            key = f"{entry['file']}::{entry['chunk_index']}"
            existing_lookup[key] = entry

    files = _collect_files(scope)
    if not files:
        click.echo("No files found to index.")
        return

    new_entries: list[dict] = []
    files_scanned = 0
    files_embedded = 0
    chunks_to_embed: list[tuple[str, int, str, float]] = []  # file, chunk_idx, text, mtime

    for fpath in files:
        files_scanned += 1
        rel = str(fpath.relative_to(OBSIDIAN_DIR))
        mtime = fpath.stat().st_mtime
        text = fpath.read_text(errors="replace")
        chunks = _chunk_markdown(text)

        file_needs_embed = False
        for ci, chunk in enumerate(chunks):
            key = f"{rel}::{ci}"
            cached = existing_lookup.get(key)
            if cached and cached.get("mtime", 0) >= mtime and cached.get("text") == chunk:
                new_entries.append(cached)
            else:
                file_needs_embed = True
                chunks_to_embed.append((rel, ci, chunk, mtime))

        if file_needs_embed:
            files_embedded += 1

    # Embed all new/changed chunks in batches
    if chunks_to_embed:
        client = _get_client()
        texts = [c[2] for c in chunks_to_embed]
        click.echo(f"Embedding {len(texts)} chunks from {files_embedded} files...")
        embeddings = _embed_texts(client, texts)
        for (rel, ci, chunk, mtime), embedding in zip(chunks_to_embed, embeddings):
            new_entries.append(
                {
                    "file": rel,
                    "chunk_index": ci,
                    "text": chunk,
                    "mtime": mtime,
                    "embedding": embedding,
                }
            )
    else:
        click.echo("All files up to date, nothing to embed.")

    # Sort entries by file and chunk index for deterministic output
    new_entries.sort(key=lambda e: (e["file"], e["chunk_index"]))

    index_data = {
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIMENSIONS,
        "indexed_at": time.time(),
        "entries": new_entries,
    }
    _save_index(index_data)
    click.echo(
        f"Index updated: {len(new_entries)} chunks from {files_scanned} files. "
        f"({files_embedded} files re-embedded)"
    )


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
    index_data = _load_index()
    entries = index_data.get("entries", [])
    if not entries:
        click.echo("Index is empty. Run 'index' first.")
        return

    # Filter by scope
    if scope == "memory":
        entries = [e for e in entries if e["file"].startswith("memory/")]
    elif scope == "knowledge":
        entries = [e for e in entries if e["file"].startswith("knowledge_graph/")]

    if not entries:
        click.echo(f"No indexed entries in scope '{scope}'.")
        return

    client = _get_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
        dimensions=EMBEDDING_DIMENSIONS,
    )
    query_embedding = response.data[0].embedding

    # Score all entries
    scored = []
    for entry in entries:
        sim = _cosine_similarity(query_embedding, entry["embedding"])
        if sim >= threshold:
            scored.append((sim, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = scored[:top_k]

    if not results:
        click.echo("No results above threshold.")
        return

    for i, (score, entry) in enumerate(results, 1):
        click.echo(f"\n--- Result {i} (score: {score:.4f}) ---")
        click.echo(f"File: {entry['file']}")
        # Show a preview of the chunk (first 300 chars)
        preview = entry["text"][:300]
        if len(entry["text"]) > 300:
            preview += "..."
        click.echo(preview)


@cli.command()
def status() -> None:
    """Show index statistics."""
    if not INDEX_PATH.exists():
        click.echo("No index found. Run 'index' to build one.")
        return

    index_data = _load_index()
    entries = index_data.get("entries", [])
    indexed_at = index_data.get("indexed_at", 0)

    # Count files and chunks
    files = set()
    memory_chunks = 0
    knowledge_chunks = 0
    for entry in entries:
        files.add(entry["file"])
        if entry["file"].startswith("memory/"):
            memory_chunks += 1
        elif entry["file"].startswith("knowledge_graph/"):
            knowledge_chunks += 1

    from datetime import datetime

    ts = datetime.fromtimestamp(indexed_at).strftime("%Y-%m-%d %H:%M:%S") if indexed_at else "never"

    click.echo(f"Model: {index_data.get('model', 'unknown')}")
    click.echo(f"Dimensions: {index_data.get('dimensions', 'unknown')}")
    click.echo(f"Last indexed: {ts}")
    click.echo(f"Total chunks: {len(entries)}")
    click.echo(f"Total files: {len(files)}")
    click.echo(f"  Memory chunks: {memory_chunks}")
    click.echo(f"  Knowledge chunks: {knowledge_chunks}")

    # Index file size
    size_mb = INDEX_PATH.stat().st_size / (1024 * 1024)
    click.echo(f"Index size: {size_mb:.2f} MB")


if __name__ == "__main__":
    cli()
