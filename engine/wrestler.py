class Wrestler:
    ATTRIBUTE_ALIASES = {
        "tech": "technical",
        "technical": "technical",
        "brawl": "brawling",
        "brawling": "brawling",
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

    NON_ATTRIBUTE_KEYS = {
        "name",
        "finisher",
        "persona",
        "overall",
        "attributes",
        "image",
        "record",
        "injured",
        "injury_duration",
    }

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.finisher = data.get("finisher")
        self.persona = data.get("persona")  # "Face" or "Heel"
        self.overall = data.get("overall", 0)

        self.attributes = {}
        # Flatten nested attributes first, then overlay any top-level values
        self.attributes.update(self._normalize_attribute_dict(data.get("attributes", {})))
        self.attributes.update(self._normalize_attribute_dict(data))

        for key, val in self.DEFAULT_ATTRIBUTES.items():
            self.attributes.setdefault(key, val)
            setattr(self, key, self.attributes[key])

    @classmethod
    def _normalize_attribute_key(cls, key: str):
        if not isinstance(key, str):
            return None
        normalized = cls.ATTRIBUTE_ALIASES.get(key.lower(), key.lower())
        if normalized in cls.DEFAULT_ATTRIBUTES:
            return normalized
        return None

    @classmethod
    def _normalize_attribute_dict(cls, source: dict) -> dict:
        normalized = {}
        for key, value in source.items():
            if key.lower() in cls.NON_ATTRIBUTE_KEYS:
                continue
            normalized_key = cls._normalize_attribute_key(key)
            if normalized_key:
                normalized[normalized_key] = value
        return normalized

    def get_attribute_value(self, attribute: str) -> int:
        if not attribute:
            return 0
        normalized = self._normalize_attribute_key(attribute)
        if not normalized:
            return 0
        return self.attributes.get(normalized, self.DEFAULT_ATTRIBUTES.get(normalized, 0))

    def get_match_rating(self, modifier: str = "normal") -> int:
        if modifier.lower() == "normal":
            return self.overall
        return self.overall + self.get_attribute_value(modifier)
