"""Tests for the discussion_partners ask_model.py CLI."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

# Import ask_model.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "ask_model",
    Path(__file__).resolve().parents[2]
    / "skills"
    / "discussion_partners"
    / "scripts"
    / "ask_model.py",
)
assert _spec is not None and _spec.loader is not None
ask_model = importlib.util.module_from_spec(_spec)
sys.modules["ask_model"] = ask_model
_spec.loader.exec_module(ask_model)


class TestParseProvider:
    """Test _parse_provider model string parsing."""

    def test_openai_prefix(self) -> None:
        key_name, prefix, thinking = ask_model._parse_provider("openai:gpt-5.2")
        assert key_name == "OPENAI_API_KEY"
        assert prefix == "openai"
        assert "openai_reasoning_effort" in thinking

    def test_openai_responses_prefix(self) -> None:
        key_name, prefix, thinking = ask_model._parse_provider("openai-responses:gpt-5.2")
        assert key_name == "OPENAI_API_KEY"
        assert prefix == "openai-responses"

    def test_anthropic_prefix(self) -> None:
        key_name, prefix, thinking = ask_model._parse_provider("anthropic:claude-opus-4-6")
        assert key_name == "ANTHROPIC_API_KEY"
        assert prefix == "anthropic"
        assert "anthropic_thinking" in thinking

    def test_google_prefix(self) -> None:
        key_name, prefix, thinking = ask_model._parse_provider("google-gla:gemini-2.5-pro")
        assert key_name == "GOOGLE_API_KEY"
        assert prefix == "google-gla"
        assert "google_thinking_config" in thinking

    def test_unknown_prefix_raises(self) -> None:
        with pytest.raises(click.BadParameter, match="Unknown model prefix 'unknown'"):
            ask_model._parse_provider("unknown:some-model")

    def test_no_colon_uses_whole_string_as_prefix(self) -> None:
        with pytest.raises(click.BadParameter, match="Unknown model prefix 'badmodel'"):
            ask_model._parse_provider("badmodel")


class TestProviderConfig:
    """Test PROVIDER_CONFIG data structure."""

    def test_all_providers_have_two_element_tuples(self) -> None:
        for prefix, config in ask_model.PROVIDER_CONFIG.items():
            assert len(config) == 2, (
                f"Provider {prefix} config should be (env_var, thinking_settings)"
            )
            env_var, thinking = config
            assert isinstance(env_var, str)
            assert isinstance(thinking, dict)

    def test_all_env_vars_end_with_key(self) -> None:
        for prefix, (env_var, _) in ask_model.PROVIDER_CONFIG.items():
            assert env_var.endswith("_KEY"), f"Provider {prefix} env var should end with _KEY"


class TestCLIMissingQuestion:
    """Test CLI behavior when question is missing."""

    def test_no_question_shows_error(self) -> None:
        result = CliRunner().invoke(ask_model.main, [])
        assert result.exit_code != 0

    def test_no_question_with_model_flag(self) -> None:
        result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2"])
        assert result.exit_code != 0


class TestCLIListModels:
    """Test --list-models flag."""

    def test_list_models_returns_models(self) -> None:
        result = CliRunner().invoke(ask_model.main, ["--list-models", ""])
        assert result.exit_code == 0
        assert len(result.output.strip().split("\n")) > 1

    def test_list_models_with_prefix_filter(self) -> None:
        result = CliRunner().invoke(ask_model.main, ["--list-models", "openai:"])
        assert result.exit_code == 0
        for line in result.output.strip().split("\n"):
            assert line.startswith("openai:")

    def test_list_models_ignores_question(self) -> None:
        """--list-models should work even without a question."""
        result = CliRunner().invoke(ask_model.main, ["--list-models", ""])
        assert result.exit_code == 0


class TestCLIMissingApiKey:
    """Test CLI behavior when API key is not set."""

    def test_missing_openai_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2", "What is 2+2?"])
        assert result.exit_code != 0
        assert "OPENAI_API_KEY not set" in result.output

    def test_missing_anthropic_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result = CliRunner().invoke(
            ask_model.main,
            ["--model", "anthropic:claude-opus-4-6", "What is 2+2?"],
        )
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY not set" in result.output

    def test_missing_google_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = CliRunner().invoke(
            ask_model.main,
            ["--model", "google-gla:gemini-2.5-pro", "What is 2+2?"],
        )
        assert result.exit_code != 0
        assert "GOOGLE_API_KEY not set" in result.output


class TestCLISuccessfulCall:
    """Test CLI with mocked API calls."""

    def test_successful_call_prints_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_result = MagicMock()
        mock_result.output = "The answer is 4."

        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result

        with patch.object(ask_model, "Agent", return_value=mock_agent) as mock_agent_cls:
            result = CliRunner().invoke(
                ask_model.main, ["--model", "openai:gpt-5.2", "What is 2+2?"]
            )

        assert result.exit_code == 0
        assert "The answer is 4." in result.output
        mock_agent_cls.assert_called_once()
        mock_agent.run_sync.assert_called_once()

    def test_custom_system_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_result = MagicMock()
        mock_result.output = "Done."

        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result

        with patch.object(ask_model, "Agent", return_value=mock_agent) as mock_agent_cls:
            result = CliRunner().invoke(
                ask_model.main,
                ["--system", "You are a math tutor.", "Explain calculus."],
            )

        assert result.exit_code == 0
        # Verify custom system prompt was passed to Agent
        call_kwargs = mock_agent_cls.call_args
        assert call_kwargs[1]["system_prompt"] == "You are a math tutor."

    def test_default_system_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_result = MagicMock()
        mock_result.output = "Response."

        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result

        with patch.object(ask_model, "Agent", return_value=mock_agent) as mock_agent_cls:
            CliRunner().invoke(ask_model.main, ["What is AI?"])

        call_kwargs = mock_agent_cls.call_args
        assert "discussion partner" in call_kwargs[1]["system_prompt"]


class TestCLIErrorHandling:
    """Test CLI error handling for API errors."""

    def test_insufficient_quota_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("insufficient_quota")

        with patch.object(ask_model, "Agent", return_value=mock_agent):
            result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2", "test"])

        assert result.exit_code != 0
        assert "insufficient quota" in result.output

    def test_invalid_api_key_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("invalid_api_key")

        with patch.object(ask_model, "Agent", return_value=mock_agent):
            result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2", "test"])

        assert result.exit_code != 0
        assert "invalid" in result.output

    def test_rate_limit_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("rate_limit exceeded")

        with patch.object(ask_model, "Agent", return_value=mock_agent):
            result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2", "test"])

        assert result.exit_code != 0
        assert "Rate limited" in result.output

    def test_generic_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("Something unexpected happened")

        with patch.object(ask_model, "Agent", return_value=mock_agent):
            result = CliRunner().invoke(ask_model.main, ["--model", "openai:gpt-5.2", "test"])

        assert result.exit_code != 0
        assert "Something unexpected happened" in result.output


class TestGetKnownModels:
    """Test _get_known_models helper."""

    def test_returns_sorted_list(self) -> None:
        models = ask_model._get_known_models()
        assert isinstance(models, list)
        assert models == sorted(models)
        assert len(models) > 0

    def test_contains_expected_prefixes(self) -> None:
        models = ask_model._get_known_models()
        prefixes = {m.split(":")[0] for m in models if ":" in m}
        assert "openai" in prefixes
        assert "anthropic" in prefixes
