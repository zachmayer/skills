"""Tests for the vector search skill.

Uses lazy imports and mocking so tests run without faiss-cpu or
sentence-transformers installed. The script itself uses lazy imports
for heavy deps, so importlib loading works with only click available.
"""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

# Import vector_search.py from the skill directory via importlib.
# Heavy deps (faiss, numpy, sentence_transformers) are lazily imported
# inside wrapper functions, so the module loads with only click.
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
def vault(tmp_path: Path) -> Path:
    """Create a temp vault directory with some markdown files."""
    (tmp_path / "note1.md").write_text("# Note 1\nSome content about machine learning.")
    (tmp_path / "note2.md").write_text("# Note 2\nSome content about cooking recipes.")
    subdir = tmp_path / "memory"
    subdir.mkdir()
    (subdir / "note3.md").write_text("# Note 3\nDaily log entry.")
    return tmp_path


class TestCollectFiles:
    def test_finds_markdown_files(self, vault: Path) -> None:
        files = vs.collect_files(vault)
        assert len(files) == 3
        assert "note1.md" in files
        assert "note2.md" in files
        assert "memory/note3.md" in files

    def test_skips_dotdirs(self, vault: Path) -> None:
        git_dir = vault / ".git"
        git_dir.mkdir()
        (git_dir / "config.md").write_text("git config")
        files = vs.collect_files(vault)
        assert ".git/config.md" not in files

    def test_skips_vector_index_dir(self, vault: Path) -> None:
        idx_dir = vault / ".vector_index"
        idx_dir.mkdir()
        (idx_dir / "cache.md").write_text("cache")
        files = vs.collect_files(vault)
        assert ".vector_index/cache.md" not in files

    def test_empty_vault(self, tmp_path: Path) -> None:
        files = vs.collect_files(tmp_path)
        assert files == {}

    def test_returns_mtimes(self, vault: Path) -> None:
        files = vs.collect_files(vault)
        for mtime in files.values():
            assert isinstance(mtime, float)
            assert mtime > 0


class TestIndexCommand:
    def test_no_files(self, tmp_path: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["index", str(tmp_path)])
        assert result.exit_code == 0
        assert "No markdown files found" in result.output

    def test_builds_index(self, vault: Path) -> None:
        fake_vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        mock_ix = MagicMock()

        with (
            patch.object(vs, "_load_cache", return_value=({}, {})),
            patch.object(vs, "_embed", return_value=fake_vectors),
            patch.object(vs, "_build_faiss_index", return_value=mock_ix),
            patch.object(vs, "_write_faiss_index"),
            patch.object(vs, "_save_embeddings"),
        ):
            result = CliRunner().invoke(vs.cli, ["index", str(vault)])
            assert result.exit_code == 0
            assert "Indexed 3 files" in result.output
            assert "3 embedded" in result.output

        # Verify cache.json was written
        cache_path = vault / ".vector_index" / "cache.json"
        assert cache_path.exists()
        cache = json.loads(cache_path.read_text())
        assert cache["model"] == "all-MiniLM-L6-v2"
        assert len(cache["files"]) == 3

    def test_skips_unchanged_files(self, vault: Path) -> None:
        """When cache mtimes match, files are not re-embedded."""
        current_files = vs.collect_files(vault)
        cached_vectors = {p: [0.1] * 384 for p in current_files}
        cached_mtimes = dict(current_files)

        mock_ix = MagicMock()
        with (
            patch.object(vs, "_load_cache", return_value=(cached_vectors, cached_mtimes)),
            patch.object(vs, "_embed") as embed_mock,
            patch.object(vs, "_build_faiss_index", return_value=mock_ix),
            patch.object(vs, "_write_faiss_index"),
            patch.object(vs, "_save_embeddings"),
        ):
            result = CliRunner().invoke(vs.cli, ["index", str(vault)])
            assert result.exit_code == 0
            assert "All 3 files up to date" in result.output
            # _embed should NOT be called when all files are cached
            embed_mock.assert_not_called()

    def test_force_rebuilds_all(self, vault: Path) -> None:
        """--force flag ignores cache and re-embeds everything."""
        current_files = vs.collect_files(vault)
        cached_vectors = {p: [0.1] * 384 for p in current_files}
        cached_mtimes = dict(current_files)

        fake_vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        mock_ix = MagicMock()

        with (
            patch.object(
                vs, "_load_cache", return_value=(cached_vectors, cached_mtimes)
            ) as load_mock,
            patch.object(vs, "_embed", return_value=fake_vectors),
            patch.object(vs, "_build_faiss_index", return_value=mock_ix),
            patch.object(vs, "_write_faiss_index"),
            patch.object(vs, "_save_embeddings"),
        ):
            result = CliRunner().invoke(vs.cli, ["index", "--force", str(vault)])
            assert result.exit_code == 0
            assert "3 embedded" in result.output
            # _load_cache should NOT be called when --force is used
            load_mock.assert_not_called()

    def test_detects_new_file(self, vault: Path) -> None:
        """Adding a new file triggers re-embedding for that file."""
        cached_vectors = {"note1.md": [0.1] * 384, "note2.md": [0.2] * 384}
        cached_mtimes = {
            "note1.md": (vault / "note1.md").stat().st_mtime,
            "note2.md": (vault / "note2.md").stat().st_mtime,
        }

        fake_new_vector = [[0.3] * 384]
        mock_ix = MagicMock()

        with (
            patch.object(
                vs, "_load_cache", return_value=(cached_vectors, cached_mtimes)
            ),
            patch.object(vs, "_embed", return_value=fake_new_vector) as embed_mock,
            patch.object(vs, "_build_faiss_index", return_value=mock_ix),
            patch.object(vs, "_write_faiss_index"),
            patch.object(vs, "_save_embeddings"),
        ):
            result = CliRunner().invoke(vs.cli, ["index", str(vault)])
            assert result.exit_code == 0
            assert "1 embedded" in result.output
            assert "2 cached" in result.output
            embed_mock.assert_called_once()


