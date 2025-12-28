import json
import os
import tempfile
import unittest
from copy import deepcopy
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
            "tag_result_chart": [
                {"difference": "0-9999", "high_rated_wins": "1-100", "low_rated_wins": "101-200"}
            ],
            "tag_win_charts": {
                "TV Taping": {
                    "Face": [{"range": "1-100", "result": "Tag Clean Win"}],
                    "Heel": [{"range": "1-100", "result": "Tag Heel Win"}],
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

    def test_tag_match_averages_team_overalls_and_tag_ratings(self):
        face_team = [
            {
                "name": "Face Captain",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 40,
                "attributes": {"tag": 30},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Face Partner",
                "persona": "Face",
                "overall": 900,
                "overall_modifier": 0,
                "attributes": {"tag": 10},
                "heat_modifier": 0,
                "titles": [],
            },
        ]
        heel_team = [
            {
                "name": "Heel Bruiser",
                "persona": "Heel",
                "overall": 940,
                "overall_modifier": 10,
                "attributes": {"tag": 5},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Heel Rogue",
                "persona": "Heel",
                "overall": 960,
                "overall_modifier": -10,
                "attributes": {"tag": 15},
                "heat_modifier": 0,
                "titles": [],
            },
        ]

        match = TagMatch(
            face_team,
            heel_team,
            "TV Taping",
            self.base_game_data,
            assigned_roles={"Face": ["Face Captain", "Face Partner"], "Heel": ["Heel Bruiser", "Heel Rogue"]},
        )

        with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
            log = match.simulate()

        self.assertIn("Overall + Tag + Normal + Adjustment = 970.0 + 20.0 + 0 + 0 = 990.0", log)
        self.assertIn("Overall + Tag + Normal + Adjustment = 950.0 + 10.0 + 0 + 0 = 960.0", log)

    def test_pre_match_events_and_team_adjustments_apply(self):
        game_data = deepcopy(self.base_game_data)
        game_data["pre_match_chart"] = [{"roll": 0, "result": "Heel"}]
        game_data["pre_match_events"]["Heel"] = [
            {
                "roll": "5",
                "event": "Momentum Swing",
                "description": "{wrestler} rallies the crowd",
                "effect": {"target": "HEEL", "attribute": "Overall", "change": 40, "duration": "This match only"},
            }
        ]

        face_team = [
            {
                "name": "Face Captain",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 20},
                "heat_modifier": 15,
                "titles": [],
            },
            {
                "name": "Face Partner",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 20},
                "heat_modifier": 5,
                "titles": [],
            },
        ]
        heel_team = [
            {
                "name": "Heel Bruiser",
                "persona": "Heel",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 10},
                "heat_modifier": -10,
                "titles": [],
            },
            {
                "name": "Heel Rogue",
                "persona": "Heel",
                "overall": 1000,
                "overall_modifier": 0,
                "attributes": {"tag": 10},
                "heat_modifier": 0,
                "titles": [],
            },
        ]

        roster = {
            "wrestlers": [
                {
                    "name": "Face Captain",
                    "persona": "Face",
                    "overall": 1000,
                    "overall_modifier": 0,
                    "attributes": {"tag": 20},
                    "heat_modifier": 15,
                    "injured": True,
                    "injury_duration": 2,
                    "titles": [],
                },
                {
                    "name": "Face Partner",
                    "persona": "Face",
                    "overall": 1000,
                    "overall_modifier": 0,
                    "attributes": {"tag": 20},
                    "heat_modifier": 5,
                    "titles": [],
                },
                {
                    "name": "Heel Bruiser",
                    "persona": "Heel",
                    "overall": 1000,
                    "overall_modifier": 0,
                    "attributes": {"tag": 10},
                    "heat_modifier": -10,
                    "titles": [],
                },
                {
                    "name": "Heel Rogue",
                    "persona": "Heel",
                    "overall": 1000,
                    "overall_modifier": 0,
                    "attributes": {"tag": 10},
                    "heat_modifier": 0,
                    "titles": [],
                },
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            json.dump(roster, tmp)
            roster_path = tmp.name

        try:
            match = TagMatch(
                face_team,
                heel_team,
                "TV Taping",
                game_data,
                assigned_roles={"Face": ["Face Captain", "Face Partner"], "Heel": ["Heel Bruiser", "Heel Rogue"]},
                wrestlers_file=roster_path,
                advanced_rules_config={"enabled": True, "enable_persistent_modifiers": True, "enable_heat": True, "enable_injuries": True},
            )

            with patch("random.randint", side_effect=[1, 0, 5, 1, 1]):
                log = match.simulate()
        finally:
            os.remove(roster_path)

        self.assertIn("Face Captain is injured (2 weeks left)", log)
        self.assertIn("Face Captain carries heat modifier +15", log)
        self.assertIn("Heel Bruiser carries heat modifier -10", log)
        self.assertIn("Pre-Match Event (Heel): Heel Bruiser & Heel Rogue rallies the crowd", log)
        self.assertIn("Overall + Tag + Normal + Adjustment = 1000.0 + 20.0 + 0 + -40.0 = 980.0", log)
        self.assertIn("Overall + Tag + Normal + Adjustment = 1000.0 + 10.0 + 0 + 35.0 = 1045.0", log)

    def test_tag_specific_result_chart_drives_outcome(self):
        game_data = deepcopy(self.base_game_data)
        game_data["result_chart"] = [
            {"difference": "0-9999", "high_rated_wins": "1-10", "low_rated_wins": "11-100"}
        ]
        game_data["tag_result_chart"] = [
            {"difference": "0-9999", "high_rated_wins": "1-100", "low_rated_wins": "101-200"}
        ]

        face_team = [
            {
                "name": "Face One",
                "persona": "Face",
                "overall": 1050,
                "overall_modifier": 0,
                "attributes": {"tag": 25},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Face Two",
                "persona": "Face",
                "overall": 1050,
                "overall_modifier": 0,
                "attributes": {"tag": 25},
                "heat_modifier": 0,
                "titles": [],
            },
        ]
        heel_team = [
            {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 900,
                "overall_modifier": 0,
                "attributes": {"tag": 5},
                "heat_modifier": 0,
                "titles": [],
            },
            {
                "name": "Heel Two",
                "persona": "Heel",
                "overall": 900,
                "overall_modifier": 0,
                "attributes": {"tag": 5},
                "heat_modifier": 0,
                "titles": [],
            },
        ]

        match = TagMatch(
            face_team,
            heel_team,
            "TV Taping",
            game_data,
            assigned_roles={"Face": ["Face One", "Face Two"], "Heel": ["Heel One", "Heel Two"]},
        )

        with patch("random.randint", side_effect=[1, 0, 1, 50, 1]):
            log = match.simulate()

        self.assertIn("Winner: Face One & Face Two (Face)", log)
        self.assertIn("Tag Clean Win", log)


if __name__ == "__main__":
    unittest.main()
