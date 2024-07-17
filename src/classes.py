# Wrestler and Match classes

import random

class Match:
    def __init__(self, wrestler1, wrestler2, match_type, data_manager):
        self.wrestler1 = wrestler1
        self.wrestler2 = wrestler2
        self.match_type = match_type
        self.data_manager = data_manager
        self.winner = None
        self.loser = None
        self.match_modifier = None
        self.log = []

    def apply_match_modifier(self):
        self.match_modifier = self.data_manager.get_random_match_modifier()
        self.log.append(f"Match Modifier: {self.match_modifier}")

    def determine_result(self):
        roll = random.randint(1, 100)
        self.log.append(f"Result Roll: {roll}")
        
        result = self.data_manager.get_result(self.match_type, self.winner.persona, roll)
        self.log.append(f"Match Result: {result}")

    def determine_winner(self):
        w1_score = self.wrestler1.overall + self.wrestler1.get_attribute(self.match_modifier)
        w2_score = self.wrestler2.overall + self.wrestler2.get_attribute(self.match_modifier)
        
        self.log.append(f"{self.wrestler1.name} Score: {w1_score}")
        self.log.append(f"{self.wrestler2.name} Score: {w2_score}")
        
        if w1_score > w2_score:
            self.winner, self.loser = self.wrestler1, self.wrestler2
        elif w2_score > w1_score:
            self.winner, self.loser = self.wrestler2, self.wrestler1
        else:
            self.winner, self.loser = random.choice([(self.wrestler1, self.wrestler2), (self.wrestler2, self.wrestler1)])
        
        self.log.append(f"Winner: {self.winner.name}")

    def get_match_summary(self):
        return "\n".join(self.log)
    
    def run_match(self):
        self.log.append(f"Match: {self.wrestler1.name} vs {self.wrestler2.name}")
        self.log.append(f"Match Type: {self.match_type}")
        
        self.apply_match_modifier()
        self.determine_winner()
        self.determine_result()
        
        return self.get_match_summary()

class Wrestler:
    def __init__(self, data):
        self.name = data['name']
        self.persona = data['persona']
        self.finisher = data['finisher']
        self.overall = data['overall']
        self.heat = data.get('heat', 0)
        self.attributes = data.get('attributes', {})

    def __str__(self):
        return f"{self.name} ({self.persona})"

    def get_attribute(self, attr):
        return self.attributes.get(attr.lower(), 0)