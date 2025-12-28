import json
import os
import random
import tempfile
from typing import Iterable, List, Sequence

from engine.wrestler import Wrestler
from engine.advanced_rules import AdvancedRulesEngine, AdvancedRulesConfig


class TagTeam:
    """Represents a team of wrestlers competing together."""

    def __init__(self, wrestlers: Sequence[dict], side: str):
        if not isinstance(wrestlers, Iterable) or isinstance(wrestlers, (str, bytes)):
            raise ValueError("TagTeam expects an iterable of wrestler data")

        self.members: List[Wrestler] = [Wrestler(w) for w in wrestlers]
        if not self.members:
            raise ValueError("TagTeam requires at least one member")

        self.side = side
        self.name = " & ".join([member.name for member in self.members])
        self.persona = side
        self.state = {
            "momentum": sum((wrestler.get("heat_modifier") or 0) for wrestler in wrestlers),
            "injured_members": [wrestler.get("name") for wrestler in wrestlers if wrestler.get("injured")],
        }

    @property
    def member_names(self) -> List[str]:
        return [member.name for member in self.members]

    def get_base_overall(self) -> float:
        total = sum(member.get_base_overall() for member in self.members)
        return total / len(self.members)

    def get_attribute_value(self, attribute: str) -> float:
        total = sum(member.get_attribute_value(attribute) for member in self.members)
        return total / len(self.members)

    def get_tag_bonus(self) -> float:
        return self.get_attribute_value("tag")


class Match:
    def __init__(self, wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles, wrestlers_file="data/wrestlers.json", advanced_rules_config=None):
        self.face = Wrestler(wrestler_a_data if assigned_roles['Face'] == wrestler_a_data['name'] else wrestler_b_data)
        self.heel = Wrestler(wrestler_b_data if self.face.name == wrestler_a_data['name'] else wrestler_a_data)
        self._init_common(match_type, game_data, wrestlers_file, advanced_rules_config)

    def _init_common(self, match_type, game_data, wrestlers_file="data/wrestlers.json", advanced_rules_config=None):
        self.match_type = match_type
        self.game_data = game_data
        self.result_log = []
        self.wrestlers_file = wrestlers_file
        if isinstance(advanced_rules_config, AdvancedRulesConfig):
            self.advanced_config = advanced_rules_config
        else:
            self.advanced_config = AdvancedRulesConfig.from_dict(advanced_rules_config or {})
        self.advanced_rules = AdvancedRulesEngine(self.wrestlers_file, self.advanced_config) if self.advanced_config.enabled else None

    def _competitor_names(self, competitor) -> List[str]:
        if hasattr(competitor, "member_names"):
            return getattr(competitor, "member_names")
        return [competitor.name]

    def _rating_components(self, competitor, modifier: str, adjustment: float):
        base = competitor.get_base_overall()
        mod_value = 0 if modifier == "normal" else competitor.get_attribute_value(modifier)
        return {"base": base, "tag": 0, "modifier": mod_value, "adjustment": adjustment}

    def _format_rating_debug(self, competitor_name: str, display_modifier: str, components: dict) -> str:
        base = components["base"]
        mod = components["modifier"]
        tag = components.get("tag", 0)
        adj = components["adjustment"]
        rating = base + mod + tag + adj

        if tag:
            return (
                f"[DEBUG] Match rating formula: {competitor_name} = Overall + Tag + {display_modifier} + Adjustment = "
                f"{base} + {tag} + {mod} + {adj} = {rating}"
            )

        return (
            f"[DEBUG] Match rating formula: {competitor_name} = Overall + {display_modifier} + Adjustment = "
            f"{base} + {mod} + {adj} = {rating}"
        )

    def simulate(self):
        self.result_log.clear()
        self.result_log.append("[DEBUG] Starting match simulation")

        # Step 1: Match Modifier
        modifier_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for match modifier: {modifier_roll}")
        modifier_entry = next((m for m in self.game_data["match_modifiers"] if m["roll"] == modifier_roll), None)
        modifier_raw = modifier_entry["modifier"] if modifier_entry else "normal"
        modifier = Wrestler.normalize_attribute_name(modifier_raw) or "normal"
        display_modifier = modifier.replace("_", " ").title()
        self.result_log.append(f"Match Modifier Rolled: {display_modifier}")

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
        if self.advanced_rules:
            advanced_adjustment = self.advanced_rules.apply_pre_match(
                self._competitor_names(self.face), self._competitor_names(self.heel), self.result_log
            )
            for side, delta in advanced_adjustment.items():
                match_adjustment[side] += delta
        if effect:
            attr = Wrestler.normalize_attribute_name(effect.get("attribute", ""))
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
        face_components = self._rating_components(self.face, modifier, match_adjustment["Face"])
        heel_components = self._rating_components(self.heel, modifier, match_adjustment["Heel"])
        rating_face = sum(face_components.values())
        rating_heel = sum(heel_components.values())

        self.result_log.append(self._format_rating_debug(self.face.name, display_modifier, face_components))
        self.result_log.append(self._format_rating_debug(self.heel.name, display_modifier, heel_components))
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

        if self.advanced_rules:
            self.advanced_rules.apply_post_match(
                self._competitor_names(self.face),
                self._competitor_names(self.heel),
                self._competitor_names(winner),
                self.match_type,
                post_result_entry,
                self.result_log,
            )

        return "\n".join(self.result_log)

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

            target = self.face if target_side == "FACE" else self.heel
            target_names = self._competitor_names(target)
            attribute_key = Wrestler.normalize_attribute_name(attribute)
            found = False
            for wrestler in wrestlers:
                if wrestler.get("name") in target_names:
                    found = True
                    if attribute_key == "overall":
                        old_val = wrestler.get("overall", 0)
                        wrestler["overall"] = old_val + change
                    else:
                        wrestler.setdefault("attributes", {})
                        old_val = wrestler["attributes"].get(attribute_key, 0)
                        wrestler["attributes"][attribute_key] = old_val + change
                    self.result_log.append(
                        f"[DEBUG] {wrestler.get('name')}'s {attribute_key} permanently changed from {old_val} to {old_val + change}"
                    )
            if not found:
                missing = ", ".join(target_names)
                raise ValueError(f"Wrestler named {missing} not found.")

            self._safe_write_json(self.wrestlers_file, data)
        except Exception as e:
            self.result_log.append(f"[ERROR] Failed to update permanent change: {e}")


