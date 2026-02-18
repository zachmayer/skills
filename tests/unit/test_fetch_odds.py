"""Tests for march_madness fetch_odds.py parsing and CLI."""

import importlib.util
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


SAMPLE_FUTURES = [
    {
        "id": "abc123",
        "sport_key": "basketball_ncaab_championship_winner",
        "commence_time": "2026-04-07T00:00:00Z",
        "bookmakers": [
            {
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [
                    {
                        "key": "outrights",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": 600},
                            {"name": "Houston Cougars", "price": 800},
                            {"name": "Auburn Tigers", "price": 1000},
                        ],
                    }
                ],
            },
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "outrights",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": 550},
                            {"name": "Houston Cougars", "price": 850},
                        ],
                    }
                ],
            },
        ],
    }
]

SAMPLE_GAME_ODDS = [
    {
        "id": "game1",
        "sport_key": "basketball_ncaab",
        "commence_time": "2026-02-15T00:00:00Z",
        "home_team": "Duke Blue Devils",
        "away_team": "North Carolina Tar Heels",
        "bookmakers": [
            {
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": -180},
                            {"name": "North Carolina Tar Heels", "price": 150},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {"name": "Duke Blue Devils", "price": -110, "point": -4.5},
                            {"name": "North Carolina Tar Heels", "price": -110, "point": 4.5},
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": -110, "point": 152.5},
                            {"name": "Under", "price": -110, "point": 152.5},
                        ],
                    },
                ],
            },
        ],
    }
]


class TestParseFutures:
    """Test parse_futures function."""

    def test_basic_parsing(self) -> None:
        rows = fetch_odds.parse_futures(SAMPLE_FUTURES)
        assert len(rows) == 3

    def test_team_names_sorted(self) -> None:
        rows = fetch_odds.parse_futures(SAMPLE_FUTURES)
        names = [r["team_name"] for r in rows]
        assert names == ["Auburn Tigers", "Duke Blue Devils", "Houston Cougars"]

    def test_wide_format_uses_api_title(self) -> None:
        rows = fetch_odds.parse_futures(SAMPLE_FUTURES)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["FanDuel"] == 600
        assert duke["DraftKings"] == 550

    def test_missing_bookmaker_is_none(self) -> None:
        rows = fetch_odds.parse_futures(SAMPLE_FUTURES)
        auburn = next(r for r in rows if r["team_name"] == "Auburn Tigers")
        assert auburn["FanDuel"] == 1000
        assert auburn["DraftKings"] is None

    def test_empty_data(self) -> None:
        assert fetch_odds.parse_futures([]) == []

    def test_ignores_non_outright_markets(self) -> None:
        data = [
            {
                "bookmakers": [
                    {
                        "title": "FanDuel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [{"name": "Team A", "price": 100}],
                            }
                        ],
                    }
                ]
            }
        ]
        rows = fetch_odds.parse_futures(data)
        assert rows == []


class TestParseGameOdds:
    """Test parse_game_odds function."""

    def test_row_count(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        assert len(rows) == 2

    def test_team_names(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        assert {r["team_name"] for r in rows} == {"Duke Blue Devils", "North Carolina Tar Heels"}

    def test_h2h(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["h2h"] == -180

    def test_spreads(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["spread_point"] == -4.5
        assert duke["spread_price"] == -110

    def test_totals_are_game_level(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        for row in rows:
            assert row["total_point"] == 152.5

    def test_home_away(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        unc = next(r for r in rows if r["team_name"] == "North Carolina Tar Heels")
        assert duke["is_home"] is True
        assert unc["is_home"] is False

    def test_bookmaker_uses_api_title(self) -> None:
        rows = fetch_odds.parse_game_odds(SAMPLE_GAME_ODDS)
        assert all(r["bookmaker"] == "FanDuel" for r in rows)

    def test_empty_data(self) -> None:
        assert fetch_odds.parse_game_odds([]) == []

    def test_multiple_bookmakers(self) -> None:
        data = [
            {
                "id": "g1",
                "commence_time": "2026-02-15T00:00:00Z",
                "home_team": "Team A",
                "away_team": "Team B",
                "bookmakers": [
                    {
                        "key": "bk1",
                        "title": "Book1",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": -150},
                                    {"name": "Team B", "price": 130},
                                ],
                            }
                        ],
                    },
                    {
                        "key": "bk2",
                        "title": "Book2",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": -140},
                                    {"name": "Team B", "price": 120},
                                ],
                            }
                        ],
                    },
                ],
            }
        ]
        rows = fetch_odds.parse_game_odds(data)
        assert len(rows) == 4  # 2 teams * 2 bookmakers


class TestWriteCsv:
    """Test write_csv function."""

    def test_writes_csv(self, tmp_path: Path) -> None:
        rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        out = tmp_path / "test.csv"
        fetch_odds.write_csv(rows, out)
        content = out.read_text()
        assert "a,b" in content
        assert "1,2" in content

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        rows = [{"x": 1}]
        out = tmp_path / "sub" / "dir" / "test.csv"
        fetch_odds.write_csv(rows, out)
        assert out.exists()

    def test_empty_rows_no_file(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.csv"
        fetch_odds.write_csv([], out)
        assert not out.exists()


class TestCLIMissingApiKey:
    """Test CLI behavior when ODDS_API_KEY is not set."""

    def test_futures_missing_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ODDS_API_KEY", raising=False)
        result = CliRunner().invoke(fetch_odds.cli, ["futures"])
        assert result.exit_code != 0

    def test_game_odds_missing_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ODDS_API_KEY", raising=False)
        result = CliRunner().invoke(fetch_odds.cli, ["game-odds"])
        assert result.exit_code != 0

    def test_fetch_all_missing_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ODDS_API_KEY", raising=False)
        result = CliRunner().invoke(fetch_odds.cli, ["fetch-all"])
        assert result.exit_code != 0


class TestCLIWithMockedApi:
    """Test CLI commands with mocked API calls."""

    def _mock_response(self, data: list, status_code: int = 200) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = data
        resp.headers = {
            "x-requests-last": "1",
            "x-requests-remaining": "499",
        }
        resp.raise_for_status.return_value = None
        return resp

    def test_futures_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_resp = self._mock_response(SAMPLE_FUTURES)

        with patch("httpx.get", return_value=mock_resp):
            result = CliRunner().invoke(fetch_odds.cli, ["futures", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0
        assert (tmp_path / "mens_futures.csv").exists()

    def test_game_odds_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")
        mock_resp = self._mock_response(SAMPLE_GAME_ODDS)

        with patch("httpx.get", return_value=mock_resp):
            result = CliRunner().invoke(
                fetch_odds.cli, ["game-odds", "--output-dir", str(tmp_path)]
            )

        assert result.exit_code == 0
        assert (tmp_path / "game_odds.csv").exists()

    def test_fetch_all_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("ODDS_API_KEY", "test-key")

        futures_resp = self._mock_response(SAMPLE_FUTURES)
        game_resp = self._mock_response(SAMPLE_GAME_ODDS)

        call_count = 0

        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            url = args[0] if args else kwargs.get("url", "")
            if "championship_winner" in url:
                return futures_resp
            return game_resp

        with patch("httpx.get", side_effect=mock_get):
            result = CliRunner().invoke(
                fetch_odds.cli, ["fetch-all", "--output-dir", str(tmp_path)]
            )

        assert result.exit_code == 0
        assert (tmp_path / "mens_futures.csv").exists()
        assert (tmp_path / "game_odds.csv").exists()
