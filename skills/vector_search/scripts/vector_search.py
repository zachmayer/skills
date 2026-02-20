#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.3.0",
#     "sentence-transformers>=3.0.0",
#     "faiss-cpu>=1.9.0",
#     "numpy>=1.24.0",
# ]
# ///
"""Semantic search over markdown files using local embeddings and FAISS."""

import json
import re
from pathlib import Path

import click
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_DIR = ".vector_index"
SKIP_DIRS = {".git", ".vector_index", ".obsidian", "node_modules"}


def chunk_file(text: str, file_path: str) -> list[dict]:
    """Split markdown into chunks by ## headers."""
    parts = re.split(r"^(## .+)$", text, flags=re.MULTILINE)
    chunks = []

    # Content before first ## header
    if parts[0].strip():
        chunks.append({"file": file_path, "heading": "", "text": parts[0].strip()})

    # Pairs of (header, content)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if content:
            chunks.append({"file": file_path, "heading": heading, "text": f"{heading}\n{content}"})

    # File with no ## headers and no content captured above
    if not chunks and text.strip():
        chunks.append({"file": file_path, "heading": "", "text": text.strip()})

    return chunks


def collect_chunks(vault: Path) -> list[dict]:
    """Walk vault and chunk all markdown files."""
    chunks = []
    for md_file in sorted(vault.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        try:
            text = md_file.read_text(errors="replace")
        except OSError:
            continue
        rel = str(md_file.relative_to(vault))
        chunks.extend(chunk_file(text, rel))
    return chunks


@click.group()
def cli():
    """Semantic search over markdown files."""


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
def index(vault_path: str):
    """Index all markdown files in VAULT_PATH."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR
    index_dir.mkdir(exist_ok=True)

    chunks = collect_chunks(vault)
    if not chunks:
        click.echo("No markdown content found.")
        return

    click.echo(f"Embedding {len(chunks)} chunks...")
    model = SentenceTransformer(MODEL_NAME)
    vectors = model.encode(
        [c["text"] for c in chunks],
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    vectors = np.ascontiguousarray(vectors, dtype=np.float32)

    dim = vectors.shape[1]
    ix = faiss.IndexHNSWFlat(dim, 32)
    ix.add(vectors)

    faiss.write_index(ix, str(index_dir / "index.faiss"))
    meta = {
        "model": MODEL_NAME,
        "dim": dim,
        "count": len(chunks),
        "chunks": [
            {"file": c["file"], "heading": c["heading"], "preview": c["text"][:500]} for c in chunks
        ],
    }
    (index_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

    n_files = len({c["file"] for c in chunks})
    click.echo(f"Indexed {len(chunks)} chunks from {n_files} files.")


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
@click.argument("query")
@click.option("-k", "--top-k", default=5, type=int, help="Number of results.")
@click.option("--scope", default=None, help="Filter results to path prefix.")
def search(vault_path: str, query: str, top_k: int, scope: str | None):
    """Search indexed vault for QUERY."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR

    if not (index_dir / "index.faiss").exists():
        click.echo("No index found. Run 'index' first.")
        raise SystemExit(1)

    ix = faiss.read_index(str(index_dir / "index.faiss"))
    meta = json.loads((index_dir / "metadata.json").read_text())
    chunks = meta["chunks"]

    model = SentenceTransformer(meta["model"])
    qvec = model.encode([query], normalize_embeddings=True)
    qvec = np.ascontiguousarray(qvec, dtype=np.float32)

    # Over-fetch to allow for scope filtering
    n_search = min(top_k * 5, len(chunks))
    distances, indices = ix.search(qvec, n_search)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx]
        if scope and not chunk["file"].startswith(scope):
            continue
        # L2² to cosine similarity for normalized vectors
        sim = 1.0 - float(dist) / 2.0
        results.append((sim, chunk))
        if len(results) >= top_k:
            break

    if not results:
        click.echo("No results found.")
        return

    for sim, chunk in results:
        label = chunk["file"]
        if chunk["heading"]:
            label += f" > {chunk['heading']}"
        click.echo(f"\n[{sim:.3f}] {label}")
        click.echo(chunk["preview"][:200])


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
def status(vault_path: str):
    """Show index status for VAULT_PATH."""
    vault = Path(vault_path)
    meta_path = vault / INDEX_DIR / "metadata.json"

    if not meta_path.exists():
        click.echo("No index found. Run 'index' first.")
        return

    meta = json.loads(meta_path.read_text())
    n_files = len({c["file"] for c in meta["chunks"]})
    click.echo(f"Model: {meta['model']}")
    click.echo(f"Dimensions: {meta['dim']}")
    click.echo(f"Chunks: {meta['count']}")
    click.echo(f"Files: {n_files}")


if __name__ == "__main__":
    cli()
