import random

class Match:
    def __init__(self, wrestler_a, wrestler_b, match_type, game_data):
        self.wrestler_a = Wrestler(wrestler_a)
        self.wrestler_b = Wrestler(wrestler_b)
        self.match_type = match_type
        self.game_data = game_data
        self.rating_a = 0
        self.rating_b = 0

    def resolve_match(self):
        results = []

        self.rating_a = self.wrestler_a.get_rating(self.match_type)
        self.rating_b = self.wrestler_b.get_rating(self.match_type)
        results.append(f"Initial Ratings - {self.wrestler_a.name}: {self.rating_a}, {self.wrestler_b.name}: {self.rating_b}")

        modifier = self.game_data['modifiers'].get(self.match_type, None)
        if modifier:
            mod_type = modifier['type']
            if mod_type == 'Use Savvy':
                if self.wrestler_a.savvy > self.wrestler_b.savvy:
                    self.rating_a += 1
                    results.append(f"{self.wrestler_a.name} gains +1 for higher Savvy.")
                elif self.wrestler_b.savvy > self.wrestler_a.savvy:
                    self.rating_b += 1
                    results.append(f"{self.wrestler_b.name} gains +1 for higher Savvy.")
            elif mod_type == 'Use Speed':
                if self.wrestler_a.speed > self.wrestler_b.speed:
                    self.rating_a += 1
                    results.append(f"{self.wrestler_a.name} gains +1 for higher Speed.")
                elif self.wrestler_b.speed > self.wrestler_a.speed:
                    self.rating_b += 1
                    results.append(f"{self.wrestler_b.name} gains +1 for higher Speed.")

        # Pre-match events
        pre_match_text = self.handle_pre_match()
        results.append(pre_match_text)

        point_diff = abs(self.rating_a - self.rating_b)
        roll = random.randint(1, 100)

        if self.rating_a > self.rating_b:
            if roll <= 75:
                winner = self.wrestler_a.name
            else:
                winner = self.wrestler_b.name
        elif self.rating_b > self.rating_a:
            if roll <= 75:
                winner = self.wrestler_b.name
            else:
                winner = self.wrestler_a.name
        else:
            winner = self.wrestler_a.name if roll <= 50 else self.wrestler_b.name

        results.append(f"Match Roll: {roll}")
        results.append(f"Winner: {winner}")

        return "\n".join(results)

    def handle_pre_match(self):
        PRE_MATCH_EVENTS = [
            {
                "description": "A surprise manager returns to ringside for {wrestler}, boosting their confidence!",
                "rating_bonus": 1
            },
            {
                "description": "{wrestler} jumps the bell and attacks before the match begins!",
                "rating_bonus": 2
            },
            {
                "description": "A fan distraction throws {opponent} off their game.",
                "rating_penalty": 1
            },
            {
                "description": "{wrestler} delivers a backstage promo that electrifies the crowd!",
                "rating_bonus": 1
            },
            {
                "description": "Security scuffle! {wrestler} arrives flustered, losing momentum.",
                "rating_penalty": 2
            }
        ]

        event_roll = random.randint(1, 100)
        if event_roll > 25:
            return "No pre-match events occurred."

        event = random.choice(PRE_MATCH_EVENTS)
        target = random.choice(['A', 'B'])

        if target == 'A':
            wrestler = self.wrestler_a
            opponent = self.wrestler_b
        else:
            wrestler = self.wrestler_b
            opponent = self.wrestler_a

        desc = event['description'].format(wrestler=wrestler.name, opponent=opponent.name)

        bonus = event.get("rating_bonus", 0)
        penalty = event.get("rating_penalty", 0)

        if bonus:
            if target == 'A':
                self.rating_a += bonus
            else:
                self.rating_b += bonus
        if penalty:
            if target == 'A':
                self.rating_a -= penalty
            else:
                self.rating_b -= penalty

        return f"PRE-MATCH EVENT: {desc}"


class Wrestler:
    def __init__(self, data):
        self.name = data.get("name")
        self.overall = data.get("overall", 0)
        self.cheat = data.get("cheat", 0)
        self.speed = data.get("speed", 0)
        self.savvy = data.get("savvy", 0)
        self.heat = data.get("heat", 0)

    def get_rating(self, match_type):
        return self.overall
