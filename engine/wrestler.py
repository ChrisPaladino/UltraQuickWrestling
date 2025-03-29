class Wrestler:
    def __init__(self, data: dict):
        self.name = data.get("name")
        self.finisher = data.get("finisher")
        self.persona = data.get("persona")  # "Face" or "Heel"
        self.overall = data.get("overall", 0)

        # Normalize all attribute keys to lowercase
        self.attributes = {
            k.lower(): v for k, v in data.items()
            if k.lower() not in {"name", "finisher", "persona", "overall"}
        }

        # Explicitly set expected attributes (optional fallback values)
        defaults = {
            "strength": 0, "speed": 0, "savvy": 0, "technical": 0, "cheating": 0, "size": 0, "heat": 0,
            "cage": 0, "object": 0, "brawling": 0, "ladder": 0, "table": 0, "tag": 0
        }
        for key, val in defaults.items():
            self.attributes.setdefault(key, val)

    def get_match_rating(self, modifier: str = "normal") -> int:
        if modifier.lower() == "normal":
            return self.overall
        return self.overall + self.attributes.get(modifier.lower(), 0)
