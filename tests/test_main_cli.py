import argparse
import unittest

from src.engine.match import TagMatch, create_match
from main import _build_match_from_args


class CLIMatchBuildTests(unittest.TestCase):
    def setUp(self):
        self.game_data = {
            "win_charts": {"TV Taping": {"Face": [], "Heel": []}},
            "match_modifiers": [],
            "pre_match_chart": [],
            "pre_match_events": {"Face": [], "Heel": []},
            "result_chart": [],
            "unusual_results": [],
        }
        self.wrestlers = [
            {"name": "Hero", "persona": "Face"},
            {"name": "Villain", "persona": "Heel"},
            {"name": "Face One", "persona": "Face"},
            {"name": "Face Two", "persona": "Face"},
            {"name": "Heel One", "persona": "Heel"},
            {"name": "Heel Two", "persona": "Heel"},
        ]

    def test_singles_alignment_accepts_role_lists(self):
        match = create_match(
            self.wrestlers[0],
            self.wrestlers[1],
            "TV Taping",
            self.game_data,
            assigned_roles={"Face": ["Hero"], "Heel": ["Villain"]},
        )

        self.assertEqual(match.face.name, "Hero")
        self.assertEqual(match.heel.name, "Villain")

    def test_build_match_from_args_tag_alignment_auto_assigns(self):
        args = argparse.Namespace(
            team_a="Face One,Face Two",
            team_b="Heel One,Heel Two",
            tag=True,
            face_team=None,
            match_type="TV Taping",
        )

        match = _build_match_from_args(args, self.wrestlers, self.game_data)

        self.assertIsInstance(match, TagMatch)
        self.assertEqual(match.face.member_names, ["Face One", "Face Two"])
        self.assertEqual(match.heel.member_names, ["Heel One", "Heel Two"])

    def test_build_match_from_args_requires_tag_for_multi_member(self):
        args = argparse.Namespace(
            team_a="Hero,Face One",
            team_b="Villain",
            tag=False,
            face_team=None,
            match_type="TV Taping",
        )

        with self.assertRaises(ValueError):
            _build_match_from_args(args, self.wrestlers, self.game_data)


if __name__ == "__main__":
    unittest.main()
