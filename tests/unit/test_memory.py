"""Tests for the hierarchical memory CLI."""

import importlib.util
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import memory.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "memory",
    Path(__file__).resolve().parents[2]
    / "skills"
    / "hierarchical_memory"
    / "scripts"
    / "memory.py",
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


class TestMonthlyPath:
    def test_specific_date(self) -> None:
        assert memory.monthly_path(datetime(2026, 1, 15)).name == "2026-01.md"


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


class TestClassifyFile:
    def test_daily(self) -> None:
        assert memory.classify_file("2026-01-15.md") == "daily"

    def test_monthly(self) -> None:
        assert memory.classify_file("2026-01.md") == "monthly"

    def test_overall(self) -> None:
        assert memory.classify_file("memory.md") == "overall"


class TestMonthFromFilename:
    def test_daily(self) -> None:
        assert memory.month_from_filename("2026-01-15.md") == "2026-01"

    def test_monthly(self) -> None:
        assert memory.month_from_filename("2026-01.md") == "2026-01"

    def test_overall(self) -> None:
        assert memory.month_from_filename("memory.md") is None


class TestStatusCommand:
    def test_empty_dir(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "No memory files found" in result.output

    def test_daily_only_needs_create(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Notes\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "CREATE" in result.output
        assert "2026-01" in result.output

    def test_daily_newer_than_monthly_needs_update(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        time.sleep(0.05)
        (mem_dir / "2026-01-20.md").write_text("# New daily\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "UPDATE" in result.output
        assert "2026-01-20.md" in result.output

    def test_monthly_newer_than_daily_is_ok(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Daily\n")
        time.sleep(0.05)
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "**OK**" in result.output

    def test_overall_create(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "CREATE" in result.output
        assert "no memory.md exists" in result.output

    def test_overall_update(self, mem_dir: Path) -> None:
        (mem_dir / "memory.md").write_text("# Overall\n")
        time.sleep(0.05)
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "UPDATE" in result.output
        assert "monthly summaries are newer" in result.output

    def test_overall_ok(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        time.sleep(0.05)
        (mem_dir / "memory.md").write_text("# Overall\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "memory.md is up to date" in result.output

    def test_obsidian_vault_listing(self, mem_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        vault = mem_dir / "vault"
        vault.mkdir()
        (vault / "Note1.md").write_text("# Note\n")
        sub = vault / "Projects"
        sub.mkdir()
        (sub / "Proj1.md").write_text("# Project\n")
        monkeypatch.setattr(memory, "VAULT_DIR", vault)
        # Need at least one memory file so status doesn't exit early
        (mem_dir / "memory.md").write_text("# Overall\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "Obsidian Vault" in result.output
        assert "Note1.md" in result.output
        assert "Projects" in result.output
