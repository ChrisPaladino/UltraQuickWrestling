# data_manager.py

import json
import os
import random

class DataManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.wrestlers = self.load_json('wrestlers.json').get('wrestlers', [])
        self.game_data = self.load_json('game_data.json')

    def add_wrestler(self, wrestler):
        self.wrestlers.append(wrestler.to_dict())
        self.save_wrestlers()

    def delete_wrestler(self, name):
        self.wrestlers = [w for w in self.wrestlers if w['name'] != name]
        self.save_wrestlers()

    def get_pre_match_event(self, persona):
        events = self.game_data['pre_match_events'].get(persona, [])
        roll = random.randint(1, 100)
        for event in events:
            start, end = map(int, event['roll'].split('-'))
            if start <= roll <= end:
                return event
        return {'event': 'No event', 'effect': None}
    
    def get_pre_match_persona(self, roll):
        return next(item['result'] for item in self.game_data['pre_match_chart'] if item['roll'] == str(roll))

    def get_random_match_modifier(self):
        roll = random.randint(0, 9)
        return next(mod['modifier'] for mod in self.game_data['match_modifiers'] if mod['roll'] == roll)

    def get_unusual_result(self):
        roll = random.randint(1, 100)
        for result in self.game_data['unusual_results']:
            roll_value = result['roll']
            if '-' in roll_value:
                start, end = map(int, roll_value.split('-'))
                if start <= roll <= end:
                    return result
            else:
                if roll == int(roll_value):
                    return result
        return {'event': 'No unusual event', 'effect': None}

    def get_win_chance(self, point_differential):
        for row in self.game_data['result_chart']:
            if self.in_range(point_differential, row['difference']):
                return int(row['high_rated_wins'].split('-')[1])
        return 51  # Default to 51% if no range is found

    def get_win_result(self, match_type, persona, roll):
        chart = self.game_data['win_charts'].get(match_type, {}).get(persona, [])
        for result in chart:
            start, end = map(int, result['range'].split('-'))
            if start <= roll <= end:
                return result['result']
        return "Normal win"  # Default result if no match is found

    def get_wrestler(self, name):
        for wrestler in self.wrestlers:
            if wrestler['name'].lower() == name.lower():
                return wrestler
        return None

    def get_wrestler_names(self):
        return [wrestler['name'] for wrestler in self.wrestlers]

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

    def save_json(self, filename, data):
        file_path = os.path.join(self.base_path, 'data', filename)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def save_wrestlers(self):
        wrestlers_data = {'wrestlers': self.wrestlers}
        self.save_json('wrestlers.json', wrestlers_data)

    def update_wrestler(self, updated_wrestler):
        wrestler_dict = updated_wrestler.to_dict()
        wrestler_exists = False
        for i, wrestler in enumerate(self.wrestlers):
            if wrestler['name'] == wrestler_dict['name']:
                self.wrestlers[i] = wrestler_dict
                wrestler_exists = True
                break
        if not wrestler_exists:
            self.wrestlers.append(wrestler_dict)
        self.save_wrestlers()

    @staticmethod
    def in_range(value, range_str):
        if range_str.endswith('or Less'):
            return value <= int(range_str.split()[0])
        elif range_str.startswith('1901 or More'):
            return value >= 1901
        else:
            start, end = map(int, range_str.split('-'))
            return start <= value <= end