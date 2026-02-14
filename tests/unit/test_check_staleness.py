"""Tests for the obsidian check_staleness CLI."""

import importlib.util
import sys
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import check_staleness.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "check_staleness",
    Path(__file__).resolve().parents[2] / "skills" / "obsidian" / "scripts" / "check_staleness.py",
)
assert _spec is not None and _spec.loader is not None
check_staleness = importlib.util.module_from_spec(_spec)
sys.modules["check_staleness"] = check_staleness
_spec.loader.exec_module(check_staleness)


@pytest.fixture()
def vault_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect KNOWLEDGE_DIR to a temp directory."""
    monkeypatch.setattr(check_staleness, "KNOWLEDGE_DIR", tmp_path)
    return tmp_path


def _make_note(path: Path, source: str | None = None, date: str | None = None) -> None:
    """Create a minimal obsidian note with optional Source/Date metadata."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {path.stem}", "#test"]
    if source is not None:
        lines.append(f"Source: {source}")
    if date is not None:
        lines.append(f"Date: {date}")
    lines.append("\nSome content here.\n")
    path.write_text("\n".join(lines))


class TestParseNote:
    def test_parses_source_and_date(self, tmp_path: Path) -> None:
        p = tmp_path / "test.md"
        _make_note(p, source="https://example.com", date="2026-01-15")
        note = check_staleness.parse_note(p)
        assert note.source == "https://example.com"
        assert note.date == "2026-01-15"
        assert note.has_url is True

    def test_no_metadata(self, tmp_path: Path) -> None:
        p = tmp_path / "bare.md"
        p.write_text("# Bare note\n\nJust content.\n")
        note = check_staleness.parse_note(p)
        assert note.source is None
        assert note.date is None
        assert note.has_url is False

    def test_non_url_source(self, tmp_path: Path) -> None:
        p = tmp_path / "session.md"
        _make_note(p, source="Claude Code session", date="2026-02-10")
        note = check_staleness.parse_note(p)
        assert note.source == "Claude Code session"
        assert note.has_url is False

    def test_source_original(self, tmp_path: Path) -> None:
        p = tmp_path / "original.md"
        _make_note(p, source="original", date="2026-02-10")
        note = check_staleness.parse_note(p)
        assert note.source == "original"
        assert note.has_url is False

    def test_http_source(self, tmp_path: Path) -> None:
        p = tmp_path / "http.md"
        _make_note(p, source="http://example.com/page", date="2026-02-10")
        note = check_staleness.parse_note(p)
        assert note.has_url is True

    def test_case_insensitive_metadata(self, tmp_path: Path) -> None:
        p = tmp_path / "case.md"
        p.write_text("# Case test\nsource: https://example.com\ndate: 2026-01-01\n")
        note = check_staleness.parse_note(p)
        assert note.source == "https://example.com"
        assert note.date == "2026-01-01"


class TestNoteMetadata:
    def test_missing_date(self, tmp_path: Path) -> None:
        p = tmp_path / "nodate.md"
        _make_note(p, source="https://example.com")
        note = check_staleness.parse_note(p)
        assert note.missing_date is True
        assert note.days_old() is None

    def test_missing_source(self, tmp_path: Path) -> None:
        p = tmp_path / "nosource.md"
        _make_note(p, date="2026-02-10")
        note = check_staleness.parse_note(p)
        assert note.missing_source is True

    def test_days_old(self, tmp_path: Path) -> None:
        p = tmp_path / "old.md"
        _make_note(p, source="https://example.com", date="2026-01-01")
        note = check_staleness.parse_note(p)
        now = datetime(2026, 2, 14)
        assert note.days_old(now) == 44

    def test_is_stale_under_threshold(self, tmp_path: Path) -> None:
        p = tmp_path / "fresh.md"
        _make_note(p, source="https://example.com", date="2026-02-01")
        note = check_staleness.parse_note(p)
        now = datetime(2026, 2, 14)
        assert note.is_stale(90, now) is False

    def test_is_stale_over_threshold(self, tmp_path: Path) -> None:
        p = tmp_path / "stale.md"
        _make_note(p, source="https://example.com", date="2025-10-01")
        note = check_staleness.parse_note(p)
        now = datetime(2026, 2, 14)
        assert note.is_stale(90, now) is True

    def test_not_stale_without_url(self, tmp_path: Path) -> None:
        p = tmp_path / "session.md"
        _make_note(p, source="Claude Code session", date="2025-01-01")
        note = check_staleness.parse_note(p)
        now = datetime(2026, 2, 14)
        assert note.is_stale(90, now) is False

    def test_not_stale_without_date(self, tmp_path: Path) -> None:
        p = tmp_path / "nodate.md"
        _make_note(p, source="https://example.com")
        note = check_staleness.parse_note(p)
        assert note.is_stale(90) is False


