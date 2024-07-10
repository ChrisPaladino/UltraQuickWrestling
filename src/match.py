import random

class Match:
    def __init__(self, wrestler1, wrestler2, match_type, data_manager):
        self.wrestler1 = wrestler1
        self.wrestler2 = wrestler2
        self.match_type = match_type
        self.data_manager = data_manager
        self.winner = None
        self.pre_match_event = None
        self.in_match_event = None
        self.post_match_event = None

    def run_match(self):
        self.apply_pre_match_event()
        self.determine_winner()
        self.apply_post_match_event()
        self.update_heat()

    def apply_pre_match_event(self):
        events = self.data_manager.load_pre_match_events()
        self.pre_match_event = random.choice(events)
        # Apply the event's effects

    def determine_winner(self):
        w1_score = self.calculate_score(self.wrestler1)
        w2_score = self.calculate_score(self.wrestler2)
        
        if w1_score > w2_score:
            self.winner = self.wrestler1
        elif w2_score > w1_score:
            self.winner = self.wrestler2
        else:
            self.winner = random.choice([self.wrestler1, self.wrestler2])

        self.apply_in_match_event()

    def calculate_score(self, wrestler):
        base_score = wrestler.overall
        match_bonus = wrestler.get_specialty(self.match_type)
        modifier_bonus = self.apply_match_modifier(wrestler)
        return base_score + match_bonus + modifier_bonus

    def apply_match_modifier(self, wrestler):
        modifier = self.data_manager.get_random_match_modifier()
        return wrestler.get_attribute(modifier.lower())

    def apply_in_match_event(self):
        events = self.data_manager.load_in_match_events()
        self.in_match_event = random.choice(events)
        # Apply the event's effects

    def apply_post_match_event(self):
        events = self.data_manager.load_post_match_events()
        self.post_match_event = random.choice(events)
        # Apply the event's effects

    def update_heat(self):
        # Update heat based on match outcome and events
        pass

    def get_result(self):
        result = f"{self.winner.name} defeats {self.wrestler1.name if self.winner == self.wrestler2 else self.wrestler2.name} in a {self.match_type} match."
        if self.pre_match_event:
            result = f"Pre-match event: {self.pre_match_event}\n" + result
        if self.in_match_event:
            result += f"\nIn-match event: {self.in_match_event}"
        if self.post_match_event:
            result += f"\nPost-match event: {self.post_match_event}"
        return result