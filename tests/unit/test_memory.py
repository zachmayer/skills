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

    def test_reports_aggregation_staleness(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["note", "staleness check"])
        assert result.exit_code == 0
        # Daily file exists with no monthly → CREATE
        assert "Aggregation stale:" in result.output
        assert "CREATE" in result.output

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


class TestComputeStaleness:
    def test_no_files_returns_none(self, mem_dir: Path) -> None:
        assert memory._compute_staleness() is None

    def test_daily_only_needs_create(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Notes\n")
        report = memory._compute_staleness()
        assert report is not None
        assert len(report.needs_create) == 1
        assert report.needs_create[0]["month"] == "2026-01"
        assert report.needs_update == []
        assert report.ok == []

    def test_stale_monthly_needs_update(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        time.sleep(0.05)
        (mem_dir / "2026-01-20.md").write_text("# New daily\n")
        report = memory._compute_staleness()
        assert report is not None
        assert report.needs_create == []
        assert len(report.needs_update) == 1
        assert report.needs_update[0]["month"] == "2026-01"

    def test_fresh_monthly_and_overall_returns_ok(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01-15.md").write_text("# Daily\n")
        time.sleep(0.05)
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        time.sleep(0.05)
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        report = memory._compute_staleness()
        assert report is not None
        assert report.needs_create == []
        assert report.needs_update == []
        assert report.ok == ["2026-01"]
        assert report.overall == "OK"

    def test_overall_needs_create(self, mem_dir: Path) -> None:
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        report = memory._compute_staleness()
        assert report is not None
        assert report.overall == "CREATE"

    def test_overall_needs_update(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        time.sleep(0.05)
        (mem_dir / "2026-01.md").write_text("# Monthly\n")
        report = memory._compute_staleness()
        assert report is not None
        assert report.overall == "UPDATE"


class TestParseMonthName:
    def test_standard_months(self) -> None:
        assert memory._parse_month_name("Jan") == 1
        assert memory._parse_month_name("February") == 2
        assert memory._parse_month_name("Dec") == 12

    def test_case_insensitive(self) -> None:
        assert memory._parse_month_name("jan") == 1
        assert memory._parse_month_name("MARCH") == 3

    def test_unknown(self) -> None:
        assert memory._parse_month_name("xyz") == 0


class TestExtractDatedFacts:
    def test_iso_date(self) -> None:
        content = "- **2026-01-15**: something happened\n"
        now = datetime(2026, 2, 14)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        assert facts[0].date == datetime(2026, 1, 15)
        assert facts[0].age_days == 30

    def test_month_year(self) -> None:
        content = "- Completed in Feb 2026\n"
        now = datetime(2026, 3, 15)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        assert facts[0].date == datetime(2026, 2, 1)
        assert facts[0].age_days == 42

    def test_yyyy_mm(self) -> None:
        content = "- Summary for 2026-01\n"
        now = datetime(2026, 2, 14)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        assert facts[0].date == datetime(2026, 1, 1)

    def test_skips_headers(self) -> None:
        content = "# Header 2026-01-01\n- body 2026-01-02\n"
        now = datetime(2026, 2, 14)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        assert facts[0].text == "- body 2026-01-02"

    def test_skips_empty_lines(self) -> None:
        content = "\n\n- fact 2026-01-01\n\n"
        now = datetime(2026, 2, 14)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1

    def test_multiple_dates_uses_latest(self) -> None:
        content = "- Started 2025-01-01 completed 2026-01-15\n"
        now = datetime(2026, 2, 14)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        assert facts[0].date == datetime(2026, 1, 15)

    def test_no_dates(self) -> None:
        content = "- A fact without any date\n- Another one\n"
        facts = memory._extract_dated_facts(content)
        assert len(facts) == 0

    def test_iso_preferred_over_month_year(self) -> None:
        content = "- Event on 2026-02-14 in Feb 2025\n"
        now = datetime(2026, 3, 1)
        facts = memory._extract_dated_facts(content, now)
        assert len(facts) == 1
        # ISO date 2026-02-14 is more specific and should be picked
        assert facts[0].date == datetime(2026, 2, 14)

    def test_line_numbers_correct(self) -> None:
        content = "# Header\n\n- First 2026-01-01\n- Second 2026-01-02\n"
        facts = memory._extract_dated_facts(content, datetime(2026, 2, 1))
        assert len(facts) == 2
        assert facts[0].line_num == 3
        assert facts[1].line_num == 4


class TestOverallAgeDays:
    def test_no_file(self, mem_dir: Path) -> None:
        assert memory._overall_age_days() is None

    def test_with_file(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        age = memory._overall_age_days()
        assert age is not None
        assert age >= 0
        # File just created — should be 0 days old
        assert age == 0


class TestFreshnessWarning:
    def test_no_file(self, mem_dir: Path) -> None:
        assert memory._freshness_warning() is None

    def test_fresh_file(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\n")
        # Just created, so should be fresh
        assert memory._freshness_warning() is None

    def test_stale_file(self, mem_dir: Path) -> None:
        path = mem_dir / "overall_memory.md"
        path.write_text("# Overall\n")
        # Set mtime to 60 days ago
        import os

        old_time = time.time() - 60 * 86400
        os.utime(path, (old_time, old_time))
        warning = memory._freshness_warning()
        assert warning is not None
        assert "60 days old" in warning
        assert "freshness" in warning.lower()


class TestFreshnessCommand:
    def test_no_overall(self, mem_dir: Path) -> None:
        result = CliRunner().invoke(memory.cli, ["freshness"])
        assert result.exit_code == 0
        assert "No overall memory file found" in result.output

    def test_no_dated_facts(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\n\n- A fact without dates\n")
        result = CliRunner().invoke(memory.cli, ["freshness"])
        assert result.exit_code == 0
        assert "No dated facts found" in result.output

    def test_fresh_facts(self, mem_dir: Path) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        (mem_dir / "overall_memory.md").write_text(f"# Overall\n\n- Recent fact {today}\n")
        result = CliRunner().invoke(memory.cli, ["freshness"])
        assert result.exit_code == 0
        assert "0 stale" in result.output

    def test_stale_facts(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text(
            "# Overall\n\n- Old fact 2020-01-01\n- Fresh fact 2099-12-31\n"
        )
        result = CliRunner().invoke(memory.cli, ["freshness"])
        assert result.exit_code == 0
        assert "STALE" in result.output
        assert "1 stale" in result.output
        assert "1 fresh" in result.output
        assert "verifying stale facts" in result.output.lower()

    def test_custom_days(self, mem_dir: Path) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        (mem_dir / "overall_memory.md").write_text(f"# Overall\n\n- Fact from {today}\n")
        # With --days 0, even today's fact should be "stale" (age_days >= 0)
        result = CliRunner().invoke(memory.cli, ["freshness", "--days", "0"])
        assert result.exit_code == 0
        assert "STALE" in result.output

    def test_truncates_long_lines(self, mem_dir: Path) -> None:
        long_fact = "- " + "x" * 200 + " 2020-01-01"
        (mem_dir / "overall_memory.md").write_text(f"# Overall\n\n{long_fact}\n")
        result = CliRunner().invoke(memory.cli, ["freshness"])
        assert result.exit_code == 0
        assert "..." in result.output


class TestReadOverallFreshness:
    def test_fresh_no_warning(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\nContent here.\n")
        result = CliRunner().invoke(memory.cli, ["read-overall"])
        assert result.exit_code == 0
        assert "[Freshness]" not in result.output
        assert "Content here" in result.output

    def test_stale_shows_warning(self, mem_dir: Path) -> None:
        path = mem_dir / "overall_memory.md"
        path.write_text("# Overall\nContent here.\n")
        import os

        old_time = time.time() - 60 * 86400
        os.utime(path, (old_time, old_time))
        result = CliRunner().invoke(memory.cli, ["read-overall"])
        assert result.exit_code == 0
        assert "[Freshness]" in result.output
        assert "Content here" in result.output


class TestReadCurrentFreshness:
    def test_stale_shows_warning(self, mem_dir: Path) -> None:
        path = mem_dir / "overall_memory.md"
        path.write_text("# Overall\nContent.\n")
        import os

        old_time = time.time() - 45 * 86400
        os.utime(path, (old_time, old_time))
        result = CliRunner().invoke(memory.cli, ["read-current"])
        assert result.exit_code == 0
        assert "[Freshness]" in result.output

    def test_fresh_no_warning(self, mem_dir: Path) -> None:
        (mem_dir / "overall_memory.md").write_text("# Overall\nContent.\n")
        result = CliRunner().invoke(memory.cli, ["read-current"])
        assert result.exit_code == 0
        assert "[Freshness]" not in result.output
