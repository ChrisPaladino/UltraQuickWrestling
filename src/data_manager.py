import json
import os
import random

class DataManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.wrestlers = self.load_json('wrestlers.json')
        self.game_data = self.load_json('game_data.json')

    def load_json(self, filename):
        file_path = os.path.join(self.base_path, 'data', filename)
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {file_path}")
            return {}

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

    def get_random_match_modifier(self):
        roll = random.randint(0, 9)
        return next(mod['modifier'] for mod in self.game_data['match_modifiers'] if mod['roll'] == roll)

    def get_pre_match_persona(self, roll):
        return next(item['result'] for item in self.game_data['pre_match_chart'] if item['roll'] == roll)

    def get_pre_match_event(self, persona):
        events = self.pre_match_events.get(persona, [])
        roll = random.randint(1, 100)
        for event in events:
            start, end = map(int, event['roll'].split('-'))
            if start <= roll <= end:
                return event
        return {'event': 'No event', 'effect': None}

    def get_win_chance(self, point_differential):
        for row in self.result_chart:
            if self.in_range(point_differential, row['difference']):
                return int(row['high_rated_wins'].split('-')[1])
        return 51  # Default to 51% if no range is found

    def get_win_result(self, match_type, persona, roll):
        chart = self.win_charts.get(match_type, {}).get(persona, [])
        for result in chart:
            start, end = map(int, result['range'].split('-'))
            if start <= roll <= end:
                return result['result']
        return "Normal win"  # Default result if no match is found

    def get_unusual_result(self):
        roll = random.randint(1, 100)
        for result in self.unusual_results:
            start, end = map(int, result['roll'].split('-'))
            if start <= roll <= end:
                return result
        return {'event': 'No unusual event', 'effect': None}

    def get_wrestler(self, name):
        for wrestler in self.wrestlers:
            if wrestler['name'].lower() == name.lower():
                return wrestler
        return None

    @staticmethod
    def in_range(value, range_str):
        if range_str.endswith('or Less'):
            return value <= int(range_str.split()[0])
        elif range_str.startswith('1901 or More'):
            return value >= 1901
        else:
            start, end = map(int, range_str.split('-'))
            return start <= value <= end