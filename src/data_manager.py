import json
import os
import random

class DataManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.wrestlers = self.load_wrestlers()
        self.match_modifiers = self.load_json('match_modifiers.json').get('modifiers', [])
        self.win_charts = self.load_json('win_charts.json')

    def load_wrestlers(self):
        wrestlers_file = os.path.join(self.base_path, 'data', 'wrestlers', 'wrestlers.json')
        try:
            with open(wrestlers_file, 'r') as file:
                data = json.load(file)
                return data.get('wrestlers', [])
        except FileNotFoundError:
            print(f"File not found: {wrestlers_file}")
            return []
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {wrestlers_file}")
            return []

    def load_json(self, filename):
        file_path = os.path.join(self.base_path, 'data', 'gamedata', filename)
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {file_path}")
            return {}
        
    def get_result(self, match_type, persona, roll):
        chart = self.win_charts.get(match_type, {}).get(persona, [])
        for result in chart:
            start, end = map(int, result['range'].split('-'))
            if start <= roll <= end:
                return result['result']
        return "No result found"

    def get_wrestler(self, name):
        for wrestler in self.wrestlers:
            if wrestler['name'].lower() == name.lower():
                return wrestler
        return None

    def get_random_match_modifier(self):
        return random.choice(self.match_modifiers)['modifier']