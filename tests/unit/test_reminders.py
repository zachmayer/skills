"""Tests for the reminders CLI."""

import importlib.util
import json
import sys
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import reminders.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "reminders",
    Path(__file__).resolve().parents[2] / "skills" / "reminders" / "scripts" / "reminders.py",
)
assert _spec is not None and _spec.loader is not None
reminders = importlib.util.module_from_spec(_spec)
sys.modules["reminders"] = reminders
_spec.loader.exec_module(reminders)


@pytest.fixture()
def rem_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect MEMORY_DIR and REMINDERS_FILE to a temp directory."""
    monkeypatch.setattr(reminders, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(reminders, "REMINDERS_FILE", tmp_path / "reminders.json")
    return tmp_path


class TestAddCommand:
    def test_add_date_only(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["add", "Test reminder", "2026-03-01"])
        assert result.exit_code == 0
        assert "Added:" in result.output
        assert "Test reminder" in result.output
        data = json.loads((rem_dir / "reminders.json").read_text())
        assert len(data) == 1
        assert data[0]["text"] == "Test reminder"
        assert data[0]["completed"] is False

    def test_add_datetime(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["add", "Meeting", "2026-03-01T14:30"])
        assert result.exit_code == 0
        data = json.loads((rem_dir / "reminders.json").read_text())
        assert "14:30" in data[0]["due"]

    def test_add_bad_date(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["add", "Bad date", "not-a-date"])
        assert result.exit_code != 0

    def test_add_multiple(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "First", "2026-03-01"])
        runner.invoke(reminders.cli, ["add", "Second", "2026-03-02"])
        data = json.loads((rem_dir / "reminders.json").read_text())
        assert len(data) == 2


class TestListCommand:
    def test_empty(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["list"])
        assert "No reminders" in result.output

    def test_list_active(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "Active one", "2099-01-01"])
        result = runner.invoke(reminders.cli, ["list"])
        assert result.exit_code == 0
        assert "Active one" in result.output
        assert "pending" in result.output

    def test_list_hides_completed(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "Will complete", "2099-01-01"])
        data = json.loads((rem_dir / "reminders.json").read_text())
        short_id = data[0]["id"][:8]
        runner.invoke(reminders.cli, ["complete", short_id])
        result = runner.invoke(reminders.cli, ["list"])
        assert "No active reminders" in result.output

    def test_list_all_shows_completed(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "Completed one", "2099-01-01"])
        data = json.loads((rem_dir / "reminders.json").read_text())
        short_id = data[0]["id"][:8]
        runner.invoke(reminders.cli, ["complete", short_id])
        result = runner.invoke(reminders.cli, ["list", "--all"])
        assert "Completed one" in result.output
        assert "DONE" in result.output


class TestDueCommand:
    def test_no_due(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "Future", "2099-01-01"])
        result = runner.invoke(reminders.cli, ["due"])
        assert "No reminders due" in result.output

    def test_overdue_shown(self, rem_dir: Path) -> None:
        runner = CliRunner()
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        runner.invoke(reminders.cli, ["add", "Overdue item", yesterday])
        result = runner.invoke(reminders.cli, ["due"])
        assert "Overdue item" in result.output
        assert "OVERDUE" in result.output

    def test_completed_not_shown_as_due(self, rem_dir: Path) -> None:
        runner = CliRunner()
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        runner.invoke(reminders.cli, ["add", "Done item", yesterday])
        data = json.loads((rem_dir / "reminders.json").read_text())
        short_id = data[0]["id"][:8]
        runner.invoke(reminders.cli, ["complete", short_id])
        result = runner.invoke(reminders.cli, ["due"])
        assert "No reminders due" in result.output


class TestCompleteCommand:
    def test_complete_reminder(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "To complete", "2099-01-01"])
        data = json.loads((rem_dir / "reminders.json").read_text())
        short_id = data[0]["id"][:8]
        result = runner.invoke(reminders.cli, ["complete", short_id])
        assert result.exit_code == 0
        assert "Completed: To complete" in result.output
        data = json.loads((rem_dir / "reminders.json").read_text())
        assert data[0]["completed"] is True

    def test_complete_not_found(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["complete", "nonexist"])
        assert result.exit_code != 0
        assert "No reminder found" in result.output


class TestRemoveCommand:
    def test_remove_reminder(self, rem_dir: Path) -> None:
        runner = CliRunner()
        runner.invoke(reminders.cli, ["add", "To remove", "2099-01-01"])
        data = json.loads((rem_dir / "reminders.json").read_text())
        short_id = data[0]["id"][:8]
        result = runner.invoke(reminders.cli, ["remove", short_id])
        assert result.exit_code == 0
        assert "Removed: To remove" in result.output
        data = json.loads((rem_dir / "reminders.json").read_text())
        assert len(data) == 0

    def test_remove_not_found(self, rem_dir: Path) -> None:
        result = CliRunner().invoke(reminders.cli, ["remove", "nonexist"])
        assert result.exit_code != 0
        assert "No reminder found" in result.output


class TestParseDue:
    def test_date_only(self) -> None:
        dt = reminders._parse_due("2026-03-01")
        assert dt == datetime(2026, 3, 1)

    def test_datetime(self) -> None:
        dt = reminders._parse_due("2026-03-01T14:30")
        assert dt == datetime(2026, 3, 1, 14, 30)

    def test_bad_format_raises(self) -> None:
        with pytest.raises(Exception):
            reminders._parse_due("not-a-date")


class TestFormatReminder:
    def test_pending(self) -> None:
        now = datetime(2026, 2, 14)
        r = {
            "id": "abcdef1234567890",
            "text": "Future",
            "due": "2026-03-01T00:00:00",
            "completed": False,
        }
        line = reminders._format_reminder(r, now)
        assert "pending" in line
        assert "Future" in line
        assert "abcdef12" in line

    def test_overdue(self) -> None:
        now = datetime(2026, 3, 15)
        r = {
            "id": "abcdef1234567890",
            "text": "Past",
            "due": "2026-03-01T00:00:00",
            "completed": False,
        }
        line = reminders._format_reminder(r, now)
        assert "OVERDUE" in line

    def test_done(self) -> None:
        now = datetime(2026, 2, 14)
        r = {
            "id": "abcdef1234567890",
            "text": "Done",
            "due": "2026-03-01T00:00:00",
            "completed": True,
        }
        line = reminders._format_reminder(r, now)
        assert "DONE" in line


class TestLoadSave:
    def test_load_empty(self, rem_dir: Path) -> None:
        assert reminders._load_reminders() == []

    def test_roundtrip(self, rem_dir: Path) -> None:
        data = [
            {
                "id": "test",
                "text": "hello",
                "due": "2026-01-01T00:00:00",
                "created": "2026-01-01T00:00:00",
                "completed": False,
            }
        ]
        reminders._save_reminders(data)
        loaded = reminders._load_reminders()
        assert loaded == data
