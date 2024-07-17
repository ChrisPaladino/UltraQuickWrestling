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
        self.pre_match_event = None
        self.unusual_result = None
        self.log = []

    def run_match(self):
        self.log.append(f"Match: {self.wrestler1.name} vs {self.wrestler2.name}")
        self.log.append(f"Match Type: {self.match_type}")
        
        self.apply_match_modifier()
        self.apply_pre_match_event()
        self.determine_winner()
        self.apply_win_result()
        
        return self.get_match_summary()

    def apply_match_modifier(self):
        self.match_modifier = self.data_manager.get_random_match_modifier()
        self.log.append(f"Match Modifier: {self.match_modifier}")
        
        # Apply modifier to wrestlers
        w1_mod = self.wrestler1.apply_modifier(self.match_modifier)
        w2_mod = self.wrestler2.apply_modifier(self.match_modifier)
        
        self.log.append(f"{self.wrestler1.name} {self.match_modifier} modifier: {w1_mod}")
        self.log.append(f"{self.wrestler2.name} {self.match_modifier} modifier: {w2_mod}")

    def apply_pre_match_event(self):
        pre_match_roll = random.randint(0, 9)
        persona = self.data_manager.get_pre_match_persona(pre_match_roll)
        self.pre_match_event = self.data_manager.get_pre_match_event(persona)
        self.log.append(f"Pre-Match Event Roll: {pre_match_roll} ({persona})")
        self.log.append(f"Pre-Match Event: {self.pre_match_event['event']}")
        self.apply_event_effect(self.pre_match_event['effect'])

    def determine_winner(self):
        w1_score = self.wrestler1.get_adjusted_overall()
        w2_score = self.wrestler2.get_adjusted_overall()
        
        self.log.append(f"{self.wrestler1.name} Adjusted Score: {w1_score}")
        self.log.append(f"{self.wrestler2.name} Adjusted Score: {w2_score}")
        
        point_differential = abs(w1_score - w2_score)
        high_rated_wrestler = self.wrestler1 if w1_score > w2_score else self.wrestler2
        low_rated_wrestler = self.wrestler2 if w1_score > w2_score else self.wrestler1

        win_chance = self.data_manager.get_win_chance(point_differential)
        roll = random.randint(1, 100)

        self.log.append(f"Point Differential: {point_differential}")
        self.log.append(f"Win Chance for {high_rated_wrestler.name}: {win_chance}%")
        self.log.append(f"Roll: {roll}")

        if roll <= win_chance:
            self.winner, self.loser = high_rated_wrestler, low_rated_wrestler
        else:
            self.winner, self.loser = low_rated_wrestler, high_rated_wrestler

        self.log.append(f"Winner: {self.winner.name}")

    def apply_win_result(self):
        roll = random.randint(1, 100)
        result = self.data_manager.get_win_result(self.match_type, self.winner.persona, roll)
        
        self.log.append(f"Win Result Roll: {roll}")
        
        if result == "Go To Unusual Results":
            self.apply_unusual_result()
        else:
            self.log.append(f"Match Result: {result}")

    def apply_unusual_result(self):
        self.unusual_result = self.data_manager.get_unusual_result()
        self.log.append(f"Unusual Result: {self.unusual_result['event']}")
        self.apply_event_effect(self.unusual_result['effect'])

    def apply_event_effect(self, effect):
        if effect is None:
            return
        
        if isinstance(effect, dict):
            target = self.wrestler1 if effect['target'] == self.wrestler1.persona else self.wrestler2
            if 'attribute' in effect:
                if effect['attribute'] == 'Overall':
                    target.adjust_overall(effect['change'])
                elif effect['attribute'] == 'Heat':
                    target.adjust_heat(effect['change'])
                
                if 'duration' in effect and effect['duration'] == 'This match only':
                    self.log.append(f"{target.name} {effect['attribute']} adjusted by {effect['change']} for this match")
                else:
                    self.log.append(f"{target.name} {effect['attribute']} permanently adjusted by {effect['change']}")

    def get_match_summary(self):
        return "\n".join(self.log)

class Wrestler:
    def __init__(self, data):
        self.name = data['name']
        self.persona = data['persona']
        self.finisher = data['finisher']
        self.attributes = data['attributes']
        self.overall = data['overall']
        self.heat = data.get('heat', 0)
        self.temporary_adjustments = {}

    def apply_modifier(self, modifier):
        modifier_value = self.attributes.get(modifier.lower(), 0)
        self.temporary_adjustments['modifier'] = modifier_value
        return modifier_value  # Return the modifier value for logging

    def get_adjusted_overall(self):
        return self.overall + sum(self.temporary_adjustments.values())

    def adjust_overall(self, change):
        self.overall += change

    def adjust_heat(self, change):
        self.heat += change

    def reset_temporary_adjustments(self):
        self.temporary_adjustments = {}

    def get_attribute(self, attr):
        return self.attributes.get(attr.lower(), 0)