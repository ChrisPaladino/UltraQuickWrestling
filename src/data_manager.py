import os
import json
import random

class DataManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.wrestlers_path = os.path.join(base_path, 'data', 'wrestlers', 'wrestlers.json')
        self.gamedata_path = os.path.join(base_path, 'data', 'gamedata')
        self.charts_path = os.path.join(base_path, 'data', 'charts')
        self.wrestlers = self.load_json(self.wrestlers_path)['wrestlers']

    def load_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def save_json(self, data, file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def get_wrestler(self, name):
        return next((w for w in self.wrestlers if w['name'].lower() == name.lower()), None)

    def add_wrestler(self, wrestler_data):
        self.wrestlers.append(wrestler_data)
        self.save_json({'wrestlers': self.wrestlers}, self.wrestlers_path)

    def update_wrestler(self, name, updated_data):
        for wrestler in self.wrestlers:
            if wrestler['name'].lower() == name.lower():
                wrestler.update(updated_data)
                self.save_json({'wrestlers': self.wrestlers}, self.wrestlers_path)
                return True
        return False

    def delete_wrestler(self, name):
        self.wrestlers = [w for w in self.wrestlers if w['name'].lower() != name.lower()]
        self.save_json({'wrestlers': self.wrestlers}, self.wrestlers_path)

    def load_match_modifiers(self):
        return self.load_json(os.path.join(self.gamedata_path, 'match_modifiers.json'))

    def load_match_types(self):
        return self.load_json(os.path.join(self.gamedata_path, 'match_types.json'))

    def load_result_chart(self):
        return self.load_json(os.path.join(self.charts_path, 'result_chart.json'))

    def load_pre_match_events(self):
        return self.load_json(os.path.join(self.gamedata_path, 'pre_match_events.json'))

    def load_in_match_events(self):
        return self.load_json(os.path.join(self.gamedata_path, 'in_match_events.json'))

    def load_post_match_events(self):
        return self.load_json(os.path.join(self.gamedata_path, 'post_match_events.json'))

    def get_random_match_modifier(self):
        modifiers = self.load_match_modifiers()
        return random.choice(modifiers)

    def update_wrestler_stats(self, wrestler, changes):
        for wrestler_data in self.wrestlers:
            if wrestler_data['name'] == wrestler.name:
                for key, value in changes.items():
                    if key in wrestler_data:
                        wrestler_data[key] += value
        self.save_json({'wrestlers': self.wrestlers}, self.wrestlers_path)

# Usage
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_manager = DataManager(base_path)
    
    # Example usage
    print(data_manager.get_wrestler("Ric Flair"))
    print(data_manager.load_match_modifiers())