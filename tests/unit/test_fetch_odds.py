"""Tests for march_madness odds fetching and parsing."""

from skills.march_madness.scripts.fetch_odds import display_name
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


class TestDisplayName:
    def test_known_bookmaker(self):
        assert display_name("fanduel") == "FanDuel"
        assert display_name("williamhill_us") == "Caesars"

    def test_unknown_bookmaker(self):
        assert display_name("some_new_book") == "some_new_book"


class TestParseFutures:
    def test_basic_parsing(self):
        rows = parse_futures(SAMPLE_FUTURES)
        assert len(rows) == 3  # 3 teams

    def test_team_names(self):
        rows = parse_futures(SAMPLE_FUTURES)
        names = [r["team_name"] for r in rows]
        assert "Auburn Tigers" in names
        assert "Duke Blue Devils" in names
        assert "Houston Cougars" in names

    def test_wide_format(self):
        rows = parse_futures(SAMPLE_FUTURES)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["FanDuel"] == 600
        assert duke["DraftKings"] == 550

    def test_missing_bookmaker_is_none(self):
        rows = parse_futures(SAMPLE_FUTURES)
        auburn = next(r for r in rows if r["team_name"] == "Auburn Tigers")
        # Auburn only in FanDuel, not DraftKings
        assert auburn["FanDuel"] == 1000
        assert auburn["DraftKings"] is None

    def test_empty_data(self):
        assert parse_futures([]) == []


class TestParseGameOdds:
    def test_basic_parsing(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        # 1 game × 2 teams × 1 bookmaker = 2 rows
        assert len(rows) == 2

    def test_team_names(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        names = {r["team_name"] for r in rows}
        assert names == {"Duke Blue Devils", "North Carolina Tar Heels"}

    def test_h2h_odds(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["h2h"] == -180

    def test_spreads(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["spread_point"] == -4.5
        assert duke["spread_price"] == -110

    def test_totals(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        assert duke["total_point"] == 152.5
        assert duke["total_over"] == -110
        assert duke["total_under"] == -110

    def test_home_away(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        duke = next(r for r in rows if r["team_name"] == "Duke Blue Devils")
        unc = next(r for r in rows if r["team_name"] == "North Carolina Tar Heels")
        assert duke["is_home"] is True
        assert unc["is_home"] is False

    def test_bookmaker_name(self):
        rows = parse_game_odds(SAMPLE_GAME_ODDS)
        assert all(r["bookmaker"] == "FanDuel" for r in rows)

    def test_empty_data(self):
        assert parse_game_odds([]) == []
