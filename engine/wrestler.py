class Wrestler:
    def __init__(self, data: dict):
        self.name = data.get("name")
        self.finisher = data.get("finisher")
        self.persona = data.get("persona")  # "Face" or "Heel"
        self.overall = data.get("overall", 0)
        self.attributes = {
            "strength": data.get("strength", 0),
            "speed": data.get("speed", 0),
            "savvy": data.get("savvy", 0),
            "technical": data.get("technical", 0),
            "cheating": data.get("cheating", 0),
            "size": data.get("size", 0),
            "heat": data.get("heat", 0),
            "cage": data.get("cage", 0),
            "object": data.get("object", 0),
            "brawling": data.get("brawling", 0),
            "ladder": data.get("ladder", 0),
            "table": data.get("table", 0),
            "tag": data.get("tag", 0),
        }

    def get_match_rating(self, modifier: str = "normal") -> int:
        if modifier.lower() == "normal":
            return self.overall
        return self.overall + self.attributes.get(modifier.lower(), 0)
