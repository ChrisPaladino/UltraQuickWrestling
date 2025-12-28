import json
import os
import random
import tempfile
from dataclasses import dataclass, field, fields
from typing import Dict, Optional


@dataclass
class AdvancedRulesConfig:
    enabled: bool = False
    enable_injuries: bool = True
    enable_titles: bool = True
    enable_rivalries: bool = True
    enable_heat: bool = True
    enable_seasons: bool = True
    enable_persistent_modifiers: bool = True
    enable_title_overall_bonus: bool = True
    clean_win_bonus: int = 0
    clean_loss_penalty: int = 0
    title_overall_bonus: int = 0
    heat_change_on_titles: bool = True
    heat_on_title_changes: Optional[bool] = None
    title_on_the_line: Optional[str] = None
    injury_chance: float = 0.15
    injury_penalty: int = -100
    injury_duration: int = 3
    rivalry_heat_bonus: int = 10
    rivalry_heat_penalty: int = -5
    base_heat_delta: int = 5
    season_length: int = 12
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self):
        if self.heat_on_title_changes is not None:
            self.heat_change_on_titles = self.heat_on_title_changes

    @classmethod
    def from_dict(cls, config: Optional[dict]) -> "AdvancedRulesConfig":
        if isinstance(config, cls):
            return config
        if not isinstance(config, dict):
            return cls()

        allowed_fields = {f.name for f in fields(cls)}
        alias_map = {"heat_on_title_changes": "heat_change_on_titles"}
        normalized: Dict[str, object] = {}
        for key, value in config.items():
            target = alias_map.get(key, key)
            if target in allowed_fields:
                normalized[target] = value
        return cls(**normalized)


