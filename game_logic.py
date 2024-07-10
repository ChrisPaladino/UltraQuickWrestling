import random
from wrestler import Wrestler
from match import Match

class GameLogic:
    def __init__(self):
        self.wrestlers = []

    def load_wrestlers(self, wrestler_data):
        for data in wrestler_data:
            wrestler = Wrestler(data['name'], data['persona'], data['finisher'], data['attributes'])
            self.wrestlers.append(wrestler)

    def create_match(self, wrestler1, wrestler2, match_type="TV"):
        return Match(wrestler1, wrestler2, match_type)

    def run_match(self, match):
        match.determine_winner()
        match.apply_match_effects()
        return match.get_result()

    def apply_skill_modifier(self, match):
        # Implement skill modifier logic
        pass

    def roll_dice(self):
        return random.randint(1, 100)

    # Add more game logic methods as needed