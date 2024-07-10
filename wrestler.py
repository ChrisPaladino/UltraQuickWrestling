class Wrestler:
    def __init__(self, name, persona, finisher, attributes):
        self.name = name
        self.persona = persona  # 'FACE' or 'HEEL'
        self.finisher = finisher
        self.attributes = attributes
        self.heat = 0

    def __str__(self):
        return f"{self.name} ({self.persona})"

    def get_attribute(self, attr):
        return self.attributes.get(attr, 0)