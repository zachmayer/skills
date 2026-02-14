"""Unit tests for discussion_partners ask_model.py."""

from unittest.mock import MagicMock
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from skills.discussion_partners.scripts.ask_model import DEFAULT_MODEL
from skills.discussion_partners.scripts.ask_model import PROVIDER_CONFIG
from skills.discussion_partners.scripts.ask_model import _get_known_models
from skills.discussion_partners.scripts.ask_model import _parse_provider
from skills.discussion_partners.scripts.ask_model import main


class TestParseProvider:
    """Test _parse_provider model string parsing."""

    def test_openai_prefix(self) -> None:
        key_name, prefix, thinking = _parse_provider("openai:gpt-5.2")
        assert key_name == "OPENAI_API_KEY"
        assert prefix == "openai"
        assert "openai_reasoning_effort" in thinking

    def test_openai_responses_prefix(self) -> None:
        key_name, prefix, thinking = _parse_provider("openai-responses:gpt-5.2")
        assert key_name == "OPENAI_API_KEY"
        assert prefix == "openai-responses"

    def test_anthropic_prefix(self) -> None:
        key_name, prefix, thinking = _parse_provider("anthropic:claude-opus-4-6")
        assert key_name == "ANTHROPIC_API_KEY"
        assert prefix == "anthropic"
        assert "anthropic_thinking" in thinking

    def test_google_prefix(self) -> None:
        key_name, prefix, thinking = _parse_provider("google-gla:gemini-2.5-pro")
        assert key_name == "GOOGLE_API_KEY"
        assert prefix == "google-gla"
        assert "google_thinking_config" in thinking

    def test_unknown_prefix_raises(self) -> None:
        with pytest.raises(click.BadParameter, match="Unknown model prefix 'unknown'"):
            _parse_provider("unknown:some-model")

    def test_no_colon_uses_whole_string(self) -> None:
        """A model string without ':' uses the whole string as prefix."""
        with pytest.raises(click.BadParameter, match="Unknown model prefix 'nonexistent'"):
            _parse_provider("nonexistent")

    def test_all_configured_providers_parse(self) -> None:
        """Every provider in PROVIDER_CONFIG should parse successfully."""
        for prefix in PROVIDER_CONFIG:
            key_name, parsed_prefix, thinking = _parse_provider(f"{prefix}:test-model")
            assert parsed_prefix == prefix
            assert isinstance(key_name, str)
            assert isinstance(thinking, dict)


class TestGetKnownModels:
    """Test _get_known_models."""

    def test_returns_sorted_list(self) -> None:
        models = _get_known_models()
        assert isinstance(models, list)
        assert models == sorted(models)

    def test_contains_expected_prefixes(self) -> None:
        models = _get_known_models()
        prefixes = {m.split(":")[0] for m in models if ":" in m}
        assert "openai" in prefixes
        assert "anthropic" in prefixes


class TestCLI:
    """Test CLI behavior using Click's test runner."""

    def test_missing_question_shows_error(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "QUESTION" in result.output

    def test_list_models_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--list-models", ""])
        assert result.exit_code == 0
        assert len(result.output.strip().splitlines()) > 5

    def test_list_models_with_filter(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--list-models", "openai"])
        assert result.exit_code == 0
        for line in result.output.strip().splitlines():
            assert line.startswith("openai")

    def test_unknown_model_prefix_error(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--model", "badprefix:model", "question?"])
        assert result.exit_code != 0
        assert "Unknown model prefix" in result.output

    def test_missing_api_key_error(self) -> None:
        runner = CliRunner()
        env = {"OPENAI_API_KEY": ""}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code != 0
        assert "OPENAI_API_KEY" in result.output

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_successful_run(self, mock_agent_cls: MagicMock) -> None:
        """Test a successful end-to-end run with mocked Agent."""
        mock_result = MagicMock()
        mock_result.output = "The answer is 42."
        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "What is 6*7?"], env=env)
        assert result.exit_code == 0
        assert "The answer is 42." in result.output
        mock_agent.run_sync.assert_called_once()

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_custom_system_prompt(self, mock_agent_cls: MagicMock) -> None:
        """System prompt is passed to the Agent constructor."""
        mock_result = MagicMock()
        mock_result.output = "ok"
        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(
            main, ["--model", "openai:gpt-5.2", "--system", "Be concise.", "test?"], env=env
        )
        assert result.exit_code == 0
        mock_agent_cls.assert_called_once()
        _, kwargs = mock_agent_cls.call_args
        assert kwargs["system_prompt"] == "Be concise."

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_default_system_prompt(self, mock_agent_cls: MagicMock) -> None:
        """Default system prompt is used when none provided."""
        mock_result = MagicMock()
        mock_result.output = "ok"
        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code == 0
        _, kwargs = mock_agent_cls.call_args
        assert "discussion partner" in kwargs["system_prompt"]

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_insufficient_quota_error(self, mock_agent_cls: MagicMock) -> None:
        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("insufficient_quota")
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code != 0
        assert "insufficient quota" in result.output.lower()

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_invalid_api_key_error(self, mock_agent_cls: MagicMock) -> None:
        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("Incorrect API key provided")
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-bad-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code != 0
        assert "invalid" in result.output.lower()

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_rate_limit_error(self, mock_agent_cls: MagicMock) -> None:
        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("rate_limit exceeded 429")
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code != 0
        assert "rate limited" in result.output.lower()

    @patch("skills.discussion_partners.scripts.ask_model.Agent")
    def test_generic_error(self, mock_agent_cls: MagicMock) -> None:
        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("Something totally unexpected")
        mock_agent_cls.return_value = mock_agent

        runner = CliRunner()
        env = {"OPENAI_API_KEY": "sk-test-key"}
        result = runner.invoke(main, ["--model", "openai:gpt-5.2", "test?"], env=env)
        assert result.exit_code != 0
        assert "Something totally unexpected" in result.output

    def test_default_model_value(self) -> None:
        assert DEFAULT_MODEL == "openai:gpt-5.2"
