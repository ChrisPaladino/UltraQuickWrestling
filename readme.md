# Ultra Quick Wrestling - Python Edition

A Python console simulation of **Ultra Quick Wrestling**, the fast-paced 1991-themed pro wrestling game originally published by Downey Games. This version recreates the action using real wrestler stats, dynamic match types, and storytelling logic pulled straight from the rulebook.

---

## 📦 Project Structure

ultra_quick_wrestling/
├── main.py              # Entry point for the console app
├── engine/
│   ├── __init__.py
│   ├── match.py         # Core match simulation
│   ├── wrestler.py      # Wrestler model + rating logic
│   └── data_loader.py   # Reads wrestlers.json and game_data.json
├── data/
│   ├── wrestlers.json
│   └── game_data.json
├── rules/
│   └── UltraQuickWrestling_Rules.md

---

## ▶️ Getting Started

### Requirements

- Python 3.x
- Standard Library modules only: `json`, `os`, `random`

### How to Run (Console)

From the repository root, run the console driver:

```bash
python main.py
```

You'll be prompted to:

1. Select two wrestlers from the 1991 roster (by number).
2. Resolve any duplicate personas by designating who works Face and who works Heel.
3. Choose a match type (TV Taping, PPV, Cage, No DQ, Specialty).
4. View the narrated match log in your terminal.

---

## 🧠 Rules & Logic Overview

This project implements the official UQW rules including:

- Wrestler attributes like **Savvy**, **Cheating**, **Speed**, and **Heat**
- A rule-driven flow:
  - **Match modifier roll (d10):** adjusts which attribute feeds the core rating for this bout.
  - **Pre-match chart (d10 → d100):** selects which side is targeted, applies storyline events, and can temporarily or permanently tweak ratings before the bell.
  - **Result chart (d100):** compares the adjusted Face/Heel ratings and rolls against the difference bands to determine the winner, then consults the appropriate match-type result table.
- Post-match outcomes pulled from the match-type win chart, with optional unusual results when triggered.
- Possibility of unusual or storyline-driven results (like run-ins, distractions, surprise wins).

Advanced and supplemental rules are partially implemented or planned.

---

## 🏷️ Tag Matches

Tag support treats each side as a team array and factors every member's **TAG** rating into the match formula.

- **Inputs (CLI):** Use `--tag` to enable tag mode, and pass `--team-a` / `--team-b` as comma-separated lists or JSON arrays of wrestler names. Each wrestler can define a `tag` attribute (top-level or inside `attributes`); if absent it defaults to `0` so legacy rosters still work.
- **Face/Heel assignment:** In tag mode the app will only auto-assign if every member of Team A is a Face and every member of Team B is a Heel (or vice versa). Mixed-persona teams must set `--face-team A` or `--face-team B` so the engine knows who works Face for this bout.
- **Match type selection:** `--match-type` can point to either a singles or tag win chart. When omitted, the first available tag win chart is used; if no tag charts exist the engine falls back to singles charts.

Example CLI calls:

```bash
# Two-on-two tag bout, explicit Face side
python main.py --tag \
  --team-a "Bret Hart, Jim Neidhart" \
  --team-b "[\"Ted DiBiase\",\"IRS\"]" \
  --face-team A \
  --match-type "PPV"

# Trios match using JSON arrays and a specialty chart
python main.py --tag \
  --team-a '["Road Warrior Hawk","Road Warrior Animal","Dusty Rhodes"]' \
  --team-b '["Ric Flair","Arn Anderson","Tully Blanchard"]' \
  --face-team B \
  --match-type "Specialty"
```

Example programmatic/API payload (mirrors the CLI fields):

```json
{
  "tag": true,
  "team_a": ["Bret Hart", "Jim Neidhart"],
  "team_b": ["Ted DiBiase", "IRS"],
  "match_type": "PPV",
  "face_team": "A"
}
```

---

## 🔮 Future Roadmap

- Match history log / federation tracker
- Tag Team and Battle Royale support
- Heat rating persistence
- Toggle between core and advanced rule modes
- Planned GUI exploration (design TBD; not yet shipped)

---

## ⚙️ Optional & Advanced Rules

Advanced rule handling lives in `engine/advanced_rules.py` and can be toggled when creating a `Match`. These hooks cover persistent Heat changes, rivalry escalation, injury penalties/recovery, title swaps, and simple season ticking.

### Enabling

Pass an `advanced_rules_config` dictionary (or `AdvancedRulesConfig`) into `Match`. The defaults keep everything on except for bonuses that would change ratings on clean finishes:

```python
from engine.match import Match

config = {
  "enabled": True,
  "title_on_the_line": "World Championship",  # optional
  "injury_chance": 0.15,
  "enable_seasons": True,                     # default: True
  "enable_persistent_modifiers": True,        # default: True
  "enable_title_overall_bonus": True,         # default: True
  "heat_change_on_titles": True,              # alias: heat_on_title_changes, default: True
  "clean_win_bonus": 5,                       # default: 0 (off)
  "clean_loss_penalty": 5,                    # default: 0 (off)
  "title_overall_bonus": 5,                   # default: 0 (off)
  "season_length": 12,                        # default: 12 weeks
}
match = Match(face_data, heel_data, match_type, game_data, assigned_roles, advanced_rules_config=config)
```

