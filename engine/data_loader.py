import json
import os

def load_json(filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Up from /engine/
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r") as f:
        return json.load(f)

def load_wrestlers():
    data = load_json("wrestlers.json")
    return data["wrestlers"]

def load_game_data():
    return load_json("game_data.json")
