import json
import os

from engine.game_data import normalize_game_data


def load_json(filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Up from /engine/
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r") as f:
        return json.load(f)

def load_wrestlers():
    data = load_json("wrestlers.json")
    return data["wrestlers"]

def load_game_data():
    raw_data = load_json("game_data.json")
    return normalize_game_data(raw_data)
