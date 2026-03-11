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

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_DIR = ".vector_index"
SKIP_DIRS = {".git", ".vector_index", ".obsidian", "node_modules"}


def collect_files(vault: Path) -> dict[str, float]:
    """Walk vault and return {relative_path: mtime} for all markdown files."""
    files: dict[str, float] = {}
    for md_file in sorted(vault.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        try:
            rel = str(md_file.relative_to(vault))
            files[rel] = md_file.stat().st_mtime
        except OSError:
            continue
    return files


# --- Heavy-dep wrappers (lazy imports, mockable in tests) ---


def _load_numpy() -> object:
    """Lazy import numpy."""
    import numpy as np

    return np


def _embed(texts: list[str]) -> list:
    """Embed texts using sentence-transformers. Returns array of shape (n, dim)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=len(texts) > 10)


def _load_cache(cache_path: Path, embeddings_path: Path) -> tuple[dict, dict]:
    """Load cached vectors and mtimes from disk. Returns (vectors_dict, mtimes_dict)."""
    import numpy as np

    cached_vectors: dict[str, object] = {}
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
    return cached_vectors, cached_mtimes


def _build_faiss_index(vectors_list: list, dim: int) -> object:
    """Build a FAISS IndexFlatIP from a list of vectors. Returns the index."""
    import faiss
    import numpy as np

    vectors = np.array(vectors_list, dtype=np.float32)
    vectors = np.ascontiguousarray(vectors)
    ix = faiss.IndexFlatIP(dim)
    ix.add(vectors)
    return ix


def _write_faiss_index(ix: object, path: str) -> None:
    """Write a FAISS index to disk."""
    import faiss

    faiss.write_index(ix, path)


def _read_faiss_index(path: str) -> object:
    """Read a FAISS index from disk."""
    import faiss

    return faiss.read_index(path)


def _save_embeddings(vectors_list: list, path: str) -> None:
    """Save embedding vectors to a numpy file."""
    import numpy as np

    np.save(path, np.array(vectors_list, dtype=np.float32))


def _encode_query(model_name: str, query: str) -> object:
    """Encode a query string. Returns (n, dim) array."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    qvec = model.encode([query], normalize_embeddings=True)
    return np.ascontiguousarray(qvec, dtype=np.float32)


def _search_index(ix: object, qvec: object, n: int) -> tuple:
    """Search a FAISS index. Returns (scores, indices)."""
    return ix.search(qvec, n)


# --- CLI ---


@click.group()
def cli() -> None:
    """Semantic search over markdown files."""


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="Rebuild entire index, ignoring mtime cache.")
def index(vault_path: str, force: bool) -> None:
    """Index all markdown files in VAULT_PATH.

    Embeds whole files (not chunks). Caches embeddings and skips files
    that haven't changed since last index. Use --force to rebuild from scratch.
    """
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR
    index_dir.mkdir(exist_ok=True)

    current_files = collect_files(vault)
    if not current_files:
        click.echo("No markdown files found.")
        return

    cache_path = index_dir / "cache.json"
    embeddings_path = index_dir / "embeddings.npy"

    # Load cached embeddings unless --force
    if force:
        cached_vectors: dict[str, object] = {}
        cached_mtimes: dict[str, float] = {}
    else:
        cached_vectors, cached_mtimes = _load_cache(cache_path, embeddings_path)

    # Determine which files need embedding
    to_embed: list[str] = []
    reused = 0
    for path, mtime in current_files.items():
        if path in cached_vectors and cached_mtimes.get(path, 0) >= mtime:
            reused += 1
            continue
        to_embed.append(path)

    if to_embed:
        click.echo(f"Embedding {len(to_embed)} files ({reused} cached)...")
        texts = [(vault / path).read_text(errors="replace") for path in to_embed]
        new_vectors = _embed(texts)
        for i, path in enumerate(to_embed):
            cached_vectors[path] = new_vectors[i]
    else:
        click.echo(f"All {reused} files up to date.")

    # Build ordered arrays -- only include current files
    ordered_paths = sorted(current_files.keys())
    vectors_list = [cached_vectors[p] for p in ordered_paths]
    dim = len(vectors_list[0]) if vectors_list else 384

    ix = _build_faiss_index(vectors_list, dim)
    _write_faiss_index(ix, str(index_dir / "index.faiss"))
    _save_embeddings(vectors_list, str(embeddings_path))

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
@click.option("--threshold", default=0.0, type=float, help="Minimum similarity score (0.0-1.0).")
def search(vault_path: str, query: str, top_k: int, scope: str | None, threshold: float) -> None:
    """Search indexed vault for QUERY. Returns matching filenames."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR

    if not (index_dir / "index.faiss").exists():
        click.echo("No index found. Run 'index' first.")
        raise SystemExit(1)

    ix = _read_faiss_index(str(index_dir / "index.faiss"))
    cache = json.loads((index_dir / "cache.json").read_text())
    files = cache["files"]
    ordered_paths = sorted(files.keys(), key=lambda p: files[p]["index"])

    qvec = _encode_query(cache["model"], query)

    n_search = min(top_k * 5, len(ordered_paths))
    scores, indices = _search_index(ix, qvec, n_search)

    results: list[tuple[float, str]] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        similarity = float(score)
        if similarity < threshold:
            continue
        path = ordered_paths[idx]
        if scope and not path.startswith(scope):
            continue
        results.append((similarity, path))
        if len(results) >= top_k:
            break

    if not results:
        click.echo("No results found.")
        return

    for score, path in results:
        click.echo(f"[{score:.3f}] {path}")


@cli.command()
@click.argument("vault_path", type=click.Path(exists=True))
def status(vault_path: str) -> None:
    """Show index status for VAULT_PATH."""
    vault = Path(vault_path)
    index_dir = vault / INDEX_DIR

    if not (index_dir / "cache.json").exists():
        click.echo("No index found. Run 'index' first.")
        return

    cache = json.loads((index_dir / "cache.json").read_text())
    files = cache.get("files", {})
    current_files = collect_files(vault)

    stale = sum(1 for p, m in current_files.items() if p in files and files[p]["mtime"] < m)
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
