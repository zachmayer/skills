"""Tests for the vector search skill."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Import vector_search.py from the skill directory.
# Heavy deps (sentence_transformers, usearch, numpy) are lazily imported
# inside functions, so the module loads without them.
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
    monkeypatch.setattr(vs, "INDEX_PATH", tmp_path / ".vector_search.usearch")
    monkeypatch.setattr(vs, "META_PATH", tmp_path / ".vector_search_meta.json")
    return tmp_path


class TestChunkMarkdown:
    def test_short_text(self) -> None:
        assert vs.chunk_markdown("Hello world") == ["Hello world"]

    def test_sections(self) -> None:
        text = "## Section 1\nContent 1\n## Section 2\nContent 2"
        chunks = vs.chunk_markdown(text)
        assert len(chunks) == 2
        assert "Section 1" in chunks[0]
        assert "Section 2" in chunks[1]

    def test_preamble_before_first_header(self) -> None:
        text = "Preamble text\n## Section\nContent"
        chunks = vs.chunk_markdown(text)
        assert len(chunks) == 2
        assert "Preamble" in chunks[0]
        assert "Section" in chunks[1]

    def test_long_section_splits_on_paragraphs(self) -> None:
        long_section = "## Long\n\n" + "word " * 500 + "\n\n" + "more " * 500
        chunks = vs.chunk_markdown(long_section, max_chars=1000)
        assert len(chunks) >= 2

    def test_empty_text(self) -> None:
        assert vs.chunk_markdown("") == []

    def test_whitespace_only(self) -> None:
        assert vs.chunk_markdown("   \n\n   ") == []


class TestCollectFiles:
    def test_all_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "note.md").write_text("mem")
        (obsidian_dir / "knowledge_graph" / "topic.md").write_text("kg")
        files = vs.collect_files("all")
        assert len(files) == 2

    def test_memory_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "note.md").write_text("mem")
        (obsidian_dir / "knowledge_graph" / "topic.md").write_text("kg")
        files = vs.collect_files("memory")
        assert len(files) == 1
        assert "memory" in str(files[0])

    def test_knowledge_scope(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "note.md").write_text("mem")
        (obsidian_dir / "knowledge_graph" / "topic.md").write_text("kg")
        files = vs.collect_files("knowledge")
        assert len(files) == 1
        assert "knowledge_graph" in str(files[0])

    def test_missing_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(vs, "MEMORY_DIR", tmp_path / "nonexistent")
        monkeypatch.setattr(vs, "KNOWLEDGE_DIR", tmp_path / "also_nonexistent")
        assert vs.collect_files("all") == []

    def test_nested_knowledge_files(self, obsidian_dir: Path) -> None:
        subdir = obsidian_dir / "knowledge_graph" / "Technical"
        subdir.mkdir()
        (subdir / "deep_note.md").write_text("deep")
        files = vs.collect_files("knowledge")
        assert len(files) == 1
        assert "deep_note.md" in str(files[0])


class TestIndexCommand:
    def test_no_files(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["index"])
        assert result.exit_code == 0
        assert "No files found" in result.output

    def test_builds_index(self, obsidian_dir: Path) -> None:
        (obsidian_dir / "memory" / "note.md").write_text("# Test\nSome content here")
        mock_embeddings = [[0.1] * vs.NDIM]
        mock_index = MagicMock()

        with (
            patch.object(vs, "_embed", return_value=mock_embeddings),
            patch.object(vs, "_build_usearch", return_value=mock_index),
        ):
            result = CliRunner().invoke(vs.cli, ["index"])
            assert result.exit_code == 0
            assert "Index built" in result.output
            mock_index.save.assert_called_once()

        # Verify metadata was saved
        assert vs.META_PATH.exists()
        meta = json.loads(vs.META_PATH.read_text())
        assert len(meta["entries"]) == 1
        assert meta["model"] == vs.MODEL_NAME

    def test_skips_unchanged(self, obsidian_dir: Path) -> None:
        note = obsidian_dir / "memory" / "note.md"
        note.write_text("content")
        mtime = note.stat().st_mtime

        vs.save_meta(
            {
                "model": vs.MODEL_NAME,
                "dimensions": vs.NDIM,
                "indexed_at": 1234567890.0,
                "file_mtimes": {"memory/note.md": mtime},
                "entries": {"0": {"file": "memory/note.md", "chunk_index": 0, "text": "content"}},
            }
        )

        result = CliRunner().invoke(vs.cli, ["index"])
        assert result.exit_code == 0
        assert "up to date" in result.output

    def test_force_rebuilds(self, obsidian_dir: Path) -> None:
        note = obsidian_dir / "memory" / "note.md"
        note.write_text("content")
        mtime = note.stat().st_mtime

        vs.save_meta(
            {
                "file_mtimes": {"memory/note.md": mtime},
                "entries": {"0": {"file": "memory/note.md", "chunk_index": 0, "text": "content"}},
            }
        )

        mock_index = MagicMock()
        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM]),
            patch.object(vs, "_build_usearch", return_value=mock_index),
        ):
            result = CliRunner().invoke(vs.cli, ["index", "--force"])
            assert result.exit_code == 0
            assert "Index built" in result.output

    def test_detects_new_file(self, obsidian_dir: Path) -> None:
        """Adding a new file triggers re-index even if existing files unchanged."""
        note1 = obsidian_dir / "memory" / "note1.md"
        note1.write_text("first")
        vs.save_meta(
            {
                "file_mtimes": {"memory/note1.md": note1.stat().st_mtime},
                "entries": {"0": {"file": "memory/note1.md", "chunk_index": 0, "text": "first"}},
            }
        )

        (obsidian_dir / "memory" / "note2.md").write_text("second")
        mock_index = MagicMock()
        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM, [0.2] * vs.NDIM]),
            patch.object(vs, "_build_usearch", return_value=mock_index),
        ):
            result = CliRunner().invoke(vs.cli, ["index"])
            assert result.exit_code == 0
            assert "Index built" in result.output


class TestSearchCommand:
    def test_no_index(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["search", "test query"])
        assert result.exit_code == 0
        assert "No index found" in result.output

    def test_basic_search(self, obsidian_dir: Path) -> None:
        (obsidian_dir / ".vector_search.usearch").write_bytes(b"fake")
        vs.save_meta(
            {
                "entries": {
                    "0": {"file": "memory/note.md", "chunk_index": 0, "text": "About ML"},
                    "1": {"file": "knowledge_graph/ai.md", "chunk_index": 0, "text": "AI notes"},
                },
            }
        )

        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM]),
            patch.object(vs, "_query_usearch", return_value=[(0, 0.2), (1, 0.5)]),
        ):
            result = CliRunner().invoke(vs.cli, ["search", "machine learning"])
            assert result.exit_code == 0
            assert "score: 0.8000" in result.output
            assert "memory/note.md" in result.output

    def test_scope_filter(self, obsidian_dir: Path) -> None:
        (obsidian_dir / ".vector_search.usearch").write_bytes(b"fake")
        vs.save_meta(
            {
                "entries": {
                    "0": {"file": "memory/note.md", "chunk_index": 0, "text": "Memory note"},
                    "1": {"file": "knowledge_graph/kg.md", "chunk_index": 0, "text": "KG note"},
                },
            }
        )

        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM]),
            patch.object(vs, "_query_usearch", return_value=[(1, 0.1), (0, 0.3)]),
        ):
            result = CliRunner().invoke(vs.cli, ["search", "test", "--scope", "memory"])
            assert result.exit_code == 0
            assert "memory/note.md" in result.output
            assert "knowledge_graph" not in result.output

    def test_threshold_filter(self, obsidian_dir: Path) -> None:
        (obsidian_dir / ".vector_search.usearch").write_bytes(b"fake")
        vs.save_meta(
            {
                "entries": {
                    "0": {"file": "memory/note.md", "chunk_index": 0, "text": "Note"},
                },
            }
        )

        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM]),
            patch.object(vs, "_query_usearch", return_value=[(0, 0.9)]),
        ):
            result = CliRunner().invoke(vs.cli, ["search", "test", "--threshold", "0.5"])
            assert result.exit_code == 0
            assert "No results above threshold" in result.output

    def test_preview_truncation(self, obsidian_dir: Path) -> None:
        (obsidian_dir / ".vector_search.usearch").write_bytes(b"fake")
        long_text = "x" * 500
        vs.save_meta(
            {
                "entries": {
                    "0": {"file": "memory/note.md", "chunk_index": 0, "text": long_text},
                },
            }
        )

        with (
            patch.object(vs, "_embed", return_value=[[0.1] * vs.NDIM]),
            patch.object(vs, "_query_usearch", return_value=[(0, 0.1)]),
        ):
            result = CliRunner().invoke(vs.cli, ["search", "test"])
            assert result.exit_code == 0
            assert "..." in result.output


class TestStatusCommand:
    def test_no_index(self, obsidian_dir: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["status"])
        assert result.exit_code == 0
        assert "No index found" in result.output

    def test_with_index(self, obsidian_dir: Path) -> None:
        index_path = obsidian_dir / ".vector_search.usearch"
        index_path.write_bytes(b"x" * 1024)
        vs.save_meta(
            {
                "model": "all-MiniLM-L6-v2",
                "dimensions": 384,
                "indexed_at": 1709164800.0,
                "entries": {
                    "0": {"file": "memory/note.md", "chunk_index": 0, "text": "test"},
                    "1": {"file": "knowledge_graph/kg.md", "chunk_index": 0, "text": "test"},
                },
            }
        )

        result = CliRunner().invoke(vs.cli, ["status"])
        assert result.exit_code == 0
        assert "all-MiniLM-L6-v2" in result.output
        assert "Total chunks: 2" in result.output
        assert "Total files: 2" in result.output
        assert "Memory chunks: 1" in result.output
        assert "Knowledge chunks: 1" in result.output
        assert "1.0 KB" in result.output
