"""Tests for march_madness odds fetching and parsing."""

from skills.march_madness.scripts.fetch_odds import parse_futures
from skills.march_madness.scripts.fetch_odds import parse_game_odds

# Sample API response for championship futures
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

# Sample API response for game odds
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
    def test_basic_parsing(self):
        rows = parse_futures(SAMPLE_FUTURES)
        assert len(rows) == 3

    def test_team_names_sorted(self):
        rows = parse_futures(SAMPLE_FUTURES)
        names = [r["team_name"] for r in rows]
        assert names == ["Auburn Tigers", "Duke Blue Devils", "Houston Cougars"]

    def test_wide_format_uses_api_title(self):
        rows = parse_futures(SAMPLE_FUTURES)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["FanDuel"] == 600
        assert duke["DraftKings"] == 550

    def test_missing_bookmaker_is_none(self):
        rows = parse_futures(SAMPLE_FUTURES)
        auburn = next(r for r in rows if r["team_name"] == "Auburn Tigers")
        assert auburn["FanDuel"] == 1000
        assert auburn["DraftKings"] is None

    def test_empty_data(self):
        assert parse_futures([]) == []


class TestParseGameOdds:
    def test_row_count(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        assert len(rows) == 2  # 1 game × 2 teams × 1 bookmaker

    def test_team_names(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        assert {r["team_name"] for r in rows} == {"Duke Blue Devils", "North Carolina Tar Heels"}

    def test_h2h(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["h2h"] == -180

    def test_spreads(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["spread_point"] == -4.5
        assert duke["spread_price"] == -110

    def test_totals_are_game_level(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        for row in rows:
            assert row["total_point"] == 152.5
            assert row["total_over"] == -110
            assert row["total_under"] == -110

    def test_home_away(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        unc = next(r for r in rows if r["team_name"] == "North Carolina Tar Heels")
        assert duke["is_home"] is True
        assert unc["is_home"] is False

    def test_bookmaker_uses_api_title(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        assert all(r["bookmaker"] == "FanDuel" for r in rows)

    def test_empty_data(self):
        assert parse_game_odds([]) == []
