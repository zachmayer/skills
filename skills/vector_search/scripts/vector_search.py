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
from pathlib import Path

import click
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_DIR = ".vector_index"
SKIP_DIRS = {".git", ".vector_index", ".obsidian", "node_modules"}


def collect_files(vault: Path) -> dict[str, float]:
    """Walk vault and return {relative_path: mtime} for all markdown files."""
    files = {}
    for md_file in sorted(vault.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        try:
            rel = str(md_file.relative_to(vault))
            files[rel] = md_file.stat().st_mtime
        except OSError:
            continue
    return files


@click.group()
def cli():
    """Semantic search over markdown files."""


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
def index(vault_path: str):
    """Index all markdown files in VAULT_PATH.

    Embeds whole files (not chunks). Caches embeddings and skips files
    that haven't changed since last index.
    """
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR
    index_dir.mkdir(exist_ok=True)

    current_files = collect_files(vault)
    if not current_files:
        click.echo("No markdown files found.")
        return

    # Load cached embeddings if available
    cache_path = index_dir / "cache.json"
    embeddings_path = index_dir / "embeddings.npy"
    cached_vectors: dict[str, np.ndarray] = {}
    cached_mtimes: dict[str, float] = {}

    if cache_path.exists() and embeddings_path.exists():
        cache = json.loads(cache_path.read_text())
        cached_files = cache.get("files", {})
        all_vectors = np.load(str(embeddings_path))
        cached_order = sorted(cached_files.keys(), key=lambda p: cached_files[p]["index"])
        for i, path in enumerate(cached_order):
            if i < len(all_vectors):
                cached_vectors[path] = all_vectors[i]
                cached_mtimes[path] = cached_files[path].get("mtime", 0)

    # Determine which files need embedding
    to_embed = []
    reused = 0
    for path, mtime in current_files.items():
        if path in cached_vectors and cached_mtimes.get(path, 0) >= mtime:
            reused += 1
            continue
        to_embed.append(path)

    if to_embed:
        click.echo(f"Embedding {len(to_embed)} files ({reused} cached)...")
        model = SentenceTransformer(MODEL_NAME)
        texts = []
        for path in to_embed:
            texts.append((vault / path).read_text(errors="replace"))
        new_vectors = model.encode(
            texts, normalize_embeddings=True, show_progress_bar=len(to_embed) > 10
        )
        for i, path in enumerate(to_embed):
            cached_vectors[path] = new_vectors[i]
    else:
        click.echo(f"All {reused} files up to date.")

    # Build ordered arrays — only include current files
    ordered_paths = sorted(current_files.keys())
    vectors = np.array([cached_vectors[p] for p in ordered_paths], dtype=np.float32)
    vectors = np.ascontiguousarray(vectors)

    dim = vectors.shape[1]
    ix = faiss.IndexFlatIP(dim)  # inner product = cosine sim for normalized vectors
    ix.add(vectors)

    faiss.write_index(ix, str(index_dir / "index.faiss"))
    np.save(str(embeddings_path), vectors)

    new_cache = {
        "model": MODEL_NAME,
        "dim": dim,
        "files": {
            path: {"mtime": current_files[path], "index": i} for i, path in enumerate(ordered_paths)
        },
    }
    (index_dir / "cache.json").write_text(json.dumps(new_cache, indent=2))
    click.echo(f"Indexed {len(ordered_paths)} files ({len(to_embed)} embedded, {reused} cached).")


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
@click.argument("query")
@click.option("-k", "--top-k", default=5, type=int, help="Number of results.")
@click.option("--scope", default=None, help="Filter results to path prefix.")
def search(vault_path: str, query: str, top_k: int, scope: str | None):
    """Search indexed vault for QUERY. Returns matching filenames."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR

    if not (index_dir / "index.faiss").exists():
        click.echo("No index found. Run 'index' first.")
        raise SystemExit(1)

    ix = faiss.read_index(str(index_dir / "index.faiss"))
    cache = json.loads((index_dir / "cache.json").read_text())
    files = cache["files"]
    ordered_paths = sorted(files.keys(), key=lambda p: files[p]["index"])

    model = SentenceTransformer(cache["model"])
    qvec = model.encode([query], normalize_embeddings=True)
    qvec = np.ascontiguousarray(qvec, dtype=np.float32)

    n_search = min(top_k * 5, len(ordered_paths))
    scores, indices = ix.search(qvec, n_search)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        path = ordered_paths[idx]
        if scope and not path.startswith(scope):
            continue
        results.append((float(score), path))
        if len(results) >= top_k:
            break

    if not results:
        click.echo("No results found.")
        return

    for score, path in results:
        click.echo(f"[{score:.3f}] {path}")


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
def status(vault_path: str):
    """Show index status for VAULT_PATH."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR

    if not (index_dir / "cache.json").exists():
        click.echo("No index found. Run 'index' first.")
        return

    cache = json.loads((index_dir / "cache.json").read_text())
    files = cache.get("files", {})
    current_files = collect_files(vault)

    stale = sum(1 for p, m in current_files.items() if p not in files or files[p]["mtime"] < m)
    new = sum(1 for p in current_files if p not in files)
    removed = sum(1 for p in files if p not in current_files)

    click.echo(f"Model: {cache['model']}")
    click.echo(f"Dimensions: {cache.get('dim', 'unknown')}")
    click.echo(f"Indexed: {len(files)} files")
    click.echo(f"Vault: {len(current_files)} files")
    if stale or new or removed:
        click.echo(f"Need re-index: {stale} stale, {new} new, {removed} removed")
    else:
        click.echo("All files up to date.")


if __name__ == "__main__":
    cli()
