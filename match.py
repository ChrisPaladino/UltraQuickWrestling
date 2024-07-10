import random

class Match:
    def __init__(self, wrestler1, wrestler2, match_type="TV"):
        self.wrestler1 = wrestler1
        self.wrestler2 = wrestler2
        self.match_type = match_type
        self.winner = None

    def determine_winner(self):
        # Simplified logic for now
        w1_score = sum(self.wrestler1.attributes.values())
        w2_score = sum(self.wrestler2.attributes.values())
        
        if w1_score > w2_score:
            self.winner = self.wrestler1
        elif w2_score > w1_score:
            self.winner = self.wrestler2
        else:
            self.winner = random.choice([self.wrestler1, self.wrestler2])

    def apply_match_effects(self):
        # Implement match effects (heat changes, etc.)
        pass

    def get_result(self):
        return f"{self.winner.name} defeats {self.wrestler1.name if self.winner == self.wrestler2 else self.wrestler2.name} in a {self.match_type} match."