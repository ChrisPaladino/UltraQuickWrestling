from classes import Match, Wrestler

class GameLogic:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def create_match(self, wrestler1, wrestler2, match_type):
        return Match(wrestler1, wrestler2, match_type, self.data_manager)

    def get_wrestler(self, name):
        wrestler_data = next((w for w in self.data_manager.wrestlers if w['name'] == name), None)
        if wrestler_data:
            return Wrestler(wrestler_data)
        return None

    def run_match(self, match):
        return match.run_match()