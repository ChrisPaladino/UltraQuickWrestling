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

    def _simulate_with_rolls(self, face, heel, roster_path, advanced_config, randint_side_effect, random_value=None):
        match = self._build_match(face, heel, roster_path, advanced_config)
        randint_patch = patch("random.randint", side_effect=randint_side_effect)
        if random_value is None:
            with randint_patch:
                log = match.simulate()
        else:
            with randint_patch, patch("random.random", return_value=random_value):
                log = match.simulate()

        with open(roster_path) as f:
            updated = json.load(f)
        return log, updated

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

    def test_persistent_modifiers_can_be_disabled(self):
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
                    "enable_persistent_modifiers": False,
                    "clean_win_bonus": 10,
                    "clean_loss_penalty": 5,
                    "injury_chance": 0,
                    "enable_seasons": False,
                },
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
                _ = match.simulate()

            with open(roster_path) as f:
                updated = json.load(f)
            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            updated_heel = next(w for w in updated["wrestlers"] if w["name"] == "Heel One")
            self.assertEqual(updated_face["heat_modifier"], 0)
            self.assertEqual(updated_heel["heat_modifier"], 0)
            self.assertEqual(updated_face.get("overall_modifier", 0), 0)
            self.assertEqual(updated_heel.get("overall_modifier", 0), 0)

    def test_heat_on_title_changes_alias_is_respected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Face One",
                "persona": "Face",
                "overall": 1100,
                "overall_modifier": 0,
                "titles": ["World"],
                "heat_modifier": 0,
            }
            heel = {
                "name": "Heel One",
                "persona": "Heel",
                "overall": 900,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            roster_path = self._build_roster([face, heel], tmpdir)
            match = self._build_match(
                face,
                heel,
                roster_path,
                {
                    "enabled": True,
                    "title_on_the_line": "World",
                    "title_overall_bonus": 5,
                    "heat_on_title_changes": False,
                    "enable_seasons": False,
                    "enable_heat": True,
                    "injury_chance": 0,
                },
            )

            with patch("random.randint", side_effect=[1, 0, 1, 1, 1]):
                _ = match.simulate()

            with open(roster_path) as f:
                updated = json.load(f)

            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Face One")
            self.assertEqual(updated_face.get("overall_modifier", 0), 5)
            self.assertEqual(updated_face.get("title_heat_bonus_applied", 0), 0)
            self.assertEqual(updated_face.get("heat_modifier", 0), 5)

    def test_clean_finish_updates_persistent_modifiers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            face = {
                "name": "Steady Face",
                "persona": "Face",
                "overall": 1050,
                "overall_modifier": 1,
                "titles": [],
                "heat_modifier": 1,
            }
            heel = {
                "name": "Risky Heel",
                "persona": "Heel",
                "overall": 950,
                "overall_modifier": -1,
                "titles": [],
                "heat_modifier": -1,
            }
            config = {
                "enabled": True,
                "clean_win_bonus": 5,
                "clean_loss_penalty": 2,
                "base_heat_delta": 3,
                "enable_heat": True,
                "enable_persistent_modifiers": True,
                "injury_chance": 0,
                "enable_seasons": False,
            }
            roster_path = self._build_roster([face, heel], tmpdir)

            log, updated = self._simulate_with_rolls(face, heel, roster_path, config, [1, 0, 1, 50, 1])

            self.assertIn("Clean finish", log)
            updated_face = next(w for w in updated["wrestlers"] if w["name"] == "Steady Face")
            updated_heel = next(w for w in updated["wrestlers"] if w["name"] == "Risky Heel")

            self.assertEqual(updated_face.get("overall_modifier", 0), 6)  # 1 + clean win bonus 5
            self.assertEqual(updated_heel.get("overall_modifier", 0), -3)  # -1 - clean loss penalty 2
            self.assertEqual(updated_face.get("heat_modifier", 0), 4)  # 1 + base_heat_delta 3
            self.assertEqual(updated_heel.get("heat_modifier", 0), -4)  # -1 - base_heat_delta 3

    def test_title_modifiers_sync_on_swaps(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            challenger = {
                "name": "Challenger",
                "persona": "Face",
                "overall": 1150,
                "overall_modifier": 0,
                "titles": [],
                "heat_modifier": 0,
            }
            champion = {
                "name": "Champion",
                "persona": "Heel",
                "overall": 1000,
                "overall_modifier": 0,
                "titles": ["World"],
                "heat_modifier": 0,
            }
            config = {
                "enabled": True,
                "title_on_the_line": "World",
                "title_overall_bonus": 4,
                "base_heat_delta": 2,
                "enable_heat": True,
                "enable_title_overall_bonus": True,
                "enable_persistent_modifiers": True,
                "injury_chance": 0,
                "enable_seasons": False,
            }
            roster_path = self._build_roster([challenger, champion], tmpdir)

            first_log, updated_after_first = self._simulate_with_rolls(
                challenger, champion, roster_path, config, [1, 0, 1, 50, 1]
            )

            updated_challenger = next(w for w in updated_after_first["wrestlers"] if w["name"] == "Challenger")
            updated_champion = next(w for w in updated_after_first["wrestlers"] if w["name"] == "Champion")

            self.assertIn("wins the World", first_log)
            self.assertIn("World", updated_challenger.get("titles", []))
            self.assertNotIn("World", updated_champion.get("titles", []))
            self.assertEqual(updated_challenger.get("overall_modifier", 0), 4)
            self.assertEqual(updated_challenger.get("title_overall_bonus_applied", 0), 4)
            self.assertEqual(updated_challenger.get("heat_modifier", 0), 4)  # heat + title heat bonus
            self.assertEqual(updated_challenger.get("title_heat_bonus_applied", 0), 2)

            updated_champion["overall"] = 1300
            roster_path = self._build_roster([updated_challenger, updated_champion], tmpdir)

            second_log, updated_after_second = self._simulate_with_rolls(
                updated_challenger, updated_champion, roster_path, config, [1, 0, 1, 50, 1]
            )

            final_challenger = next(w for w in updated_after_second["wrestlers"] if w["name"] == "Challenger")
            final_champion = next(w for w in updated_after_second["wrestlers"] if w["name"] == "Champion")

            self.assertIn("wins the World", second_log)
            self.assertNotIn("World", final_challenger.get("titles", []))
            self.assertIn("World", final_champion.get("titles", []))

            self.assertEqual(final_challenger.get("overall_modifier", 0), 0)
            self.assertEqual(final_challenger.get("title_overall_bonus_applied", 0), 0)
            self.assertEqual(final_challenger.get("heat_modifier", 0), 0)
            self.assertEqual(final_challenger.get("title_heat_bonus_applied", 0), 0)

            self.assertEqual(final_champion.get("overall_modifier", 0), 4)
            self.assertEqual(final_champion.get("title_overall_bonus_applied", 0), 4)
            self.assertEqual(final_champion.get("heat_modifier", 0), 2)  # heat delta + title heat bonus
            self.assertEqual(final_champion.get("title_heat_bonus_applied", 0), 2)


if __name__ == "__main__":
    unittest.main()
