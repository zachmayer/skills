"""Tests for the march_madness fetch_odds.py CLI."""

import csv
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Import fetch_odds.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "fetch_odds",
    Path(__file__).resolve().parents[2] / "skills" / "march_madness" / "scripts" / "fetch_odds.py",
)
assert _spec is not None and _spec.loader is not None
fetch_odds = importlib.util.module_from_spec(_spec)
sys.modules["fetch_odds"] = fetch_odds
_spec.loader.exec_module(fetch_odds)


# --- Fixtures ---

SAMPLE_GAME_ODDS_RESPONSE = [
    {
        "id": "event1",
        "sport_key": "basketball_ncaab",
        "home_team": "Duke Blue Devils",
        "away_team": "North Carolina Tar Heels",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": -150},
                            {"name": "North Carolina Tar Heels", "price": 130},
                        ],
                    }
                ],
            },
            {
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": -145},
                            {"name": "North Carolina Tar Heels", "price": 125},
                        ],
                    }
                ],
            },
        ],
    },
    {
        "id": "event2",
        "sport_key": "basketball_ncaab",
        "home_team": "Kansas Jayhawks",
        "away_team": "Kentucky Wildcats",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Kansas Jayhawks", "price": -200},
                            {"name": "Kentucky Wildcats", "price": 170},
                        ],
                    }
                ],
            },
        ],
    },
]

SAMPLE_FUTURES_RESPONSE = [
    {
        "id": "futures1",
        "sport_key": "basketball_ncaab_championship_winner",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "outrights",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": 400},
                            {"name": "Kansas Jayhawks", "price": 600},
                            {"name": "Auburn Tigers", "price": 800},
                        ],
                    }
                ],
            },
            {
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [
                    {
                        "key": "outrights",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": 450},
                            {"name": "Kansas Jayhawks", "price": 550},
                        ],
                    }
                ],
            },
        ],
    },
]


def _mock_response(status_code: int = 200, data: list | None = None) -> MagicMock:
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {
        "x-requests-remaining": "99900",
        "x-requests-last": "1",
    }
    resp.json.return_value = data or []
    resp.text = json.dumps(data or [])
    return resp


# --- Tests for _parse_game_odds ---


class TestParseGameOdds:
    def test_basic_parsing(self) -> None:
        rows = fetch_odds._parse_game_odds(SAMPLE_GAME_ODDS_RESPONSE)
        assert len(rows) == 4  # 2 events x 2 teams each

    def test_team_names(self) -> None:
        rows = fetch_odds._parse_game_odds(SAMPLE_GAME_ODDS_RESPONSE)
        names = [r["teamname"] for r in rows]
        assert "Duke Blue Devils" in names
        assert "North Carolina Tar Heels" in names
        assert "Kansas Jayhawks" in names
        assert "Kentucky Wildcats" in names

    def test_bookmaker_columns(self) -> None:
        rows = fetch_odds._parse_game_odds(SAMPLE_GAME_ODDS_RESPONSE)
        duke = next(r for r in rows if r["teamname"] == "Duke Blue Devils")
        assert duke["draftkings"] == -150
        assert duke["fanduel"] == -145

    def test_missing_bookmaker_is_empty(self) -> None:
        rows = fetch_odds._parse_game_odds(SAMPLE_GAME_ODDS_RESPONSE)
        # Kentucky only has draftkings, not fanduel
        kentucky = next(r for r in rows if r["teamname"] == "Kentucky Wildcats")
        assert kentucky["draftkings"] == 170
        assert kentucky["fanduel"] == ""

    def test_empty_events(self) -> None:
        rows = fetch_odds._parse_game_odds([])
        assert rows == []


# --- Tests for _parse_futures ---


class TestParseFutures:
    def test_basic_parsing(self) -> None:
        rows = fetch_odds._parse_futures(SAMPLE_FUTURES_RESPONSE)
        assert len(rows) == 3  # Duke, Kansas, Auburn

    def test_team_names_sorted(self) -> None:
        rows = fetch_odds._parse_futures(SAMPLE_FUTURES_RESPONSE)
        names = [r["teamname"] for r in rows]
        assert names == sorted(names)

    def test_bookmaker_columns(self) -> None:
        rows = fetch_odds._parse_futures(SAMPLE_FUTURES_RESPONSE)
        duke = next(r for r in rows if r["teamname"] == "Duke Blue Devils")
        assert duke["draftkings"] == 400
        assert duke["fanduel"] == 450

    def test_missing_bookmaker_is_empty(self) -> None:
        rows = fetch_odds._parse_futures(SAMPLE_FUTURES_RESPONSE)
        auburn = next(r for r in rows if r["teamname"] == "Auburn Tigers")
        assert auburn["draftkings"] == 800
        assert auburn["fanduel"] == ""

    def test_empty_events(self) -> None:
        rows = fetch_odds._parse_futures([])
        assert rows == []


# --- Tests for CLI commands ---


class TestCLIMissingApiKey:
    def test_missing_odds_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ODDS_API_KEY", raising=False)
        result = CliRunner().invoke(fetch_odds.cli, ["game-odds"])
        assert result.exit_code != 0
        assert "ODDS_API_KEY not set" in result.output


