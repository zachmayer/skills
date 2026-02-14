"""Tests for the evergreen maintenance CLI."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import evergreen.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "evergreen",
    Path(__file__).resolve().parents[2] / "skills" / "evergreen" / "scripts" / "evergreen.py",
)
assert _spec is not None and _spec.loader is not None
evergreen = importlib.util.module_from_spec(_spec)
sys.modules["evergreen"] = evergreen
_spec.loader.exec_module(evergreen)


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    """Create a minimal obsidian vault structure."""
    kg = tmp_path / "knowledge_graph"
    kg.mkdir()
    mem = tmp_path / "memory"
    mem.mkdir()
    return tmp_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# extract_wikilinks
# ---------------------------------------------------------------------------


class TestExtractWikilinks:
    def test_basic_link(self) -> None:
        assert evergreen._extract_wikilinks("See [[Foo Bar]]") == {"Foo Bar"}

    def test_aliased_link(self) -> None:
        assert evergreen._extract_wikilinks("See [[Foo|display text]]") == {"Foo"}

    def test_multiple_links(self) -> None:
        links = evergreen._extract_wikilinks("[[A]] and [[B]] and [[C]]")
        assert links == {"A", "B", "C"}

    def test_no_links(self) -> None:
        assert evergreen._extract_wikilinks("plain text") == set()

    def test_empty_string(self) -> None:
        assert evergreen._extract_wikilinks("") == set()


# ---------------------------------------------------------------------------
# note_title
# ---------------------------------------------------------------------------


class TestNoteTitle:
    def test_basic(self) -> None:
        assert evergreen._note_title(Path("/foo/bar/My Note.md")) == "My Note"

    def test_nested(self) -> None:
        assert evergreen._note_title(Path("/a/b/c.md")) == "c"


# ---------------------------------------------------------------------------
# Knowledge maintenance
# ---------------------------------------------------------------------------


class TestKnowledgeMaintenance:
    def test_finds_orphan_notes(self, vault: Path, runner: CliRunner) -> None:
        kg = vault / "knowledge_graph"
        # Hub links to A but not B
        (kg / "Hub.md").write_text("# Hub\nSource: test\nDate: 2026-01-01\n\n[[A]]\n")
        (kg / "A.md").write_text("# A\nSource: test\nDate: 2026-01-01\n\nLinked from hub\n")
        (kg / "B.md").write_text("# B\nSource: test\nDate: 2026-01-01\n\nOrphan!\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "B" in result.output
        # Hub is also orphan (nothing links to it) — that's expected for top-level MOCs
        assert "orphans" in result.output.lower() or "Orphan" in result.output

    def test_finds_broken_links(self, vault: Path, runner: CliRunner) -> None:
        kg = vault / "knowledge_graph"
        (kg / "Note.md").write_text("# Note\nSource: test\nDate: 2026-01-01\n\n[[Nonexistent]]\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "Nonexistent" in result.output

    def test_finds_duplicate_names(self, vault: Path, runner: CliRunner) -> None:
        kg = vault / "knowledge_graph"
        sub1 = kg / "subdir1"
        sub2 = kg / "subdir2"
        sub1.mkdir()
        sub2.mkdir()
        (sub1 / "Same.md").write_text("# Same\nSource: test\nDate: 2026-01-01\n")
        (sub2 / "Same.md").write_text("# Same\nSource: test\nDate: 2026-01-01\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "Duplicate" in result.output
        assert "Same" in result.output

    def test_finds_missing_metadata(self, vault: Path, runner: CliRunner) -> None:
        kg = vault / "knowledge_graph"
        (kg / "NoMeta.md").write_text("# No Metadata\n\nJust content.\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "NoMeta" in result.output
        assert "Missing Source" in result.output
        assert "Missing Date" in result.output

    def test_no_false_positive_on_good_metadata(self, vault: Path, runner: CliRunner) -> None:
        kg = vault / "knowledge_graph"
        (kg / "Good.md").write_text("# Good\nSource: https://example.com\nDate: 2026-01-01\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "Missing Source metadata: 0" in result.output
        assert "Missing Date metadata: 0" in result.output

    def test_empty_vault(self, vault: Path, runner: CliRunner) -> None:
        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "No markdown files" in result.output

    def test_missing_knowledge_graph(self, tmp_path: Path, runner: CliRunner) -> None:
        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(tmp_path)])
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_wikilinks_to_memory_not_broken(self, vault: Path, runner: CliRunner) -> None:
        """Links to memory files should not show as broken."""
        kg = vault / "knowledge_graph"
        mem = vault / "memory"
        (kg / "Note.md").write_text("# Note\nSource: test\nDate: 2026-01-01\n\n[[2026-02]]\n")
        (mem / "2026-02.md").write_text("# February\n")

        result = runner.invoke(evergreen.cli, ["knowledge", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "Broken wikilinks: 0" in result.output


# ---------------------------------------------------------------------------
# Memory maintenance
# ---------------------------------------------------------------------------


class TestMemoryMaintenance:
    def test_finds_duplicates(self, vault: Path, runner: CliRunner) -> None:
        mem = vault / "memory"
        (mem / "2026-02-13.md").write_text(
            "# Notes for 2026-02-13\n\n- **2026-02-13T10:00:00** [ctx]: DONE: Fixed the bug\n"
        )
        (mem / "2026-02-14.md").write_text(
            "# Notes for 2026-02-14\n\n- **2026-02-14T08:00:00** [ctx]: DONE: Fixed the bug\n"
        )

        result = runner.invoke(evergreen.cli, ["memory", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "1" in result.output  # 1 duplicate
        assert "fixed the bug" in result.output.lower()

    def test_no_duplicates(self, vault: Path, runner: CliRunner) -> None:
        mem = vault / "memory"
        (mem / "2026-02-13.md").write_text(
            "# Notes for 2026-02-13\n\n- **2026-02-13T10:00:00** [ctx]: DONE: Task A\n"
        )
        (mem / "2026-02-14.md").write_text(
            "# Notes for 2026-02-14\n\n- **2026-02-14T08:00:00** [ctx]: DONE: Task B\n"
        )

        result = runner.invoke(evergreen.cli, ["memory", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "0 duplicates" in result.output

    def test_empty_memory(self, vault: Path, runner: CliRunner) -> None:
        result = runner.invoke(evergreen.cli, ["memory", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "No daily memory files" in result.output

    def test_missing_memory_dir(self, tmp_path: Path, runner: CliRunner) -> None:
        result = runner.invoke(evergreen.cli, ["memory", "--vault", str(tmp_path)])
        assert result.exit_code == 0
        assert "not found" in result.output


# ---------------------------------------------------------------------------
# extract_entries
# ---------------------------------------------------------------------------


class TestExtractEntries:
    def test_basic_entry(self) -> None:
        content = "- **2026-02-14T10:00:00** [ctx]: DONE: Did something"
        entries = evergreen._extract_entries(content)
        assert len(entries) == 1
        assert "done: did something" in entries[0]

    def test_entry_without_context(self) -> None:
        content = "- **2026-02-14T10:00:00** Did something"
        entries = evergreen._extract_entries(content)
        assert len(entries) == 1
        assert "did something" in entries[0]

    def test_ignores_non_entries(self) -> None:
        content = "# Title\n\nJust some text\n\n- normal bullet"
        entries = evergreen._extract_entries(content)
        assert len(entries) == 0

    def test_multiple_entries(self) -> None:
        content = (
            "- **2026-02-14T10:00:00** [a]: Entry one\n- **2026-02-14T11:00:00** [b]: Entry two\n"
        )
        entries = evergreen._extract_entries(content)
        assert len(entries) == 2


# ---------------------------------------------------------------------------
# Repo maintenance (with mocked git)
# ---------------------------------------------------------------------------


class TestRepoMaintenance:
    def test_dry_run_shows_merged_branches(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test repo maintenance with a real git repo."""
        # Create a git repo with a merged branch
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "checkout", "-b", "main"], capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)
        subprocess.run(
            ["git", "-C", str(tmp_path), "checkout", "-b", "feature"], capture_output=True
        )
        subprocess.run(["git", "-C", str(tmp_path), "checkout", "main"], capture_output=True)

        result = runner.invoke(evergreen.cli, ["repo", str(tmp_path)])
        assert result.exit_code == 0
        assert "feature" in result.output
        assert "Merged local branches" in result.output

    def test_prune_deletes_merged_branches(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test that --prune actually deletes merged branches."""
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "checkout", "-b", "main"], capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)
        subprocess.run(
            ["git", "-C", str(tmp_path), "checkout", "-b", "old-feature"], capture_output=True
        )
        subprocess.run(["git", "-C", str(tmp_path), "checkout", "main"], capture_output=True)

        result = runner.invoke(evergreen.cli, ["repo", str(tmp_path), "--prune"])
        assert result.exit_code == 0
        assert "deleted: old-feature" in result.output

        # Verify branch is actually gone
        branches = subprocess.run(
            ["git", "-C", str(tmp_path), "branch"],
            capture_output=True,
            text=True,
        )
        assert "old-feature" not in branches.stdout

    def test_no_merged_branches(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test with a repo that has no merged branches."""
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "checkout", "-b", "main"], capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)

        result = runner.invoke(evergreen.cli, ["repo", str(tmp_path)])
        assert result.exit_code == 0
        assert "(none)" in result.output


# ---------------------------------------------------------------------------
# Run-all command
# ---------------------------------------------------------------------------


class TestRunAll:
    def test_runs_knowledge_and_memory(self, vault: Path, runner: CliRunner) -> None:
        """Test that 'all' without repo_path runs knowledge + memory."""
        kg = vault / "knowledge_graph"
        (kg / "Note.md").write_text("# Note\nSource: test\nDate: 2026-01-01\n")

        result = runner.invoke(evergreen.cli, ["all", "--vault", str(vault)])
        assert result.exit_code == 0
        assert "KNOWLEDGE MAINTENANCE" in result.output
        assert "MEMORY MAINTENANCE" in result.output
        # No repo maintenance when repo_path not given
        assert "REPO MAINTENANCE" not in result.output
