import random

class GameLogic:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.match_types = ["TV Taping", "PPV", "No DQ", "Cage", "Specialty"]

    def create_match(self, wrestler1_name, wrestler2_name, match_type):
        wrestler1_data = self.data_manager.get_wrestler(wrestler1_name)
        wrestler2_data = self.data_manager.get_wrestler(wrestler2_name)
        
        if wrestler1_data and wrestler2_data:
            wrestler1 = Wrestler(wrestler1_data)
            wrestler2 = Wrestler(wrestler2_data)
            return Match(wrestler1, wrestler2, match_type)
        else:
            return None

    def run_match(self, match):
        match.determine_winner()
        return match.get_result()

    def get_match_modifier(self):
        modifiers = ["Normal", "Size", "Speed", "Strength", "Savvy", "Cheating", "Tech"]
        return random.choice(modifiers)

    def apply_match_modifier(self, match, modifier):
        if modifier != "Normal":
            w1_mod = match.wrestler1.get_attribute(modifier.lower())
            w2_mod = match.wrestler2.get_attribute(modifier.lower())
            match.wrestler1.overall += w1_mod
            match.wrestler2.overall += w2_mod

    # Add more game logic methods as needed