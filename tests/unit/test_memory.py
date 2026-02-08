"""Tests for the hierarchical memory CLI."""

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import memory.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "memory",
    Path(__file__).resolve().parents[2] / "skills" / "hierarchical_memory" / "scripts" / "memory.py",
)
assert _spec is not None and _spec.loader is not None
memory = importlib.util.module_from_spec(_spec)
sys.modules["memory"] = memory
_spec.loader.exec_module(memory)


@pytest.fixture()
def mem_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect MEMORY_DIR to a temp directory."""
    monkeypatch.setattr(memory, "MEMORY_DIR", tmp_path)
    return tmp_path


class TestDailyPath:
    def test_uses_current_date(self) -> None:
        path = memory.daily_path()
        assert path.suffix == ".md"
        assert datetime.now().strftime("%Y-%m-%d") in path.name

    def test_specific_date(self) -> None:
        assert memory.daily_path(datetime(2026, 1, 15)).name == "2026-01-15.md"


class TestWeeklyPath:
    def test_specific_date(self) -> None:
        assert memory.weekly_path(datetime(2026, 1, 15)).name == "2026-W03.md"


class TestNoteCommand:
    def test_creates_daily_file(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["note", "test note"])
        assert result.exit_code == 0
        assert "Saved to" in result.output
        daily_files = list(mem_dir.glob("????-??-??.md"))
        assert len(daily_files) == 1
        content = daily_files[0].read_text()
        assert "test note" in content
        assert "# Notes for" in content

    def test_appends(self, mem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(memory.cli, ["note", "first"])
        runner.invoke(memory.cli, ["note", "second"])
        content = list(mem_dir.glob("????-??-??.md"))[0].read_text()
        assert "first" in content
        assert "second" in content


class TestTodayCommand:
    def test_shows_notes(self, mem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(memory.cli, ["note", "today test"])
        result = runner.invoke(memory.cli, ["today"])
        assert result.exit_code == 0
        assert "today test" in result.output

    def test_no_notes(self, mem_dir: Path) -> None:
        assert "No notes for today" in CliRunner().invoke(memory.cli, ["today"]).output


class TestShowCommand:
    def test_shows_date(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Test\n\n- a note\n")
        result = CliRunner().invoke(memory.cli, ["show", "2026-01-15"])
        assert "a note" in result.output

    def test_missing_date(self, mem_dir: Path) -> None:
        assert "No notes found" in CliRunner().invoke(memory.cli, ["show", "2099-12-31"]).output


class TestSearchCommand:
    def test_finds_match(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Notes\n\n- bought groceries\n")
        result = CliRunner().invoke(memory.cli, ["search", "groceries"])
        assert "1 matches" in result.output

    def test_case_insensitive(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Notes\n\n- Python stuff\n")
        assert "1 matches" in CliRunner().invoke(memory.cli, ["search", "python"]).output

    def test_no_matches(self, mem_dir: Path) -> None:
        assert "No matches" in CliRunner().invoke(memory.cli, ["search", "nothing"]).output


class TestAggregateCommand:
    def test_creates_weekly_and_overall(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-12.md").write_text("# Notes for 2026-01-12\n\n- monday\n")
        (mem_dir / "2026-01-13.md").write_text("# Notes for 2026-01-13\n\n- tuesday\n")
        result = CliRunner().invoke(memory.cli, ["aggregate"])
        assert result.exit_code == 0

        weekly = list(mem_dir.glob("????-W??.md"))
        assert len(weekly) == 1
        assert "monday" in weekly[0].read_text()

        overall = mem_dir / "memory.md"
        assert overall.exists()
        assert "# Memory" in overall.read_text()

    def test_no_daily_notes(self, mem_dir: Path) -> None:
        assert "No daily notes" in CliRunner().invoke(memory.cli, ["aggregate"]).output
