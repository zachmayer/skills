"""Tests for the vector search CLI."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Import vector_search.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "vector_search",
    Path(__file__).resolve().parents[2]
    / "skills"
    / "vector_search"
    / "scripts"
    / "vector_search.py",
)
assert _spec is not None and _spec.loader is not None
vs = importlib.util.module_from_spec(_spec)
sys.modules["vector_search"] = vs
_spec.loader.exec_module(vs)


@pytest.fixture()
def obsidian_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up a temp obsidian directory with memory and knowledge_graph subdirs."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    knowledge_dir = tmp_path / "knowledge_graph"
    knowledge_dir.mkdir()
    monkeypatch.setattr(vs, "OBSIDIAN_DIR", tmp_path)
    monkeypatch.setattr(vs, "MEMORY_DIR", memory_dir)
    monkeypatch.setattr(vs, "KNOWLEDGE_DIR", knowledge_dir)
    monkeypatch.setattr(vs, "INDEX_PATH", tmp_path / ".vector_index.json")
    return tmp_path


def _make_embedding(dim: int = 256, seed: float = 0.0) -> list[float]:
    """Create a deterministic fake embedding vector."""
    import math

    return [math.sin(seed + i) for i in range(dim)]


class TestChunkMarkdown:
    def test_empty_text(self) -> None:
        assert vs._chunk_markdown("") == []

    def test_short_text(self) -> None:
        text = "Hello world"
        chunks = vs._chunk_markdown(text)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_splits_on_headers(self) -> None:
        text = "## Section 1\nContent 1\n\n## Section 2\nContent 2"
        chunks = vs._chunk_markdown(text)
        assert len(chunks) == 2
        assert "Section 1" in chunks[0]
        assert "Section 2" in chunks[1]

    def test_preserves_header_in_chunk(self) -> None:
        text = "## My Section\nSome content here"
        chunks = vs._chunk_markdown(text)
        assert len(chunks) == 1
        assert chunks[0].startswith("## My Section")

    def test_splits_long_section_into_paragraphs(self) -> None:
        # Create a section longer than MAX_CHUNK_CHARS
        para = "A" * 800
        text = f"## Big Section\n\n{para}\n\n{para}\n\n{para}\n\n{para}"
        chunks = vs._chunk_markdown(text, max_chars=2000)
        assert len(chunks) > 1

    def test_no_empty_chunks(self) -> None:
        text = "## A\n\n\n\n## B\n\n\n\n## C\nContent"
        chunks = vs._chunk_markdown(text)
        for chunk in chunks:
            assert chunk.strip() != ""

    def test_content_before_first_header(self) -> None:
        text = "Some preamble\n\n## Section\nContent"
        chunks = vs._chunk_markdown(text)
        assert len(chunks) == 2
        assert "preamble" in chunks[0]
        assert "Section" in chunks[1]


class TestCollectFiles:
    def test_all_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "2026-01-01.md").write_text("day note")
        (obsidian_dir / "knowledge_graph" / "test.md").write_text("knowledge")
        files = vs._collect_files("all")
        assert len(files) == 2

    def test_memory_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "2026-01-01.md").write_text("day note")
        (obsidian_dir / "knowledge_graph" / "test.md").write_text("knowledge")
        files = vs._collect_files("memory")
        assert len(files) == 1
        assert "memory" in str(files[0])

    def test_knowledge_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "2026-01-01.md").write_text("day note")
        (obsidian_dir / "knowledge_graph" / "test.md").write_text("knowledge")
        files = vs._collect_files("knowledge")
        assert len(files) == 1
        assert "knowledge_graph" in str(files[0])

    def test_empty_dirs(self, obsidian_dir: Path) -> None:
        files = vs._collect_files("all")
        assert len(files) == 0

    def test_knowledge_rglob(self, obsidian_dir: Path) -> None:
        subdir = obsidian_dir / "knowledge_graph" / "Technical"
        subdir.mkdir()
        (subdir / "note.md").write_text("nested note")
        files = vs._collect_files("knowledge")
        assert len(files) == 1


class TestCosineSimilarity:
    def test_identical_vectors(self) -> None:
        v = [1.0, 2.0, 3.0]
        assert abs(vs._cosine_similarity(v, v) - 1.0) < 1e-10

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(vs._cosine_similarity(a, b)) < 1e-10

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert abs(vs._cosine_similarity(a, b) - (-1.0)) < 1e-10

    def test_zero_vector(self) -> None:
        a = [0.0, 0.0]
        b = [1.0, 2.0]
        assert vs._cosine_similarity(a, b) == 0.0


class TestIndexSaveLoad:
    def test_save_and_load(self, obsidian_dir: Path) -> None:
        index_data = {
            "model": "test-model",
            "dimensions": 3,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "hello",
                    "mtime": 1000.0,
                    "embedding": [1.0, 2.0, 3.0],
                }
            ],
        }
        vs._save_index(index_data)
        loaded = vs._load_index()
        assert loaded["model"] == "test-model"
        assert len(loaded["entries"]) == 1
        assert loaded["entries"][0]["text"] == "hello"

    def test_load_missing_index(self, obsidian_dir: Path) -> None:
        loaded = vs._load_index()
        assert loaded["entries"] == []
        assert loaded["model"] == vs.EMBEDDING_MODEL


class TestIndexCommand:
    def test_index_no_files(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["index"])
        assert result.exit_code == 0
        assert "No files found" in result.output

    @patch.object(vs, "_get_client")
    def test_index_creates_entries(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        # Create a test file
        (obsidian_dir / "memory" / "test.md").write_text("## Hello\nWorld")

        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding()
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["index"])
        assert result.exit_code == 0
        assert "Embedding" in result.output
        assert "Index updated" in result.output

        # Verify index was saved
        index = vs._load_index()
        assert len(index["entries"]) == 1
        assert index["entries"][0]["file"] == "memory/test.md"

    @patch.object(vs, "_get_client")
    def test_index_incremental_skip(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        # Pre-populate index with a matching entry
        fpath = obsidian_dir / "memory" / "test.md"
        fpath.write_text("## Hello\nWorld")
        mtime = fpath.stat().st_mtime

        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "## Hello\nWorld",
                    "mtime": mtime,
                    "embedding": _make_embedding(),
                }
            ],
        }
        vs._save_index(index_data)

        result = CliRunner().invoke(vs.cli, ["index"])
        assert result.exit_code == 0
        assert "nothing to embed" in result.output.lower()
        # Client should not have been called
        mock_get_client.assert_not_called()

    @patch.object(vs, "_get_client")
    def test_index_force_reembeds(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        # Pre-populate index
        fpath = obsidian_dir / "memory" / "test.md"
        fpath.write_text("## Hello\nWorld")
        mtime = fpath.stat().st_mtime

        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "## Hello\nWorld",
                    "mtime": mtime,
                    "embedding": _make_embedding(),
                }
            ],
        }
        vs._save_index(index_data)

        # Mock client for force re-embed
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding(seed=1.0)
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["index", "--force"])
        assert result.exit_code == 0
        assert "Embedding" in result.output

    @patch.object(vs, "_get_client")
    def test_index_scope_memory(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "test.md").write_text("memory note")
        (obsidian_dir / "knowledge_graph" / "test.md").write_text("knowledge note")

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding()
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["index", "--scope", "memory"])
        assert result.exit_code == 0

        index = vs._load_index()
        # Should only have memory entries
        for entry in index["entries"]:
            assert entry["file"].startswith("memory/")


class TestSearchCommand:
    def test_search_empty_index(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["search", "test query"])
        assert result.exit_code == 0
        assert "empty" in result.output.lower()

    @patch.object(vs, "_get_client")
    def test_search_returns_results(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        # Pre-populate index
        emb1 = _make_embedding(seed=0.0)
        emb2 = _make_embedding(seed=5.0)
        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": [
                {
                    "file": "memory/2026-01-01.md",
                    "chunk_index": 0,
                    "text": "March Madness basketball predictions",
                    "mtime": 1000.0,
                    "embedding": emb1,
                },
                {
                    "file": "knowledge_graph/Tax.md",
                    "chunk_index": 0,
                    "text": "Tax preparation notes for 2025",
                    "mtime": 1000.0,
                    "embedding": emb2,
                },
            ],
        }
        vs._save_index(index_data)

        # Mock query embedding (similar to emb1)
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding(seed=0.1)  # close to emb1
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["search", "basketball"])
        assert result.exit_code == 0
        assert "Result 1" in result.output
        assert "score:" in result.output

    @patch.object(vs, "_get_client")
    def test_search_scope_filter(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        emb1 = _make_embedding(seed=0.0)
        emb2 = _make_embedding(seed=0.0)  # same embedding, different scope
        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "memory content",
                    "mtime": 1000.0,
                    "embedding": emb1,
                },
                {
                    "file": "knowledge_graph/test.md",
                    "chunk_index": 0,
                    "text": "knowledge content",
                    "mtime": 1000.0,
                    "embedding": emb2,
                },
            ],
        }
        vs._save_index(index_data)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding(seed=0.0)
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["search", "test", "--scope", "knowledge"])
        assert result.exit_code == 0
        assert "knowledge_graph" in result.output
        assert "memory/" not in result.output

    @patch.object(vs, "_get_client")
    def test_search_top_k(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        entries = []
        for i in range(10):
            entries.append(
                {
                    "file": f"memory/note{i}.md",
                    "chunk_index": 0,
                    "text": f"Note {i} content",
                    "mtime": 1000.0,
                    "embedding": _make_embedding(seed=float(i)),
                }
            )
        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": entries,
        }
        vs._save_index(index_data)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding(seed=0.0)
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["search", "test", "-k", "3"])
        assert result.exit_code == 0
        assert "Result 3" in result.output
        assert "Result 4" not in result.output

    @patch.object(vs, "_get_client")
    def test_search_threshold(self, mock_get_client: MagicMock, obsidian_dir: Path) -> None:
        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "test content",
                    "mtime": 1000.0,
                    "embedding": _make_embedding(seed=100.0),  # very different
                }
            ],
        }
        vs._save_index(index_data)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_embedding = MagicMock()
        mock_embedding.embedding = _make_embedding(seed=0.0)
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        result = CliRunner().invoke(vs.cli, ["search", "test", "--threshold", "0.99"])
        assert result.exit_code == 0
        assert "No results above threshold" in result.output


class TestStatusCommand:
    def test_status_no_index(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["status"])
        assert result.exit_code == 0
        assert "No index found" in result.output

    def test_status_with_index(self, obsidian_dir: Path) -> None:
        index_data = {
            "model": vs.EMBEDDING_MODEL,
            "dimensions": vs.EMBEDDING_DIMENSIONS,
            "indexed_at": 1700000000.0,
            "entries": [
                {
                    "file": "memory/test.md",
                    "chunk_index": 0,
                    "text": "hello",
                    "mtime": 1000.0,
                    "embedding": [1.0, 2.0, 3.0],
                },
                {
                    "file": "knowledge_graph/note.md",
                    "chunk_index": 0,
                    "text": "world",
                    "mtime": 1000.0,
                    "embedding": [4.0, 5.0, 6.0],
                },
            ],
        }
        vs._save_index(index_data)

        result = CliRunner().invoke(vs.cli, ["status"])
        assert result.exit_code == 0
        assert "Total chunks: 2" in result.output
        assert "Total files: 2" in result.output
        assert "Memory chunks: 1" in result.output
        assert "Knowledge chunks: 1" in result.output
        assert "MB" in result.output


class TestEmbedTexts:
    @patch.object(vs, "_get_client")
    def test_single_batch(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        emb1 = MagicMock()
        emb1.embedding = [1.0, 2.0]
        emb2 = MagicMock()
        emb2.embedding = [3.0, 4.0]
        mock_response = MagicMock()
        mock_response.data = [emb1, emb2]
        mock_client.embeddings.create.return_value = mock_response

        result = vs._embed_texts(mock_client, ["hello", "world"])
        assert len(result) == 2
        assert result[0] == [1.0, 2.0]
        assert result[1] == [3.0, 4.0]


class TestGetClient:
    def test_missing_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(Exception, match="OPENAI_API_KEY"):
            vs._get_client()
