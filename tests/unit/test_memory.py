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

    def test_includes_repo_name(self, mem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(memory.cli, ["note", "repo test"])
        content = list(mem_dir.glob("????-??-??.md"))[0].read_text()
        # Should have hostname:reponame format
        assert ":" in content.split("[")[1].split("]")[0]


class TestListCommand:
    def test_empty(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["list"])
        assert "No memory files found" in result.output

    def test_lists_files_with_types(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Daily\n")
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        result = CliRunner().invoke(memory.cli, ["list"])
        assert result.exit_code == 0
        assert "daily" in result.output
        assert "monthly" in result.output
        assert "overall" in result.output

    def test_warns_unknown_files(self, mem_dir: Path) -> None:
        (mem_dir / "random.md").write_text("# Unknown\n")
        result = CliRunner().invoke(memory.cli, ["list"])
        assert "unknown" in result.output
        assert "Warning" in result.output


class TestReadDayCommand:
    def test_shows_today(self, mem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(memory.cli, ["note", "today test"])
        result = runner.invoke(memory.cli, ["read-day"])
        assert result.exit_code == 0
        assert "today test" in result.output

    def test_shows_specific_date(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Test\n\n- a note\n")
        result = CliRunner().invoke(memory.cli, ["read-day", "2026-01-15"])
        assert "a note" in result.output

    def test_no_notes(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-day"])
        assert "No notes for" in result.output

    def test_rejects_bad_format(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-day", "../../etc/passwd"])
        assert result.exit_code != 0

    def test_rejects_arbitrary_string(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-day", "foo"])
        assert result.exit_code != 0


class TestReadMonthCommand:
    def test_shows_specific_month(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# January summary\n")
        result = CliRunner().invoke(memory.cli, ["read-month", "2026-01"])
        assert "January summary" in result.output

    def test_no_summary(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-month"])
        assert "No monthly summary" in result.output

    def test_rejects_bad_format(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-month", "bad"])
        assert result.exit_code != 0


class TestReadOverallCommand:
    def test_shows_overall(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\nKey facts here.\n")
        result = CliRunner().invoke(memory.cli, ["read-overall"])
        assert "Key facts here" in result.output

    def test_no_overall(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-overall"])
        assert "No overall memory file found" in result.output


class TestReadCurrentCommand:
    def test_shows_all_sections(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall content\n")
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        (mem_dir / f"{month}.md").write_text("# Monthly content\n")
        (mem_dir / f"{today}.md").write_text("# Daily content\n")
        result = CliRunner().invoke(memory.cli, ["read-current"])
        assert result.exit_code == 0
        assert "Overall Memory" in result.output
        assert "Overall content" in result.output
        assert "Current Month" in result.output
        assert "Monthly content" in result.output
        assert "Today" in result.output
        assert "Daily content" in result.output

    def test_handles_missing_files(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["read-current"])
        assert result.exit_code == 0
        assert "not yet created" in result.output
        assert "no notes yet" in result.output


class TestClassifyFile:
    def test_daily(self) -> None:
        assert memory.classify_file("2026-01-15.md") == "daily"

    def test_monthly(self) -> None:
        assert memory.classify_file("2026-01.md") == "monthly"

    def test_overall(self) -> None:
        assert memory.classify_file("overall_memory.md") == "overall"

    def test_old_memory_md_is_unknown(self) -> None:
        assert memory.classify_file("memory.md") == "unknown"

    def test_random_file_is_unknown(self) -> None:
        assert memory.classify_file("random.md") == "unknown"


class TestMonthFromFilename:
    def test_daily(self) -> None:
        assert memory.month_from_filename("2026-01-15.md") == "2026-01"

    def test_monthly(self) -> None:
        assert memory.month_from_filename("2026-01.md") == "2026-01"

    def test_overall(self) -> None:
        assert memory.month_from_filename("overall_memory.md") is None


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
        assert "no overall_memory.md exists" in result.output

    def test_overall_update(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        time.sleep(0.05)
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "UPDATE" in result.output
        assert "monthly summaries are newer" in result.output

    def test_overall_ok(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        time.sleep(0.05)
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "overall_memory.md is up to date" in result.output

    def test_knowledge_graph_listing(self, mem_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        kg = mem_dir / "kg"
        kg.mkdir()
        (kg / "Note1.md").write_text("# Note\n")
        sub = kg / "Projects"
        sub.mkdir()
        (sub / "Proj1.md").write_text("# Project\n")
        monkeypatch.setattr(memory, "KNOWLEDGE_DIR", kg)
        # Need at least one memory file so status doesn't exit early
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        result = CliRunner().invoke(memory.cli, ["status"])
        assert result.exit_code == 0
        assert "Knowledge Graph" in result.output
        assert "Note1.md" in result.output
        assert "Projects" in result.output