If `enabled` is `False` or omitted, core rules run unchanged.

### Available Toggles

- `enable_injuries` (default `True`): Apply injury penalties, decrement durations, and add new injuries based on `injury_chance`.
- `enable_titles` (default `True`): Move `title_on_the_line` between competitors.
- `enable_rivalries` (default `True`): When both wrestlers share `rivalry_id`, apply rivalry heat bonuses/penalties.
- `enable_heat` (default `True`): Persist `heat_modifier` changes per match and factor them into ratings.
- `enable_seasons` (default `True`): Track `season.current_week`/`season.length` in `data/wrestlers.json`.
- `enable_persistent_modifiers` (default `True`): Allow permanent modifiers to be written/read. Turn this off to disable rivalry heat swings, clean-finish bonuses/penalties, title sync bonuses, and ongoing heat deltas even while other advanced hooks stay active.
- `enable_title_overall_bonus` (default `True`): Gate whether held titles feed the `title_overall_bonus` into persistent `overall_modifier`.
- `heat_change_on_titles` (default `True`; alias `heat_on_title_changes`): Toggle whether title wins/losses apply `base_heat_delta` to the `heat_modifier`.

Other tunables include `injury_penalty`, `injury_duration`, `rivalry_heat_bonus`, `rivalry_heat_penalty`, and `base_heat_delta`.

#### Persistent modifiers

- Clean finishes can apply overall changes (`clean_win_bonus`, `clean_loss_penalty`), and champions can gain an overall boost (`title_overall_bonus`) and optional Heat delta (`heat_change_on_titles`). These are saved to `overall_modifier`/`heat_modifier`.
- Defaults mirror the existing behavior: persistence is on, clean bonuses/penalties are `0` (off), `title_overall_bonus` is `0` (off), and `heat_on_title_changes` is `True`.
- Persistent modifiers share the same `data/wrestlers.json` storage that `enable_seasons` uses. You can run persistent modifiers with or without seasons enabled; turning seasons off does not disable modifier persistence.
- `overall_modifier` feeds directly into a wrestler's base overall for every future match. `heat_modifier` is averaged across the side in pre-match adjustments, directly nudging the `Face`/`Heel` ratings before the result chart roll.
- Season tracking is independent but complementary: for leagues tracking weekly play, keep `enable_seasons` on so `season.current_week` ticks forward while persistent modifiers keep momentum changes between shows.

### Persisted Data

`data/wrestlers.json` now carries optional fields per wrestler:

- `titles`: list of championships held
- `rivalry_id`: identifier string shared by opponents in a feud
- `heat_modifier`: persistent heat delta applied to match ratings
- `injured` / `injury_duration`: injury tracking (backward compatible defaults provided)
- `tag`: optional rating for tag matches; defaults to `0` when missing so existing rosters remain valid.
- `overall_modifier`: long-term overall swings from clean finishes or title bonuses
- `title_overall_bonus_applied` / `title_heat_bonus_applied`: internal bookkeeping for syncing title-driven modifiers
- `season`: top-level block with `length` and `current_week` when season tracking is active.

Example structure with all advanced toggles on and clean/title bonuses enabled:

```python
advanced_rules_config = {
  "enabled": True,
  "enable_persistent_modifiers": True,
  "enable_heat": True,
  "enable_title_overall_bonus": True,
  "heat_change_on_titles": True,
  "clean_win_bonus": 5,
  "clean_loss_penalty": 5,
  "title_overall_bonus": 5,
  "enable_seasons": True,
}
```

`data/wrestlers.json` then accrues fields such as:

```json
{
  "name": "Sample Wrestler",
  "overall_modifier": 5,
  "heat_modifier": 10,
  "titles": ["World Championship"],
  "title_overall_bonus_applied": 5,
  "title_heat_bonus_applied": 5,
  "rivalry_id": "FEUD-123",
  "season": {"length": 12, "current_week": 4}
}
```

Tag-specific charts live alongside the singles data in `data/game_data.json`:

- `tag_result_chart`: Uses the same `difference` / `high_rated_wins` / `low_rated_wins` bands as singles, but tuned for team math. If omitted, it reuses the singles `result_chart` automatically.
- `tag_win_charts`: Match-type outcome tables for Faces and Heels in tag bouts. If a tag chart is missing for a type, the engine defaults to the singles `win_charts`, keeping legacy data playable.

A top-level `season` block (`length`, `current_week`) tracks booking seasons when enabled.

---

## 📚 Reference

- All rules implemented based on *Ultra Quick Wrestling* by Downey Games (© 2005)
- Wrestler data pulled from the 1991 set provided with the game

## AI Wrestler Prompts

Describe the physical appearance of this pro wrestler such that I can feed a paragraph into an AI art generation program and get a portrait. Do not include mood, or feeling - only physical descriptions. Do so in a paragraph format, not a list, not a character sheet.

This is a fictional pro wrestler named . They're a . I'd like you to estimate height (in inches) and weight (in lbs). I also need 2 suggestions they're finishing move.
