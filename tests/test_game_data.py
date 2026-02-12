import copy
import pytest

from src.engine.game_data import normalize_game_data


def _base_payload():
    return {
        "match_modifiers": [],
        "pre_match_chart": [],
        "pre_match_events": {"Face": [], "Heel": []},
        "result_chart": [{"difference": "0-10", "high_rated_wins": "1-100", "low_rated_wins": "101-200"}],
        "win_charts": {"TV Taping": {"Face": [], "Heel": []}},
    }


def test_normalize_adds_tag_defaults_without_mutating_original():
    raw = _base_payload()
    normalized = normalize_game_data(raw)

    assert "tag_result_chart" in normalized
    assert "tag_win_charts" in normalized
    assert normalized["tag_result_chart"] == raw["result_chart"]
    assert normalized["tag_win_charts"] == raw["win_charts"]
    assert normalized["tag_result_chart"] is not raw["result_chart"]
    assert normalized["tag_win_charts"] is not raw["win_charts"]
    assert "tag_result_chart" not in raw
    assert "tag_win_charts" not in raw


def test_normalize_raises_for_missing_keys():
    raw = _base_payload()
    bad = copy.deepcopy(raw)
    bad.pop("result_chart")

    with pytest.raises(ValueError):
        normalize_game_data(bad)