class TestSearchCommand:
    def _setup_index(self, vault: Path) -> None:
        """Write a minimal cache.json so search finds an index."""
        index_dir = vault / ".vector_index"
        index_dir.mkdir(exist_ok=True)
        (index_dir / "index.faiss").write_bytes(b"fake")
        cache = {
            "model": "all-MiniLM-L6-v2",
            "dim": 384,
            "files": {
                "note1.md": {"mtime": 1.0, "index": 0},
                "note2.md": {"mtime": 1.0, "index": 1},
                "memory/note3.md": {"mtime": 1.0, "index": 2},
            },
        }
        (index_dir / "cache.json").write_text(json.dumps(cache))

    def test_no_index(self, tmp_path: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["search", str(tmp_path), "query"])
        assert result.exit_code == 1
        assert "No index found" in result.output

    def test_basic_search(self, vault: Path) -> None:
        self._setup_index(vault)

        # Use plain lists — _search_index returns (scores, indices) where
        # each is indexable as result[0] yielding an iterable of values.
        mock_scores = [[0.95, 0.80, 0.60]]
        mock_indices = [[0, 2, 1]]

        with (
            patch.object(vs, "_read_faiss_index", return_value=MagicMock()),
            patch.object(vs, "_encode_query", return_value=MagicMock()),
            patch.object(vs, "_search_index", return_value=(mock_scores, mock_indices)),
        ):
            result = CliRunner().invoke(
                vs.cli, ["search", str(vault), "machine learning"]
            )
            assert result.exit_code == 0
            assert "[0.950] note1.md" in result.output
            assert "[0.800] memory/note3.md" in result.output
            assert "[0.600] note2.md" in result.output

    def test_scope_filter(self, vault: Path) -> None:
        self._setup_index(vault)

        mock_scores = [[0.95, 0.80, 0.60]]
        mock_indices = [[0, 2, 1]]

        with (
            patch.object(vs, "_read_faiss_index", return_value=MagicMock()),
            patch.object(vs, "_encode_query", return_value=MagicMock()),
            patch.object(vs, "_search_index", return_value=(mock_scores, mock_indices)),
        ):
            result = CliRunner().invoke(
                vs.cli,
                ["search", str(vault), "query", "--scope", "memory/"],
            )
            assert result.exit_code == 0
            assert "memory/note3.md" in result.output
            assert "note1.md" not in result.output

    def test_threshold_filters_low_scores(self, vault: Path) -> None:
        self._setup_index(vault)

        mock_scores = [[0.95, 0.30, 0.10]]
        mock_indices = [[0, 1, 2]]

        with (
            patch.object(vs, "_read_faiss_index", return_value=MagicMock()),
            patch.object(vs, "_encode_query", return_value=MagicMock()),
            patch.object(vs, "_search_index", return_value=(mock_scores, mock_indices)),
        ):
            result = CliRunner().invoke(
                vs.cli,
                ["search", str(vault), "query", "--threshold", "0.5"],
            )
            assert result.exit_code == 0
            assert "[0.950] note1.md" in result.output
            assert "note2.md" not in result.output
            assert "memory/note3.md" not in result.output

    def test_threshold_no_results(self, vault: Path) -> None:
        self._setup_index(vault)

        mock_scores = [[0.20, 0.10, 0.05]]
        mock_indices = [[0, 1, 2]]

        with (
            patch.object(vs, "_read_faiss_index", return_value=MagicMock()),
            patch.object(vs, "_encode_query", return_value=MagicMock()),
            patch.object(vs, "_search_index", return_value=(mock_scores, mock_indices)),
        ):
            result = CliRunner().invoke(
                vs.cli,
                ["search", str(vault), "query", "--threshold", "0.9"],
            )
            assert result.exit_code == 0
            assert "No results found" in result.output

    def test_top_k_limits_results(self, vault: Path) -> None:
        self._setup_index(vault)

        mock_scores = [[0.95, 0.80, 0.60]]
        mock_indices = [[0, 1, 2]]

        with (
            patch.object(vs, "_read_faiss_index", return_value=MagicMock()),
            patch.object(vs, "_encode_query", return_value=MagicMock()),
            patch.object(vs, "_search_index", return_value=(mock_scores, mock_indices)),
        ):
            result = CliRunner().invoke(
                vs.cli, ["search", str(vault), "query", "-k", "1"]
            )
            assert result.exit_code == 0
            assert result.output.count("[") == 1


