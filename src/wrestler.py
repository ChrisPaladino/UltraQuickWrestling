class Wrestler:
    def __init__(self, data):
        self.__dict__.update(data)

    def __str__(self):
        return f"{self.name} ({self.persona})"

    def get_attribute(self, attr):
        return self.attributes.get(attr, 0)

    def get_specialty(self, match_type):
        return self.specialtyMatches.get(match_type, 0)