class TestGameOddsCommand:
    @patch("fetch_odds.requests.get")
    def test_game_odds_success(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(200, SAMPLE_GAME_ODDS_RESPONSE)

        output = str(tmp_path / "game_odds.csv")
        result = CliRunner().invoke(fetch_odds.cli, ["game-odds", "--output", output])

        assert result.exit_code == 0
        assert "4 rows" in result.output
        assert Path(output).exists()

        # Verify CSV content
        with open(output) as f:
            reader = list(csv.DictReader(f))
        assert len(reader) == 4
        assert "teamname" in reader[0]
        assert "draftkings" in reader[0]

    @patch("fetch_odds.requests.get")
    def test_game_odds_inactive(self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(422)

        result = CliRunner().invoke(fetch_odds.cli, ["game-odds"])
        assert result.exit_code != 0


class TestMensFuturesCommand:
    @patch("fetch_odds.requests.get")
    def test_mens_futures_success(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(200, SAMPLE_FUTURES_RESPONSE)

        output = str(tmp_path / "mens_futures.csv")
        result = CliRunner().invoke(fetch_odds.cli, ["mens-futures", "--output", output])

        assert result.exit_code == 0
        assert "3 rows" in result.output
        assert Path(output).exists()


class TestWomensGameOddsCommand:
    @patch("fetch_odds.requests.get")
    def test_womens_game_odds_inactive_exits_clean(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When basketball_wncaab is inactive, should print message and exit 0."""
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(422)

        result = CliRunner().invoke(fetch_odds.cli, ["womens-game-odds"])
        assert result.exit_code == 0
        assert "not currently active" in result.output

    @patch("fetch_odds.requests.get")
    def test_womens_game_odds_active(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(200, SAMPLE_GAME_ODDS_RESPONSE)

        output = str(tmp_path / "womens_game_odds.csv")
        result = CliRunner().invoke(fetch_odds.cli, ["womens-game-odds", "--output", output])

        assert result.exit_code == 0
        assert "4 rows" in result.output

    @patch("fetch_odds.requests.get")
    def test_womens_output_schema_matches_game_odds(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Women's game odds should have same schema as men's game odds."""
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(200, SAMPLE_GAME_ODDS_RESPONSE)

        mens_output = str(tmp_path / "game_odds.csv")
        womens_output = str(tmp_path / "womens_game_odds.csv")

        CliRunner().invoke(fetch_odds.cli, ["game-odds", "--output", mens_output])
        CliRunner().invoke(fetch_odds.cli, ["womens-game-odds", "--output", womens_output])

        with open(mens_output) as f:
            mens_headers = f.readline().strip()
        with open(womens_output) as f:
            womens_headers = f.readline().strip()

        assert mens_headers == womens_headers


class TestFetchAllCommand:
    @patch("fetch_odds.requests.get")
    def test_fetch_all_with_all_active(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(200, SAMPLE_GAME_ODDS_RESPONSE)

        output_dir = str(tmp_path / "output")
        result = CliRunner().invoke(fetch_odds.cli, ["fetch-all", "--output-dir", output_dir])

        assert result.exit_code == 0
        assert Path(output_dir, "game_odds.csv").exists()
        assert Path(output_dir, "mens_futures.csv").exists()
        assert Path(output_dir, "womens_game_odds.csv").exists()

    @patch("fetch_odds.requests.get")
    def test_fetch_all_womens_inactive_nonfatal(
        self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """fetch-all should succeed even if womens odds are inactive."""
        monkeypatch.setenv("ODDS_API_KEY", "test-key")

        def side_effect(*args: object, **kwargs: object) -> MagicMock:
            url = args[0] if args else kwargs.get("url", "")
            assert isinstance(url, str)
            if "wncaab" in url:
                return _mock_response(422)
            return _mock_response(200, SAMPLE_GAME_ODDS_RESPONSE)

        mock_get.side_effect = side_effect

        output_dir = str(tmp_path / "output")
        result = CliRunner().invoke(fetch_odds.cli, ["fetch-all", "--output-dir", output_dir])

        assert result.exit_code == 0
        assert Path(output_dir, "game_odds.csv").exists()
        assert Path(output_dir, "mens_futures.csv").exists()
        # womens file should NOT exist since sport was inactive
        assert not Path(output_dir, "womens_game_odds.csv").exists()


class TestAPIErrorHandling:
    @patch("fetch_odds.requests.get")
    def test_401_invalid_key(self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "bad-key")
        mock_get.return_value = _mock_response(401)

        result = CliRunner().invoke(fetch_odds.cli, ["game-odds"])
        assert result.exit_code != 0
        assert "Invalid ODDS_API_KEY" in result.output

    @patch("fetch_odds.requests.get")
    def test_429_rate_limited(self, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_get.return_value = _mock_response(429)

        result = CliRunner().invoke(fetch_odds.cli, ["game-odds"])
        assert result.exit_code != 0
        assert "Rate limited" in result.output
