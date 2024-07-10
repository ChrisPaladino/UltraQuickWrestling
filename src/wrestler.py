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