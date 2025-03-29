import random
from engine.wrestler import Wrestler

class Match:
    def __init__(self, wrestler_a_data, wrestler_b_data, match_type, game_data):
        self.wrestler_a = Wrestler(wrestler_a_data)
        self.wrestler_b = Wrestler(wrestler_b_data)
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

        rating_a = self.wrestler_a.get_match_rating(modifier)
        rating_b = self.wrestler_b.get_match_rating(modifier)
        self.result_log.append(f"[DEBUG] Match ratings: {self.wrestler_a.name}={rating_a}, {self.wrestler_b.name}={rating_b}")

        # Step 2: Pre-Match Chart
        pre_chart_roll = random.randint(0, 9)
        self.result_log.append(f"[DEBUG] Rolled d10 for pre-match chart: {pre_chart_roll}")
        chart_entry = next((c for c in self.game_data["pre_match_chart"] if c["roll"] == pre_chart_roll), None)
        target_side = chart_entry["target"] if chart_entry else "Face"
        target = self.wrestler_a if self.wrestler_a.persona == target_side else self.wrestler_b
        self.result_log.append(f"[DEBUG] Pre-match target side: {target_side}, Target Wrestler: {target.name}")

        events = self.game_data["pre_match_events"][target_side]
        pre_event = random.choice(events)
        self.result_log.append(f"[DEBUG] Selected pre-match event: {pre_event}")

        if isinstance(pre_event, dict):
            desc_template = pre_event.get("description") or pre_event.get("event", str(pre_event))
            rating_bonus = pre_event.get("rating_bonus", 0)
            rating_penalty = pre_event.get("rating_penalty", 0)
        else:
            desc_template = str(pre_event)
            rating_bonus = 0
            rating_penalty = 0

        desc = desc_template.format(
            wrestler=target.name,
            roll=pre_chart_roll,
            bonus=rating_bonus,
            penalty=rating_penalty
        )
        self.result_log.append(f"Pre-Match Event ({target_side}): {desc}")

        if target == self.wrestler_a:
            rating_a += rating_bonus - rating_penalty
        else:
            rating_b += rating_bonus - rating_penalty

        self.result_log.append(f"[DEBUG] Adjusted match ratings: {self.wrestler_a.name}={rating_a}, {self.wrestler_b.name}={rating_b}")

        # Step 3: Determine Winner
        diff = abs(rating_a - rating_b)
        diff_key = str(diff)
        result_chart = self.game_data["result_chart"]
        self.result_log.append(f"[DEBUG] Point difference: {diff_key}")

        # Convert list to dict if needed (handle older format)
        if isinstance(result_chart, list):
            result_chart = {str(entry["diff"]): entry for entry in result_chart}
            result_chart["default"] = next((e for e in result_chart.values() if e.get("default")), {
                "wrestler_a": 50, "winner_type_a": "Face", "winner_type_b": "Heel"
            })

        odds = result_chart.get(diff_key, result_chart["default"])

        roll = random.randint(1, 100)
        threshold = odds["wrestler_a"]
        if roll <= threshold:
            winner = self.wrestler_a
            winner_type = odds.get("winner_type_a", "Face")
        else:
            winner = self.wrestler_b
            winner_type = odds.get("winner_type_b", "Heel")

        self.result_log.append(f"Roll: {roll} → Winner: {winner.name} ({winner_type})")

        # Step 4: Post-Match Result (handled in win_charts)
        post_chart = self.game_data["win_charts"].get(self.match_type, {})
        post_results = post_chart.get(winner_type, [])
        post_result = random.choice(post_results) if post_results else "No post-match result."
        self.result_log.append(f"Post-Match Result: {post_result}")

        # Step 5: Unusual Results
        if "Unusual" in post_result:
            unusual_pool = self.game_data["unusual_results"].get(self.match_type, [])
            if unusual_pool:
                unusual = random.choice(unusual_pool)
                self.result_log.append(f"Unusual Event: {unusual['description'].format(wrestler=winner.name)}")

        return "\n".join(self.result_log)

