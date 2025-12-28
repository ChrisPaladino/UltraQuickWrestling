import unittest
from unittest.mock import patch

from engine.match import TagMatch, create_match


class TagMatchTests(unittest.TestCase):
    def setUp(self):
        self.base_game_data = {
            "match_modifiers": [
                {"roll": 0, "modifier": "Cheating"},
                {"roll": 1, "modifier": "Normal"},
            ],
            "pre_match_chart": [{"roll": 0, "result": "Face"}],
            "pre_match_events": {
                "Face": [{"roll": "1", "event": "Normal Match", "effect": None}],
                "Heel": [{"roll": "1", "event": "Normal Match", "effect": None}],
            },
            "result_chart": [{"difference": "0-9999", "high_rated_wins": "1-100", "low_rated_wins": "101-200"}],
            "win_charts": {
                "TV Taping": {
                    "Face": [{"range": "1-100", "result": "Clean Win"}],
                    "Heel": [{"range": "1-100", "result": "Clean Win"}],
                }
            },
            "unusual_results": [],
        }

    def test_tag_match_includes_tag_bonus(self):
        face_team = [
            {
                "name": "Face One",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 20, "technical": 10},
                "heat_modifier": 5,
                "titles": [],
            },
            {
                "name": "Face Two",
                "persona": "Face",
                "overall": 900,
                "overall_modifier": 0,
                "attributes": {"tag": 40, "technical": 0},
                "heat_modifier": 0,
                "titles": [],
            },
        ]
        heel_team = [
            {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 950,
                "overall_modifier": 0,
                "attributes": {"tag": 5, "technical": 5},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Heel Two",
                "persona": "Heel",
                "overall": 950,
                "overall_modifier": 0,
                "attributes": {"tag": 10, "technical": 0},
                "heat_modifier": 0,
                "titles": [],
            },
        ]

        match = TagMatch(
            face_team,
            heel_team,
            "TV Taping",
            self.base_game_data,
            assigned_roles={"Face": ["Face One", "Face Two"], "Heel": ["Heel One", "Heel Two"]},
        )

        with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
            log = match.simulate()

        self.assertIn("Overall + Tag + Normal + Adjustment", log)
        self.assertIn("980.0", log)  # 950 base + 30 tag bonus

    def test_factory_builds_tag_match(self):
        face_team = [{"name": "Face One", "persona": "Face", "overall": 1000}]
        heel_team = [{"name": "Heel One", "persona": "Heel", "overall": 1000}]

        match = create_match(
            face_team,
            heel_team,
            "TV Taping",
            self.base_game_data,
            assigned_roles={"Face": ["Face One"], "Heel": ["Heel One"]},
            tag_match=True,
        )

        self.assertIsInstance(match, TagMatch)

    def test_tag_match_prefers_tag_charts(self):
        face_team = [
            {
                "name": "Face One",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 0},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Face Two",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 0},
                "heat_modifier": 0,
                "titles": [],
            },
        ]
        heel_team = [
            {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 0},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Heel Two",
                "persona": "Heel",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 0},
                "heat_modifier": 0,
                "titles": [],
            },
        ]

        game_data = {
            **self.base_game_data,
            "tag_result_chart": [{"difference": "0-9999", "high_rated_wins": "1-20", "low_rated_wins": "21-100"}],
            "tag_win_charts": {
                "TV Taping": {
                    "Face": [{"range": "1-100", "result": "Tag Clean Win"}],
                    "Heel": [{"range": "1-100", "result": "Tag Clean Win"}],
                }
            },
        }

        match = TagMatch(
            face_team,
            heel_team,
            "TV Taping",
            game_data,
            assigned_roles={"Face": ["Face One", "Face Two"], "Heel": ["Heel One", "Heel Two"]},
        )

        with patch("random.randint", side_effect=[1, 0, 1, 50, 1]):
            log = match.simulate()

        self.assertIn("Winner: Heel One & Heel Two (Heel)", log)
        self.assertIn("Tag Clean Win", log)


if __name__ == "__main__":
    unittest.main()
