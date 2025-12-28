class Wrestler:
    @staticmethod
    def _normalize_attribute_name(name: str) -> str:
        if not isinstance(name, str):
            return ""

        normalized = name.strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "tech": "technical",
            "technical": "technical",
            "brawl": "brawling",
            "brawling": "brawling",
            "foreign_object": "object",
            "object": "object",
            "overall": "overall",
            "normal": "normal",
        }

        return aliases.get(normalized, normalized)

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.finisher = data.get("finisher")
        self.persona = data.get("persona")  # "Face" or "Heel"
        self.overall = data.get("overall", 0)

        # Normalize all attribute keys to lowercase
        self.attributes = {}

        nested_attributes = data.get("attributes", {})
        if isinstance(nested_attributes, dict):
            for key, value in nested_attributes.items():
                normalized = self._normalize_attribute_name(key)
                self.attributes[normalized] = value

        for key, value in data.items():
            normalized = self._normalize_attribute_name(key)
            if normalized in {"name", "finisher", "persona", "overall", "attributes"}:
                continue
            if isinstance(value, dict):
                continue
            self.attributes[normalized] = value

        # Explicitly set expected attributes (optional fallback values)
        defaults = {
            "strength": 0, "speed": 0, "savvy": 0, "technical": 0, "cheating": 0, "size": 0, "heat": 0,
            "cage": 0, "object": 0, "brawling": 0, "ladder": 0, "table": 0, "tag": 0
        }
        for key, val in defaults.items():
            self.attributes.setdefault(key, val)

    def get_match_rating(self, modifier: str = "normal") -> int:
        return self.overall + self.get_attribute_bonus(modifier)

    def get_attribute_bonus(self, modifier: str) -> int:
        normalized = self._normalize_attribute_name(modifier)
        if normalized == "normal":
            return 0
        return self.attributes.get(normalized, 0)
