import json
import os
from typing import Any, Dict, List

from engine.file_utils import safe_write_json
from engine.game_data import normalize_game_data


BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Up from /engine/
DATA_DIR = os.path.join(BASE_DIR, "data")


def data_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


def load_json(filename: str) -> Dict[str, Any]:
    filepath = data_path(filename)
    with open(filepath, "r") as f:
        return json.load(f)


def load_wrestlers() -> List[dict]:
    data = load_json("wrestlers.json")
    return data.get("wrestlers", [])


def load_belts() -> List[dict]:
    data = load_json("belts.json")
    return data.get("belts", [])


def save_wrestlers(wrestlers: List[dict]) -> None:
    payload = {"wrestlers": wrestlers}
    safe_write_json(data_path("wrestlers.json"), payload)


def save_belts(belts: List[dict]) -> None:
    payload = {"belts": belts}
    safe_write_json(data_path("belts.json"), payload)


def load_game_data():
    raw_data = load_json("game_data.json")
    return normalize_game_data(raw_data)
