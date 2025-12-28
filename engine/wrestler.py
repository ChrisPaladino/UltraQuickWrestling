class Wrestler:
    ATTRIBUTE_SYNONYMS = {
        "tech": "technical",
        "brawl": "brawling",
    }

    DEFAULT_ATTRIBUTES = {
        "strength": 0,
        "speed": 0,
        "savvy": 0,
        "technical": 0,
        "cheating": 0,
        "size": 0,
        "heat": 0,
        "cage": 0,
        "object": 0,
        "brawling": 0,
        "ladder": 0,
        "table": 0,
        "tag": 0,
    }

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.finisher = data.get("finisher")
        self.persona = data.get("persona")  # "Face" or "Heel"
        self.overall = data.get("overall", 0)

        known_keys = {"name", "finisher", "persona", "overall", "attributes"}
        raw_attributes = dict(data.get("attributes", {}))
        for key, value in data.items():
            if key not in known_keys:
                raw_attributes.setdefault(key, value)
        normalized_attributes = {}
        for key, value in raw_attributes.items():
            normalized_key = self.ATTRIBUTE_SYNONYMS.get(key.lower(), key.lower())
            normalized_attributes[normalized_key] = value

        self.attributes = {**self.DEFAULT_ATTRIBUTES, **normalized_attributes}

        # Expose attribute modifiers as direct attributes for convenience
        for key, value in self.attributes.items():
            setattr(self, key, value)

    def get_match_rating(self, modifier: str = "normal") -> int:
        if modifier.lower() == "normal":
            return self.overall
        return self.overall + self.attributes.get(modifier.lower(), 0)
