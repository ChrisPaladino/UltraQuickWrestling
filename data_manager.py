import json

class DataManager:
    @staticmethod
    def load_wrestlers():
        with open('wrestlers.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def save_wrestlers(wrestlers):
        with open('wrestlers.json', 'w') as f:
            json.dump(wrestlers, f)

    # Add more data management methods as needed