class TestStatusCommand:
    def test_no_index(self, tmp_path: Path) -> None:
        result = CliRunner().invoke(vs.cli, ["status", str(tmp_path)])
        assert result.exit_code == 0
        assert "No index found" in result.output

    def test_all_up_to_date(self, vault: Path) -> None:
        index_dir = vault / ".vector_index"
        index_dir.mkdir()
        current_files = vs.collect_files(vault)
        cache = {
            "model": "all-MiniLM-L6-v2",
            "dim": 384,
            "files": {
                p: {"mtime": m, "index": i}
                for i, (p, m) in enumerate(current_files.items())
            },
        }
        (index_dir / "cache.json").write_text(json.dumps(cache))

        result = CliRunner().invoke(vs.cli, ["status", str(vault)])
        assert result.exit_code == 0
        assert "all-MiniLM-L6-v2" in result.output
        assert "Indexed: 3 files" in result.output
        assert "Vault: 3 files" in result.output
        assert "All files up to date" in result.output

    def test_stale_files(self, vault: Path) -> None:
        index_dir = vault / ".vector_index"
        index_dir.mkdir()
        cache = {
            "model": "all-MiniLM-L6-v2",
            "dim": 384,
            "files": {
                "note1.md": {"mtime": 0.0, "index": 0},
                "note2.md": {"mtime": 0.0, "index": 1},
                "memory/note3.md": {"mtime": 0.0, "index": 2},
            },
        }
        (index_dir / "cache.json").write_text(json.dumps(cache))

        result = CliRunner().invoke(vs.cli, ["status", str(vault)])
        assert result.exit_code == 0
        assert "Need re-index:" in result.output
        assert "3 stale" in result.output

    def test_new_and_removed_files(self, vault: Path) -> None:
        index_dir = vault / ".vector_index"
        index_dir.mkdir()
        cache = {
            "model": "all-MiniLM-L6-v2",
            "dim": 384,
            "files": {
                "old_note.md": {"mtime": 1.0, "index": 0},
            },
        }
        (index_dir / "cache.json").write_text(json.dumps(cache))

        result = CliRunner().invoke(vs.cli, ["status", str(vault)])
        assert result.exit_code == 0
        assert "3 new" in result.output
        assert "1 removed" in result.output
