import random
from engine.wrestler import Wrestler

class Match:
    def __init__(self, wrestler_a_data, wrestler_b_data, match_type, game_data, assigned_roles):
        self.face = Wrestler(wrestler_a_data if assigned_roles['Face'] == wrestler_a_data['name'] else wrestler_b_data)
        self.heel = Wrestler(wrestler_b_data if self.face.name == wrestler_a_data['name'] else wrestler_a_data)
        self.match_type = match_type
        self.game_data = game_data
        self.result_log = []

    def simulate(self):
        self.result_log.clear()
        self.result_log.append("[DEBUG] Starting match simulation")

        # Step 1: Match Modifier
        modifier_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for match modifier: {modifier_roll}")
        modifier_entry = next((m for m in self.game_data["match_modifiers"] if m["roll"] == modifier_roll), None)
        modifier = modifier_entry["modifier"].lower() if modifier_entry else "normal"
        self.result_log.append(f"Match Modifier Rolled: {modifier.title()}")

        rating_face = self.face.get_match_rating(modifier)
        rating_heel = self.heel.get_match_rating(modifier)
        self.result_log.append(f"[DEBUG] Match ratings: {self.face.name}={rating_face}, {self.heel.name}={rating_heel}")

        # Step 2: Pre-Match Chart
        pre_chart_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for pre-match chart: {pre_chart_roll}")
        chart_entry = next((c for c in self.game_data["pre_match_chart"] if c["roll"] == pre_chart_roll), None)
        target_side = chart_entry["result"] if chart_entry else "Face"
        target = self.face if target_side == "Face" else self.heel

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
        if effect and effect["attribute"].lower() == "overall" and effect["duration"] == "This match only":
            if target == self.face:
                rating_face += effect["change"]
            else:
                rating_heel += effect["change"]

        self.result_log.append(f"[DEBUG] Adjusted match ratings: {self.face.name}={rating_face}, {self.heel.name}={rating_heel}")

        # Step 3: Determine Winner
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

        # Step 4: Post-Match Result
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

        # Step 5: Unusual Results
        if "Unusual" in post_result:
            unusual_data = self.game_data.get("unusual_results", {})
            unusual_pool = unusual_data.get(self.match_type, []) if isinstance(unusual_data, dict) else []
            if unusual_pool:
                unusual = random.choice(unusual_pool)
                self.result_log.append(f"Unusual Event: {unusual['description'].format(wrestler=winner.name)}")

        return "\n".join(self.result_log)