class TestScanVault:
    def test_empty_vault(self, vault_dir: Path) -> None:
        notes = check_staleness.scan_vault(vault_dir)
        assert notes == []

    def test_finds_all_notes(self, vault_dir: Path) -> None:
        _make_note(vault_dir / "a.md", source="https://a.com", date="2026-02-01")
        _make_note(vault_dir / "sub" / "b.md", source="https://b.com", date="2026-02-01")
        _make_note(vault_dir / "c.md")
        notes = check_staleness.scan_vault(vault_dir)
        assert len(notes) == 3

    def test_nonexistent_dir(self, tmp_path: Path) -> None:
        notes = check_staleness.scan_vault(tmp_path / "nonexistent")
        assert notes == []


class TestCheckCommand:
    def test_fresh_note(self, tmp_path: Path) -> None:
        p = tmp_path / "fresh.md"
        today = datetime.now().strftime("%Y-%m-%d")
        _make_note(p, source="https://example.com", date=today)
        result = CliRunner().invoke(check_staleness.cli, ["check", str(p)])
        assert result.exit_code == 0
        assert "Stale: False" in result.output
        assert "Has URL: True" in result.output

    def test_stale_note_exits_1(self, tmp_path: Path) -> None:
        p = tmp_path / "stale.md"
        old_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        _make_note(p, source="https://example.com/docs", date=old_date)
        result = CliRunner().invoke(check_staleness.cli, ["check", str(p)])
        assert result.exit_code == 1
        assert "Stale: True" in result.output
        assert "REFRESH RECOMMENDED" in result.output

    def test_missing_file(self, tmp_path: Path) -> None:
        result = CliRunner().invoke(check_staleness.cli, ["check", str(tmp_path / "nope.md")])
        assert result.exit_code != 0
        assert "File not found" in result.output

    def test_note_without_url(self, tmp_path: Path) -> None:
        p = tmp_path / "session.md"
        _make_note(p, source="Claude Code session", date="2025-01-01")
        result = CliRunner().invoke(check_staleness.cli, ["check", str(p)])
        assert result.exit_code == 0
        assert "Stale: False" in result.output

    def test_custom_threshold(self, tmp_path: Path) -> None:
        p = tmp_path / "borderline.md"
        date_50_ago = (datetime.now() - timedelta(days=50)).strftime("%Y-%m-%d")
        _make_note(p, source="https://example.com", date=date_50_ago)
        # Default 90 days: not stale
        result = CliRunner().invoke(check_staleness.cli, ["check", str(p)])
        assert result.exit_code == 0
        # Custom 30 days: stale
        result = CliRunner().invoke(check_staleness.cli, ["check", str(p), "--days", "30"])
        assert result.exit_code == 1


class TestAuditCommand:
    def test_empty_vault(self, vault_dir: Path) -> None:
        result = CliRunner().invoke(check_staleness.cli, ["audit", "--vault-dir", str(vault_dir)])
        assert "No notes found" in result.output

    def test_reports_counts(self, vault_dir: Path) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        _make_note(vault_dir / "with_url.md", source="https://example.com", date=today)
        _make_note(vault_dir / "no_date.md", source="https://example.com")
        _make_note(vault_dir / "no_source.md", date=today)
        _make_note(vault_dir / "bare.md")
        result = CliRunner().invoke(check_staleness.cli, ["audit", "--vault-dir", str(vault_dir)])
        assert result.exit_code == 0
        assert "Total notes: 4" in result.output
        assert "With Source URL: 2" in result.output
        assert "Missing Date: 2" in result.output
        assert "Missing Source: 2" in result.output

    def test_reports_stale(self, vault_dir: Path) -> None:
        old_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        _make_note(vault_dir / "stale.md", source="https://stale.example.com", date=old_date)
        _make_note(
            vault_dir / "fresh.md",
            source="https://fresh.example.com",
            date=datetime.now().strftime("%Y-%m-%d"),
        )
        result = CliRunner().invoke(check_staleness.cli, ["audit", "--vault-dir", str(vault_dir)])
        assert "Stale (>90 days, has URL): 1" in result.output
        assert "stale.md" in result.output
        assert "stale.example.com" in result.output


class TestStaleUrlsCommand:
    def test_lists_stale_urls(self, vault_dir: Path) -> None:
        old_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        _make_note(vault_dir / "stale.md", source="https://stale.example.com", date=old_date)
        _make_note(
            vault_dir / "fresh.md",
            source="https://fresh.example.com",
            date=datetime.now().strftime("%Y-%m-%d"),
        )
        result = CliRunner().invoke(
            check_staleness.cli, ["stale-urls", "--vault-dir", str(vault_dir)]
        )
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert len(lines) == 1
        parts = lines[0].split("|")
        assert len(parts) == 3
        assert "stale.md" in parts[0]
        assert parts[1] == "https://stale.example.com"

    def test_empty_when_all_fresh(self, vault_dir: Path) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        _make_note(vault_dir / "fresh.md", source="https://example.com", date=today)
        result = CliRunner().invoke(
            check_staleness.cli, ["stale-urls", "--vault-dir", str(vault_dir)]
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""
