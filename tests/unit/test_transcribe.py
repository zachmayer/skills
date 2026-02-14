"""Tests for the voice_notes transcription CLI."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Import transcribe.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "transcribe",
    Path(__file__).resolve().parents[2] / "skills" / "voice_notes" / "scripts" / "transcribe.py",
)
assert _spec is not None and _spec.loader is not None
transcribe = importlib.util.module_from_spec(_spec)
sys.modules["transcribe"] = transcribe
_spec.loader.exec_module(transcribe)


@pytest.fixture()
def audio_file(tmp_path: Path) -> Path:
    """Create a fake audio file."""
    f = tmp_path / "test.mp3"
    f.write_bytes(b"fake audio content")
    return f


@pytest.fixture()
def large_audio_file(tmp_path: Path) -> Path:
    """Create an audio file exceeding the size limit."""
    f = tmp_path / "large.mp3"
    f.write_bytes(b"x" * (26 * 1024 * 1024))  # 26MB
    return f


class TestInputValidation:
    def test_missing_api_key(self, audio_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = CliRunner().invoke(transcribe.transcribe, [str(audio_file)])
        assert result.exit_code != 0
        assert "OPENAI_API_KEY" in result.output

    def test_unsupported_format(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        f = tmp_path / "test.txt"
        f.write_text("not audio")
        result = CliRunner().invoke(transcribe.transcribe, [str(f)])
        assert result.exit_code != 0
        assert "Unsupported format" in result.output

    def test_file_too_large(self, large_audio_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        result = CliRunner().invoke(transcribe.transcribe, [str(large_audio_file)])
        assert result.exit_code != 0
        assert "too large" in result.output

    def test_nonexistent_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        result = CliRunner().invoke(transcribe.transcribe, ["/nonexistent/audio.mp3"])
        assert result.exit_code != 0


class TestSupportedFormats:
    @pytest.mark.parametrize(
        "ext", [".mp3", ".mp4", ".m4a", ".wav", ".webm", ".mpeg", ".mpga", ".oga", ".ogg"]
    )
    def test_accepted_format(
        self, tmp_path: Path, ext: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        f = tmp_path / f"test{ext}"
        f.write_bytes(b"fake audio")

        mock_transcript = MagicMock()
        mock_transcript.text = "hello world"

        with patch("openai.OpenAI") as mock_client:
            mock_client.return_value.audio.transcriptions.create.return_value = mock_transcript
            result = CliRunner().invoke(transcribe.transcribe, [str(f)])

        assert result.exit_code == 0
        assert "hello world" in result.output


class TestTranscription:
    def test_stdout_output(self, audio_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        mock_transcript = MagicMock()
        mock_transcript.text = "This is the transcribed text."

        with patch("openai.OpenAI") as mock_client:
            mock_client.return_value.audio.transcriptions.create.return_value = mock_transcript
            result = CliRunner().invoke(transcribe.transcribe, [str(audio_file)])

        assert result.exit_code == 0
        assert "This is the transcribed text." in result.output

    def test_file_output(
        self, audio_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        out_file = tmp_path / "transcript.txt"

        mock_transcript = MagicMock()
        mock_transcript.text = "Written to file."

        with patch("openai.OpenAI") as mock_client:
            mock_client.return_value.audio.transcriptions.create.return_value = mock_transcript
            result = CliRunner().invoke(
                transcribe.transcribe, [str(audio_file), "--output", str(out_file)]
            )

        assert result.exit_code == 0
        assert out_file.read_text() == "Written to file."
        assert "Transcript written to" in result.output

    def test_language_option(self, audio_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        mock_transcript = MagicMock()
        mock_transcript.text = "Hola mundo."

        with patch("openai.OpenAI") as mock_client:
            mock_create = mock_client.return_value.audio.transcriptions.create
            mock_create.return_value = mock_transcript
            result = CliRunner().invoke(
                transcribe.transcribe, [str(audio_file), "--language", "es"]
            )

            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["language"] == "es"

        assert result.exit_code == 0

    def test_no_language_omits_param(
        self, audio_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        mock_transcript = MagicMock()
        mock_transcript.text = "Auto detected."

        with patch("openai.OpenAI") as mock_client:
            mock_create = mock_client.return_value.audio.transcriptions.create
            mock_create.return_value = mock_transcript
            result = CliRunner().invoke(transcribe.transcribe, [str(audio_file)])

            call_kwargs = mock_create.call_args[1]
            assert "language" not in call_kwargs

        assert result.exit_code == 0

    def test_custom_model(self, audio_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
        mock_transcript = MagicMock()
        mock_transcript.text = "Custom model output."

        with patch("openai.OpenAI") as mock_client:
            mock_create = mock_client.return_value.audio.transcriptions.create
            mock_create.return_value = mock_transcript
            result = CliRunner().invoke(
                transcribe.transcribe, [str(audio_file), "--model", "whisper-1"]
            )

            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["model"] == "whisper-1"

        assert result.exit_code == 0

    def test_api_key_passed_to_client(
        self, audio_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
        mock_transcript = MagicMock()
        mock_transcript.text = "test"

        with patch("openai.OpenAI") as mock_client:
            mock_client.return_value.audio.transcriptions.create.return_value = mock_transcript
            CliRunner().invoke(transcribe.transcribe, [str(audio_file)])

            mock_client.assert_called_once_with(api_key="sk-test-key-123")


class TestConstants:
    def test_supported_formats_complete(self) -> None:
        expected = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".mpeg", ".mpga", ".oga", ".ogg"}
        assert transcribe.SUPPORTED_FORMATS == expected

    def test_max_file_size(self) -> None:
        assert transcribe.MAX_FILE_SIZE == 25 * 1024 * 1024