class TagMatch(Match):
    def __init__(self, face_team_data, heel_team_data, match_type, game_data, assigned_roles=None, wrestlers_file="data/wrestlers.json", advanced_rules_config=None):
        self._init_common(match_type, game_data, wrestlers_file, advanced_rules_config)
        self.face = TagTeam(face_team_data, "Face")
        self.heel = TagTeam(heel_team_data, "Heel")
        self.assigned_roles = assigned_roles or {"Face": self.face.member_names, "Heel": self.heel.member_names}

    def _rating_components(self, competitor, modifier: str, adjustment: float):
        base = competitor.get_base_overall()
        tag_bonus = competitor.get_tag_bonus()
        mod_value = 0 if modifier == "normal" else competitor.get_attribute_value(modifier)
        return {"base": base, "tag": tag_bonus, "modifier": mod_value, "adjustment": adjustment}


def create_match(wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles=None, tag_match=False, **kwargs):
    """
    Factory to create a singles or tag match based on the provided inputs.

    - If both wrestler inputs are sequences (teams) or tag_match=True, a TagMatch is created.
    - Otherwise, a standard Match is created.
    """
    if tag_match or (isinstance(wrestler_a_data, (list, tuple)) and isinstance(wrestler_b_data, (list, tuple))):
        return TagMatch(
            wrestler_a_data,
            wrestler_b_data,
            match_type,
            game_data,
            assigned_roles=assigned_roles or {},
            **kwargs,
        )

    if assigned_roles is None:
        raise ValueError("assigned_roles is required for singles matches")

    return Match(wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles, **kwargs)
