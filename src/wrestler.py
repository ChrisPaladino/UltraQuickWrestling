class Wrestler:
    def __init__(self, data):
        self.name = data['name']
        self.persona = data['persona']
        self.finisher = data['finisher']
        self.attributes = data['attributes']
        self.overall = data['overall']
        self.heat = data.get('heat', 0)
        self.temporary_adjustments = {}
        self.record = data.get('record', {'wins': 0, 'losses': 0, 'draws': 0})
        self.injured = data.get('injured', False)
        self.injury_duration = data.get('injury_duration', 0)
        self.image = data.get('image')

    def adjust_overall(self, change):
        self.overall += change

    def adjust_heat(self, change):
        self.heat += change

    def apply_modifier(self, modifier):
        modifier_value = self.attributes.get(modifier.lower(), 0)
        self.temporary_adjustments['modifier'] = modifier_value
        return modifier_value  # Return the modifier value for logging

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def get_adjusted_overall(self):
        return self.overall + sum(self.temporary_adjustments.values())

    def get_attribute(self, attr):
        return self.attributes.get(attr.lower(), 0)

    def reset_temporary_adjustments(self):
        self.temporary_adjustments = {}

    def to_dict(self):
        return {
            'name': self.name,
            'persona': self.persona,
            'finisher': self.finisher,
            'overall': self.overall,
            'attributes': self.attributes,
            'image': self.image,
            'heat': self.heat,
            'record': self.record,
            'injured': self.injured,
            'injury_duration': self.injury_duration
        }

    def update_record(self, result):
        if result == 'win':
            self.record['wins'] += 1
        elif result == 'loss':
            self.record['losses'] += 1
        else:
            self.record['draws'] += 1