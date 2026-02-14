"""Tests for the mobile bridge capture CLI."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Import capture.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "capture",
    Path(__file__).resolve().parents[2] / "skills" / "mobile_bridge" / "scripts" / "capture.py",
)
assert _spec is not None and _spec.loader is not None
capture = importlib.util.module_from_spec(_spec)
sys.modules["capture"] = capture
_spec.loader.exec_module(capture)


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def obsidian_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up a temp obsidian directory."""
    monkeypatch.setenv("CLAUDE_OBSIDIAN_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def topic(monkeypatch: pytest.MonkeyPatch) -> str:
    """Set a test topic."""
    monkeypatch.setenv("CLAUDE_NTFY_TOPIC", "test-topic-abc123")
    return "test-topic-abc123"


def _make_ntfy_message(body: str, title: str = "", time: int = 1707900000) -> dict:
    """Create a mock ntfy message."""
    msg = {"event": "message", "message": body, "time": time}
    if title:
        msg["title"] = title
    return msg


def _make_poll_response(messages: list[dict]) -> bytes:
    """Create mock poll response bytes."""
    lines = [json.dumps(m) for m in messages]
    return "\n".join(lines).encode()


class TestGetTopic:
    def test_returns_topic(self, topic: str) -> None:
        assert capture._get_topic() == "test-topic-abc123"

    def test_exits_without_topic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CLAUDE_NTFY_TOPIC", raising=False)
        with pytest.raises(SystemExit):
            capture._get_topic()


class TestGetObsidianDir:
    def test_returns_from_env(self, obsidian_dir: Path) -> None:
        result = capture._get_obsidian_dir()
        assert result == obsidian_dir

    def test_default_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CLAUDE_OBSIDIAN_DIR", raising=False)
        result = capture._get_obsidian_dir()
        assert "claude/obsidian" in str(result)


class TestFormatMessage:
    def test_body_only(self) -> None:
        msg = _make_ntfy_message("hello world", time=1707900000)
        result = capture._format_message(msg)
        assert "hello world" in result
        assert "[" in result  # has timestamp

    def test_with_title(self) -> None:
        msg = _make_ntfy_message("details here", title="Important", time=1707900000)
        result = capture._format_message(msg)
        assert "Important" in result
        assert "details here" in result


class TestPollMessages:
    @patch("capture.urlopen")
    def test_returns_messages(self, mock_urlopen: MagicMock) -> None:
        messages = [
            _make_ntfy_message("msg1"),
            _make_ntfy_message("msg2"),
        ]
        mock_resp = MagicMock()
        mock_resp.read.return_value = _make_poll_response(messages)
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = capture._poll_messages("test-topic")
        assert len(result) == 2
        assert result[0]["message"] == "msg1"

    @patch("capture.urlopen")
    def test_empty_response(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b""
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = capture._poll_messages("test-topic")
        assert result == []

    @patch("capture.urlopen")
    def test_filters_non_message_events(self, mock_urlopen: MagicMock) -> None:
        data = [
            {"event": "open", "time": 1},
            {"event": "message", "message": "real", "time": 2},
            {"event": "keepalive", "time": 3},
        ]
        mock_resp = MagicMock()
        mock_resp.read.return_value = _make_poll_response(data)
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = capture._poll_messages("test-topic")
        assert len(result) == 1
        assert result[0]["message"] == "real"

    @patch("capture.urlopen")
    def test_handles_invalid_json(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'not json\n{"event":"message","message":"ok","time":1}\n'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = capture._poll_messages("test-topic")
        assert len(result) == 1

    @patch("capture.urlopen")
    def test_handles_url_error(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("connection failed")
        result = capture._poll_messages("test-topic")
        assert result == []


class TestSaveToMemory:
    def test_creates_daily_note(self, obsidian_dir: Path) -> None:
        messages = [_make_ntfy_message("test idea")]
        path = capture._save_to_memory(messages, obsidian_dir)
        assert path.exists()
        content = path.read_text()
        assert "[mobile]" in content
        assert "test idea" in content

    def test_appends_to_existing(self, obsidian_dir: Path) -> None:
        from datetime import datetime
        from datetime import timezone

        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        memory_dir = obsidian_dir / "memory"
        memory_dir.mkdir()
        daily = memory_dir / f"{today}.md"
        daily.write_text(f"# Notes for {today}\n\n- existing note\n")

        messages = [_make_ntfy_message("new from phone")]
        capture._save_to_memory(messages, obsidian_dir)

        content = daily.read_text()
        assert "existing note" in content
        assert "new from phone" in content

    def test_multiple_messages(self, obsidian_dir: Path) -> None:
        messages = [
            _make_ntfy_message("first"),
            _make_ntfy_message("second"),
        ]
        path = capture._save_to_memory(messages, obsidian_dir)
        content = path.read_text()
        assert "first" in content
        assert "second" in content

    def test_message_with_title(self, obsidian_dir: Path) -> None:
        messages = [_make_ntfy_message("details", title="Urgent")]
        path = capture._save_to_memory(messages, obsidian_dir)
        content = path.read_text()
        assert "Urgent" in content
        assert "details" in content


class TestSaveToObsidian:
    def test_creates_note(self, obsidian_dir: Path) -> None:
        messages = [_make_ntfy_message("reference info")]
        path = capture._save_to_obsidian(messages, obsidian_dir)
        assert path.exists()
        content = path.read_text()
        assert "Mobile Captures" in content
        assert "reference info" in content
        assert "#mobile" in content

    def test_includes_metadata(self, obsidian_dir: Path) -> None:
        messages = [_make_ntfy_message("test")]
        path = capture._save_to_obsidian(messages, obsidian_dir)
        content = path.read_text()
        assert "Source: ntfy mobile bridge" in content
        assert "Date:" in content


class TestCheckCommand:
    @patch("capture._poll_messages")
    def test_no_messages(self, mock_poll: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_poll.return_value = []
        result = runner.invoke(capture.cli, ["check"])
        assert result.exit_code == 0
        assert "No messages" in result.output

    @patch("capture._poll_messages")
    def test_with_messages(self, mock_poll: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_poll.return_value = [_make_ntfy_message("hello from phone", time=1707900000)]
        result = runner.invoke(capture.cli, ["check"])
        assert result.exit_code == 0
        assert "1 message(s)" in result.output
        assert "hello from phone" in result.output

    @patch("capture._poll_messages")
    def test_custom_since(self, mock_poll: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_poll.return_value = []
        runner.invoke(capture.cli, ["check", "--since", "1h"])
        mock_poll.assert_called_once_with("test-topic-abc123", since="1h")


class TestProcessCommand:
    @patch("capture.subprocess")
    @patch("capture._poll_messages")
    def test_no_messages(
        self,
        mock_poll: MagicMock,
        mock_sub: MagicMock,
        runner: CliRunner,
        topic: str,
        obsidian_dir: Path,
    ) -> None:
        mock_poll.return_value = []
        result = runner.invoke(capture.cli, ["process"])
        assert result.exit_code == 0
        assert "No messages" in result.output

    @patch("capture.subprocess")
    @patch("capture._poll_messages")
    def test_saves_to_memory(
        self,
        mock_poll: MagicMock,
        mock_sub: MagicMock,
        runner: CliRunner,
        topic: str,
        obsidian_dir: Path,
    ) -> None:
        mock_poll.return_value = [_make_ntfy_message("capture this")]
        mock_sub.run.return_value = MagicMock(returncode=0)
        result = runner.invoke(capture.cli, ["process"])
        assert result.exit_code == 0
        assert "Saved to: memory" in result.output

    @patch("capture.subprocess")
    @patch("capture._poll_messages")
    def test_saves_to_obsidian(
        self,
        mock_poll: MagicMock,
        mock_sub: MagicMock,
        runner: CliRunner,
        topic: str,
        obsidian_dir: Path,
    ) -> None:
        mock_poll.return_value = [_make_ntfy_message("durable note")]
        mock_sub.run.return_value = MagicMock(returncode=0)
        result = runner.invoke(capture.cli, ["process", "--route", "obsidian"])
        assert result.exit_code == 0
        assert "obsidian" in result.output

    @patch("capture.subprocess")
    @patch("capture._poll_messages")
    def test_saves_to_both(
        self,
        mock_poll: MagicMock,
        mock_sub: MagicMock,
        runner: CliRunner,
        topic: str,
        obsidian_dir: Path,
    ) -> None:
        mock_poll.return_value = [_make_ntfy_message("save everywhere")]
        mock_sub.run.return_value = MagicMock(returncode=0)
        result = runner.invoke(capture.cli, ["process", "--route", "both"])
        assert result.exit_code == 0
        assert "memory" in result.output
        assert "obsidian" in result.output


class TestSendCommand:
    @patch("capture._send_message")
    def test_sends_message(self, mock_send: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_send.return_value = True
        result = runner.invoke(capture.cli, ["send", "PR merged!"])
        assert result.exit_code == 0
        assert "Sent" in result.output
        mock_send.assert_called_once_with("test-topic-abc123", "PR merged!", title=None)

    @patch("capture._send_message")
    def test_send_with_title(self, mock_send: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_send.return_value = True
        result = runner.invoke(capture.cli, ["send", "All green", "--title", "CI Status"])
        assert result.exit_code == 0
        mock_send.assert_called_once_with("test-topic-abc123", "All green", title="CI Status")

    @patch("capture._send_message")
    def test_send_failure(self, mock_send: MagicMock, runner: CliRunner, topic: str) -> None:
        mock_send.return_value = False
        result = runner.invoke(capture.cli, ["send", "fail"])
        assert result.exit_code == 1


class TestSendMessage:
    @patch("capture.urlopen")
    def test_success(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        assert capture._send_message("topic", "hello") is True

    @patch("capture.urlopen")
    def test_with_title(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        capture._send_message("topic", "hello", title="Title")
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_header("Title") == "Title"

    @patch("capture.urlopen")
    def test_url_error(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("fail")
        assert capture._send_message("topic", "hello") is False
