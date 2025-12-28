import json
import os
import tempfile
import unittest
from unittest.mock import patch

from engine.match import Match


class AdvancedRulesTests(unittest.TestCase):
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

    def _build_roster(self, wrestlers, tmpdir):
        roster_path = os.path.join(tmpdir, "wrestlers.json")
        with open(roster_path, "w") as f:
            json.dump({"wrestlers": wrestlers}, f, indent=2)
        return roster_path

    def _build_match(self, face_data, heel_data, roster_path, advanced_config):
        return Match(
            face_data,
            heel_data,
            "TV Taping",
            self.base_game_data,
            assigned_roles={"Face": face_data["name"], "Heel": heel_data["name"]},
            wrestlers_file=roster_path,
            advanced_rules_config=advanced_config,
        )

    def test_injury_penalty_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Face One",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "injured": True,
                "injury_duration": 1,
                "titles": [],
                "rivalry_id": None,
                "heat_modifier": 0,
            }
            heel = {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 950,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            roster_path = self._build_roster([face, heel], tmpdir)
            match = self._build_match(
                face,
                heel,
                roster_path,
                {"enabled": True, "injury_penalty": -25, "injury_chance": 0, "enable_seasons": False},
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
                log = match.simulate()

            self.assertIn("injured (1 weeks left)", log)
            self.assertIn("recovers from injury", log)
            with open(roster_path) as f:
                updated = json.load(f)
            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            self.assertFalse(updated_face["injured"])
            self.assertEqual(updated_face["injury_duration"], 0)

    def test_new_injury_applied_to_loser(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Face One",
                "persona": "Face",
                "overall": 1050,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            heel = {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 950,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            roster_path = self._build_roster([face, heel], tmpdir)
            match = self._build_match(
                face,
                heel,
                roster_path,
                {"enabled": True, "injury_chance": 1.0, "injury_duration": 2, "enable_seasons": False},
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]), patch("random.random", return_value=0.01):
                log = match.simulate()

            self.assertIn("suffers a new injury", log)
            with open(roster_path) as f:
                updated = json.load(f)
            updated_heel = next(w for w in updated["wrestlers"] if w["name"] == "Heel One")
            self.assertTrue(updated_heel["injured"])
            self.assertEqual(updated_heel["injury_duration"], 2)

    def test_title_change_on_win(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Face One",
                "persona": "Face",
                "overall": 1100,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            heel = {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 900,
                "overall_modifier": 0,
                "titles": ["World"],
                "heat_modifier": 0,
            }
            roster_path = self._build_roster([face, heel], tmpdir)
            match = self._build_match(
                face,
                heel,
                roster_path,
                {"enabled": True, "title_on_the_line": "World", "injury_chance": 0, "enable_seasons": False},
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
                log = match.simulate()

            self.assertIn("wins the World", log)
            with open(roster_path) as f:
                updated = json.load(f)
            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            updated_heel = next(w for w in updated["wrestlers"] if w["name"] == "Heel One")
            self.assertIn("World", updated_face["titles"])
            self.assertNotIn("World", updated_heel["titles"])

    def test_rivalry_heat_progression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Face One",
                "persona": "Face",
                "overall": 1000,
                "overall_modifier": 0,
                "titles": [],
                "rivalry_id": "R1",
                "heat_modifier": 0,
            }
            heel = {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 900,
                "overall_modifier": 0,
                "titles": [],
                "rivalry_id": "R1",
                "heat_modifier": 0,
            }
            roster_path = self._build_roster([face, heel], tmpdir)
            match = self._build_match(
                face,
                heel,
                roster_path,
                {
                    "enabled": True,
                    "rivalry_heat_bonus": 4,
                    "rivalry_heat_penalty": -2,
                    "base_heat_delta": 2,
                    "injury_chance": 0,
                    "enable_seasons": False,
                },
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
                log = match.simulate()

            self.assertIn("Rivalry escalates", log)
            with open(roster_path) as f:
                updated = json.load(f)
            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            updated_heel = next(w for w in updated["wrestlers"] if w["name"] == "Heel One")
            self.assertEqual(updated_face["heat_modifier"], 6)  # +2 base +4 rivalry
            self.assertEqual(updated_heel["heat_modifier"], -4)  # -2 base + -2 rivalry


if __name__ == "__main__":
    unittest.main()
