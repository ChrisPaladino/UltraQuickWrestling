import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.engine.match import Match
from src.engine.wrestler import Wrestler


class MatchModifierTests(unittest.TestCase):
    def setUp(self):
        self.face_data = {
            "name": "Face One",
            "persona": "Face",
            "overall": 1000,
            "overall_modifier": 0,
            "attributes": {
                "cheating": 100,
                "speed": 10,
                "tech": 25,
            },
            "heat_modifier": 0,
            "titles": [],
        }
        self.heel_data = {
            "name": "Heel One",
            "persona": "Heel",
            "overall": 1000,
            "overall_modifier": 0,
            "attributes": {
                "cheating": 0,
                "speed": 5,
                "tech": 5,
            },
            "heat_modifier": 0,
            "titles": [],
        }

        self.base_game_data = {
            "match_modifiers": [
                {"roll": 0, "modifier": "Cheating"},
                {"roll": 1, "modifier": "Normal"},
                {"roll": 2, "modifier": "Speed"},
                {"roll": 3, "modifier": "Technical"},
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

    def _build_match(self, match_type="TV Taping", game_data=None):
        return Match(
            self.face_data,
            self.heel_data,
            match_type,
            game_data or self.base_game_data,
            assigned_roles={"Face": "Face One", "Heel": "Heel One"},
            wrestlers_file="data/wrestlers.json",
        )

    def test_wrestler_uses_normalized_modifier(self):
        wrestler = Wrestler(
            {
                "name": "Normalizer",
                "persona": "Face",
                "overall": 1500,
                "attributes": {"Tech": 50, "brawl": 25},
            }
        )

        self.assertEqual(wrestler.get_match_rating("technical"), 1550)
        self.assertEqual(wrestler.get_match_rating("Tech"), 1550)
        self.assertEqual(wrestler.get_match_rating("Brawling"), 1525)
        self.assertEqual(wrestler.get_match_rating("Normal"), 1500)

    def test_match_cheating_modifier_affects_rating(self):
        match = self._build_match()
        # Random rolls: modifier (0 -> Cheating), pre-match chart (0 -> Face), pre-event roll (1 -> normal),
        # result roll (1 -> higher rated wins), post-match roll (1)
        with patch("random.randint", side_effect=[0, 0, 1, 1, 1]):
            log = match.simulate()

        self.assertIn("Match Modifier Rolled: Cheating", log)
        self.assertIn("Overall + Cheating + Adjustment = 1000 + 100 + 0 = 1100", log)
        self.assertIn("Overall + Cheating + Adjustment = 1000 + 0 + 0 = 1000", log)
        self.assertIn("Winner: Face One (Face)", log)

    def test_match_normal_modifier_uses_overall_only(self):
        match = self._build_match()
        with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
            log = match.simulate()

        self.assertIn("Match Modifier Rolled: Normal", log)
        self.assertIn("Overall + Normal + Adjustment = 1000 + 0 + 0 = 1000", log)

    def test_match_speed_modifier_uses_normalized_attribute(self):
        match = self._build_match()
        with patch("random.randint", side_effect=[2, 0, 1, 1, 1]):
            log = match.simulate()

        self.assertIn("Match Modifier Rolled: Speed", log)
        self.assertIn("Overall + Speed + Adjustment = 1000 + 10 + 0 = 1010", log)
        self.assertIn("Overall + Speed + Adjustment = 1000 + 5 + 0 = 1005", log)

    def test_apply_permanent_change_uses_wrestler_normalization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            roster_path = os.path.join(tmpdir, "wrestlers.json")
            with open(roster_path, "w") as f:
                json.dump(
                    {
                        "wrestlers": [
                            {
                                "name": "Face One",
                                "overall": 1000,
                                "overall_modifier": 0,
                                "attributes": {"technical": 10},
                                "heat_modifier": 0,
                                "titles": [],
                            },
                            {
                                "name": "Heel One",
                                "overall": 1000,
                                "overall_modifier": 0,
                                "attributes": {"technical": 5},
                                "heat_modifier": 0,
                                "titles": [],
                            },
                        ]
                    },
                    f,
                )

            match = Match(
                self.face_data,
                self.heel_data,
                "TV Taping",
                self.base_game_data,
                assigned_roles={"Face": "Face One", "Heel": "Heel One"},
                wrestlers_file=roster_path,
            )

            match.apply_permanent_change("FACE", "tech", 3)

            with open(roster_path) as f:
                updated = json.load(f)

            face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            self.assertEqual(face["attributes"]["technical"], 13)


if __name__ == "__main__":
    unittest.main()