class AdvancedRulesEngine:
    """
    Encapsulates optional/advanced Ultra Quick Wrestling rules:
    - Injury penalties and recovery
    - Title tracking and swaps
    - Rivalry heat adjustments
    - Persistent Heat modifiers
    - Lightweight booking season tracking
    """

    def __init__(self, wrestlers_file: str, config: Optional[dict] = None):
        self.config = AdvancedRulesConfig.from_dict(config or {})
        self.wrestlers_file = wrestlers_file
        self._roster_cache: Optional[dict] = None

    def load_roster(self) -> dict:
        if self._roster_cache is None:
            with open(self.wrestlers_file, "r") as f:
                self._roster_cache = json.load(f)
        return self._roster_cache

    def save_roster(self):
        if self._roster_cache is None:
            return

        directory = os.path.dirname(self.wrestlers_file) or "."
        fd, tmp_path = tempfile.mkstemp(prefix="wrestlers_", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w") as tmp_file:
                json.dump(self._roster_cache, tmp_file, indent=2)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp_path, self.wrestlers_file)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def _find_wrestler(self, name: str) -> Optional[dict]:
        roster = self.load_roster()
        for wrestler in roster.get("wrestlers", []):
            if wrestler.get("name") == name:
                if wrestler.get("overall_modifier") is None:
                    wrestler["overall_modifier"] = 0
                if wrestler.get("heat_modifier") is None:
                    wrestler["heat_modifier"] = 0
                if wrestler.get("titles") is None:
                    wrestler["titles"] = []
                return wrestler
        return None

    def apply_pre_match(self, face_name: str, heel_name: str, log: list) -> Dict[str, int]:
        """Apply pre-match hooks and return per-side rating adjustments."""
        adjustments = {"Face": 0, "Heel": 0}
        if not self.config.enabled:
            return adjustments

        roster = self.load_roster()
        for side, name in (("Face", face_name), ("Heel", heel_name)):
            wrestler = self._find_wrestler(name)
            if not wrestler:
                continue

            if self.config.enable_injuries and wrestler.get("injured"):
                adjustments[side] += self.config.injury_penalty
                log.append(f"[DEBUG] {name} is injured ({wrestler.get('injury_duration', 0)} weeks left), penalty {self.config.injury_penalty}")

            if self.config.enable_heat and self.config.enable_persistent_modifiers:
                heat_mod = wrestler.get("heat_modifier", 0)
                if heat_mod:
                    adjustments[side] += heat_mod
                    log.append(f"[DEBUG] {name} carries heat modifier {heat_mod:+}")

        # Initialize season tracking if desired
        if self.config.enable_seasons:
            season = roster.setdefault("season", {})
            season.setdefault("length", self.config.season_length)
            season.setdefault("current_week", 1)

        return adjustments

    def apply_post_match(self, face_name: str, heel_name: str, winner_name: str, match_type: str, post_result_entry: Optional[dict], log: list):
        """Apply post-match hooks (injuries, titles, rivalries, heat, persistent modifiers, season ticking)."""
        if not self.config.enabled:
            return

        face = self._find_wrestler(face_name)
        heel = self._find_wrestler(heel_name)
        winner = self._find_wrestler(winner_name)
        loser = heel if winner_name == face_name else face

        if self.config.enable_titles:
            self._handle_titles(winner, loser, log)

        if self.config.enable_rivalries and self.config.enable_persistent_modifiers and self.config.enable_heat:
            self._handle_rivalries(face, heel, winner, loser, log)

        if self.config.enable_heat and self.config.enable_persistent_modifiers:
            self._handle_heat(winner, loser, log)

        self._handle_modifiers(winner, loser, match_type, post_result_entry, log)

        if self.config.enable_injuries:
            self._handle_injuries(winner, loser, log)

        if self.config.enable_seasons:
            self._advance_season(log)

        self.save_roster()

    def _handle_titles(self, winner: Optional[dict], loser: Optional[dict], log: list):
        title = self.config.title_on_the_line
        if not title or not winner:
            return

        winners_titles = winner.setdefault("titles", [])
        loser_titles = loser.setdefault("titles", []) if loser is not None else []

        if title in loser_titles and title not in winners_titles:
            loser_titles.remove(title)
            winners_titles.append(title)
            log.append(f"[DEBUG] Title Match: {winner.get('name')} wins the {title}")
        elif title not in winners_titles:
            winners_titles.append(title)
            log.append(f"[DEBUG] {winner.get('name')} claims inaugural {title}")

        if self.config.enable_persistent_modifiers:
            self._sync_title_modifiers(loser, log)
            self._sync_title_modifiers(winner, log)

    def _sync_title_modifiers(self, wrestler: Optional[dict], log: list):
        """Keep title-based modifiers in sync with held titles."""
        if not wrestler or not self.config.enable_persistent_modifiers:
            return

        titles = wrestler.get("titles", [])
        applied_overall = wrestler.get("title_overall_bonus_applied", 0)
        applied_heat = wrestler.get("title_heat_bonus_applied", 0)

        expected_overall = 0
        expected_heat = 0

        if self.config.enable_title_overall_bonus:
            expected_overall = len(titles) * self.config.title_overall_bonus
        if self.config.enable_heat and self.config.heat_change_on_titles:
            expected_heat = len(titles) * self.config.base_heat_delta

        if applied_overall != expected_overall:
            wrestler["overall_modifier"] = wrestler.get("overall_modifier", 0) + (expected_overall - applied_overall)
            wrestler["title_overall_bonus_applied"] = expected_overall
            log.append(
                f"[DEBUG] Title overall bonus synced for {wrestler.get('name')}: {applied_overall:+} -> {expected_overall:+}"
            )

        if applied_heat != expected_heat:
            wrestler["heat_modifier"] = wrestler.get("heat_modifier", 0) + (expected_heat - applied_heat)
            wrestler["title_heat_bonus_applied"] = expected_heat
            log.append(
                f"[DEBUG] Title heat bonus synced for {wrestler.get('name')}: {applied_heat:+} -> {expected_heat:+}"
            )

    def _handle_rivalries(self, face: Optional[dict], heel: Optional[dict], winner: Optional[dict], loser: Optional[dict], log: list):
        if not self.config.enable_persistent_modifiers:
            return

        if not self.config.enable_heat:
            return

        if not face or not heel or not winner or not loser:
            return

        if face.get("rivalry_id") and face.get("rivalry_id") == heel.get("rivalry_id"):
            winner_heat_bonus = self.config.rivalry_heat_bonus
            loser_heat_penalty = self.config.rivalry_heat_penalty

            winner["heat_modifier"] = winner.get("heat_modifier", 0) + winner_heat_bonus
            loser["heat_modifier"] = loser.get("heat_modifier", 0) + loser_heat_penalty
            log.append(
                f"[DEBUG] Rivalry escalates (ID: {face.get('rivalry_id')}): {winner.get('name')} {winner_heat_bonus:+} heat, {loser.get('name')} {loser_heat_penalty:+}"
            )

    def _handle_heat(self, winner: Optional[dict], loser: Optional[dict], log: list):
        if not self.config.enable_persistent_modifiers:
            return

        if not self.config.enable_heat:
            return

        heat_delta = self.config.base_heat_delta
        if winner:
            winner["heat_modifier"] = winner.get("heat_modifier", 0) + heat_delta
            log.append(f"[DEBUG] {winner.get('name')} gains heat modifier {heat_delta:+}")
        if loser:
            loser["heat_modifier"] = loser.get("heat_modifier", 0) - heat_delta
            log.append(f"[DEBUG] {loser.get('name')} loses heat modifier {-heat_delta:+}")

    def _handle_modifiers(self, winner: Optional[dict], loser: Optional[dict], match_type: str, post_result_entry: Optional[dict], log: list):
        if not self.config.enable_persistent_modifiers:
            return

        result_text = (post_result_entry or {}).get("result", "") or ""
        clean_finish = "clean" in result_text.lower()

        if clean_finish and winner and self.config.clean_win_bonus:
            winner["overall_modifier"] = winner.get("overall_modifier", 0) + self.config.clean_win_bonus
            log.append(f"[DEBUG] Clean finish: {winner.get('name')} overall modifier {self.config.clean_win_bonus:+}")

        if clean_finish and loser and self.config.clean_loss_penalty:
            penalty = -abs(self.config.clean_loss_penalty)
            loser["overall_modifier"] = loser.get("overall_modifier", 0) + penalty
            log.append(f"[DEBUG] Clean finish: {loser.get('name')} overall modifier {penalty:+}")

        # Keep title-based modifiers aligned with current champions even when no swap happens.
        self._sync_title_modifiers(winner, log)
        self._sync_title_modifiers(loser, log)

    def _handle_injuries(self, winner: Optional[dict], loser: Optional[dict], log: list):
        rng = self.config.rng
        for wrestler in (winner, loser):
            if not wrestler:
                continue
            if wrestler.get("injured"):
                wrestler["injury_duration"] = max(0, wrestler.get("injury_duration", 0) - 1)
                if wrestler["injury_duration"] == 0:
                    wrestler["injured"] = False
                    log.append(f"[DEBUG] {wrestler.get('name')} recovers from injury.")

        if loser and not loser.get("injured") and rng.random() <= self.config.injury_chance:
            loser["injured"] = True
            loser["injury_duration"] = self.config.injury_duration
            log.append(
                f"[DEBUG] {loser.get('name')} suffers a new injury (duration: {self.config.injury_duration} matches)."
            )

    def _advance_season(self, log: list):
        roster = self.load_roster()
        season = roster.setdefault("season", {"length": self.config.season_length, "current_week": 1})
        season_length = season.get("length", self.config.season_length)
        season["current_week"] = (season.get("current_week", 1) % season_length) + 1
        log.append(f"[DEBUG] Season advances to week {season['current_week']} of {season_length}")
