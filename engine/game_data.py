from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


REQUIRED_GAME_DATA_KEYS = [
    "match_modifiers",
    "pre_match_chart",
    "pre_match_events",
    "result_chart",
    "win_charts",
]


def normalize_game_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the loaded game data structure.

    Ensures required keys are present and provides tag-specific defaults so
    downstream consumers can treat tag and singles odds independently without
    breaking legacy files that only defined singles charts.
    """

    if not isinstance(raw_data, dict):
        raise ValueError("Game data must be a dictionary of values")

    normalized = deepcopy(raw_data)

    missing = [key for key in REQUIRED_GAME_DATA_KEYS if key not in normalized]
    if missing:
        raise ValueError(f"Game data missing required keys: {', '.join(missing)}")

    normalized.setdefault("tag_result_chart", deepcopy(normalized["result_chart"]))
    normalized.setdefault("tag_win_charts", deepcopy(normalized["win_charts"]))

    return normalized
