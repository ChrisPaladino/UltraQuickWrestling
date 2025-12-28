import json
import os
import random
import tempfile
from engine.wrestler import Wrestler

class Match:
    def __init__(self, wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles, wrestlers_file="data/wrestlers.json"):
        self.face = Wrestler(wrestler_a_data if assigned_roles['Face'] == wrestler_a_data['name'] else wrestler_b_data)
        self.heel = Wrestler(wrestler_b_data if self.face.name == wrestler_a_data['name'] else wrestler_a_data)
        self.match_type = match_type
        self.game_data = game_data
        self.result_log = []
        self.wrestlers_file = wrestlers_file

    def simulate(self):
        self.result_log.clear()
        self.result_log.append("[DEBUG] Starting match simulation")

        # Step 1: Match Modifier
        modifier_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for match modifier: {modifier_roll}")
        modifier_entry = next((m for m in self.game_data["match_modifiers"] if m["roll"] == modifier_roll), None)
        modifier = modifier_entry["modifier"].lower() if modifier_entry else "normal"
        self.result_log.append(f"Match Modifier Rolled: {modifier.title()}")

        # Step 2: Pre-Match Chart
        pre_chart_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for pre-match chart: {pre_chart_roll}")
        chart_entry = next((c for c in self.game_data["pre_match_chart"] if c["roll"] == pre_chart_roll), None)
        target_side = chart_entry["result"] if chart_entry else "Face"
        target = self.face if target_side == "Face" else self.heel
        self.result_log.append(f"[DEBUG] Pre-match target side: {target_side}, Target Wrestler: {target.name}")

        pre_event_roll = random.randint(1, 100)
        self.result_log.append(f"[DEBUG] Rolled d100 for pre-match event: {pre_event_roll}")

        def match_roll(event):
            r = event.get("roll")
            if not r:
                return False
            if "-" in r:
                low, high = map(int, r.split("-"))
                return low <= pre_event_roll <= high
            else:
                return int(r) == pre_event_roll

        events = self.game_data["pre_match_events"][target_side]
        pre_event = next((e for e in events if match_roll(e)), None)
        if not pre_event:
            pre_event = {"event": "Normal Match", "effect": None}

        self.result_log.append(f"[DEBUG] Selected pre-match event: {pre_event}")
        desc_template = pre_event.get("description") or pre_event.get("event", "")
        desc = desc_template.format(wrestler=target.name)
        self.result_log.append(f"Pre-Match Event ({target_side}): {desc}")

        effect = pre_event.get("effect")
        match_adjustment = {"Face": 0, "Heel": 0}
        if effect:
            attr = effect.get("attribute", "").lower()
            change = effect.get("change")
            duration = effect.get("duration", "")
            apply_to = effect.get("target")

            # Temporary effects for this match
            if duration == "This match only" and isinstance(change, int):
                if attr == "overall":
                    if apply_to == "FACE":
                        match_adjustment["Face"] += change
                    elif apply_to == "HEEL":
                        match_adjustment["Heel"] += change

            # Permanent changes
            elif duration == "Permanently" and isinstance(change, int):
                self.result_log.append(f"[DEBUG] Applying permanent change: {apply_to} {attr.title()} {change:+}")
                self.apply_permanent_change(apply_to, attr, change)

        # Step 3: Calculate match ratings (AFTER applying pre-match modifiers)
        base_face = getattr(self.face, 'overall', 0)
        base_heel = getattr(self.heel, 'overall', 0)
        mod_face = getattr(self.face, modifier, 0)
        mod_heel = getattr(self.heel, modifier, 0)
        adj_face = match_adjustment["Face"]
        adj_heel = match_adjustment["Heel"]
        rating_face = base_face + mod_face + adj_face
        rating_heel = base_heel + mod_heel + adj_heel

        self.result_log.append(f"[DEBUG] Match rating formula: {self.face.name} = Overall + {modifier.title()} + Adjustment = {base_face} + {mod_face} + {adj_face} = {rating_face}")
        self.result_log.append(f"[DEBUG] Match rating formula: {self.heel.name} = Overall + {modifier.title()} + Adjustment = {base_heel} + {mod_heel} + {adj_heel} = {rating_heel}")
        self.result_log.append(f"[DEBUG] Adjusted match ratings: {self.face.name}={rating_face}, {self.heel.name}={rating_heel}")

        # Step 4: Determine Winner
        diff = abs(rating_face - rating_heel)
        self.result_log.append(f"[DEBUG] Point difference: {diff}")

        odds = None
        for entry in self.game_data["result_chart"]:
            range_str = entry.get("difference")
            if not range_str:
                continue
            start, end = map(int, range_str.split("-"))
            if start <= diff <= end:
                odds = entry
                break

        if odds is None:
            odds = {"high_rated_wins": "1-50", "low_rated_wins": "51-100"}
            self.result_log.append("[DEBUG] No matching result_chart range found, using default 50/50")

        roll = random.randint(1, 100)
        high_range = list(map(int, odds["high_rated_wins"].split("-")))
        if roll >= high_range[0] and roll <= high_range[1]:
            winner = self.face if rating_face >= rating_heel else self.heel
            winner_type = "Face" if winner == self.face else "Heel"
        else:
            winner = self.heel if rating_face >= rating_heel else self.face
            winner_type = "Heel" if winner == self.heel else "Face"

        self.result_log.append(f"Roll: {roll} → Winner: {winner.name} ({winner_type})")

        # Step 5: Post-Match Result
        post_chart = self.game_data["win_charts"].get(self.match_type, {})
        post_results = post_chart.get(winner_type, [])
        post_roll = random.randint(1, 100)
        self.result_log.append(f"[DEBUG] Rolled d100 for post-match result: {post_roll}")

        def match_post(entry):
            r = entry.get("range")
            if not r:
                return False
            start, end = map(int, r.split("-"))
            return start <= post_roll <= end

        post_result_entry = next((e for e in post_results if match_post(e)), {"result": "No post-match result."})
        post_result = post_result_entry["result"]
        self.result_log.append(f"Post-Match Result: {post_result}")

        # Step 6: Unusual Results
        if "Unusual" in post_result:
            unusual_pool = self.game_data.get("unusual_results", [])
            if unusual_pool:
                selected = random.choice(unusual_pool)
                desc = selected.get("event", "An unusual event occurs.")
                self.result_log.append(f"[DEBUG] Rolled on unusual_results")
                self.result_log.append(f"Unusual Event: {desc.format(wrestler=winner.name)}")
            else:
                self.result_log.append("[DEBUG] No unusual results available.")

        return "\n".join(self.result_log)

    @staticmethod
    def _normalize_attribute(attribute: str) -> str:
        normalized = attribute.lower()
        return Wrestler.ATTRIBUTE_SYNONYMS.get(normalized, normalized)

    @staticmethod
    def _safe_write_json(filepath: str, data: dict) -> None:
        directory = os.path.dirname(filepath) or "."
        fd, tmp_path = tempfile.mkstemp(prefix="wrestlers_", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w") as tmp_file:
                json.dump(data, tmp_file, indent=2)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp_path, filepath)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def apply_permanent_change(self, target_side, attribute, change):
        try:
            with open(self.wrestlers_file, "r") as f:
                data = json.load(f)

            wrestlers = data.get("wrestlers")
            if wrestlers is None:
                raise ValueError("Expected 'wrestlers' key in data file.")

            target_name = self.face.name if target_side == "FACE" else self.heel.name
            attribute_key = self._normalize_attribute(attribute)
            for wrestler in wrestlers:
                if wrestler.get("name") == target_name:
                    if attribute_key == "overall":
                        old_val = wrestler.get("overall", 0)
                        wrestler["overall"] = old_val + change
                    else:
                        wrestler.setdefault("attributes", {})
                        old_val = wrestler["attributes"].get(attribute_key, 0)
                        wrestler["attributes"][attribute_key] = old_val + change
                    self.result_log.append(
                        f"[DEBUG] {target_name}'s {attribute_key} permanently changed from {old_val} to {old_val + change}"
                    )
                    break
            else:
                raise ValueError(f"Wrestler named {target_name} not found.")

            self._safe_write_json(self.wrestlers_file, data)
        except Exception as e:
            self.result_log.append(f"[ERROR] Failed to update permanent change: {e}")
